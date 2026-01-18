import json
import logging
import time
from typing import Dict, Optional

import paho.mqtt.client as mqtt

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML not installed. Run: uv add pyyaml")

from hub import Hub, create_hub_from_config

logger = logging.getLogger(__name__)


class Gateway:
    """Main gateway coordinating multiple hubs and MQTT communication."""

    def __init__(self, config_file: str = "config.yaml"):
        """Initialize gateway from configuration file."""
        self.config = self._load_config(config_file)
        self.hubs: Dict[str, Hub] = {}
        self.mqtt_client: Optional[mqtt.Client] = None
        self.running = False

        # Load configuration
        self._setup_logging()
        self._initialize_hubs()
        self._setup_mqtt()

    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config file {config_file}: {e}")
            raise

    def _setup_logging(self):
        """Configure logging from config."""
        log_config = self.config.get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO"))
        log_format = log_config.get(
            "format", "%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.basicConfig(level=log_level, format=log_format)
        logger.info("Logging configured")

    def _initialize_hubs(self):
        """Create all hubs from configuration."""
        hub_configs = self.config.get("hubs", [])

        if not hub_configs:
            logger.warning("No hubs defined in configuration!")
            return

        for hub_config in hub_configs:
            try:
                hub = create_hub_from_config(hub_config)
                self.hubs[hub.hub_id] = hub
                logger.info(f"Hub {hub.hub_id} initialized with {len(hub.nodes)} nodes")
            except Exception as e:
                logger.error(f"Failed to create hub {hub_config.get('hub_id')}: {e}")

        total_nodes = sum(len(hub.nodes) for hub in self.hubs.values())
        logger.info(f"Gateway initialized: {len(self.hubs)} hubs, {total_nodes} nodes")

    def _setup_mqtt(self):
        """Setup MQTT client and callbacks."""
        mqtt_config = self.config.get("mqtt", {})

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message

        broker = mqtt_config.get("broker", "localhost")
        port = mqtt_config.get("port", 1883)

        try:
            self.mqtt_client.connect(broker, port, 60)
            logger.info(f"MQTT client connected to {broker}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback when MQTT client connects."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to vehicle status updates for all hubs
            for hub_id in self.hubs.keys():
                vehicle_topic = f"iot/hubs/{hub_id}/vehicles/+"
                client.subscribe(vehicle_topic)
                logger.info(f"Subscribed to vehicle updates: {vehicle_topic}")

                # Subscribe to policy updates for each hub
                policy_topic = f"iot/hubs/{hub_id}/policy"
                client.subscribe(policy_topic)
                logger.info(f"Subscribed to policy updates: {policy_topic}")
        else:
            logger.error(f"MQTT connection failed with code: {rc}")

    def _on_mqtt_message(self, client, userdata, msg):
        """
        Callback for incoming MQTT messages from cloud.

        Two types of messages:

        1. Vehicle status updates:
           Topic: iot/hubs/<hub_id>/vehicles/<vehicle_id>
           Payload: {
               "node_id": "station_1",
               "vehicle_soc": 45,
               "authorized": true,
               "connected": true  // false for disconnection
           }

        2. Policy updates:
           Topic: iot/hubs/<hub_id>/policy
           Payload: {
               "policy_name": "priority"
           }
        """
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) < 3:
                logger.warning(f"Malformed topic: {msg.topic}")
                return

            hub_id = topic_parts[2]
            hub = self.hubs.get(hub_id)
            if not hub:
                logger.warning(f"Unknown hub: {hub_id}")
                return

            # Parse payload
            try:
                payload = json.loads(msg.payload.decode())
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from {msg.topic}: {e}")
                return

            # Handle based on topic type
            if len(topic_parts) >= 4 and topic_parts[3] == "vehicles":
                # Vehicle status update
                self._handle_vehicle_update(hub, topic_parts, payload)
            elif len(topic_parts) >= 4 and topic_parts[3] == "policy":
                # Policy update
                self._handle_policy_update(hub, payload)
            else:
                logger.warning(f"Unknown message type: {msg.topic}")

        except Exception as e:
            logger.error(f"Error processing MQTT message from {msg.topic}: {e}")

    def _handle_vehicle_update(self, hub: Hub, topic_parts: list, payload: dict):
        """Handle vehicle status update from cloud."""
        vehicle_id = topic_parts[4] if len(topic_parts) > 4 else None
        node_id = payload.get("node_id")

        if not node_id:
            logger.error("Vehicle update missing node_id")
            return

        # Extract status
        connected = payload.get("connected", True)
        vehicle_soc = payload.get("vehicle_soc")
        authorized = payload.get("authorized", False)

        # If disconnected, clear vehicle info
        if not connected:
            vehicle_id = None
            vehicle_soc = None
            authorized = False

        # Update hub
        success = hub.update_vehicle_status(
            node_id, vehicle_id, vehicle_soc, authorized
        )

        if success:
            status = "connected" if connected else "disconnected"
            logger.info(
                f"Vehicle {status}: {hub.hub_id}/{node_id} - "
                f"vehicle={vehicle_id}, soc={vehicle_soc}, auth={authorized}"
            )

    def _handle_policy_update(self, hub: Hub, payload: dict):
        """Handle policy update from cloud."""
        policy_name = payload.get("policy_name")

        if not policy_name:
            logger.error("Policy update missing policy_name")
            return

        hub.update_policy(policy_name)
        logger.info(f"Hub {hub.hub_id} policy updated to: {policy_name}")

    def _publish_telemetry(self):
        """Publish telemetry from all hubs/nodes to cloud."""
        if not self.mqtt_client:
            logger.error("MQTT client not initialized")
            return

        qos = self.config.get("mqtt", {}).get("qos", 0)

        for hub_id, hub in self.hubs.items():
            telemetry_data = hub.read_all_telemetry()

            for node_id, telemetry in telemetry_data.items():
                # Publish to MQTT
                topic = f"iot/hubs/{hub_id}/nodes/{node_id}/telemetry"
                payload = json.dumps(telemetry)

                result = self.mqtt_client.publish(topic, payload, qos=qos)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.debug(f"Published telemetry: {topic} -> Data: {payload}")
                else:
                    logger.warning(f"Failed to publish to {topic}: {result.rc}")

    def run(self):
        """Main gateway loop."""
        if not self.mqtt_client:
            logger.error("MQTT client not initialized, cannot run")
            return

        self.running = True
        self.mqtt_client.loop_start()

        interval = self.config.get("telemetry", {}).get("publish_interval_seconds", 1)

        logger.info(f"Gateway running (telemetry interval: {interval}s)")
        logger.info(f"Managing {len(self.hubs)} hubs:")
        for hub_id, hub in self.hubs.items():
            logger.info(f"  - {hub_id}: {len(hub.nodes)} nodes ({hub.hub_type})")

        try:
            while self.running:
                self._publish_telemetry()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop()

    def stop(self):
        """Stop the gateway gracefully."""
        logger.info("Stopping gateway...")
        self.running = False

        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

        logger.info("Gateway stopped")


def main():
    """Entry point."""
    try:
        gateway = Gateway("config.yaml")
        gateway.run()
    except Exception as e:
        logger.error(f"Gateway failed to start: {e}")
        raise


if __name__ == "__main__":
    main()
