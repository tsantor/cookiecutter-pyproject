import argparse
import logging
import sys

from . import __version__, settings
from .logging import setup_logging

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


def get_parser():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="{{cookiecutter.project_short_description}}"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument("--version", action="version", version=__version__)

    return parser.parse_args()


def run():
    """Run script."""

    args = get_parser()

    setup_logging(args.verbose, settings.LOG_FILE)

    print("Hello world!")

    sys.exit()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    run()
