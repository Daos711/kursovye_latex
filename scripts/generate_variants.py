#!/usr/bin/env python3
"""
Генератор рабочих директорий для курсовых работ.

Использование:
    python generate_variants.py              # все 12 вариантов из VARIANTS
    python generate_variants.py 1 5 11       # конкретные варианты
    python generate_variants.py --list       # показать таблицу всех 30 вариантов
    python generate_variants.py --add 25     # добавить новый вариант в существующий проект
"""

import os
import sys
import shutil

# ==============================================================
# ТАБЛИЦА ВСЕХ 30 ВАРИАНТОВ
# ==============================================================

GEOMETRIES = {
    'A': {'R': 0.035, 'R_mm': 35, 'c': 0.00005, 'c_mkm': 50,
           'L': 0.056, 'L_mm': 56, 'LD': 0.8},
    'B': {'R': 0.050, 'R_mm': 50, 'c': 0.00007, 'c_mkm': 70,
           'L': 0.080, 'L_mm': 80, 'LD': 0.8},
    'C': {'R': 0.025, 'R_mm': 25, 'c': 0.00003, 'c_mkm': 30,
           'L': 0.040, 'L_mm': 40, 'LD': 0.8},
}

DIMPLE_TYPES = {
    1:  {'name': 'Эллипсоидальный',
         'genitive': 'эллипсоидальными',
         'a': 0.00241, 'a_mm': 2.41, 'b': 0.002214, 'b_mm': 2.214,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \sqrt{1 - \left(\frac{\Delta\varphi}{b}\right)^2 - \left(\frac{\Delta Z}{a}\right)^2}'},
    2:  {'name': 'Параболический',
         'genitive': 'параболическими',
         'a': 0.00250, 'a_mm': 2.50, 'b': 0.002300, 'b_mm': 2.300,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \left[1 - \left(\frac{\Delta\varphi}{b}\right)^2 - \left(\frac{\Delta Z}{a}\right)^2\right]'},
    3:  {'name': 'Цилиндрический',
         'genitive': 'цилиндрическими',
         'a': 0.00240, 'a_mm': 2.40, 'b': 0.002200, 'b_mm': 2.200,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \text{ при } r^2 \leq 1'},
    4:  {'name': 'Эллиптический цилиндр со скруглением',
         'genitive': 'эллиптико-цилиндрическими',
         'a': 0.00245, 'a_mm': 2.45, 'b': 0.002250, 'b_mm': 2.250,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \text{ при } r\leq0.7;\; h_p\cos^2[\pi(r-0.7)/0.6] \text{ при } 0.7<r\leq1'},
    5:  {'name': 'Сферическая шапка',
         'genitive': 'сферическими',
         'a': 0.00230, 'a_mm': 2.30, 'b': 0.002300, 'b_mm': 2.300,
         'hp': 0.000012, 'hp_mkm': 12,
         'formula': r'\Delta h(\rho) = \sqrt{R_s^2 - \rho^2} - \sqrt{R_s^2 - r_0^2}'},
    6:  {'name': 'Конический',
         'genitive': 'коническими',
         'a': 0.00235, 'a_mm': 2.35, 'b': 0.002150, 'b_mm': 2.150,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \left(1 - r\right)'},
    7:  {'name': 'Суперэллиптический',
         'genitive': 'суперэллиптическими',
         'a': 0.00255, 'a_mm': 2.55, 'b': 0.002350, 'b_mm': 2.350,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \sqrt{1 - r^4}'},
    8:  {'name': 'Плоскодонный с фаской',
         'genitive': 'плоскодонными',
         'a': 0.00242, 'a_mm': 2.42, 'b': 0.002220, 'b_mm': 2.220,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \text{ при } r\leq0.6;\; h_p(1-r)/0.4 \text{ при } 0.6<r\leq1'},
    9:  {'name': 'Комбинированный двухуровневый',
         'genitive': 'комбинированными',
         'a': 0.00248, 'a_mm': 2.48, 'b': 0.002280, 'b_mm': 2.280,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \text{ при } r\leq0.5;\; 0.6h_p \text{ при } 0.5<r\leq0.8'},
    10: {'name': 'Трапецеидальный',
         'genitive': 'трапецеидальными',
         'a': 0.00238, 'a_mm': 2.38, 'b': 0.002180, 'b_mm': 2.180,
         'hp': 0.00001, 'hp_mkm': 10,
         'formula': r'\Delta h = h_p \text{ при } r_\infty\leq0.6;\; h_p(1-r_\infty)/0.4 \text{ при } r_\infty>0.6'},
}


def get_variant_info(var_num):
    """Возвращает словарь с параметрами варианта 1-30."""
    if not 1 <= var_num <= 30:
        raise ValueError(f"Номер варианта {var_num} вне диапазона 1-30")
    geom_idx = (var_num - 1) // 10
    dimple_type = (var_num - 1) % 10 + 1
    geom_letter = 'ABC'[geom_idx]
    geom = GEOMETRIES[geom_letter]
    dimple = DIMPLE_TYPES[dimple_type]
    hp_ratio = dimple['hp'] / geom['c']
    return {
        'number': var_num,
        'geom_letter': geom_letter,
        'dimple_type': dimple_type,
        **{f'geom_{k}': v for k, v in geom.items()},
        **{f'dimple_{k}': v for k, v in dimple.items()},
        'hp_ratio': f'{hp_ratio:.1f}',
    }


def generate_config_tex(info, student='', group='', supervisor=''):
    return f"""%% ==============================================================
%% КОНФИГУРАЦИЯ — Вариант {info['number']}
%% Геометрия {info['geom_letter']}, тип {info['dimple_type']} ({info['dimple_name']})
%% Сгенерировано автоматически — не редактировать вручную
%% ==============================================================

% --- Информация о студенте ---
\\newcommand{{\\varNumber}}{{{info['number']}}}
\\newcommand{{\\varStudent}}{{{student or 'Фамилия~И.О.'}}}
\\newcommand{{\\varGroup}}{{{group or 'ЗНБ21-02Б'}}}
\\newcommand{{\\varSupervisor}}{{{supervisor or 'Башмур~К.А.'}}}

% --- Геометрия подшипника (геометрия {info['geom_letter']}) ---
\\newcommand{{\\varR}}{{{info['geom_R']}}}
\\newcommand{{\\varRmm}}{{{info['geom_R_mm']}}}
\\newcommand{{\\varC}}{{{info['geom_c']}}}
\\newcommand{{\\varCmkm}}{{{info['geom_c_mkm']}}}
\\newcommand{{\\varL}}{{{info['geom_L']}}}
\\newcommand{{\\varLmm}}{{{info['geom_L_mm']}}}
\\newcommand{{\\varLD}}{{{info['geom_LD']}}}
\\newcommand{{\\varGeomLetter}}{{{info['geom_letter']}}}

% --- Тип микрорельефа (тип {info['dimple_type']}) ---
\\newcommand{{\\varDimpleType}}{{{info['dimple_type']}}}
\\newcommand{{\\varDimpleTypeName}}{{{info['dimple_name']}}}
\\newcommand{{\\varDimpleTypeGenitive}}{{{info['dimple_genitive']}}}

% --- Параметры микрорельефа ---
\\newcommand{{\\varDimpleA}}{{{info['dimple_a']}}}
\\newcommand{{\\varDimpleAmm}}{{{info['dimple_a_mm']}}}
\\newcommand{{\\varDimpleB}}{{{info['dimple_b']}}}
\\newcommand{{\\varDimpleBmm}}{{{info['dimple_b_mm']}}}
\\newcommand{{\\varDimpleHp}}{{{info['dimple_hp']}}}
\\newcommand{{\\varDimpleHpmkm}}{{{info['dimple_hp_mkm']}}}
\\newcommand{{\\varDimpleHpRatio}}{{{info['hp_ratio']}}}

% --- Формула зазора ---
\\newcommand{{\\varDimpleFormula}}{{
    {info['dimple_formula']}
}}

% --- Общие параметры ---
\\newcommand{{\\varN}}{{2980}}
\\newcommand{{\\varEta}}{{0.01105}}
\\newcommand{{\\varNphi}}{{8}}
\\newcommand{{\\varNZ}}{{11}}
\\newcommand{{\\varPhiRange}}{{$90^\\circ \\div 270^\\circ$}}
"""


def create_variant_dir(var_num, base_dir='variants', student='', group='', supervisor=''):
    info = get_variant_info(var_num)
    var_dir = os.path.join(base_dir, f'var_{var_num:02d}')
    os.makedirs(os.path.join(var_dir, 'figures'), exist_ok=True)

    # config.tex
    with open(os.path.join(var_dir, 'config.tex'), 'w', encoding='utf-8') as f:
        f.write(generate_config_tex(info, student, group, supervisor))

    # main.tex
    shutil.copy2('templates/main_template.tex', os.path.join(var_dir, 'main.tex'))

    # ch2_calculation.tex (только если не существует — не перезаписываем работу!)
    ch2_path = os.path.join(var_dir, 'ch2_calculation.tex')
    if not os.path.exists(ch2_path):
        shutil.copy2('templates/ch2_calculation_template.tex', ch2_path)

    print(f"  Вариант {var_num:2d}: геом. {info['geom_letter']}, "
          f"тип {info['dimple_type']:2d} ({info['dimple_name']:<40s}) "
          f"-> {var_dir}/  [{student or '—'}]")


def print_variants_table():
    print(f"\n{'№':>3s}  {'Геом':>4s}  {'R,мм':>5s}  {'c,мкм':>6s}  {'L,мм':>5s}  "
          f"{'Тип':>3s}  {'Описание'}")
    print('-' * 75)
    for v in range(1, 31):
        info = get_variant_info(v)
        print(f"{v:3d}  {info['geom_letter']:>4s}  {info['geom_R_mm']:5d}  "
              f"{info['geom_c_mkm']:6d}  {info['geom_L_mm']:5d}  "
              f"{info['dimple_type']:3d}  {info['dimple_name']}")


# ==============================================================
# СТУДЕНТЫ ГРУППЫ ЗНБ21-02Б
# Формат: вариант: ('ФИО в LaTeX', 'Группа', 'Руководитель')
# ==============================================================
STUDENTS = {
     1: ('Востриков~Я.В.',    'ЗНБ21-02Б', 'Башмур~К.А.'),
     3: ('Грицких~Т.А.',     'ЗНБ21-02Б', 'Башмур~К.А.'),
     5: ('Золотухин~А.Г.',   'ЗНБ21-02Б', 'Башмур~К.А.'),
    11: ('Михайловский~А.В.', 'ЗНБ21-02Б', 'Башмур~К.А.'),
    12: ('Мысягин~А.И.',     'ЗНБ21-02Б', 'Башмур~К.А.'),
    13: ('Плотников~А.М.',   'ЗНБ21-02Б', 'Башмур~К.А.'),
    15: ('Ребров~Е.В.',      'ЗНБ21-02Б', 'Башмур~К.А.'),
    17: ('Рудчик~К.Е.',      'ЗНБ21-02Б', 'Башмур~К.А.'),
    18: ('Семёнов~Е.А.',     'ЗНБ21-02Б', 'Башмур~К.А.'),
    19: ('Строгов~М.М.',     'ЗНБ21-02Б', 'Башмур~К.А.'),
    20: ('Фисин~С.В.',       'ЗНБ21-02Б', 'Башмур~К.А.'),
    23: ('Шиян~Е.А.',        'ЗНБ21-02Б', 'Башмур~К.А.'),
}

VARIANTS = sorted(STUDENTS.keys())


if __name__ == '__main__':
    if '--list' in sys.argv:
        print_variants_table()
        sys.exit(0)

    if '--add' in sys.argv:
        idx = sys.argv.index('--add')
        variants = [int(x) for x in sys.argv[idx+1:]]
        print(f"Добавление вариантов: {variants}\n")
    elif len(sys.argv) > 1:
        variants = [int(x) for x in sys.argv[1:]]
    else:
        variants = VARIANTS

    print(f"Генерация {len(variants)} вариантов: {variants}\n")

    for v in variants:
        si = STUDENTS.get(v, ('', '', ''))
        create_variant_dir(v, student=si[0], group=si[1] if si[1] else '',
                          supervisor=si[2] if len(si) > 2 and si[2] else '')

    print(f"\nГотово! {len(variants)} директорий в variants/")
    print("\nДля добавления нового варианта:")
    print("  python generate_variants.py --add 25")
