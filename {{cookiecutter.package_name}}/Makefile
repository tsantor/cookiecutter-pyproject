# -----------------------------------------------------------------------------
# Generate help output when running just `make`
# -----------------------------------------------------------------------------
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

PYTHON_VERSION=3.13.1
package_name={{ cookiecutter.package_dir }}
package_version={{ cookiecutter.version }}
aws_profile=xstudios
s3_bucket=xstudios-pypi
wheel_name=${package_name}-${package_version}-py3-none-any.whl
package_url=https://${s3_bucket}.s3.amazonaws.com/${wheel_name}

# package_version := $(shell python -c "import importlib.metadata; print(importlib.metadata.version('${package_name}'))")
# package_url=https://${s3_bucket}.s3.amazonaws.com/${package_name}-${package_version}-py3-none-any.whl

# START - Generic commands
# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

env:  ## Create virtual environment (uses `uv`)
	uv venv --python ${PYTHON_VERSION}

env_remove:  ## Remove virtual environment
	rm -rf .venv/

env_recreate: env_remove env pip_install pip_install_editable  ## Recreate environment from scratch

# -----------------------------------------------------------------------------
# Pip
# -----------------------------------------------------------------------------

pip_install:  ## Install requirements
	uv pip install --upgrade pip
	@for file in $$(ls requirements/*.txt); do \
			uv pip install -r $$file; \
	done
	pre-commit install

pip_add_dev_dependencies:  ## Add dev dependencies
	uv add twine wheel build ruff pipdeptree pre-commit --group dev

pip_add_test_dependencies:  ## Add test dependencies
	uv add pytest pytest-cov pytest-mock coverage --group test

pip_install_editable:  ## Install in editable mode
	uv pip install -e .
	uv sync --all-groups
	pre-commit install

pip_list:  ## Run pip list
	uv pip list

pip_tree: ## Run pip tree
	uv pip tree

pipdeptree:  ## # Run pipdeptree
	uv run pipdeptree

uv_sync:  ## Sync dependencies [production, dev, test]
	uv sync --all-groups

uv_lock_check:	## Check if lock file is up to date
	uv lock --check

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

pytest:  ## Run tests
	uv run pytest -vx --cov --cov-report=html

pytest_verbose:  ## Run tests in verbose mode
	uv run pytest -vvs --cov --cov-report=html

coverage:  ## Run tests with coverage
	uv run coverage run -m pytest && coverage html

coverage_verbose:  ## Run tests with coverage in verbose mode
	uv run coverage run -m pytest -vss && coverage html

coverage_skip:  ## Run tests with coverage and skip covered
	uv run coverage run -m pytest -vs && coverage html --skip-covered

open_coverage:  ## Open coverage report
	open htmlcov/index.html

# -----------------------------------------------------------------------------
# Ruff
# -----------------------------------------------------------------------------

ruff_format: ## Run ruff format
	uv run ruff format src/{{cookiecutter.package_dir}}

ruff_check: ## Run ruff check
	uv run ruff check src/{{cookiecutter.package_dir}}

ruff_clean: ## Run ruff clean
	uv run ruff clean

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

clean_build:  ## Remove build artifacts
	rm -fr build/ dist/ .eggs/
	find . -name '*.egg-info' -o -name '*.egg' -exec rm -fr {} +

clean_pyc:  ## Remove python file artifacts
	find . \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' -o -name '__pycache__' \) -exec rm -fr {} +

clean: clean_build clean_pyc ## Remove all build and python artifacts

clean_pytest_cache:  ## Clear pytest cache
	rm -rf .pytest_cache

clean_ruff_cache:  ## Clear ruff cache
	rm -rf .ruff_cache

clean_tox_cache:  ## Clear tox cache
	rm -rf .tox

clean_coverage:  ## Clear coverage cache
	rm .coverage
	rm -rf htmlcov

clean_tests: clean_pytest_cache clean_ruff_cache clean_tox_cache clean_coverage  ## Clear pytest, ruff, tox, and coverage caches

# -----------------------------------------------------------------------------
# Miscellaneous
# -----------------------------------------------------------------------------

tree:  ## Show directory tree
	tree -I 'dist|htmlcov|node_modules|__pycache__|*.egg-info|mkdocs'

# -----------------------------------------------------------------------------
# Deploy
# -----------------------------------------------------------------------------

dist: clean ## Builds source and wheel package
	python3 -m build

twine_upload_test: dist ## Upload package to pypi test
	twine upload dist/* -r pypitest

twine_upload: dist ## Package and upload a release
	twine upload dist/*

twine_check: dist ## Twine check
	twine check dist/*

# -----------------------------------------------------------------------------
# X Studios S3 PyPi
# -----------------------------------------------------------------------------

create_latest_copy: dist  ## Create latest copy of distro
	cp dist/*.whl dist/${package_name}-latest-py3-none-any.whl

push_to_s3:  ## Push distro to S3 bucket
	aws s3 sync --profile=${aws_profile} --acl public-read ./dist/ s3://${s3_bucket}/ \
        --exclude "*" --include "*.whl"
	echo "${package_url}"

requirements_dependency:	## Generate secure URL
	@sha256=$$(openssl sha256 dist/${wheel_name} | awk '{print $$2}'); \
	echo "${package_name} @ ${package_url}?sha256=$$sha256"

pyproject_dependency:	## Dependency line for pyproject.toml
	@sha256=$$(openssl sha256 dist/${wheel_name} | awk '{print $$2}'); \
	echo "${package_name}" = { url = "${package_url}", hash = "sha256=$$sha256" }

dependency_urls: requirements_dependency pyproject_dependency ## Generate dependency URLs

# END - Generic commands
# -----------------------------------------------------------------------------
# Project Specific
# -----------------------------------------------------------------------------

# Add your project specific commands here
