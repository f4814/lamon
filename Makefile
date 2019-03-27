.PHONY: build
build:
	poetry build

.PHONY: install
install: build
	poetry install

.PHONY: test
test:
	poetry run python -m unittest discover	

.PHONY: clean
clean:
	rm -rf dist

.PHONY: run
run:
	FLASK_APP=lamon FLASK_ENV=development poetry run flask run
