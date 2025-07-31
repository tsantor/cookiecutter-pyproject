import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseServiceAsync(ABC):
    """
    Base class for long-running asyncio services with graceful shutdown.
    """

    def __init__(self):
        self._shutdown_event = asyncio.Event()

    async def start(self):
        """
        Entrypoint: calls optional setup(), then run(), then optional cleanup().
        """
        try:
            await self.setup()
            await self.run()
        except Exception:
            logger.exception("Error in service run loop: %s", self.__class__.__name__)
            raise
        finally:
            await self.cleanup()

    async def stop(self):
        """
        Trigger shutdown.
        """
        logger.info("%s: Shutdown requested", self.__class__.__name__)
        self._shutdown_event.set()

    def is_shutdown(self) -> bool:
        return self._shutdown_event.is_set()

    async def wait_or_timeout(self, timeout: float):  # noqa: ASYNC109
        """
        Wait for shutdown event or timeout.
        """
        try:
            await asyncio.wait_for(self._shutdown_event.wait(), timeout)
            return True
        except TimeoutError:
            return False

    @abstractmethod
    async def setup(self):
        """
        Optional setup hook — override in subclasses if needed.
        """

    @abstractmethod
    async def cleanup(self):
        """
        Optional cleanup hook — override in subclasses if needed.
        """

    @abstractmethod
    async def run(self):
        """
        Main coroutine — must be implemented by subclasses.
        """
