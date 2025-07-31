import logging
import time
from collections.abc import Callable
from typing import Any

from .baseasync import BaseServiceAsync

logger = logging.getLogger(__name__)


class HeartbeatService(BaseServiceAsync):
    """Service to publish heartbeat messages via MQTT with support for multiple payload sources."""

    def __init__(self, *, mqtt, interval=10):
        super().__init__()
        self._mqtt = mqtt
        self.interval = interval
        self._sources: dict[str, Callable[[], Any]] = {}

    def register_source(self, name: str, source_func: Callable[[], Any]) -> None:
        """
        Register a payload source function.

        Args:
            name: Unique name for this source
            source_func: Function that returns data to include in payload
        """
        self._sources[name] = source_func
        logger.debug(
            "Registered heartbeat source: '%s' => '%s'", name, source_func.__name__
        )

    def unregister_source(self, name: str) -> bool:
        """Remove a registered source. Returns True if source was found and removed."""
        if name in self._sources:
            del self._sources[name]
            logger.debug("Unregistered heartbeat source: '%s'", name)
            return True
        return False

    def list_sources(self) -> list[str]:
        """Return list of registered source names."""
        return list(self._sources.keys())

    async def _execute_source(
        self, name: str, source_func: Callable
    ) -> tuple[str, Any, bool]:
        """Execute a single source function with error handling."""
        try:
            result = source_func()
            return name, result, True
        except Exception:
            logger.exception("Error executing heartbeat source '%s'", name)
            return name, None, False

    async def _compile_payload(self) -> dict:
        """Compile payload from all registered sources."""
        payload = {}
        # Execute all sources
        for name, source_func in self._sources.items():
            source_name, data, success = await self._execute_source(name, source_func)
            if success and data is not None:
                payload[source_name] = data

        return {"timestamp": int(time.time() * 1000), **payload}

    async def setup(self):
        pass

    async def cleanup(self):
        pass

    async def run(self):
        logger.info(
            "%s started with %d registered sources",
            self.__class__.__name__,
            len(self._sources),
        )

        topic = self._mqtt.build_topic("heartbeat")

        while not self.is_shutdown():
            if self._mqtt.connected_event.is_set():
                try:
                    payload = await self._compile_payload()
                    if payload:  # Only publish if we have data
                        await self._mqtt.publish_json(
                            topic, payload, qos=0, retain=True
                        )
                    else:
                        logger.debug("No payload data to publish")
                except Exception:
                    logger.exception("Error in heartbeat publishing")

            await self.wait_or_timeout(self.interval)

        logger.info("%s stopped", self.__class__.__name__)
