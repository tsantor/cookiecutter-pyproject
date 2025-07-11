import asyncio
import logging
import os
import sys

from .app import MyApp

logger = logging.getLogger("{{ cookiecutter.package_name }}")


def setup_windows_event_loop() -> None:
    """Configure Windows-specific event loop policy."""
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logger.debug("Set Windows Selector event loop policy")


async def main() -> None:
    """Main entry point."""
    app = MyApp()
    await app.run()


def run():
    """Run the application."""
    setup_windows_event_loop()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception:
        logger.exception("Fatal error running application")
        sys.exit(1)


if __name__ == "__main__":
    run()
