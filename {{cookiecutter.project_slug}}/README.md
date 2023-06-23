# {{ cookiecutter.project_name }}

## Overview
{{ cookiecutter.project_short_description }}

## Features

- TODO

## Installation

    pip install git+https://bitbucket.org/xstudios/{{cookiecutter.project_slug}}.git

## Development

    make env
    make reqs
    pip install -e .

## Testing
Project is at **76%** test coverage.

    pytest -v
    tox

    # Run a specific test
    pytest -v tests/test_file.py -k method

    # Run coverage
    pytest --cov-report html --cov-report term --cov=tests/

## Issues

If you experience any issues, please create an [issue](https://bitbucket.org/xstudios/{{cookiecutter.project_slug}}/issues) on Bitbucket.
