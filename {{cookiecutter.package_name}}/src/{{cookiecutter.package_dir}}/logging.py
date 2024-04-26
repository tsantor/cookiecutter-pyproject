import logging
import logging.handlers

from rich.logging import RichHandler


def setup_logging(verbose=False, log_file=None):
    """Setup logging."""

    handlers = [RichHandler()]

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

    # Set the logging level of the root logger to WARNING
    logging.basicConfig(
        handlers=handlers,
        level=logging.WARNING,
        format="[%(name)s] %(message)s",
        datefmt="%Y-%m-%d %I:%M:%S %p",
    )

    # Set the logging level of your application's logger to INFO or DEBUG
    logger = logging.getLogger("{{cookiecutter.package_name}}")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
