import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from shared.services import MQTTService

from .smart_object_resource import (
    MessageType,
    SmartObjectResource,
    ResourceDataListener,
)


class SmartObject(ABC):
    def __init__(self, object_id: str, mqtt_service: MQTTService) -> None:
        self.object_id = object_id
        self.mqtt_service = mqtt_service
        self.resource_map: Dict[str, SmartObjectResource] = {}

        self.logger = logging.getLogger(f"{object_id}")

    def get_resource(self, name: str) -> SmartObjectResource:
        return self.resource_map[name]

    def start(self) -> None:
        """Start the SmartObject behavior"""
        try:
            self.logger.info(f"🏁 Starting SmartObject {self.object_id}")

            for resource in self.resource_map.values():
                resource.start_periodic_event_update_task()

            self._register_resource_listeners()

        except Exception as e:
            raise RuntimeError(f"Failed to start SmartObject {self.object_id}: {e}")

    def stop(self) -> None:
        """Stop the SmartObject behavior"""
        self.logger.info(f"Stopping SmartObject {self.object_id}")

        for resource in self.resource_map.values():
            resource.stop_periodic_event_update_task()

    @abstractmethod
    def _register_resource_listeners(self) -> None:
        """Register listeners for resource data changes."""
        pass

    def _create_listener(
        self,
        message_type: MessageType,
        topic: str,
        qos: int = 0,
        retain: bool = False,
    ) -> ResourceDataListener:
        """
        Create a listener that publishes resource data changes to MQTT.

        The listener will:
        1. Be notified when resource data changes
        2. Call the appropriate resource method (get_info/get_status/get_telemetry)
        3. Publish the Pydantic DTO as JSON to the specified topic

        Args:
            message_type: Type of message ('info', 'status', or 'telemetry')
            topic: MQTT topic to publish to
            qos: Quality of Service (0, 1, or 2)
            retain: Whether to retain the message
        """
        mqtt_service = self.mqtt_service
        logger = self.logger

        class MessageListener(ResourceDataListener):

            def on_data_changed(
                self,
                resource: SmartObjectResource,
                **kwargs: Any,
            ) -> None:
                if kwargs.get("message_type") != message_type:
                    return

                try:
                    if message_type == "info":
                        dto = resource.get_info()
                    elif message_type == "status":
                        dto = resource.get_status()
                    elif message_type == "telemetry":
                        dto = resource.get_telemetry()
                    else:
                        raise ValueError(f"Unknown message type: {message_type}")

                    if dto is None:
                        logger.warning(
                            f"No data to publish for {message_type} of resource {resource.resource_id}"
                        )
                        return

                    payload = dto.model_dump_json()
                    mqtt_service.publish(topic, payload, qos=qos, retain=retain)

                    logger.debug(
                        f"📤 Published {message_type} for {resource.resource_id} to {topic}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to publish {message_type} for resource {resource.resource_id}: {e}"
                    )

        return MessageListener()

    def to_dict(self) -> dict:
        return {
            "id": self.object_id,
            "resources": {k: r.to_dict() for k, r in self.resource_map.items()},
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        return f"SmartObject(id={self.object_id}, resources={list(self.resource_map.keys())})"
