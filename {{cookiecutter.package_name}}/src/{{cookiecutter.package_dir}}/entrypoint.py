import asyncio
import logging
import os
import sys

from .app import MyApp

logger = logging.getLogger(__name__)


def setup_windows_event_loop() -> None:
    """Configure Windows-specific event loop policy."""
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logger.debug("Set Windows Selector event loop policy")


async def main(config) -> None:
    """Main entry point."""
    app = MyApp(config)
    await app.run()


def run(config):
    """Run the application."""
    setup_windows_event_loop()
    asyncio.run(main(config))


if __name__ == "__main__":
    run()
