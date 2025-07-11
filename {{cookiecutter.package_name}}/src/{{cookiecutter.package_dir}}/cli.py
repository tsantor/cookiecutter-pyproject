import click

from . import __version__
from .entrypoint import run as run_app
from .logging_config import setup_logger


@click.command()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Logging level",
)
@click.version_option(
    package_name="{{cookiecutter.package_dir}}",
    prog_name="{{cookiecutter.package_name}}",
    version=__version__,
)
def cli(log_level):
    """{{cookiecutter.project_short_description}}"""
    setup_logger(name="{{cookiecutter.package_name}}", level=log_level.upper())
    run_app()


if __name__ == "__main__":
    cli()
