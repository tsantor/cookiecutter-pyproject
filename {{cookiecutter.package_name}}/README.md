# {{ cookiecutter.project_name }}

![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

## Overview

{{ cookiecutter.description }}

## Installation

Install {{ cookiecutter.project_name }}:

```bash
# From pypi
python3 -m pip install {{cookiecutter.package_name}}

# From source
python3 -m pip install git+https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}.git
```

## Development

```bash
make env
make pip_install
make pip_install_editable
```

## Testing

```bash
make pytest
make coverage
make open_coverage
```

## Deploying

```bash
# Publish to PyPI Test before the live PyPi
make release_test
make release
```

## Issues

If you experience any issues, please create an [issue](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}/issues) on Github.
