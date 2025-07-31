import asyncio
import json
import logging
from collections import defaultdict
from collections.abc import Callable
from contextlib import AsyncExitStack, suppress

import aiomqtt

logger = logging.getLogger(__name__)


class AsyncMqttClient:
    """
    MQTT Client wrapper that contains the base client behavior we typically
    require.

    Reliability engineered to handle network issues.

    - Auto-reconnect on failure
    - Subscribed topic tracking (for auto-reconnect)
    - Logging of subscriptions
    - Multiple handlers per topic support
    - On connect
        - Subscribe to topics
        - Send "online" status
        - Try again on failure
    - On clean disconnect
        - Send "offline" status
    - Set LWT to notify "offline" status
    """

    def __init__(  # noqa: PLR0913
        self,
        *,
        base_topic: str,
        hostname="localhost",
        port=1883,
        identifier=None,
        username=None,
        password=None,
        keep_alive=60,
        reconnect_interval=5,
    ):
        self.hostname = hostname
        self.port = port
        self.identifier = identifier
        self.username = username
        self.password = password
        self.keep_alive = keep_alive
        self.reconnect_interval = reconnect_interval

        self.subscriptions = []
        self.message_handlers = defaultdict(
            list
        )  # Changed to support multiple handlers

        self.base_topic = base_topic.rstrip("/")

        self._message_map = {}
        self._stack = AsyncExitStack()
        self._listener_task = None
        self._reconnect_task = None
        self._client = None

        self.connected_event = asyncio.Event()
        self.shutdown_event = asyncio.Event()
        self.on_post_connect = None

    def build_topic(self, topic: str) -> str:
        return f"{self.base_topic}/{topic.lstrip('/')}"

    def _get_lwt(self):
        return {
            "topic": self.build_topic("status"),
            "payload": json.dumps({"state": "offline"}).encode(),
            "retain": True,
            "qos": 2,
        }

    async def connect(self):
        """Start the MQTT client with auto-reconnect capability."""
        if self._reconnect_task and not self._reconnect_task.done():
            logger.warning("Connect called but reconnect task already running")
            return

        self.shutdown_event.clear()
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    async def disconnect(self):
        """Cleanly disconnect from MQTT broker."""
        logger.info("Initiating clean disconnect...")
        self.shutdown_event.set()

        # Cancel reconnect task
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reconnect_task

        # Send offline status if connected
        if self.connected_event.is_set():
            try:
                await self.send_status("offline")
            except Exception as e:  # noqa: BLE001
                logger.warning("Failed to send offline status: %s", e)
        # Clean up resources
        await self._cleanup_connection()
        logger.info("Disconnected from MQTT broker")

    async def _reconnect_loop(self):
        """Main reconnection loop that handles connection failures."""
        while not self.shutdown_event.is_set():
            try:
                await self._connect_once()

                # Wait for either shutdown or connection loss
                shutdown_wait_task = asyncio.create_task(self.shutdown_event.wait())
                await asyncio.wait(
                    [shutdown_wait_task, self._listener_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                shutdown_wait_task.cancel()

            except asyncio.CancelledError:
                logger.info("Reconnect loop cancelled")
                break
            except aiomqtt.MqttError as e:
                logger.warning(
                    "MQTT error (%s). Reconnecting in %ds...",
                    e,
                    self.reconnect_interval,
                )

            # Clean up failed connection
            await self._cleanup_connection()

            # Wait before reconnecting (unless shutting down)
            if not self.shutdown_event.is_set():
                try:
                    await asyncio.wait_for(
                        self.shutdown_event.wait(), timeout=self.reconnect_interval
                    )
                except TimeoutError:
                    continue

    async def _connect_once(self):
        """Attempt to connect to MQTT broker once."""
        logger.info(
            "Attempting to connect to MQTT broker: %s:%s",
            self.hostname,
            self.port,
        )

        try:
            self._client = aiomqtt.Client(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                keepalive=self.keep_alive,
                identifier=self.identifier,
                will=aiomqtt.Will(**self._get_lwt()),
                # logger=logger,
            )

            await self._stack.enter_async_context(self._client)
            self.connected_event.set()
            logger.info("Connected to MQTT broker: %s:%s", self.hostname, self.port)

            # Resubscribe to all stored subscriptions
            for topic, qos in self.subscriptions:
                logger.info("Subscribing to: %s (QoS %d)", topic, qos)
                await self._client.subscribe(topic, qos=qos)

            await self.send_status("online")

            self._listener_task = asyncio.create_task(self._message_loop())

            if self.on_post_connect:
                try:
                    await self.on_post_connect()
                except Exception:
                    logger.exception("Error in post-connect hook")

        except aiomqtt.MqttError as e:
            logger.error("MQTT connection error: %s", e)  # noqa: TRY400
            self.connected_event.clear()
            raise
        except Exception:
            logger.exception("Unexpected error during connection")
            self.connected_event.clear()
            raise

    async def _cleanup_connection(self):
        """Clean up connection resources."""
        self.connected_event.clear()

        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._listener_task
            self._listener_task = None

        try:
            await self._stack.aclose()
        except Exception as e:  # noqa: BLE001
            logger.error("Error closing async stack %s", e)  # noqa: TRY400

        self._stack = AsyncExitStack()
        self._client = None

    async def _message_loop(self):
        """Listen for incoming MQTT messages."""
        try:
            async for msg in self._client.messages:
                if self.shutdown_event.is_set():
                    break
                await self._handle_message(msg.topic, msg.payload.decode())
        except asyncio.CancelledError:
            pass
        except aiomqtt.MqttError as e:
            logger.info("MQTT connection lost during message iteration: %s", e)
            self.connected_event.clear()
        except Exception:
            logger.exception("Unexpected error in message loop")
            self.connected_event.clear()
            raise

    async def _handle_message(self, topic, payload_raw):
        try:
            payload = json.loads(payload_raw) if payload_raw else {}
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON: %s", e)
            return

        # logger.debug("Handle message: topic=%s | payload=%s", topic, payload)

        handlers = self.message_handlers.get(str(topic), [])
        if handlers:
            # Execute all handlers for this topic
            for handler in handlers:
                try:
                    await handler(payload, topic=str(topic))
                except Exception as e:
                    logger.exception(
                        "Error in handler %s for topic: %s", handler.__name__, topic
                    )
                    await self.send_message(str(e), error=True)
        else:
            logger.warning("Unhandled topic: %s", topic)

    # --------------------------------------------------------------------------
    # Subscriptions
    # --------------------------------------------------------------------------

    async def add_subscriptions(self, topics: list[tuple[str, int]]):
        """Add subscriptions (will auto-subscribe if connected)."""
        for topic, qos in topics:
            if (topic, qos) not in self.subscriptions:
                self.subscriptions.append((topic, qos))
                if self.connected_event.is_set() and self._client:
                    try:
                        await self._client.subscribe(topic, qos=qos)
                        logger.debug("Subscribed to: %s (QoS %d)", topic, qos)
                    except Exception as e:  # noqa: BLE001
                        logger.error("Failed to subscribe to %s: %s", topic, e)  # noqa: TRY400

    async def remove_subscriptions(self, topics: list[str]):
        """Remove subscriptions (will auto-unsubscribe if connected)."""
        for topic in topics:
            self.subscriptions = [t for t in self.subscriptions if t[0] != topic]
            if self.connected_event.is_set() and self._client:
                try:
                    await self._client.unsubscribe(topic)
                    logger.debug("Unsubscribed from: %s", topic)
                except Exception as e:  # noqa: BLE001
                    logger.error("Failed to unsubscribe from %s: %s", topic, e)  # noqa: TRY400

    # --------------------------------------------------------------------------
    # Message Handling - Modified for multiple handlers
    # --------------------------------------------------------------------------

    def add_message_handler(self, topic: str, func: callable):
        """Add a message handler for a topic (multiple handlers per topic supported)."""
        if func not in self.message_handlers[topic]:
            self.message_handlers[topic].append(func)
            logger.debug(
                "Add handler: %s => %s (total: %d)",
                topic,
                func.__name__,
                len(self.message_handlers[topic]),
            )
        else:
            logger.debug("Handler %s already exists for topic %s", func.__name__, topic)

    def remove_message_handler(self, topic: str, func: Callable | None = None):
        """Remove a specific handler or all handlers for a topic."""
        if func is None:
            # Remove all handlers for this topic
            if topic in self.message_handlers:
                count = len(self.message_handlers[topic])
                del self.message_handlers[topic]
                logger.debug("Removed all %d handlers for topic: %s", count, topic)
        # Remove specific handler
        elif topic in self.message_handlers and func in self.message_handlers[topic]:
            self.message_handlers[topic].remove(func)
            logger.debug(
                "Remove handler: %s => %s (remaining: %d)",
                topic,
                func.__name__,
                len(self.message_handlers[topic]),
            )
            # Clean up empty lists
            if not self.message_handlers[topic]:
                del self.message_handlers[topic]
        else:
            logger.debug(
                "Handler %s not found for topic %s",
                func.__name__ if func else "None",
                topic,
            )

    def add_message_handlers(self, handlers: dict):
        """Add multiple handlers. Handlers dict can map topic to single function or list of functions."""
        for topic, func_or_list in handlers.items():
            if isinstance(func_or_list, list):
                for func in func_or_list:
                    self.add_message_handler(topic, func)
            else:
                self.add_message_handler(topic, func_or_list)

    def remove_message_handlers(self, keys: list[str]):
        """Remove all handlers for the specified topics."""
        for key in keys:
            self.remove_message_handler(key)

    def get_message_handlers(self, topic: str | None = None) -> dict:
        """Get handlers for a specific topic or all handlers."""
        if topic:
            return {topic: self.message_handlers.get(topic, [])}
        return dict(self.message_handlers)

    def get_handler_count(self, topic: str) -> int:
        """Get the number of handlers for a specific topic."""
        return len(self.message_handlers.get(topic, []))

    # --------------------------------------------------------------------------
    # Publishing
    # --------------------------------------------------------------------------

    async def publish_json(self, topic, payload=None, qos=0, retain=False):
        """Publish JSON payload to topic."""
        if not self.connected_event.is_set() or not self._client:
            msg = "MQTT client not connected"
            # raise RuntimeError(msg)
            logger.error("Cannot publish topic: '%s' - %s", topic, msg)
            return

        try:
            payload_bytes = json.dumps(payload or {}).encode()
            await self._client.publish(topic, payload_bytes, qos=qos, retain=retain)
        except aiomqtt.MqttError as e:
            logger.error("MQTT publish error for topic %s: %s", topic, e)  # noqa: TRY400
            self.connected_event.clear()
            raise
        except Exception as e:
            logger.error("Unexpected error publishing to topic %s: %s", topic, e)  # noqa: TRY400
            raise

    async def send_status(self, state: str):
        """Send status message."""
        await self.publish_json(
            self.build_topic("status"), {"state": state}, qos=1, retain=True
        )

    async def send_message(self, message, extra=None, error=False):
        """Send a general message."""
        payload = {"message": message}
        if extra:
            payload.update(extra)
        if error:
            payload["is_error"] = True
        await self.publish_json(self.build_topic("message"), payload, qos=2)

    def get_subscriptions(self) -> list[tuple[str, int]]:
        return self.subscriptions.copy()
