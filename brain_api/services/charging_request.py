import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from shared.mqtt_dtos.vehicle_dto import VehicleRequest

from ..repositories import NodeRepository, VehicleRepository
from .influxdb_service import InfluxDBService

if TYPE_CHECKING:
    from shared.services.mqtt_service import MQTTService


class ChargingRequestService:
    """Service for handling charging session initialization via QR code."""

    def __init__(
        self, db: Session, mqtt_service: "MQTTService", influx_service: InfluxDBService
    ) -> None:
        """
        Initialize ChargingRequestService.

        Args:
            db: Database session
            mqtt_service: MQTT service for publishing messages
            influx_service: InfluxDB service for retrieving vehicle telemetry
        """
        self.db = db
        self.mqtt_service = mqtt_service
        self.influx_service = influx_service
        self.node_repo = NodeRepository(db)
        self.vehicle_repo = VehicleRepository(db)

        self.logger = logging.getLogger(self.__class__.__name__)

    def request_charging(self, node_id: str, vehicle_id: str) -> dict:
        """
        Request a charging session by publishing to MQTT.

        Args:
            node_id: The station/node ID from the QR code
            vehicle_id: The vehicle ID from the mobile app

        Returns:
            Dict with confirmation message

        Raises:
            ValueError: If node or vehicle doesn't exist
        """
        node = self.node_repo.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        hub_id = node.hub_id

        soc_percent = 50  # Default value if telemetry not available
        if vehicle_id:
            vehicle = self.vehicle_repo.get(vehicle_id)
            self.logger.info(f"Retrieved vehicle: {vehicle}")
            if not vehicle:
                raise ValueError(f"Vehicle {vehicle_id} not found")

            try:
                telemetry = self.influx_service.get_latest_vehicle_telemetry(vehicle_id)
                if telemetry and "battery_level" in telemetry:
                    soc_percent = int(telemetry["battery_level"])
                    self.logger.info(f"Retrieved SOC from telemetry: {soc_percent}%")
                else:
                    self.logger.warning(
                        f"No battery_level in telemetry for {vehicle_id}, using default {soc_percent}%"
                    )
            except Exception as e:
                self.logger.error(
                    f"Error retrieving telemetry for {vehicle_id}: {e}. Using default {soc_percent}%"
                )
        topic = f"iot/hubs/{hub_id}/requests"
        payload = VehicleRequest(
            node_id=node_id, vehicle_id=vehicle_id, soc_percent=soc_percent
        )

        payload_json = payload.model_dump_json()

        self.logger.info(f"Publishing charging request to topic: {topic}")
        self.logger.debug(f"Payload: {payload_json}")

        try:
            self.mqtt_service.publish(topic, payload_json, qos=1)
            self.logger.info(
                f"Successfully published charging request for node {node_id}, vehicle {vehicle_id}"
            )
            return {
                "message": "Charging request sent successfully",
                "node_id": node_id,
                "vehicle_id": vehicle_id,
                "hub_id": hub_id,
            }
        except Exception as e:
            self.logger.error(f"Failed to publish charging request: {e}")
            raise
