import json
from typing import Optional

from shared.mqtt_dtos import GeoLocation, VehicleRequest
from shared.services import MQTTService
from simulation import ChargingRequestEmulator
from smart_objects.resources import SmartObject, VehicleEngineResource


class ElectricVehicle(SmartObject):
    def __init__(
        self,
        vehicle_id: str,
        mqtt_service: MQTTService,
        gpx_file_name: Optional[str] = None,
        simulation: bool = True,
        static_position: Optional[GeoLocation] = None,
    ):
        super().__init__(vehicle_id, mqtt_service)

        engine_resource = VehicleEngineResource(
            f"{vehicle_id}_engine",
            simulation=simulation,
            vehicle_id=vehicle_id,
            gpx_file_name=gpx_file_name,
            mqtt_service=mqtt_service,
            static_position=static_position,
        )
        self.resource_map["engine"] = engine_resource

        self.charging_request_service: Optional[ChargingRequestEmulator] = None
        if simulation:
            self.charging_request_service = ChargingRequestEmulator(
                vehicle_id=vehicle_id,
                mqtt_service=mqtt_service,
                get_battery_level_callback=lambda: engine_resource.battery_level,
                get_location_callback=lambda: engine_resource.current_location,
            )

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

        request_topic = "iot/hubs/+/requests"
        self.mqtt_service.subscribe(request_topic, self._on_charging_request)

    def _on_charging_request(self, msg) -> None:
        """Handle charging request messages."""
        try:
            data = json.loads(msg.payload.decode())
            request = VehicleRequest(**data)

            if request.vehicle_id != self.object_id:
                return

            hub_id = msg.topic.split("/")[2]

            self.logger.info(f"Received charging request for node {request.node_id}")

            engine_resource = self.resource_map["engine"]
            if isinstance(engine_resource, VehicleEngineResource):
                engine_resource.handle_charging_request(hub_id, request.node_id)

        except Exception as e:
            self.logger.error(f"Error processing charging request: {e}")

    def start(self) -> None:
        """Start the vehicle and charging request service if in simulation mode."""
        super().start()

        if self.charging_request_service:
            self.charging_request_service.start()
            self.logger.info("Charging request service started")

    def stop(self) -> None:
        """Stop the vehicle and charging request service."""
        if self.charging_request_service:
            self.charging_request_service.stop()
            self.logger.info("Charging request service stopped")

        super().stop()
