import logging
from typing import Callable, Optional

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MQTTService:
    """Simple MQTT service for publishing and subscribing to topics."""

    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        client_id: Optional[str] = None,
    ):
        """
        Initialize MQTT service.

        Args:
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            client_id: Optional client ID (auto-generated if None)
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id=client_id or "")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self._connected = False

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self._connected = True
            logger.info(
                f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}"
            )
        else:
            self._connected = False
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self._connected = False
        if rc != 0:
            logger.warning(
                f"Unexpected disconnection from MQTT broker. Return code: {rc}"
            )
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Default message handler."""
        logger.debug(f"Received message on topic '{msg.topic}': {msg.payload.decode()}")

    def connect(self) -> None:
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()

    def publish(
        self, topic: str, payload: str, qos: int = 0, retain: bool = False
    ) -> None:
        """
        Publish a message to a topic.

        Args:
            topic: MQTT topic to publish to
            payload: Message payload
            qos: Quality of Service (0, 1, or 2)
            retain: Whether to retain the message
        """
        if not self._connected:
            logger.warning("Cannot publish: not connected to broker")
            return

        result = self.client.publish(topic, payload, qos=qos, retain=retain)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.debug(f"Published to '{topic}': {payload}")
        else:
            logger.error(f"Failed to publish to '{topic}'. Return code: {result.rc}")

    def subscribe(
        self, topic: str, callback: Optional[Callable] = None, qos: int = 0
    ) -> None:
        """
        Subscribe to a topic.

        Args:
            topic: MQTT topic to subscribe to
            callback: Optional callback function for messages (msg parameter)
            qos: Quality of Service (0, 1, or 2)
        """
        if callback:
            self.client.message_callback_add(
                topic, lambda client, userdata, msg: callback(msg)
            )

        result = self.client.subscribe(topic, qos=qos)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to subscribe to '{topic}'. Return code: {result[0]}")

    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from a topic.

        Args:
            topic: MQTT topic to unsubscribe from
        """
        result = self.client.unsubscribe(topic)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Unsubscribed from topic: {topic}")
        else:
            logger.error(
                f"Failed to unsubscribe from '{topic}'. Return code: {result[0]}"
            )

    @property
    def is_connected(self) -> bool:
        """Check if connected to the broker."""
        return self._connected
