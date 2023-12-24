## Environment Setup

1. We use [Poetry](https://python-poetry.org/docs/#installation) for managing virtual
   environments and dependencies.
   Once Poetry is installed, run `poetry install` in this repo to get started.
2. For managing linters, static-analysis, and other tools, we
   use [pre-commit](https://pre-commit.com/#installation).
   Once Pre-commit is installed, run `pre-commit install` in this repo to install the
   hooks.
   Using pre-commit ensures PRs match the linting requirements of the codebase.

## Documentation

Whenever possible, please add docstrings to your code!
To confirm docstrings are valid, build the docs by running `poetry run make html` in
the `docs/` folder.

## Unit Tests

We use the [pytest](https://docs.pytest.org/) framework for unit testing.

## Coding Style

I'm sure you can figure it out.
