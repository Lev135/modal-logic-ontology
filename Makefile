.DEFAULT_GOAL := help

FILE ?= viz/main.dl

clean:
	rm -rf out/

souffle: out/libfunctors.so
	@mkdir -p out/declared/
	@mkdir -p out/all_logics/
	@mkdir -p out/norm_approximation/
	@mkdir -p out/norm_complexity/
	souffle -L out/ -l functors src/$(FILE) -F src/ -D out/
	@echo "Sorting all CSV files in out/ and its subdirectories..."
	@find out -type f -name "*.csv" -exec sh -c ' \
		for file do \
			sort -o "$$file" "$$file"; \
		done' _ {} +
	python3 scripts/checker.py

viz: souffle
	python3 scripts/viz.py

viz: FILE=viz/main.dl

out/libfunctors.so: functors/functors.cpp
	@mkdir -p out/
	g++ -O3 -fPIC -shared -o out/libfunctors.so functors/functors.cpp

help:
	@echo "Available commands:"
	@echo "  make clean - Remove /out directory and all its content"
	@echo "  make souffle - Run souffle on file src/FILE (src/viz/main.dl by default) "
	@echo "  make viz     - Run souffle on src/viz.dl and then generate visualization"
