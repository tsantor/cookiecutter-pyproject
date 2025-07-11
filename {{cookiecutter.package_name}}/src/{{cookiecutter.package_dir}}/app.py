import asyncio
import logging
from contextlib import asynccontextmanager

from .mqtt import client
from .services.heartbeat import HeartbeatService
from .settings import mqtt_config
from .shutdown import ShutdownManager

logger = logging.getLogger("{{cookiecutter.package_name}}")


class MyApp:
    """Main application."""

    def __init__(self):
        self.mqtt: client.AsyncMqttClient | None = None
        self._tasks: set[asyncio.Task] = set()
        self._shutdown = ShutdownManager()

        self.device_id = mqtt_config.device_id
        self.base_topic = f"client/project/{mqtt_config.device_id}"

        # Services
        self.heartbeat: HeartbeatService | None = None

    async def setup_mqtt(self) -> None:
        """Initialize and configure MQTT client."""
        self.mqtt = client.AsyncMqttClient(
            base_topic=self.base_topic,
            hostname=mqtt_config.host,
            port=mqtt_config.port,
            identifier=self.device_id,
            username=mqtt_config.username,
            password=mqtt_config.password,
            keep_alive=mqtt_config.keep_alive,
            logger=logger,
        )

        await self.mqtt.connect()

        # Add message handlers (TODO: Put into a service)
        message_handlers = {
            f"{self.base_topic}/config": self.handle_config,
            f"{self.base_topic}/command": self.handle_command,
        }
        self.mqtt.add_message_handlers(message_handlers)

    async def handle_config(self, payload: dict) -> None:
        """Handle incoming MQTT commands."""
        try:
            logger.info("Received config: %r", payload)
            # Add your command processing logic here

        except Exception:
            logger.exception("Error processing config: %r", payload)

    async def handle_command(self, payload: dict) -> None:
        try:
            logger.debug("-" * 40)
            logger.info("Received command: %r", payload)
            action = payload.get("action")
            data = payload.get("data", {})

            # Map actions to handler methods
            action_map = {
                "recalibrate": lambda: self.on_recalibrate(data),
                "foo": lambda: self.on_foo(data),
            }

            handler = action_map.get(action)
            if handler:
                await handler()
            else:
                logger.warning("Unknown action: %r", action)
        except Exception:
            logger.exception("Error processing command: %r", payload)

    # --------------------------------------------------------------------------
    # App specific commands
    # --------------------------------------------------------------------------

    async def on_recalibrate(self, data: dict) -> None:
        """Handle recalibration command."""
        logger.info("Recalibration requested")
        # Implement recalibration logic here
        await asyncio.sleep(2)  # Simulate recalibration delay
        logger.info("Recalibration complete")

    async def on_foo(self, data: dict) -> None:
        """Handle 'foo' command."""
        logger.info("Received 'foo' command with data: %r", data)
        # Schedule handler as independent task
        task = asyncio.create_task(asyncio.sleep(data["sleep"]), name="foo_handler")
        self._tasks.add(task)

        # Cleanup done tasks
        task.add_done_callback(self._tasks.discard)
        task.add_done_callback(
            lambda t: logger.info(
                "Task completed: %r (name=%s)", t.result(), t.get_name()
            )
        )

    # --------------------------------------------------------------------------

    async def run(self):
        self._shutdown.install()
        try:
            await self.setup_mqtt()
            await self.mqtt.connected_event.wait()

            def heartbeat_payload():
                return {
                    "timestamp": asyncio.get_event_loop().time(),
                    # Add more here as needed
                }

            self.heartbeat = HeartbeatService(
                mqtt=self.mqtt,
                base_topic=self.base_topic,
                payload_func=heartbeat_payload,
            )
            self._tasks.add(asyncio.create_task(self.heartbeat.run()))

            await self._shutdown.wait()

        except Exception:
            logger.exception("Error in main loop")
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("Starting cleanup...")
        if hasattr(self, "heartbeat"):
            self.heartbeat.shutdown()

        logger.info(
            "Waiting for %d running tasks to finish…",
            len(self._tasks),
        )
        await asyncio.gather(*self._tasks, return_exceptions=True)
        if self.mqtt:
            await self.mqtt.disconnect()
        logger.info("All tasks complete. Shutting down cleanly.")
