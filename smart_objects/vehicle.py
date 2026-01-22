from shared.services import MQTTService
from smart_objects.resources import SmartObject, VehicleEngineResource


class ElectricVehicle(SmartObject):
    def __init__(self, vehicle_id: str, mqtt_service: MQTTService, gpx_file_name: str):
        super().__init__(vehicle_id, mqtt_service)

        engine_resource = VehicleEngineResource(f"{vehicle_id}_engine", gpx_file_name)
        self.resource_map["engine"] = engine_resource

    def _register_resource_listeners(self) -> None:
        """Register listeners for resource data changes."""
        engine_resource = self.resource_map["engine"]

        telemetry_topic = f"iot/vehicles/{self.object_id}/telemetry"
        telemetry_listener = self._create_listener(
            message_type="telemetry",
            topic=telemetry_topic,
            qos=0,
            retain=False,
        )
        engine_resource.add_data_listener(telemetry_listener)
