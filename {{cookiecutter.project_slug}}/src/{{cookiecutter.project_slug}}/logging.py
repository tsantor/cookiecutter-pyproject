import logging
import logging.handlers

# Shut up these 3rd party packages
shutup = ["urllib3"]
for package in shutup:
    logging.getLogger(package).setLevel(logging.WARNING)


def setup_logging(verbose=False, log_file=None):
    """Setup logging."""

    handlers = [logging.StreamHandler()]
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            backupCount=5,
        )
        handlers.append(file_handler)

    logging.basicConfig(
        handlers=handlers,
        level=logging.INFO,
        format="[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %I:%M:%S %p",
    )
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
