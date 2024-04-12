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
	python3 -m pip install -U pip -r requirements_dev.txt

env_remove:  ## Remove virtual environment
	pyenv uninstall -f ${venv}

env_from_scratch: env_remove env  ## Create environment from scratch

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
	rm -rf python_package_boilerplate

# -----------------------------------------------------------------------------
