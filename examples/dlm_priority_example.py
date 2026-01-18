"""
Example demonstrating DLM with vehicle requests and policy execution.
"""

import json
import time

from core.mqtt_dtos.enums import GeoLocation
from core.policies import PriorityPolicy
from core.services.mqtt_service import MQTTService
from smart_objects.hub import Hub


def simulate_cloud_request(mqtt_service: MQTTService, hub_id: str, vehicle_data: dict):
    """Simulate a vehicle request from the cloud/brain API."""
    topic = f"iot/hubs/{hub_id}/requests"
    payload = json.dumps(vehicle_data)
    mqtt_service.publish(topic, payload, qos=1)
    print(f"☁️  Cloud sent request: {vehicle_data}")


def main():
    # Initialize MQTT service
    mqtt_service = MQTTService(
        broker_host="localhost", broker_port=1883, client_id="hub_01"
    )
    mqtt_service.connect()

    # Create a Hub with Priority DLM policy
    hub = Hub(
        hub_id="hub_01",
        mqtt_service=mqtt_service,
        location=GeoLocation(lat=44.6469, lon=10.9252, alt=50.0),
        max_power_kw=60.0,  # Limited grid capacity
        firmware_version="1.0.0",
        dlm_policy=PriorityPolicy(max_grid_capacity_kw=60.0),
        dlm_interval=5.0,  # Apply policy every 5 seconds
    )

    # Add nodes
    hub.add_node(node_id="node_01", max_power_kw=22.0, simulation=True)
    hub.add_node(node_id="node_02", max_power_kw=50.0, simulation=True)
    hub.add_node(node_id="node_03", max_power_kw=22.0, simulation=True)

    # Start hub (subscribes to requests and starts DLM)
    hub.start()

    print("\n" + "=" * 60)
    print("🏁 Hub started - listening for vehicle requests")
    print("📊 Grid capacity: 60kW | DLM Policy: Priority")
    print("=" * 60 + "\n")

    time.sleep(2)

    # Vehicle 1 arrives (low priority, low SoC)
    print("\n🚗 Vehicle 1 arrives at node_01")
    simulate_cloud_request(
        mqtt_service,
        "hub_01",
        {
            "vehicle_id": "vehicle_001",
            "node_id": "node_01",
            "soc_percent": 20,
            "priority": 1,  # Low priority
        },
    )
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
            "priority": 5,  # High priority
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
            "priority": 3,  # Medium priority
        },
    )
    print("⚡ DLM will prioritize the low SoC vehicle...")
    time.sleep(10)

    print("\n" + "=" * 60)
    print("📊 DLM continues to rebalance power every 5 seconds")
    print("=" * 60 + "\n")

    time.sleep(10)

    # Stop everything
    print("\n🛑 Stopping hub...")
    hub.stop()

    mqtt_service.disconnect()
    print("✅ Example completed")
    print("\n💡 Check MQTT messages published to:")
    print("   - iot/hubs/hub_01/nodes/+/telemetry (power allocations)")
    print("   - iot/hubs/hub_01/nodes/+/status (state changes)")


if __name__ == "__main__":
    main()
