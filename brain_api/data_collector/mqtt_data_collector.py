import json
import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Session

from brain_api.schemas.dtos.node import NodeUpdate
from shared.mqtt_dtos import (
    ChargingState,
    ConnectionState,
    DLMNotification,
    HubInfo,
    HubStatus,
    NodeInfo,
    NodeStatus,
)

from ..schemas import (
    ChargingSessionEnd,
    ChargingSessionStart,
    DLMEventLog,
    HubCreate,
    HubUpdate,
    NodeCreate,
)
from ..services import ChargingSessionService, DLMService, HubService, NodeService
from ..services.influxdb_service import InfluxDBService

if TYPE_CHECKING:
    from shared.services.mqtt_service import MQTTService


class MQTTDataCollector:
    """
    Collects data from MQTT topics and persists to database.

    Subscribes to:
    - iot/hubs/+/nodes/+/status
    - iot/hubs/+/dlm/events
    """

    def __init__(self, mqtt_service: "MQTTService", db: Session) -> None:
        """
        Initialize MQTT Data Collector.

        Args:
            mqtt_service: MQTT service instance
            db: Database session
        """
        self.mqtt_service = mqtt_service
        self.db = db

        self.session_service = ChargingSessionService(db)
        self.dlm_service = DLMService(db)
        self.hub_service = HubService(db)
        self.node_service = NodeService(db)
        self.influx_service = InfluxDBService()

        self.logger = logging.getLogger("MQTTDataCollector")

    def subscribe(self) -> None:
        """Start subscribing to MQTT topics."""
        self.logger.info("Starting MQTT Data Collector...")
        self.mqtt_service.subscribe("iot/hubs/+/info", self._on_hub_info, qos=1)
        self.mqtt_service.subscribe("iot/hubs/+/status", self._on_hub_status, qos=1)
        self.mqtt_service.subscribe(
            "iot/hubs/+/nodes/+/info", self._on_node_info, qos=1
        )
        self.mqtt_service.subscribe(
            "iot/hubs/+/nodes/+/status", self._on_node_status, qos=1
        )
        self.mqtt_service.subscribe("iot/hubs/+/dlm/events", self._on_dlm_event, qos=1)

        self.logger.info("MQTT Data Collector started successfully")

    def _on_hub_info(self, msg) -> None:
        """
        Handle hub info messages and create/update hub in database.

        Topic: iot/hubs/+/info
        """
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) != 4:
                self.logger.warning(f"Invalid hub info topic: {msg.topic}")
                return

            hub_id = topic_parts[2]
            payload = json.loads(msg.payload.decode())

            hub_info = HubInfo(**payload)

            existing_hub = self.hub_service.repo.get(hub_id)

            if existing_hub:
                update_data = HubUpdate(
                    lat=hub_info.location.latitude,
                    lon=hub_info.location.longitude,
                    alt=hub_info.location.altitude,
                    max_grid_capacity_kw=hub_info.max_grid_capacity_kw,
                    ip_address=hub_info.ip_address,
                    firmware_version=hub_info.firmware_version,
                )
                self.hub_service.update(hub_id, update_data)
                self.logger.info(f"Updated hub {hub_id} info")
            else:
                create_data = HubCreate(
                    hub_id=hub_id,
                    lat=hub_info.location.latitude,
                    lon=hub_info.location.longitude,
                    alt=hub_info.location.altitude,
                    max_grid_capacity_kw=hub_info.max_grid_capacity_kw,
                    ip_address=hub_info.ip_address,
                    firmware_version=hub_info.firmware_version,
                    is_active=True,
                )
                self.hub_service.create(create_data)
                self.logger.info(f"Created new hub {hub_id}")

        except Exception as e:
            self.logger.error(f"Error processing hub info message: {e}", exc_info=True)

    def _on_hub_status(self, msg) -> None:
        """
        Handle hub status messages and update hub status in database.

        Topic: iot/hubs/+/status
        """
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) != 4:
                self.logger.warning(f"Invalid hub status topic: {msg.topic}")
                return

            hub_id = topic_parts[2]
            payload = json.loads(msg.payload.decode())

            hub_status = HubStatus(**payload)

            self.hub_service.repo.update_last_seen(hub_id)

            if hub_status.state == ConnectionState.ONLINE:
                self.hub_service.activate(hub_id)
            elif hub_status.state == ConnectionState.OFFLINE:
                self.hub_service.deactivate(hub_id)

            self.logger.debug(f"Updated hub {hub_id} status: {hub_status.state.value}")

        except Exception as e:
            self.logger.error(
                f"Error processing hub status message: {e}", exc_info=True
            )

    def _on_node_info(self, msg) -> None:
        """
        Handle node info messages and create/update node in database.

        Topic: iot/hubs/+/nodes/+/info
        """
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) != 6:
                self.logger.warning(f"Invalid node info topic: {msg.topic}")
                return

            hub_id = topic_parts[2]
            node_id = topic_parts[4]
            payload = json.loads(msg.payload.decode())

            node_info = NodeInfo(**payload)

            existing_node = self.node_service.repo.get(node_id)

            if existing_node:

                update_data = NodeUpdate(
                    max_power_kw=node_info.max_power_kw,
                )
                self.node_service.update(node_id, update_data)
                self.logger.info(f"Updated node {node_id} info for hub {hub_id}")
            else:
                create_data = NodeCreate(
                    node_id=node_id,
                    hub_id=hub_id,
                    max_power_kw=node_info.max_power_kw,
                    is_maintenance=False,
                )
                self.node_service.create(create_data)
                self.logger.info(f"Created new node {node_id} for hub {hub_id}")

        except Exception as e:
            self.logger.error(f"Error processing node info message: {e}", exc_info=True)

    def _on_node_status(self, msg) -> None:
        """
        Handle node status messages and manage charging sessions.

        Topic: iot/hubs/+/nodes/+/status

        Session management:
        - CHARGING: start new session if not already active
        - IDLE/FULL/FAULTED: end active session if exists
        """
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) != 6:
                self.logger.warning(f"Invalid node status topic: {msg.topic}")
                return

            node_id = topic_parts[4]
            payload = json.loads(msg.payload.decode())

            node_status = NodeStatus(**payload)

            self._manage_charging_session(
                node_id, node_status.current_vehicle_id, node_status.state
            )
            self.logger.debug(f"Updated node {node_id} status: {node_status.state}")

        except Exception as e:
            self.logger.error(
                f"Error processing node status message: {e}", exc_info=True
            )

    def _manage_charging_session(
        self, node_id: str, vehicle_id: Optional[str], state: ChargingState
    ) -> None:
        """
        Manage charging session based on node state.

        Args:
            node_id: Node identifier
            vehicle_id: Optional vehicle identifier
            state: Current charging state
        """
        active_sessions = self.session_service.get_active(node_id=node_id)
        has_active_session = len(active_sessions) > 0

        if state == ChargingState.CHARGING:
            if not has_active_session:
                start_data = ChargingSessionStart(
                    node_id=node_id, vehicle_id=vehicle_id
                )
                session = self.session_service.start(start_data)
                self.logger.info(
                    f"Started charging session {session.charging_session_id} for node {node_id} and vehicle {vehicle_id}"
                )
        else:
            for session in active_sessions:
                metrics = self.influx_service.get_session_metrics(
                    node_id=node_id,
                    start_time=session.start_time,
                    end_time=None,
                )

                end_data = ChargingSessionEnd(
                    total_energy_kwh=metrics["total_energy_kwh"],
                    avg_power_kw=metrics["avg_power_kw"],
                )
                self.session_service.end(session.charging_session_id, end_data)
                self.logger.info(
                    f"Ended charging session {session.charging_session_id} for node {node_id} "
                    f"(state changed to {state.value}): "
                    f"{metrics['total_energy_kwh']:.2f} kWh, {metrics['avg_power_kw']:.2f} kW avg"
                )

    def _on_dlm_event(self, msg) -> None:
        """
        Handle DLM event messages.

        Topic: iot/hubs/+/dlm/events
        """
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) != 5:
                self.logger.warning(f"Invalid DLM event topic: {msg.topic}")
                return

            hub_id = topic_parts[2]
            payload = json.loads(msg.payload.decode())

            dlm_event = DLMNotification(**payload)

            log_data = DLMEventLog(
                hub_id=hub_id,
                node_id=dlm_event.affected_node_id,
                trigger_reason=dlm_event.trigger_reason,
                original_limit_kw=dlm_event.original_limit,
                new_limit_kw=dlm_event.new_limit,
                total_grid_load_kw=dlm_event.total_grid_load,
                available_capacity_at_trigger=dlm_event.available_capacity,
            )

            self.dlm_service.log(log_data)
            self.logger.info(
                f"Recorded DLM event for node {dlm_event.affected_node_id}: "
                f"{dlm_event.trigger_reason} ({dlm_event.original_limit} -> {dlm_event.new_limit} kW)"
            )

        except Exception as e:
            self.logger.error(f"Error processing DLM event message: {e}", exc_info=True)

    def unsubscribe(self) -> None:
        """Stop data collector and unsubscribe from topics."""
        self.logger.info("Stopping MQTT Data Collector...")

        self.mqtt_service.unsubscribe("iot/hubs/+/info")
        self.mqtt_service.unsubscribe("iot/hubs/+/status")
        self.mqtt_service.unsubscribe("iot/hubs/+/nodes/+/info")
        self.mqtt_service.unsubscribe("iot/hubs/+/nodes/+/status")
        self.mqtt_service.unsubscribe("iot/hubs/+/dlm/events")

        self.influx_service.close()

        self.logger.info("MQTT Data Collector stopped")
