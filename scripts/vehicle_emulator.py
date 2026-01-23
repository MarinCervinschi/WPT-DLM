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
    VEHICLE_ID = "vehicle_001"
    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883
    GPX_FILE_PATH = project_root / "shared" / "tracks" / "home-stadium.gpx"

    # Check if GPX file exists
    if not GPX_FILE_PATH.exists():
        logger.error(f"GPX file not found: {GPX_FILE_PATH}")
        sys.exit(1)

    try:
        logger.info("🚗 Starting Vehicle Emulator...")

        mqtt_service = MQTTService(
            broker_host=MQTT_BROKER_HOST,
            broker_port=MQTT_BROKER_PORT,
            client_id=f"{VEHICLE_ID}_emulator",
        )
        mqtt_service.connect()
        time.sleep(1)  # Wait for connection

        if not mqtt_service.is_connected:
            logger.error("Failed to connect to MQTT broker")
            sys.exit(1)

        logger.info("✅ Connected to MQTT broker")

        vehicle = ElectricVehicle(
            vehicle_id=VEHICLE_ID,
            mqtt_service=mqtt_service,
            gpx_file_name=str(GPX_FILE_PATH),
        )

        vehicle.start()
        logger.info(f"🚗 Vehicle {VEHICLE_ID} started and publishing telemetry")

        def signal_handler(signum, frame):
            logger.info("🛑 Received shutdown signal, stopping vehicle...")
            vehicle.stop()
            mqtt_service.disconnect()
            logger.info("✅ Vehicle emulator stopped")
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
            if "vehicle" in locals():
                vehicle.stop()
            if "mqtt_service" in locals():
                mqtt_service.disconnect()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()
