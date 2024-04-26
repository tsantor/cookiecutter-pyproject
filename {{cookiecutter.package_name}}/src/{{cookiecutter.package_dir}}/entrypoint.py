import logging
import signal
import click

from .utils import home_agnostic_path
from .core import do_something

logger = logging.getLogger("{{cookiecutter.package_name}}")


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
