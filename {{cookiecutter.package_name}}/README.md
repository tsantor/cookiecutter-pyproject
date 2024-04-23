# {{ cookiecutter.project_name }}

![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)

## Overview

{{ cookiecutter.description }}

## Installation

```bash
# From pypi
python3 -m pip install {{cookiecutter.package_name}}

# From source
python3 -m pip install git+https://githubc.org/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}.git
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

If you experience any issues, please create an [issue](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}/issues) on Github.


## Not Exactly What You Want?
This is what I want. _It might not be what you want_. If you have differences in your preferred setup, I encourage you to fork this to create your own version.
