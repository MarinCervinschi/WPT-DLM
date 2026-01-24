import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.mqtt_dtos import GeoLocation
from shared.services.mqtt_service import MQTTService
from shared.policies import PriorityPolicy
from smart_objects.hub import Hub

import logging

logging.basicConfig(
    level=logging.INFO,  # Set root to INFO to reduce noise
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dlm_priority_example")

# Enable DEBUG for specific service
#logging.getLogger("DLMService-hub_01").setLevel(logging.DEBUG)


def main():
    try:
        mqtt_service = MQTTService(
            broker_host="localhost", broker_port=1883, client_id="hub_01"
        )
        mqtt_service.connect()
        time.sleep(1)  # Wait for connection

        if not mqtt_service.is_connected:
            print("❌ Failed to connect to MQTT broker. Exiting.")
            return

        hub = Hub(
            hub_id="hub_01",
            mqtt_service=mqtt_service,
            location=GeoLocation(latitude=44.6469, longitude=10.9252, altitude=50.0),
            max_grid_capacity_kw=180.0,  # Limited grid capacity
            firmware_version="1.0.0",
            dlm_interval=5.0,  # Apply policy every 5 seconds
            dlm_policy=PriorityPolicy(max_grid_capacity_kw=180.0),
        )

        hub.add_node(node_id="node_01", max_power_kw=78.0, simulation=True)
        hub.add_node(node_id="node_02", max_power_kw=78.0, simulation=True)
        hub.add_node(node_id="node_03", max_power_kw=78.0, simulation=True)

        hub.start()

        print("\n" + "=" * 60)
        print("🏁 Hub started - listening for vehicle requests")
        print("📊 Grid capacity: 180kW | DLM Policy: Priority")
        print("=" * 60 + "\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user, shutting down...")
            print("\n🛑 Stopping hub...")
            hub.stop()
            mqtt_service.disconnect()
            print("✅ Example completed")
            return

    except Exception as e:
        logger.error(f"An error occurred while starting the hub: {e}")
        return
    finally:

        # Stop everything
        print("\n🛑 Stopping hub...")
        hub.stop()

        mqtt_service.disconnect()

        print("✅ Example completed")


if __name__ == "__main__":
    main()
