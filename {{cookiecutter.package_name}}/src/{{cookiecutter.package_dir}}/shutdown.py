import asyncio
import logging
import signal
import sys

logger = logging.getLogger("playdoh-rfid")


class ShutdownManager:
    """
    Cross-platform graceful shutdown helper.
    """

    def __init__(self):
        self.shutdown_event = asyncio.Event()

    def install(self, loop=None):
        if loop is None:
            loop = asyncio.get_running_loop()

        if sys.platform == "win32":
            # Windows: signal.signal() must be called in main thread
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            logger.info("ShutdownManager installed: Windows signals (SIGINT/SIGTERM)")
        else:
            # UNIX: we can use loop.add_signal_handler()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._signal_handler, sig)
            logger.info("ShutdownManager installed: UNIX signals (SIGINT/SIGTERM)")

    def _signal_handler(self, sig, *_):
        if isinstance(sig, int):
            try:
                sig_name = signal.Signals(sig).name
            except ValueError:
                sig_name = str(sig)
        else:
            sig_name = str(sig)
        logger.info("Received signal %s, initiating shutdown.", sig_name)
        self.shutdown_event.set()

    def is_set(self):
        """
        Check if the shutdown event is set.
        """
        return self.shutdown_event.is_set()

    async def wait(self):
        await self.shutdown_event.wait()
