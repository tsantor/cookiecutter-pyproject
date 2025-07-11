import asyncio
import logging

logger = logging.getLogger("{{cookiecutter.package_name}}")


class HeartbeatService:
    def __init__(self, mqtt, base_topic: str, payload_func, interval: int = 10):
        """
        Args:
            mqtt: MQTT client
            base_topic: base topic to publish to
            payload_func: callable returning dict payload for heartbeat
            interval: heartbeat interval in seconds
        """
        self.mqtt = mqtt
        self.base_topic = base_topic
        self.payload_func = payload_func
        self.interval = interval
        self._shutdown = asyncio.Event()

    async def run(self):
        logger.info("Heartbeat started")
        topic = f"{self.base_topic}/heartbeat"

        while not self._shutdown.is_set():
            try:
                payload = self.payload_func()
                await self.mqtt.publish_json(topic, payload, qos=0, retain=True)
            except Exception:
                logger.exception("Error in heartbeat publishing")

            try:
                await asyncio.wait_for(self._shutdown.wait(), timeout=self.interval)
            except TimeoutError:
                continue  # normal heartbeat

    def shutdown(self):
        logger.info("Shutting down heartbeat service")
        self._shutdown.set()
