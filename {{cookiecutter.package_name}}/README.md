# {{ cookiecutter.project_name }}

![Coverage](https://img.shields.io/badge/coverage-0%25-brightgreen)
<!-- ![Code Style](https://img.shields.io/badge/code_style-ruff-black) -->

## Overview

{{ cookiecutter.project_short_description }}

## Installation

```bash
# From pypi
python3 -m pip install {{cookiecutter.package_name}}

# From source
python3 -m pip install git+https://github.org/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}.git
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

## Issues

If you experience any issues, please create an [issue](https://github.org/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}/issues) on Github.
