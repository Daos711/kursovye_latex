#!/usr/bin/env python3
"""
Запуск расчёта для одного или нескольких вариантов курсовых работ.

Использование:
    python run_variant.py 1              # один вариант
    python run_variant.py 1 5 11 23      # несколько вариантов
    python run_variant.py --all          # все варианты из STUDENTS
    python run_variant.py 1 --grid 300   # вариант 1 на сетке 300×300

Результаты сохраняются в variants/var_XX/figures/ и variants/var_XX/results.csv
"""

import sys
import os
import time

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from bearing_solver.variants import get_variant
from bearing_solver.geometry import make_grid, compute_depression_centers
from bearing_solver.postprocess import (
    run_stage1_3d,
    run_stage2_epsilon_sweep,
    save_results,
)


def run_one_variant(var_num, grid_size=500, output_dir=None):
    """Полный расчёт одного варианта: 3D-поля + перебор по ε."""
    params = get_variant(var_num)

    if output_dir is None:
        output_dir = os.path.join('variants', f'var_{var_num:02d}', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    dep_name = params['depression_name']
    geom = params['geometry_key']

    print(f"\n{'='*60}")
    print(f"  Вариант {var_num}: геометрия {geom}, тип {params['depression_type']} ({dep_name})")
    print(f"  R={params['R']*1000:.0f} мм, c={params['c']*1e6:.0f} мкм, L={params['L']*1000:.0f} мм")
    print(f"  Сетка: {grid_size}×{grid_size}")
    print(f"{'='*60}")

    t0 = time.time()

    # Этап 1: 3D-поля при ε=0.6
    def progress(key, val):
        if key == 'log':
            print(f"  [{time.time()-t0:6.1f}s] {val}")

    print("\n  Этап 1: расчёт 3D-полей (ε = 0.6)...")
    stage1 = run_stage1_3d(params, epsilon_3d=0.6,
                           num_phi=grid_size, num_Z=grid_size,
                           progress_callback=progress)

    print(f"\n  Результаты при ε = 0.6:")
    print(f"    Гладкий:     F = {stage1['F_nd_3d']:.1f} Н,  μ = {stage1['mu_nd_3d']:.6f},  Q = {stage1['Q_nd_3d']:.4f} л/с")
    print(f"    С углубл.:   F = {stage1['F_dep_3d']:.1f} Н,  μ = {stage1['mu_dep_3d']:.6f},  Q = {stage1['Q_dep_3d']:.4f} л/с")

    dF = (stage1['F_dep_3d'] - stage1['F_nd_3d']) / stage1['F_nd_3d'] * 100
    dmu = (stage1['mu_dep_3d'] - stage1['mu_nd_3d']) / stage1['mu_nd_3d'] * 100
    dQ = (stage1['Q_dep_3d'] - stage1['Q_nd_3d']) / stage1['Q_nd_3d'] * 100
    print(f"    ΔF = {dF:+.2f}%,  Δμ = {dmu:+.2f}%,  ΔQ = {dQ:+.2f}%")

    # Этап 2: перебор по ε
    print(f"\n  Этап 2: перебор по ε (15 точек)...")
    result = run_stage2_epsilon_sweep(params, stage1, n_jobs=1,
                                      progress_callback=progress)

    # Сохранение
    print(f"\n  Сохранение графиков в {output_dir}/")
    save_results(result, params, output_dir)

    elapsed = time.time() - t0
    print(f"\n  Вариант {var_num} завершён за {elapsed:.1f} с ({elapsed/60:.1f} мин)")

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    grid_size = 500
    if '--grid' in sys.argv:
        idx = sys.argv.index('--grid')
        grid_size = int(sys.argv[idx + 1])
        sys.argv = sys.argv[:idx] + sys.argv[idx+2:]

    if '--all' in sys.argv:
        from scripts.generate_variants import VARIANTS
        variants = VARIANTS
    else:
        variants = [int(x) for x in sys.argv[1:]]

    print(f"Расчёт вариантов: {variants}")
    print(f"Сетка: {grid_size}×{grid_size}")

    t_total = time.time()
    for v in variants:
        try:
            run_one_variant(v, grid_size=grid_size)
        except Exception as e:
            print(f"\n  ОШИБКА в варианте {v}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"  Все расчёты завершены за {(time.time()-t_total)/60:.1f} мин")
    print(f"{'='*60}")
