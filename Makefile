.PHONY: build
build:
	poetry build

.PHONY: install
install: build
	poetry install

.PHONY: test
test:
	python -m unittest discover	

.PHONY: clean
clean:
	rm -rf dist
