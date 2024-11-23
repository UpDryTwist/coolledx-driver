
.PHONY: help setup install test unit check lint

TEST_DIR = tests
VERSION = $(shell poetry version | cut -d' ' -f2)

# Before working on something, run make bump-version-<major|minor|patch>
# When ready to commit, run make full-commit-ready or commit-ready for a faster commit
# To run a full build, run make full-build or fast-build for a faster build

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  setup             to setup project"
	@echo "  install           to install dependencies"
	@echo "  unit              to run unit tests"
	@echo "  check             to run pre-commit checks"
	@echo "  commit-ready      to run pre-commit checks and unit tests"
	@echo "  full-commit-ready to run pre-commit checks, unit tests, and bump version"

setup:
	@poetry init
	@pre-commit install

system-requirements-install:
	@installer-install rhysd/actionlint

install:
	@poetry install

autoupdate:
	@poetry update

forced-update:
	@poetry cache clear pypi --all
	@poetry update

pre-commit-autoupdate:
	@poetry run pre-commit autoupdate

just-unit:
	@poetry run pytest -s -v $(TEST_DIR)

unit:
	@poetry run coverage run -m pytest -s -v
	@poetry run coverage report -m
	@poetry run coverage html

check:
	@poetry run pre-commit run --all-files

check-manual:
	@poetry run pre-commit run --hook-stage manual --all-files

check-github-actions:
	@poetry run pre-commit run --hook-stage manual actionlint

commit-ready: check unit

full-commit-ready: pre-commit-autoupdate commit-ready check-manual

sphinx-start:
	@poetry run sphinx-quickstart docs

sphinx-build:
	@poetry run sphinx-build -b html docs docs/_build

publish-to-pypi:
	@poetry publish --build

build:
	@poetry build

bump-version-major:
	@bump-my-version bump major pyproject.toml .bumpversion.toml

bump-version-minor:
	@bump-my-version bump minor pyproject.toml .bumpversion.toml

bump-version-patch:
	@bump-my-version bump patch pyproject.toml .bumpversion.toml

bump-version-pre:
	@bump-my-version bump pre_l pyproject.toml .bumpversion.toml

bump-version-build:
	@bump-my-version bump pre_n pyproject.toml .bumpversion.toml

version-build: bump-version-build build

fast-build: just-unit version-build

full-build: full-commit-ready version-build
