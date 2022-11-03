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
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

python_version=3.9.11
venv={{ cookiecutter.project_slug }}_env
aws_profile=xstudios
s3_bucket={{ cookiecutter.project_slug }}

# -----------------------------------------------------------------------------
# Environment setup
# -----------------------------------------------------------------------------

env: ## create pyenv virtualenv
	pyenv virtualenv ${python_version} ${venv} && pyenv local ${venv}

reqs: ## install development requirements
	python -m pip install -U pip wheel build setuptools \
		&& python -m pip install -r requirements.txt \
		&& python -m pip install -r requirements_dev.txt

destroy_env:  ## destroy pyenv virtualenv
	pyenv uninstall ${venv}
	rm -rf ~/.pyenv/versions/${python_version}/envs/${venv}

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

clean: clean-build clean-pyc ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# -----------------------------------------------------------------------------
# Deploy
# -----------------------------------------------------------------------------

dist: clean ## builds source and wheel package
	python -m build --wheel
	cp dist/*.whl dist/{{ cookiecutter.project_slug }}-latest-py2.py3-none-any.whl

release_test: ## upload package to pypi test
	twine upload dist/* -r pypitest

release: dist ## package and upload a release
	twine upload dist/*

# -----------------------------------------------------------------------------
# X Studios S3 PyPi
# -----------------------------------------------------------------------------

push_to_s3:  ## push distro to S3 bucket
	aws s3 sync --profile=${aws_profile} --acl public-read ./dist/ s3://xstudios-pypi/ \
        --exclude "*" --include "*.whl"
