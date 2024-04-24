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

python_version=3.9.11
venv=cookiecutter-pyproject_env

BAKE_OPTIONS=--no-input

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

env:  ## Install virtualenv for development (uses `pyenv`)
	pyenv virtualenv ${python_version} ${venv} && pyenv local ${venv}

env_remove:  ## Remove virtual environment
	pyenv uninstall -f ${venv}

env_from_scratch: env_remove env pip_install  ## Create environment from scratch

# -----------------------------------------------------------------------------
# Pip
# -----------------------------------------------------------------------------

pip_install:  ## Install requirements
	python3 -m pip install -U pip -r requirements_dev.txt

pip_list:  ## Run pip list
	python3 -m pip list

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
	rm -rf my-python-package

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
