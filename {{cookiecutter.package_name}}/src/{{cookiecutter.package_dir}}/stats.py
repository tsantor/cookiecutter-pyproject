import asyncio
import json
import logging
from collections.abc import Callable
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles

logger = logging.getLogger(__name__)


class StatsTracker:
    """
    Tracks and periodically persists stats collected from multiple sources.
    """

    def __init__(
        self,
        stats_file: str = "stats.json",
        save_interval: float = 10.0,
    ):
        """
        :param stats_file: path to stats JSON file
        :param save_interval: seconds between periodic saves
        """
        self.stats_file = Path(stats_file)
        self.save_interval = save_interval
        self._sources: dict[str, Callable[[], Any]] = {}
        self._task: asyncio.Task | None = None
        self._shutdown = asyncio.Event()
        self._current_stats = {}  # the last collected stats

    def register_source(self, name: str, source_func: Callable[[], Any]) -> None:
        """
        Register a payload source function.

        Args:
            name: Unique name for this source
            source_func: Function that returns data to include in payload
        """
        self._sources[name] = source_func
        logger.debug(
            "Registered stats source: '%s' => '%s'", name, source_func.__name__
        )

    def unregister_source(self, name: str) -> bool:
        """Remove a registered source. Returns True if source was found and removed."""
        if name in self._sources:
            del self._sources[name]
            logger.debug("Unregistered stats source: '%s'", name)
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
            logger.exception("Error executing stats source '%s'", name)
            return name, None, False

    async def _compile_payload(self) -> dict:
        """Compile payload from all registered sources."""
        # payload = {"timestamp": int(time.time() * 1000)}
        payload = {"timestamp": datetime.now(UTC).isoformat()}

        # Execute all sources
        for name, source_func in self._sources.items():
            source_name, data, success = await self._execute_source(name, source_func)
            if success and data is not None:
                payload[source_name] = data

        return payload

    async def load(self):
        """Load stats from JSON file."""
        if not self.stats_file.exists():
            logger.info("Stats file %s not found, starting fresh.", self.stats_file)
            return

        try:
            async with aiofiles.open(self.stats_file) as f:
                content = await f.read()
                self._current_stats = json.loads(content)
            logger.info("Loaded stats from %s", self.stats_file)
        except Exception:
            logger.exception("Failed to load stats")

    async def save(self):
        """Persist current stats to JSON file."""
        try:
            async with aiofiles.open(self.stats_file, "w") as f:
                content = json.dumps(self._current_stats, indent=2)
                await f.write(content)
            # logger.debug("Saved stats to %s", self.stats_file)
        except Exception:
            logger.exception("Failed to save stats")

    def all(self) -> dict:
        """Return current collected stats."""
        return dict(self._current_stats)

    async def collect_now(self) -> dict:
        """Collect stats from all sources and update current stats."""
        self._current_stats = await self._compile_payload()
        return self._current_stats

    async def _periodic_save(self):
        """Periodic task that collects stats and saves them."""
        while not self._shutdown.is_set():
            try:
                await asyncio.wait_for(
                    self._shutdown.wait(), timeout=self.save_interval
                )
            except TimeoutError:
                # Collect fresh stats and save them
                await self.collect_now()
                await self.save()

        # Final collection and save on shutdown
        await self.collect_now()
        await self.save()

    async def start(self):
        """Start periodic save task."""
        if self._task is None:
            # Load existing stats first
            await self.load()
            logger.info("Starting stats tracker periodic save task")
            self._task = asyncio.create_task(
                self._periodic_save(), name="stats_tracker"
            )

    async def stop(self):
        """Stop periodic save task and save one last time."""
        if self._task is not None:
            logger.info("Stopping stats tracker periodic save task")
            self._shutdown.set()
            await self._task
            self._task = None
            self._shutdown.clear()
