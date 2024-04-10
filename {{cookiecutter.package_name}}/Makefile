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
venv={{ cookiecutter.package_name }}_env
aws_profile=xstudios
s3_bucket=xstudios-pypi

# START - Generic commands
# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

env:  ## Create virtual environment
	pyenv virtualenv ${python_version} ${venv} && pyenv local ${venv}

env_remove:  ## Remove virtual environment
	pyenv uninstall -f ${venv}

# -----------------------------------------------------------------------------
# Pip
# -----------------------------------------------------------------------------

pip_install:  ## Install requirements
	python3 -m pip install --upgrade pip
	@for file in $$(ls requirements/*.txt); do \
			python3 -m pip install -r $$file; \
	done
	pre-commit install

pip_editable_install:	## Install in editable mode
	python3 -m pip install -e .

pip_list:  ## Run pip list
	python3 -m pip list

pip_freeze:  ## Run pipfreezer
	pipfreezer

pip_checker:  ## Run pipchecker
	python3 manage.py pipchecker

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

pytest:  ## Run tests
	pytest -v -x

pytest_verbose:  ## Run tests in verbose mode
	pytest -vs

coverage:  ## Run tests with coverage
	coverage run -m pytest && coverage html
	# pytest --cov=django_project --cov=src --cov-report html -vs

coverage_verbose:  ## Run tests with coverage in verbose mode
	coverage run -m pytest -vs && coverage html

coverage_skip:  ## Run tests with coverage and skip covered
	coverage run -m pytest -vs && coverage html --skip-covered

open_coverage:  ## Open coverage report
	open htmlcov/index.html

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

clean_build: ## Remove build artifacts
	rm -fr build/ dist/ .eggs/
	find . -name '*.egg-info' -o -name '*.egg' -exec rm -fr {} +

clean_pyc: ## Remove python file artifacts
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
# Deploy
# -----------------------------------------------------------------------------

dist: clean ## Builds source and wheel package
	python3 -m build --wheel

release_test: dist ## Upload package to pypi test
	twine upload dist/* -r pypitest

release: dist ## Package and upload a release
	twine upload dist/*

check: dist ## Twine check
	twine check dist/*

# -----------------------------------------------------------------------------
# X Studios S3 PyPi
# -----------------------------------------------------------------------------

create_latest_copy:  dist  ## Create a copy of the latest wheel
	cp dist/*.whl dist/{{ cookiecutter.project_slug }}-latest-py3-none-any.whl

push_to_s3: create_latest_copy  ## Push distro to S3 bucket
	aws s3 sync --profile=${aws_profile} --acl public-read ./dist/ s3://${s3_bucket}/ \
        --exclude "*" --include "*.whl"
	echo "https://${s3_bucket}.s3.amazonaws.com/{{ cookiecutter.project_slug }}-latest-py3-none-any.whl"

# -----------------------------------------------------------------------------
# END - Generic commands

# -----------------------------------------------------------------------------
# Project specific commands
# -----------------------------------------------------------------------------

# Your commands here
