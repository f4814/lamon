.PHONY: build
build: install
	poetry build

.PHONY: install
install: 
	poetry install

.PHONY: test
test:
	poetry run python -m unittest discover	

.PHONY: clean
clean:
	rm -rf lamon.egg-info dist lamon/test.db

.PHONY: run
run:
	FLASK_APP=lamon FLASK_ENV=development poetry run flask run

.PHONY: html
html:
	poetry run sphinx-build -b html docs docs/_build

.PHONY: init
init:
	FLASK_APP=lamon poetry run flask db init
	FLASK_APP=lamon poetry run flask db migrate
	FLASK_APP=lamon poetry run flask db upgrade
	FLASK_APP=lamon poetry run flask user create admin 123
	FLASK_APP=lamon poetry run flask role create admin
	FLASK_APP=lamon poetry run flask user add_role admin admin
