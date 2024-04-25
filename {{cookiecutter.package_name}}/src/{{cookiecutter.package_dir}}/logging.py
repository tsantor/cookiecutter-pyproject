import logging
import logging.handlers
{%- if cookiecutter.use_rich == "y" %}

from rich.logging import RichHandler
{%- endif %}

# Shut up these 3rd party packages
shutup = ["urllib3"]
for package in shutup:
    logging.getLogger(package).setLevel(logging.WARNING)


def setup_logging(verbose=False, log_file=None):
    """Setup logging."""

    {%- if cookiecutter.use_rich == "y" %}
    handlers = [RichHandler()]
    {%- else %}
    handlers = [logging.StreamHandler()]
    {%- endif %}

    # File handler logging is more detailed
    if log_file:
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S %p",
        )
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            backupCount=5,
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        handlers=handlers,
        level=logging.INFO,
        format="[%(name)s] %(message)s",
        datefmt="%Y-%m-%d %I:%M:%S %p",
    )
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
