import asyncio
import json
import logging
from contextlib import AsyncExitStack, suppress

import aiomqtt


class AsyncMqttClient:
    """
    MQTT Client wrapper that contains the base client behavior we typically
    require.

    Reliability engineered to handle network issues.

    - Auto-reconnect on failure
    - Subscribed topic tracking (for auto-reconnect)
    - Logging of subscriptions
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
        logger=None,
    ):
        self.hostname = hostname
        self.port = port
        self.identifier = identifier
        self.username = username
        self.password = password
        self.keep_alive = keep_alive
        self.reconnect_interval = reconnect_interval
        self.subscriptions = []
        self.message_handlers = {}

        self.base_topic = base_topic.rstrip("/")

        self._message_map = {}
        self._stack = AsyncExitStack()
        self._listener_task = None
        self._reconnect_task = None
        self._client = None
        self._connected = False
        self.connected_event = asyncio.Event()
        self._shutdown_event = asyncio.Event()
        self.on_post_connect = None
        self._logger = logger or logging.getLogger(__name__)

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
            self._logger.warning("Connect called but reconnect task already running")
            return

        self._shutdown_event.clear()
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    async def disconnect(self):
        """Cleanly disconnect from MQTT broker."""
        self._logger.info("Initiating clean disconnect...")
        self._shutdown_event.set()

        # Cancel reconnect task
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reconnect_task

        # Send offline status if connected
        if self._connected:
            try:
                await self.send_status("offline")
            except Exception as e:  # noqa: BLE001
                self._logger.warning("Failed to send offline status: %s", e)

        # Clean up resources
        await self._cleanup_connection()
        self._logger.info("Disconnected from MQTT broker")

    async def _reconnect_loop(self):
        """Main reconnection loop that handles connection failures."""
        while not self._shutdown_event.is_set():
            try:
                await self._connect_once()
                # Connection successful, wait for disconnection or shutdown
                while self._connected and not self._shutdown_event.is_set():  # noqa: ASYNC110
                    await asyncio.sleep(1)

            except asyncio.CancelledError:
                self._logger.info("Reconnect loop cancelled")
                break
            except aiomqtt.MqttError as e:
                self._logger.warning(
                    "MQTT error (%s). Reconnecting in %ds...",
                    e,
                    self.reconnect_interval,
                )
            except Exception as e:  # noqa: BLE001
                self._logger.warning(
                    "Unexpected connection error (%s). Reconnecting in %ds...",
                    e,
                    self.reconnect_interval,
                )

            # Clean up failed connection
            await self._cleanup_connection()

            # Wait before reconnecting (unless shutting down)
            if not self._shutdown_event.is_set():
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(), timeout=self.reconnect_interval
                    )
                    break  # Shutdown requested
                except TimeoutError:
                    continue  # Normal reconnect interval

    async def _connect_once(self):
        """Attempt to connect to MQTT broker once."""
        self._logger.info(
            "Attempting to connect to MQTT broker: %s:%s",
            self.hostname,
            self.port,
        )

        try:
            # Create new client
            self._client = aiomqtt.Client(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                keepalive=self.keep_alive,
                identifier=self.identifier,
                will=aiomqtt.Will(**self._get_lwt()),
            )

            # Use the async context manager
            await self._stack.enter_async_context(self._client)
            self._connected = True
            self.connected_event.set()
            self._logger.info(
                "Connected to MQTT broker: %s:%s", self.hostname, self.port
            )

            # Resubscribe to all stored subscriptions
            for topic, qos in self.subscriptions:
                self._logger.info("Subscribing to: %s (QoS %d)", topic, qos)
                await self._client.subscribe(topic, qos=qos)

            # Send online status
            await self.send_status("online")

            # Start message listener
            self._listener_task = asyncio.create_task(self._message_loop())

            # Optional post-connect hook
            if self.on_post_connect:
                try:
                    await self.on_post_connect()
                except Exception:
                    self._logger.exception("Error in post-connect hook")

        except aiomqtt.MqttError as e:
            self._logger.error("MQTT connection error: %s", e)  # noqa: TRY400
            self._connected = False
            raise
        except Exception:
            self._logger.exception("Unexpected error during connection")
            self._connected = False
            raise

    async def _cleanup_connection(self):
        """Clean up connection resources."""
        self._connected = False
        self.connected_event.clear()

        # Cancel listener task
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._listener_task
            self._listener_task = None

        # Close the async context stack
        try:
            await self._stack.aclose()
        except Exception as e:  # noqa: BLE001
            self._logger.error("Error closing async stack %s", e)  # noqa: TRY400

        # Create new stack for next connection
        self._stack = AsyncExitStack()
        self._client = None

    async def _message_loop(self):
        """Listen for incoming MQTT messages."""
        try:
            # Use messages as an async iterator (no parentheses)
            async for msg in self._client.messages:
                if self._shutdown_event.is_set():
                    break
                await self._handle_message(msg.topic, msg.payload.decode())
        except asyncio.CancelledError:
            # self._logger.info("Message loop cancelled")
            pass
        except aiomqtt.MqttError as e:
            # This is expected when connection is lost during message iteration
            self._logger.info("MQTT connection lost during message iteration: %s", e)
            # Mark as disconnected to trigger reconnection
            self._connected = False
        except Exception:
            self._logger.exception("Unexpected error in message loop")
            # Mark as disconnected to trigger reconnection
            self._connected = False
            raise

    async def _handle_message(self, topic, payload_raw):
        try:
            payload = json.loads(payload_raw) if payload_raw else {}
        except json.JSONDecodeError as e:
            self._logger.warning("Invalid JSON: %s", e)
            return

        self._logger.debug("Handle message: topic=%s | payload=%s", topic, payload)

        handler = self.message_handlers.get(str(topic))
        if handler:
            try:
                await handler(payload)
            except Exception as e:
                self._logger.exception("Error in handler for topic: %s", topic)
                await self.send_message(str(e), error=True)
        else:
            self._logger.warning("Unhandled topic: %s", topic)

    # --------------------------------------------------------------------------
    # Subscriptions
    # --------------------------------------------------------------------------

    async def add_subscriptions(self, topics: list[tuple[str, int]]):
        """Add subscriptions (will auto-subscribe if connected)."""
        for topic, qos in topics:
            if (topic, qos) not in self.subscriptions:
                self.subscriptions.append((topic, qos))
                # self._logger.debug("Added subscription: %s (QoS %d)", topic, qos)

                # Subscribe immediately if connected
                if self._connected and self._client:
                    try:
                        await self._client.subscribe(topic, qos=qos)
                        self._logger.debug("Subscribed to: %s (QoS %d)", topic, qos)
                    except Exception as e:  # noqa: BLE001
                        self._logger.error("Failed to subscribe to %s: %s", topic, e)  # noqa: TRY400

    async def remove_subscriptions(self, topics: list[str]):
        """Remove subscriptions (will auto-unsubscribe if connected)."""
        for topic in topics:
            # Remove from stored subscriptions
            self.subscriptions = [t for t in self.subscriptions if t[0] != topic]
            # self._logger.debug("Removed subscription: %s", topic)

            # Unsubscribe immediately if connected
            if self._connected and self._client:
                try:
                    await self._client.unsubscribe(topic)
                    self._logger.debug("Unsubscribed from: %s", topic)
                except Exception as e:  # noqa: BLE001
                    self._logger.error("Failed to unsubscribe from %s: %s", topic, e)  # noqa: TRY400

    # --------------------------------------------------------------------------
    # Message Handling
    # --------------------------------------------------------------------------

    def add_message_handler(self, topic: str, func: callable):
        self._logger.debug("Add handler: %s => %s", topic, func.__name__)
        self.message_handlers[topic] = func

    def remove_message_handler(self, topic: str):
        self._logger.debug("Remove handler: %s", topic)
        self.message_handlers.pop(topic, None)

    def add_message_handlers(self, handlers: dict):
        for topic, func in handlers.items():
            self.add_message_handler(topic, func)

    def remove_message_handlers(self, keys: list[str]):
        for key in keys:
            self.remove_message_handler(key)

    # --------------------------------------------------------------------------
    # Publishing
    # --------------------------------------------------------------------------

    async def publish_json(self, topic, payload=None, qos=0, retain=False):
        """Publish JSON payload to topic."""
        if not self._connected or not self._client:
            msg = "MQTT client not connected"
            raise RuntimeError(msg)

        try:
            payload_bytes = json.dumps(payload or {}).encode()
            await self._client.publish(topic, payload_bytes, qos=qos, retain=retain)
        except aiomqtt.MqttError as e:
            self._logger.error("MQTT publish error for topic %s: %s", topic, e)  # noqa: TRY400
            # Mark as disconnected to trigger reconnection
            self._connected = False
            raise
        except Exception as e:
            self._logger.error("Unexpected error publishing to topic %s: %s", topic, e)  # noqa: TRY400
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

    # --------------------------------------------------------------------------
    # Status Properties
    # --------------------------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        """Check if client is currently connected."""
        return self._connected

    def get_subscriptions(self) -> list[tuple[str, int]]:
        """Get list of current subscriptions."""
        return self.subscriptions.copy()
