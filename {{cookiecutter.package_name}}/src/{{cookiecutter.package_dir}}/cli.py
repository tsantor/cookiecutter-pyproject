import logging

import click

from . import settings
from .logging import setup_logging
from .entrypoint import main

logger = logging.getLogger("{{cookiecutter.package_name}}")


def silent_echo(*args, **kwargs):
    pass


def common_options(func):
    """Decorator to add common options to a command."""
    func = click.option(
        "-p",
        "--path",
        required=True,
        type=click.Path(),
        help="Path to a file or directory.",
    )(func)
    return click.option("--verbose", is_flag=True, help="Enables verbose mode.")(func)


@click.command()
@common_options
def run(path, verbose) -> None:
    if not verbose:
        click.echo = silent_echo

    setup_logging(verbose, settings.LOG_FILE)

    main(path)


# Set up your command-line interface grouping
@click.group()
@click.version_option(package_name="{{cookiecutter.package_dir}}")
def cli():
    """{{cookiecutter.project_short_description}}"""


cli.add_command(run)

if __name__ == "__main__":
    cli()
