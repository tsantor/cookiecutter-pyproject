import logging

import click  # https://click.palletsprojects.com/

from . import settings
from .logging import setup_logging

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------


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
    click.echo(f"Hello, World! Path: {path}")


# Set up your command-line interface grouping
@click.group()
@click.version_option()
def cli():
    """{{cookiecutter.description}}"""


cli.add_command(run)

if __name__ == "__main__":
    cli()
