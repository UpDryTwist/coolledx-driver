
.PHONY: help setup install test unit check lint

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  setup      to setup project"
	@echo "  install    to install dependencies"
	@echo "  test       to run all tests"
	@echo "  unit       to run unit tests"
	@echo "  check      to run pre-commit checks"
	@echo "  lint       to run flake8"

setup:
	@poetry init
	@pre-commit install

install:
	@poetry install

pre-commit-autoupdate:
	@poetry run pre-commit autoupdate

unit:
	@poetry run coverage run pytest -s -v
	@poetry run coverage report -m
	@poetry run coverage html

check:
	@poetry run pre-commit run --all-files

lint:
	@poetry run flake8

sphinx-start:
	@poetry run sphinx-quickstart docs

sphinx-build:
	@poetry run sphinx-build -b html docs docs/_build

publish-to-pypi:
	@poetry publish --build

build:
	@poetry build
