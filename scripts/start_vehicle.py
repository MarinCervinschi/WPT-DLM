import json
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.services.mqtt_service import MQTTService
from shared.mqtt_dtos import GeoLocation, VehicleTelemetry

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dlm_priority_example")


def simulate_cloud_request(mqtt_service: MQTTService, hub_id: str, vehicle_data: dict):
    """Simulate a vehicle request from the cloud/brain API."""
    topic = f"iot/hubs/{hub_id}/requests"
    payload = json.dumps(vehicle_data)
    mqtt_service.publish(topic, payload, qos=1)
    print(f"☁️  Cloud sent request: {vehicle_data}")


def simulate_vehicle_telemetry(
    mqtt_service: MQTTService, vehicle_id: str, telemetry_data: VehicleTelemetry
):
    """Simulate vehicle telemetry publishing."""
    topic = f"iot/vehicles/{vehicle_id}/telemetry"
    payload = telemetry_data.model_dump_json()
    mqtt_service.publish(topic, payload, qos=1)
    print(f"🚗 Vehicle {vehicle_id} sent telemetry: {telemetry_data}")


def main():

    try:
        # Initialize MQTT service
        mqtt_service = MQTTService(
            broker_host="localhost", broker_port=1883, client_id="vehicle_simulator"
        )
        mqtt_service.connect()
        time.sleep(1)  # Wait for connection

        if not mqtt_service.is_connected:
            print("❌ Failed to connect to MQTT broker. Exiting.")
            return

        print("\n" + "=" * 60)
        print("🏁 Vehicle simulator started - sending vehicle requests")
        print("=" * 60 + "\n")

        telemetry_data = VehicleTelemetry(
            geo_location=GeoLocation(latitude=44.6469, longitude=10.9252, altitude=50.0),
            battery_level=50,
            is_charging=False,
            speed_kmh=0,
            engine_temp_c=25.0,
        )
        simulate_vehicle_telemetry(mqtt_service, "vehicle_002", telemetry_data)
        time.sleep(2)

        telemetry_data = VehicleTelemetry(
            geo_location=GeoLocation(latitude=44.6470, longitude=10.9255, altitude=50.0),
            battery_level=15,
            is_charging=False,
            speed_kmh=54,
            engine_temp_c=30.0,
        )
        simulate_vehicle_telemetry(mqtt_service, "vehicle_002", telemetry_data)

        print("\n" + "=" * 60)
        print("🏁 Vehicle simulator started - sending vehicle requests")
        print("=" * 60 + "\n")

        print("\n🚗 Vehicle 1 arrives at node_01")
        simulate_cloud_request(
            mqtt_service,
            "hub_01",
            {
                "vehicle_id": "vehicle_002",
                "node_id": "node_01",
                "soc_percent": 10,
            },
        )
        telemetry_data = VehicleTelemetry(
            geo_location=GeoLocation(latitude=44.6475, longitude=10.9260, altitude=50.0),
            battery_level=10,
            is_charging=True,
            speed_kmh=0,
            engine_temp_c=32.0,
        )
        simulate_vehicle_telemetry(mqtt_service, "vehicle_002", telemetry_data)
        time.sleep(7)

        # Vehicle 2 arrives (high priority, medium SoC)
        print("\n🚗 Vehicle 2 arrives at node_02 (HIGH PRIORITY)")
        simulate_cloud_request(
            mqtt_service,
            "hub_01",
            {
                "vehicle_id": "vehicle_002",
                "node_id": "node_02",
                "soc_percent": 40,
            },
        )
        print("⚡ DLM will reallocate power based on priority...")
        time.sleep(7)

        # Vehicle 3 arrives (medium priority, very low SoC - emergency)
        print("\n🚗 Vehicle 3 arrives at node_03 (EMERGENCY - 5% SoC)")
        simulate_cloud_request(
            mqtt_service,
            "hub_01",
            {
                "vehicle_id": "vehicle_003",
                "node_id": "node_03",
                "soc_percent": 5,  # Very low!
            },
        )
        print("⚡ DLM will prioritize the low SoC vehicle...")
        time.sleep(10)

        telemetry_data = VehicleTelemetry(
            geo_location=GeoLocation(latitude=44.6497, longitude=10.9246, altitude=50.0),
            battery_level=80,
            is_charging=False,
            speed_kmh=15,
            engine_temp_c=30.0,
        )
        simulate_vehicle_telemetry(mqtt_service, "vehicle_002", telemetry_data)

        print("\n" + "=" * 60)
        print("📊 DLM continues to rebalance power every 5 seconds")
        print("=" * 60 + "\n")

        time.sleep(10)
    except Exception as e:
        logger.error(f"An error occurred in the vehicle simulator: {e}")
    finally:
        # Stop everything
        print("\n🛑 Stopping vehicle simulator...")

        mqtt_service.disconnect()
        print("✅ Example completed")


if __name__ == "__main__":
    main()
