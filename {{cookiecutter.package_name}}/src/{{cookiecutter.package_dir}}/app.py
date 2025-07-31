import asyncio
import logging

from .mqtt import client
from .services.heartbeat import HeartbeatService
from .settings import SETTINGS_DIR, Settings
from .shutdown import ShutdownManager
from .stats import StatsTracker

logger = logging.getLogger("{{cookiecutter.package_name}}")


class MyApp:
    """Main application."""

    def __init__(self, config: Settings):
        self.config = config
        self._mqtt: client.AsyncMqttClient | None = None
        self._tasks: set[asyncio.Task] = set()
        self._heartbeat: HeartbeatService | None = None

        self._stats = StatsTracker(
            stats_file=SETTINGS_DIR / "stats.json", save_interval=10.0
        )

    async def setup_mqtt(self) -> None:
        """Initialize and configure MQTT client."""
        self._mqtt = client.AsyncMqttClient(
            base_topic=f"project/app/{self.config.mqtt.device_id}",
            hostname=self.config.mqtt.host,
            port=self.config.mqtt.port,
            identifier=self.config.mqtt.device_id,
            username=self.config.mqtt.username,
            password=self.config.mqtt.password,
            keep_alive=self.config.mqtt.keep_alive,
        )

        # Setup MQTT topics
        config_topic = self._mqtt.build_topic("config")
        command_topic = self._mqtt.build_topic("command")

        # Subscribe to topics
        subscriptions = [
            (config_topic, 1),
            (command_topic, 1),
        ]
        await self._mqtt.add_subscriptions(subscriptions)

        # Add message handlers
        message_handlers = {
            config_topic: self.handle_config,
            command_topic: self.handle_command,
        }
        self._mqtt.add_message_handlers(message_handlers)

        await self._mqtt.connect()
        await self._mqtt.connected_event.wait()

    # --------------------------------------------------------------------------
    # MQTT message handlers
    # --------------------------------------------------------------------------

    async def handle_config(self, payload: dict) -> None:
        """Handle incoming MQTT commands."""
        try:
            logger.info("Received config: %r", payload)
        except Exception:
            logger.exception("Error processing config: %r", payload)

    async def handle_command(self, data: dict) -> None:
        """Handle 'foo' command."""
        logger.info("Received command with data: %r", data)
        # Schedule handler as independent task
        task = asyncio.create_task(asyncio.sleep(data["sleep"]), name="command_handler")
        self._tasks.add(task)

        # Cleanup done tasks
        task.add_done_callback(self._tasks.discard)
        task.add_done_callback(
            lambda t: logger.info(
                "Task completed: %r (name=%s)", t.result(), t.get_name()
            )
        )

    # --------------------------------------------------------------------------
    # Stats
    # --------------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Get stats."""
        # return self._monitor.get_stats()
        return {}

    def restore_stats(self) -> None:
        """Restore sensor stats from saved data."""
        # saved_stats = self._stats.all().get("sensors", {})
        # self._monitor.restore_stats(saved_stats)
        logger.debug("TODO: Implement restore_stats")

    async def setup_stats(self) -> None:
        """Initialize and configure stats tracker."""
        self._stats.register_source("foo", self.get_stats)
        await self._stats.start()
        # logger.debug("TODO: Implement setup_stats")

    # --------------------------------------------------------------------------
    # App lifecycle management
    # --------------------------------------------------------------------------

    async def start_background_tasks(self) -> None:
        """Start all background tasks."""
        # self._monitor = BreakBeamMonitor(
        #     mqtt=self._mqtt,
        #     sensor_config=self.config.sensor,
        #     sound=self.config.app.sound,
        # )
        # self._tasks.add(
        #     asyncio.create_task(
        #         self._monitor.start(),
        #         name="monitor",
        #     )
        # )

        # Start heartbeat service (should be last to start)
        self._heartbeat = HeartbeatService(mqtt=self._mqtt)
        self._tasks.add(
            asyncio.create_task(
                self._heartbeat.run(),
                name="heartbeat",
            )
        )

        # self._heartbeat.register_source("health", get_health_info)

    async def shutdown_services(self) -> None:
        """Shutdown all services gracefully."""
        logger.info("-" * 40)

        if self._mqtt:
            await self._mqtt.disconnect()

        if self._heartbeat:
            await self._heartbeat.stop()

        # if self._monitor:
        #     await self._monitor.stop()

        if self._stats:
            await self._stats.stop()

    async def run(self):
        """Run the main application loop."""
        shutdown = ShutdownManager()
        shutdown.install()

        try:
            await self.setup_mqtt()
            await self.start_background_tasks()
            await self.setup_stats()
            self.restore_stats()
            await shutdown.wait()
            await self.shutdown_services()
        except Exception:
            logger.exception("Error in main loop")
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info(
            "Waiting for %d running tasks to finish...",
            len(self._tasks),
        )
        for task in self._tasks:
            logger.debug("Running task: '%s'", task.get_name())

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*self._tasks, return_exceptions=True),
                timeout=5,
            )
            for task, result in zip(self._tasks, results, strict=True):
                if isinstance(result, Exception):
                    logger.error(
                        "Task '%s' raised an exception: %s",
                        task.get_name(),
                        result,
                    )
            logger.info("All tasks complete. Shutting down cleanly.")
        except TimeoutError:
            logger.warning("Tasks did not complete within timeout")
