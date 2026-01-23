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

        # Initial telemetry
        telemetry_data = VehicleTelemetry(
            geo_location=GeoLocation(latitude=44.6469, longitude=10.9252, altitude=50.0),
            battery_level=50,
            is_charging=False,
            speed_kmh=0,
            engine_temp_c=25.0,
        )
        simulate_vehicle_telemetry(mqtt_service, "vehicle_001", telemetry_data)
        time.sleep(1)

        # Simulate multiple vehicles over time
        vehicles = [
            {"id": "vehicle_001", "node": "node_01", "soc": 20},
            {"id": "vehicle_002", "node": "node_02", "soc": 40},
            {"id": "vehicle_003", "node": "node_03", "soc": 10},
            {"id": "vehicle_004", "node": "node_01", "soc": 5},
        ]

        for vehicle in vehicles:
            print(f"\n🚗 {vehicle['id']} arrives at {vehicle['node']} (SoC: {vehicle['soc']}%)")
            simulate_cloud_request(
                mqtt_service,
                "hub_01",
                {
                    "vehicle_id": vehicle["id"],
                    "node_id": vehicle["node"],
                    "soc_percent": vehicle["soc"],
                },
            )
            # Send telemetry while charging
            telemetry_data = VehicleTelemetry(
                geo_location=GeoLocation(latitude=44.6470 + 0.001 * int(vehicle["id"].split("_")[1]), longitude=10.9255, altitude=50.0),
                battery_level=vehicle["soc"],
                is_charging=True,
                speed_kmh=0,
                engine_temp_c=30.0,
            )
            simulate_vehicle_telemetry(mqtt_service, vehicle["id"], telemetry_data)
            time.sleep(2)

        print("\n⚡ DLM balancing power across vehicles...")
        time.sleep(10)

        # Simulate some vehicles leaving or updating
        print("\n🚗 Vehicle 001 finished charging and leaves")
        # Simulate leaving by sending telemetry with is_charging=False
        telemetry_data = VehicleTelemetry(
            geo_location=GeoLocation(latitude=44.6470, longitude=10.9255, altitude=50.0),
            battery_level=80,
            is_charging=False,
            speed_kmh=20,
            engine_temp_c=28.0,
        )
        simulate_vehicle_telemetry(mqtt_service, "vehicle_001", telemetry_data)
        time.sleep(2)

        # Add more vehicles
        new_vehicles = [
            {"id": "vehicle_005", "node": "node_02", "soc": 30},
            {"id": "vehicle_006", "node": "node_03", "soc": 15},
        ]
        for vehicle in new_vehicles:
            print(f"\n🚗 {vehicle['id']} arrives at {vehicle['node']} (SoC: {vehicle['soc']}%)")
            simulate_cloud_request(
                mqtt_service,
                "hub_01",
                {
                    "vehicle_id": vehicle["id"],
                    "node_id": vehicle["node"],
                    "soc_percent": vehicle["soc"],
                },
            )
            telemetry_data = VehicleTelemetry(
                geo_location=GeoLocation(latitude=44.6470, longitude=10.9255, altitude=50.0),
                battery_level=vehicle["soc"],
                is_charging=True,
                speed_kmh=0,
                engine_temp_c=32.0,
            )
            simulate_vehicle_telemetry(mqtt_service, vehicle["id"], telemetry_data)
            time.sleep(1)

        print("\n⚡ DLM rebalancing with new arrivals...")
        time.sleep(15)

        # Simulate periodic telemetry updates
        for i in range(5):
            for vehicle in vehicles + new_vehicles:
                if vehicle["id"] != "vehicle_001":  # Skip the one that left
                    soc = min(100, vehicle["soc"] + (i+1) * 10)  # Simulate charging
                    telemetry_data = VehicleTelemetry(
                        geo_location=GeoLocation(latitude=44.6470, longitude=10.9255, altitude=50.0),
                        battery_level=soc,
                        is_charging=True,
                        speed_kmh=0,
                        engine_temp_c=30.0 + i,
                    )
                    simulate_vehicle_telemetry(mqtt_service, vehicle["id"], telemetry_data)
            time.sleep(5)

        print("\n📊 Simulation complete - data should be in DB")
        time.sleep(5)
    except Exception as e:
        logger.error(f"An error occurred in the vehicle simulator: {e}")
    finally:
        # Stop everything
        print("\n🛑 Stopping vehicle simulator...")

        mqtt_service.disconnect()
        print("✅ Example completed")


if __name__ == "__main__":
    main()
