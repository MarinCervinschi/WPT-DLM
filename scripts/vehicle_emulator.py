import logging
import signal
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.services import MQTTService
from smart_objects import ElectricVehicle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("vehicle_emulator")


def main():
    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883

    try:
        logger.info("🚗 Starting Vehicle Emulator...")

        vehicles = [
            {"id": "vehicle_01", "gpx": "shared/tracks/home-stadium.gpx"},
            {"id": "vehicle_02", "gpx": "shared/tracks/web-dief.gpx"},
            {"id": "vehicle_03", "gpx": "shared/tracks/kokoro-iport.gpx"},
        ]

        vehicles_instances = []
        for v in vehicles:

            if not Path(v["gpx"]).is_file():
                logger.error(f"GPX file not found: {v['gpx']}")
                continue

            # Create individual MQTT connection for each vehicle
            vehicle_mqtt = MQTTService(
                broker_host=MQTT_BROKER_HOST,
                broker_port=MQTT_BROKER_PORT,
                client_id=f"{v['id']}_emulator",
            )
            vehicle_mqtt.connect()
            time.sleep(0.5)  # Brief wait for connection

            if not vehicle_mqtt.is_connected:
                logger.error(f"Failed to connect MQTT for vehicle {v['id']}")
                continue

            vehicle = ElectricVehicle(
                vehicle_id=v["id"],
                mqtt_service=vehicle_mqtt,
                gpx_file_name=str(v["gpx"]),
            )
            vehicles_instances.append((vehicle, vehicle_mqtt))

            vehicle.start()
            logger.info(f"🚗 Vehicle {v['id']} started with dedicated MQTT connection")

        def signal_handler(signum, frame):
            logger.info("🛑 Received shutdown signal, stopping vehicles...")
            for vehicle, mqtt_service in vehicles_instances:
                vehicle.stop()
                mqtt_service.disconnect()
            logger.info("✅ All vehicles stopped")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("🚗 Vehicle emulator running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"❌ Error in vehicle emulator: {e}")
        sys.exit(1)
    finally:
        try:
            for vehicle, mqtt_service in vehicles_instances:
                vehicle.stop()
                mqtt_service.disconnect()
            logger.info("✅ All vehicles stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()
