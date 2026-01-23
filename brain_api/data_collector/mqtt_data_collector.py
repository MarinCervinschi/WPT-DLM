"""
MQTT Data Collector for WPT-DLM Brain API.

Subscribes to MQTT topics and persists data to the database.
"""

import json
import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from shared.mqtt_dtos import ChargingState, DLMNotification, NodeStatus
from ..schemas import ChargingSessionEnd, ChargingSessionStart, DLMEventLog
from ..services import ChargingSessionService, DLMService
from ..services.influxdb_service import InfluxDBService

if TYPE_CHECKING:
    from shared.services.mqtt_service import MQTTService

logger = logging.getLogger(__name__)


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
        
        # Initialize services
        self.session_service = ChargingSessionService(db)
        self.dlm_service = DLMService(db)
        self.influx_service = InfluxDBService()

    def subscribe(self) -> None:
        """Start subscribing to MQTT topics."""
        logger.info("Starting MQTT Data Collector...")
        
        # Subscribe to all topics
        self.mqtt_service.subscribe("iot/hubs/+/nodes/+/status", self._on_node_status, qos=1)
        self.mqtt_service.subscribe("iot/hubs/+/dlm/events", self._on_dlm_event, qos=1)
        
        logger.info("MQTT Data Collector started successfully")

    def _on_node_status(self, msg) -> None:
        """
        Handle node status messages and manage charging sessions.
        
        Topic: iot/hubs/+/nodes/+/status
        
        Session management:
        - CHARGING: start new session if not already active
        - IDLE/FULL/FAULTED: end active session if exists
        """
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) != 6:
                logger.warning(f"Invalid node status topic: {msg.topic}")
                return
            
            node_id = topic_parts[4]
            payload = json.loads(msg.payload.decode())
            
            node_status = NodeStatus(**payload)
            
            self._manage_charging_session(node_id, node_status.state)
            logger.debug(f"Updated node {node_id} status: {node_status.state}")
            
        except Exception as e:
            logger.error(f"Error processing node status message: {e}", exc_info=True)

    def _manage_charging_session(self, node_id: str, state: ChargingState) -> None:
        """
        Manage charging session based on node state.
        
        Args:
            node_id: Node identifier
            state: Current charging state
        """
        active_sessions = self.session_service.get_active(node_id=node_id)
        has_active_session = len(active_sessions) > 0
        
        if state == ChargingState.CHARGING:
            # Start new session if not already active
            if not has_active_session:
                start_data = ChargingSessionStart(node_id=node_id, vehicle_id=None)
                session = self.session_service.start(start_data)
                logger.info(f"Started charging session {session.charging_session_id} for node {node_id}")
        else:
            # End active session for IDLE, FULL, or FAULTED states
            if has_active_session:
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
                    logger.info(
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
            # Extract hub_id from topic
            topic_parts = msg.topic.split('/')
            if len(topic_parts) != 5:
                logger.warning(f"Invalid DLM event topic: {msg.topic}")
                return
            
            hub_id = topic_parts[2]
            payload = json.loads(msg.payload.decode())
            
            # Validate payload
            dlm_event = DLMNotification(**payload)
            
            # Log DLM event using service
            log_data = DLMEventLog(
                hub_id=hub_id,
                node_id=dlm_event.affected_node_id,
                trigger_reason=dlm_event.trigger_reason,
                original_limit_kw=dlm_event.original_limit,
                new_limit_kw=dlm_event.new_limit,
                total_grid_load_kw=dlm_event.total_grid_load,
                available_capacity_at_trigger=None,
            )
            
            self.dlm_service.log(log_data)
            logger.info(
                f"Recorded DLM event for node {dlm_event.affected_node_id}: "
                f"{dlm_event.trigger_reason} ({dlm_event.original_limit} -> {dlm_event.new_limit} kW)"
            )
            
        except Exception as e:
            logger.error(f"Error processing DLM event message: {e}", exc_info=True)


    def unsubscribe(self) -> None:
        """Stop data collector and unsubscribe from topics."""
        logger.info("Stopping MQTT Data Collector...")
        
        self.mqtt_service.unsubscribe("iot/hubs/+/nodes/+/status")
        self.mqtt_service.unsubscribe("iot/hubs/+/dlm/events")
        
        # Close InfluxDB connection
        self.influx_service.close()
        
        logger.info("MQTT Data Collector stopped")
