# Cookiecutter PyProject

A modern cookiecutter template for creation of a Python package following best practices.

## Features
The resulting generated Python package features:

- `pyproject.toml`
- `ruff` for formatting/linting
- `pytest` and `coverage` for running tests
- `pre-commit` to enforce formatting/linting before committing
- `click` (optional if making a CLI app)
- `sentry-sdk` for error reporting (optional)
- `twine` for publishing to PyPI
- `Makefile` with common development related commands

## Quickstart

Install Cookiecutter, if you don't already have it:

```bash
python3 -m pip install -U cookiecutter
```

Generate a Python package:

```bash
cookiecutter https://github.com/tsantor/cookiecutter-pyproject.git
```

## Development

```bash
make env
make pytest
```

Run `make` to view a list of available commands with descriptions.


## Not Exactly What You Want?
This is what I want. _It might not be what you want_. If you have differences in your preferred setup, I encourage you to fork this to create your own version.
