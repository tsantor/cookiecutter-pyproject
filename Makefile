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

BAKE_OPTIONS=--no-input
BUILD_DIR=my-python-package

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

env:  ## Install virtualenv for development (uses `uv`)
	uv venv

env_remove:  ## Remove virtual environment
	rm -rf .venv/

env_from_scratch: env_remove env pip_install  ## Create environment from scratch

# -----------------------------------------------------------------------------
# Pip
# -----------------------------------------------------------------------------

pip_install:  ## Install requirements
	uv add cookiecutter

pip_install_dev: ## Install development requirements
	uv add pip wheel build ruff pre-commit watchdog[watchmedo] binaryornot sh --group=dev

pip_install_test: ## Install test requirements
	uv add pytest pytest-cookies pytest-cov --group=test

pip_install_all: pip_install pip_install_dev pip_install_test ## Install all requirements

# pip_install_editable:  ## Install editable package
# 	uv pip install -e .
# 	# uv run pre-commit install

pip_list:  ## Run pip list
	uv pip list

# -----------------------------------------------------------------------------
# Cookiecutter
# -----------------------------------------------------------------------------

bake:  ## Generate project using defaults
	cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists

watch: bake  ## Generate project using defaults and watch for changes
	watchmedo shell-command -p '*.*' -c 'make bake -e BAKE_OPTIONS=$(BAKE_OPTIONS)' -W -R -D \{{cookiecutter.package_name}}/

replay: BAKE_OPTIONS=--replay  # Replay last cookiecutter run and watch for changes
replay: watch
	;

eat:  ## Remove generated project
	rm -rf ${BUILD_DIR}

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

pytest:  ## Run tests
	pytest -vx

# pytest_generation:  ## Run tests for cookiecutter generation
# 	pytest -vx tests/test_cookiecutter_generation.py

pytest_verbose:  ## Run tests in verbose mode
	pytest -vvs

# coverage:  ## Run tests with coverage
# 	coverage run -m pytest && coverage html

# coverage_verbose:  ## Run tests with coverage in verbose mode
# 	coverage run -m pytest -vss && coverage html

# coverage_skip:  ## Run tests with coverage and skip covered
# 	coverage run -m pytest -vs && coverage html --skip-covered

# open_coverage:  ## Open coverage report
# 	open htmlcov/index.html

# -----------------------------------------------------------------------------
# Miscellaneous
# -----------------------------------------------------------------------------

tree:  ## Show directory tree
	tree -I 'build|dist|htmlcov|node_modules|migrations|contrib|__pycache__|*.egg-info|staticfiles|media|my-python-package'

# -----------------------------------------------------------------------------
