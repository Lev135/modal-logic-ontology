.DEFAULT_GOAL := help

FILE ?= main.dl

clean:
	rm -rf out/

souffle:
	@mkdir -p out/
	@mkdir -p out/declared/
	@mkdir -p out/all_logics/
	@mkdir -p out/norm_approximation/
	@mkdir -p out/norm_complexity/
	souffle src/$(FILE) -F src/ -D out/
	python3 scripts/checker.py

viz: souffle
	python3 scripts/viz.py

viz: FILE=viz/main.dl


help:
	@echo "Available commands:"
	@echo "  make clean - Remove /out directory and all its content"
	@echo "  make souffle - Run souffle on file src/FILE (src/main.dl by default) "
	@echo "  make viz     - Run souffle on src/viz.dl and then generate visualization"
