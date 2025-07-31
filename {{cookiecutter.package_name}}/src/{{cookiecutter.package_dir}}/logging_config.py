import logging
import logging.handlers
from pathlib import Path

from rich.logging import RichHandler


def setup_logger(
    name: str,
    log_file: Path,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
) -> None:
    # Ensure the log directory exists
    if not log_file.parent.exists():
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.touch(exist_ok=True)

    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    datefmt = "%Y-%m-%d %I:%M:%S %p"

    # Console handler
    console_handler = RichHandler(
        level=console_level.upper(),
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )
    console_formatter = logging.Formatter("%(message)s", datefmt=datefmt)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt=datefmt,
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Set up package logger
    package_logger = logging.getLogger(name)
    package_logger.setLevel(logging.DEBUG)

    # Adjust logging levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("pygame").setLevel(logging.ERROR)
