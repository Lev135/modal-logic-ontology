.DEFAULT_GOAL := help

FILE ?= main.dl

clean:
	rm -rf out/

souffle:
	@mkdir -p out/
	souffle src/$(FILE) -F src/ -D out/

viz: souffle
	python3 scripts/viz.py

viz: FILE=viz.dl


help:
	@echo "Available commands:"
	@echo "  make clean - Remove /out directory and all its content"
	@echo "  make souffle - Run souffle on file src/FILE (src/main.dl by default) "
	@echo "  make viz     - Run souffle on src/viz.dl and then generate visualization"
