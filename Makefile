BAKE_OPTIONS=--no-input

help:
	@echo "env	install virtualenv for development"
	@echo "bake 	generate project using defaults"
	@echo "watch 	generate project using defaults and watch for changes"
	@echo "replay 	replay last cookiecutter run and watch for changes"

env:
	pyenv virtualenv 3.9.4 cookiecutter_mkdocs_env && pyenv local cookiecutter_mkdocs_env
	python -m pip install -U pip -r requirements_dev.txt

bake:
	cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists

watch: bake
	watchmedo shell-command -p '*.*' -c 'make bake -e BAKE_OPTIONS=$(BAKE_OPTIONS)' -W -R -D \{{cookiecutter.project_slug}}/

replay: BAKE_OPTIONS=--replay
replay: watch
	;
