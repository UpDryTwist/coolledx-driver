
.PHONY: help setup install test unit check lint

TEST_DIR = tests
DOCKER_REPO = registry.supercroy.com/updrytwist
DOCKER_PROJ = coolledx
VERSION = $(shell poetry version | rev | cut -d' ' -f1 | rev)
BUILD_DOCKER ?= true

# Before working on something, run make bump-version-<major|minor|patch>
# When ready to commit, run make full-commit-ready or commit-ready for a faster commit
# To run a full build, run make full-build or fast-build for a faster build

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  setup             to setup project (not needed - template does this)"
	@echo "  poetry-config     to configure Poetry (only needed once per system)"
	@echo "  system-requirements-install    to install system requirements (only needed once per system)"
	@echo "  install           to install dependencies"
	@echo "  add-to-git        to add project to git"
	@echo "  first-make        to run install, add-to-git, full-commit-ready"
	@echo "  add-to-github     to add the project to github"
	@echo "  unit              to run unit tests"
	@echo "  check             to run pre-commit checks"
	@echo "  commit-ready      to run pre-commit checks and unit tests"
	@echo "  full-commit-ready to run pre-commit checks, unit tests, and bump version"
	@echo "  fast-build        to build with just unit tests and version bump"
	@echo "  max-build         to run a complete dependencies refresh, full build, and docker build/publish"
	@echo "  docker-dev        to start development Docker stack"
	@echo "  docker-dev-clean  to build a clean development Docker stack and then run clean"
	@echo "  docker-prod       to start production Docker stack"
	@echo "  docker-down       to stop Docker stack"
	@echo "  docker-logs       to view Docker logs"
	@echo "  fast-docker-build to run the minimal docker build and publish"
	@echo "  publish-to-pypi   to publish to PyPI"
	@echo "  autoupdate        to update dependencies"
	@echo "  forced-update     to force update dependencies (clear Poetry cache)"
	@echo "  template-update   to run the copier update (latest template release)"
	@echo "  template-update-tip   to run the copier update (latest template tip)"
	@echo "  check-uncommitted to check for uncommitted changes in Git"
	@echo "  commit-and-tag-release    to commit and tag the release"
	@echo "  build-and-release-patch   to run the full build and release a patch"
	@echo "  build-and-release-minor   to run the full build and release a minor"
	@echo "  build-and-release-major   to run the full build and release a major"

setup:
	@poetry init
	@pre-commit install

poetry-config:
	@poetry config virtualenvs.in-project true
	@poetry config virtualenvs.create true
	@poetry config virtualenvs.path .venv

system-requirements-install:
ifeq ($(IS_WINDOWS),Windows_NT)
	@winget install rhysd.actionlint koalaman.shellcheck mvdan.shfmt Gitleaks.Gitleaks Thoughtworks.Talisman waterlan.dos2unix GitHub.cli
else
	@set -e; \
	sudo apt-get update; \
	sudo apt-get install -y shellcheck shfmt gitleaks dos2unix; \
	# actionlint (install from upstream if missing)
	if ! command -v actionlint >/dev/null 2>&1; then \
	  echo "Installing actionlint..."; \
	  tmpdir=$$(mktemp -d); cd $$tmpdir; \
	  curl -fsSL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash -o dl.sh; \
	  bash dl.sh latest . >/dev/null; \
	  sudo install -m 0755 actionlint /usr/local/bin/actionlint; \
	  cd /; rm -rf $$tmpdir; \
	fi; \
	\
	# talisman (install from upstream if missing)
	if ! command -v talisman >/dev/null 2>&1; then \
	  echo "Installing Talisman..."; \
	  tmpdir=$$(mktemp -d); cd $$tmpdir; \
	  curl -fsSL https://thoughtworks.github.io/talisman/install.sh -o install.sh; \
	  bash install.sh latest . >/dev/null; \
	  sudo install -m 0755 talisman /usr/local/bin/talisman; \
	  cd /; rm -rf $$tmpdir; \
	fi; \
	\
	# GitHub CLI (add official repo if not installed)
	if ! command -v gh >/dev/null 2>&1; then \
	  echo "Installing GitHub CLI (gh)..."; \
	  sudo mkdir -p -m 0755 /etc/apt/keyrings; \
	  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null; \
	  sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg; \
	  echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null; \
	  sudo apt-get update; \
	  sudo apt-get install -y gh; \
	fi
endif

lint-tools-check:
	@echo "---- tool versions ----"; \
	for cmd in actionlint shellcheck shfmt gitleaks talisman dos2unix gh; do \
	  if command -v $$cmd >/dev/null 2>&1; then \
	    printf "%-10s " $$cmd; $$cmd --version 2>/dev/null || $$cmd version 2>/dev/null || echo "(installed)"; \
	  else \
	    echo "$$cmd NOT FOUND"; \
	  fi; \
	done

install:
	@poetry install
	@poetry update

autoupdate:
	@poetry run pre-commit autoupdate
	@poetry update

forced-update:
	@poetry cache clear pypi --all
	@poetry run pre-commit autoupdate
	@poetry update

