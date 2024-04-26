import logging
from pathlib import Path
import signal

import click

from . import settings
from .core import do_something
from .logging import setup_logging
from .utils import home_agnostic_path

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Entry point - handles graceful exit on SIGINT/SIGTERM
# -----------------------------------------------------------------------------


class GracefulExit(SystemExit):
    code = 1


def _raise_graceful_exit(signum, frame):
    raise GracefulExit()


def main(path):
    """Main entry point for the CLI."""
    signal.signal(signal.SIGINT, _raise_graceful_exit)
    signal.signal(signal.SIGTERM, _raise_graceful_exit)

    try:
        click.echo("Hello, World!")
        click.echo(f"Path: {home_agnostic_path(path)}")
        do_something()
    except GracefulExit:
        pass
    finally:
        click.echo("Cleaning up...")


# -----------------------------------------------------------------------------
# Command-line interface
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

    main(path)


# Set up your command-line interface grouping
@click.group()
@click.version_option(package_name="{{cookiecutter.package_dir}}")
def cli():
    """{{cookiecutter.description}}"""


cli.add_command(run)

if __name__ == "__main__":
    cli()
