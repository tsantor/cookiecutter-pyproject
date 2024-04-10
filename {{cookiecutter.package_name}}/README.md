# {{ cookiecutter.project_name }}

## Overview

{{ cookiecutter.project_short_description }}

## Installation

```bash
# From pypi
python3 -m pip install {{cookiecutter.package_name}}

# From source
python3 -m pip install git+https://bitbucket.org/xstudios/{{cookiecutter.package_name}}.git
```

## Development

```bash
make env
make pip_install
make pip_editable_install
```

## Testing

```bash
make pytest
make coverage
make open_coverage
```

## Issues

If you experience any issues, please create an [issue](https://bitbucket.org/xstudios/{{cookiecutter.package_name}}/issues) on Bitbucket.