add-to-git:
	@git init
	@git add .
	@git add --chmod=+x run_scripts/*.sh
	@git commit -m "Initial commit from Copier template"
	@git config --global --add safe.directory $(CURDIR)
	@poetry run pre-commit install

add-to-github:
	@gh repo create coolledx-driver --public --source=.
	@git branch -M main
	@git remote add origin https://github.com/UpDryTwist/coolledx-driver.git
	@git push -u origin main

first-make: install add-to-git autoupdate full-commit-ready

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

full-commit-ready: autoupdate commit-ready check-manual

sphinx-start:
	@poetry run sphinx-quickstart docs

sphinx-build:
	@poetry run sphinx-build -b html docs docs/_build

publish-to-pypi:
	@poetry publish --build

build:
	@poetry build

docker-build-one:
ifeq ($(BUILD_DOCKER),true)
	@docker build -t $(DOCKER_PROJ):$(VERSION) .
endif

# You need to set up buildx. Run `docker buildx create --name mybuilder` and `docker buildx use mybuilder`
docker-build:
ifeq ($(BUILD_DOCKER),true)
	@docker buildx build --platform linux/amd64 \
		-t $(DOCKER_REPO)/$(DOCKER_PROJ):$(VERSION) \
		-t $(DOCKER_REPO)/$(DOCKER_PROJ):latest \
		--push .
endif

# Multi-architecture build (use this once size is optimized)
docker-build-multi:
ifeq ($(BUILD_DOCKER),true)
	@docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(DOCKER_REPO)/$(DOCKER_PROJ):$(VERSION) \
		-t $(DOCKER_REPO)/$(DOCKER_PROJ):latest \
		--push .
endif

docker-publish-one: docker-build-one
ifeq ($(BUILD_DOCKER),true)
	@docker tag $(DOCKER_PROJ):$(VERSION) $(DOCKER_REPO)/$(DOCKER_PROJ):$(VERSION)
	@docker push $(DOCKER_REPO)/$(DOCKER_PROJ):$(VERSION)
	@docker tag $(DOCKER_PROJ):$(VERSION) $(DOCKER_REPO)/$(DOCKER_PROJ):latest
	@docker push $(DOCKER_REPO)/$(DOCKER_PROJ):latest
endif

bump-version-major:
	@poetry run bump-my-version bump major pyproject.toml .bumpversion.toml
	@dos2unix .bumpversion.toml
	@dos2unix pyproject.toml

bump-version-minor:
	@poetry run bump-my-version bump minor pyproject.toml .bumpversion.toml
	@dos2unix .bumpversion.toml
	@dos2unix pyproject.toml

bump-version-patch:
	@poetry run bump-my-version bump patch pyproject.toml .bumpversion.toml
	@dos2unix .bumpversion.toml
	@dos2unix pyproject.toml

bump-version-pre:
	@poetry run bump-my-version bump pre_l pyproject.toml .bumpversion.toml
	@dos2unix .bumpversion.toml
	@dos2unix pyproject.toml

bump-version-build:
	@poetry run bump-my-version bump pre_n pyproject.toml .bumpversion.toml
	@dos2unix .bumpversion.toml
	@dos2unix pyproject.toml

version-build: bump-version-build build

fast-build: just-unit version-build

full-build: full-commit-ready version-build

max-build: autoupdate full-build docker-build-multi docker-dev-build

fast-docker-build: just-unit bump-version-build docker-publish-one

# Docker development targets
docker-dev:
	@docker compose up -d

docker-dev-build:
	@docker compose down -v
	@docker system prune -f
	@docker compose build --no-cache battery-hawk

docker-dev-clean: docker-dev-build
	@clear
	@docker compose up -d
	@docker compose logs -f

docker-prod:
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

docker-down:
	@docker compose down

docker-logs:
	@docker compose logs -f

docker-clean:
	@docker compose down -v
	@docker system prune -f

check-uncommitted:
	@if [ -n "$(shell git status --porcelain)" ]; then echo "Uncommitted changes in Git"; git status --short; exit 1; fi

commit-and-tag-release:
	@git add pyproject.toml .bumpversion.toml
	@git commit -m "Release version $(VERSION)"
	@git tag -a v$(VERSION) -m "Release version $(VERSION)"
	@git push origin main
	@git push origin v$(VERSION)

make-github-release:
	@gh release create v$(VERSION) --title "Release $(VERSION)" --notes "Release $(VERSION)"

pre-build-and-release-version: check-uncommitted autoupdate full-build docker-build-one

post-build-and-release-version: commit-and-tag-release make-github-release docker-publish-one

build-and-release-patch: pre-build-and-release-version bump-version-patch post-build-and-release-version

build-and-release-minor: pre-build-and-release-version bump-version-minor post-build-and-release-version

build-and-release-major: pre-build-and-release-version bump-version-major post-build-and-release-version

template-update:
	@copier update --trust --defaults --conflict inline

template-update-tip:
	@copier update --trust --defaults --conflict inline --vcs-ref=HEAD
