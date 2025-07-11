import logging
import logging.handlers

from rich.logging import RichHandler

from .settings import LOG_FILE


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.info("Setting up logger '%s' with level '%s'", name, level)

    # Prevent propagation to root logger (to avoid other packages)
    logger.propagate = False

    # If already configured, return as-is
    if logger.hasHandlers():
        logger.info("Logger '%s' already has handlers configured", name)
        return logger

    # Console handler
    console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True)
    # console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    # console_formatter = logging.Formatter("[%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    # console_handler.setFormatter(console_formatter)

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    # file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get the logger instance, setting it up if not already configured."""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        setup_logger(name)
    return logger
