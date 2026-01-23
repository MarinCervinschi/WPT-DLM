from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, List, Literal, Optional

from pydantic import BaseModel

MessageType = Literal["info", "status", "telemetry"]


class ResourceDataListener(ABC):

    @abstractmethod
    def on_data_changed(self, resource: SmartObjectResource, **kwargs: Any) -> None:
        pass


class SmartObjectResource(ABC):
    def __init__(self, resource_id: str):
        self.type: Optional[str] = None
        self.resource_id: str = resource_id
        self.resource_listener_list: List[ResourceDataListener] = []

        self.logger = logging.getLogger(f"{resource_id}")

    def get_info(self) -> Optional[BaseModel]:
        """Get info message DTO. Override if resource publishes info messages."""
        return None

    def get_status(self) -> Optional[BaseModel]:
        """Get status message DTO. Override if resource publishes status messages."""
        return None

    def get_telemetry(self) -> Optional[BaseModel]:
        """Get telemetry message DTO. Override if resource publishes telemetry messages."""
        return None

    @abstractmethod
    def start_periodic_event_update_task(self) -> None:
        """Abstract method to be implemented by subclasses for starting periodic updates."""
        pass

    @abstractmethod
    def stop_periodic_event_update_task(self) -> None:
        """Abstract method to be implemented by subclasses for stopping periodic updates."""
        pass

    def add_data_listener(self, resource_data_listener: ResourceDataListener) -> None:
        """Add a new listener to be notified of changes"""
        if resource_data_listener not in self.resource_listener_list:
            self.resource_listener_list.append(resource_data_listener)
        else:
            self.logger.debug(f"Listener already registered: {resource_data_listener}")

    def remove_data_listener(
        self, resource_data_listener: ResourceDataListener
    ) -> None:
        """Remove an existing listener"""
        if resource_data_listener in self.resource_listener_list:
            self.resource_listener_list.remove(resource_data_listener)
        else:
            self.logger.debug(f"Listener not found: {resource_data_listener}")

    def notify_update(self, message_type: MessageType) -> None:
        """Notify all registered listeners of a value change"""
        if not self.resource_listener_list:
            self.logger.info("No active listeners - nothing to notify")
            return

        for listener in self.resource_listener_list:
            if listener is not None:
                listener.on_data_changed(self, message_type=message_type)

    def to_dict(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "type": self.type,
        }

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
