import click
import sentry_sdk

from . import settings
from .entrypoint import run as run_app
from .logging_config import setup_logger


@click.command()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Logging level",
)
@click.version_option()
def cli(log_level):
    """{{cookiecutter.project_short_description}}"""

    setup_logger(
        name=settings.APP_NAME, log_file=settings.LOG_FILE, console_level=log_level
    )

    config = settings.load_config()

    {%- if cookiecutter.use_sentry == "y" %}
    if config.sentry.dsn:
        sentry_sdk.init(
            dsn=config.sentry.dsn,
            environment=config.sentry.env,
            traces_sample_rate=1.0,
        )
    {% endif %}

    run_app(config)


if __name__ == "__main__":
    cli()
