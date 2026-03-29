# Курсовые работы: Анализ дискретного микрорельефа подшипника скольжения

Группа **ЗНБ21-02Б**, руководитель **Башмур К.А.**, 12 вариантов.

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. (Опционально) Установить GPU-солвер (требует NVIDIA CUDA + CuPy)
pip install cupy-cuda12x
pip install -e ./reynolds_solver

# 3. Запустить расчёт для одного варианта
python run_variant.py 1

# 4. Запустить расчёт для всех вариантов
python run_variant.py --all

# 5. Открыть в VS Code
code kursovye.code-workspace

# 6. Скомпилировать PDF
cd variants/var_01 && pdflatex main.tex && pdflatex main.tex
```

## Структура проекта

```
kursovye/
├── bearing_solver/          # Расчётное ядро (10 типов углублений)
│   ├── variants.py          #   30 вариантов заданий
│   ├── geometry.py          #   10 функций профиля микрорельефа
│   ├── solver.py            #   Решатель Рейнольдса (GPU → CPU fallback)
│   └── postprocess.py       #   F, μ, Q + графики
│
├── reynolds_solver/         # GPU-бэкенд (CuPy/CUDA, Red-Black SOR)
│   ├── solver.py            #   GPU-солвер с кэшированием буферов
│   ├── kernels.py           #   CUDA C ядра
│   └── api.py               #   Единый интерфейс solve_reynolds()
│
├── shared/                  # Общий LaTeX-контент (пишется 1 раз)
│   ├── preamble.tex         #   преамбула
│   ├── bibliography.tex     #   библиографический список
│   ├── sections/
│   │   ├── titlepage.tex    #   титульный лист (параметризованный)
│   │   ├── introduction.tex #   введение
│   │   ├── ch1_theory.tex   #   Глава 1: теория + мат. модель
│   │   └── conclusion.tex   #   заключение
│   └── figures/             #   иллюстрации из методички
│
├── variants/                # 12 вариантов студентов
│   ├── var_01/              #   Востриков Я.В. — эллипсоидальный, геом. A
│   │   ├── main.tex         #     ← компилировать этот файл
│   │   ├── config.tex       #     параметры (R, c, L, тип, ФИО)
│   │   ├── ch2_calculation.tex  # расчётная часть (заполнить!)
│   │   └── figures/         #     графики (генерируются run_variant.py)
│   ├── var_03/              #   Грицких Т.А.
│   ├── var_05/              #   Золотухин А.Г.
│   ├── var_11/              #   Михайловский А.В.
│   ├── var_12/              #   Мысягин А.И.
│   ├── var_13/              #   Плотников А.М.
│   ├── var_15/              #   Ребров Е.В.
│   ├── var_17/              #   Рудчик К.Е.
│   ├── var_18/              #   Семёнов Е.А.
│   ├── var_19/              #   Строгов М.М.
│   ├── var_20/              #   Фисин С.В.
│   └── var_23/              #   Шиян Е.А.
│
├── templates/               # Шаблоны (для генерации новых вариантов)
├── scripts/
│   └── generate_variants.py # Генератор директорий
├── run_variant.py           # Запуск расчёта
├── Makefile                 # make calc_01, make pdf_01
└── kursovye.code-workspace  # Для VS Code
```

## Как устроено переключение GPU/CPU

`bearing_solver/solver.py` автоматически определяет бэкенд:

1. Если установлен `reynolds_solver` (+ CuPy + CUDA) → GPU, **~65x быстрее**
2. Иначе → CPU через Numba JIT

Интерфейс одинаковый: `solve_reynolds(H, d_phi, d_Z, R, L) → (P, delta, n_iter)`

## Расширение проекта (добавление нового варианта)

```bash
# 1. Добавить в scripts/generate_variants.py:
STUDENTS[25] = ('Новиков~Н.Н.', 'ЗНБ21-02Б', 'Башмур~К.А.')

# 2. Сгенерировать директорию:
python scripts/generate_variants.py --add 25

# 3. Запустить расчёт:
python run_variant.py 25

# 4. Скомпилировать PDF:
cd variants/var_25 && pdflatex main.tex && pdflatex main.tex
```

## Порядок работы с каждым вариантом

1. `python run_variant.py N` — расчёт, графики → `variants/var_N/figures/`
2. Открыть `variants/var_N/ch2_calculation.tex`:
   - раскомментировать `\includegraphics` (убрать `\fbox{...}`)
   - заполнить таблицы числами из `results.csv`
   - написать анализ
3. `cd variants/var_N && pdflatex main.tex && pdflatex main.tex`
