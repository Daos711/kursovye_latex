# Сборка курсовых работ
# make generate        — создать директории 12 вариантов
# make calc_01         — запустить расчёт варианта 1
# make pdf_01          — скомпилировать PDF варианта 1
# make all_calc        — расчёт всех вариантов
# make all_pdf         — PDF всех вариантов
# make clean           — удалить временные файлы LaTeX

GRID ?= 500
VARIANTS = $(shell ls -d variants/var_* 2>/dev/null | sed 's/variants\/var_//')

.PHONY: generate clean all_calc all_pdf

generate:
	cd scripts && python3 generate_variants.py

calc_%:
	python3 run_variant.py $* --grid $(GRID)

pdf_%:
	cd variants/var_$* && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex

all_calc:
	python3 run_variant.py --all --grid $(GRID)

all_pdf: $(addprefix pdf_, $(VARIANTS))

clean:
	find variants/ -name "*.aux" -o -name "*.log" -o -name "*.toc" \
	    -o -name "*.out" -o -name "*.synctex.gz" -o -name "*.fls" \
	    -o -name "*.fdb_latexmk" | xargs rm -f 2>/dev/null || true
