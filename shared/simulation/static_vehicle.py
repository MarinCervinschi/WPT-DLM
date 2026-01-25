import logging
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.mqtt_dtos import GeoLocation
from shared.services.mqtt_service import MQTTService
from smart_objects.vehicle import ElectricVehicle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("StaticVehicle")


def run_static_vehicle():
    """Run a static vehicle for hardware testing."""
    logger.info("Starting Static Vehicle for Hardware Testing")

    STATIC_POSITION = GeoLocation(latitude=44.62958, longitude=10.94864, altitude=50.0)

    VEHICLE_ID = "EJ231ZK"

    mqtt_service = MQTTService(
        broker_host="localhost",
        broker_port=1883,
        client_id=f"{VEHICLE_ID}_mqtt",
    )

    logger.info("Connecting to MQTT broker...")
    mqtt_service.connect()
    time.sleep(1)

    if not mqtt_service.is_connected:
        logger.error("Failed to connect to MQTT broker. Exiting.")
        return

    logger.info("✅ MQTT connected")

    vehicle = ElectricVehicle(
        vehicle_id=VEHICLE_ID,
        mqtt_service=mqtt_service,
        gpx_file_name=None,
        simulation=False,
        static_position=STATIC_POSITION,
    )

    logger.info(f"Vehicle {VEHICLE_ID} created at position {STATIC_POSITION}")
    logger.info("Starting vehicle...")

    vehicle.start()

    logger.info("✅ Vehicle started and ready")
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nStopping vehicle...")
        vehicle.stop()
        mqtt_service.disconnect()
        logger.info("Vehicle stopped")


if __name__ == "__main__":
    run_static_vehicle()
