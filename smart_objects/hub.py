import random
from typing import Dict, Optional

from shared.mqtt_dtos import (
    ChargingState,
    ConnectionState,
    GeoLocation,
    HubInfo,
    HubStatus,
)
from shared.policies import IPolicy, EqualSharingPolicy, PowerAllocation
from shared.services import DLMService, MQTTService
from smart_objects.resources import Node, SmartObject


class Hub(SmartObject):
    """
    A charging hub device containing multiple charging nodes (resources).

    Architecture:
    - Hub = SmartObject (this class)
    - Nodes = SmartObjectResource (charging points)
    - Each node publishes: info, status, telemetry
    - Hub publishes: info, status
    - DLMService handles all DLM logic
    """

    def __init__(
        self,
        hub_id: str,
        mqtt_service: MQTTService,
        location: GeoLocation,
        max_grid_capacity_kw: float = 100.0,
        ip_address: str = "0.0.0.0",
        firmware_version: str = "1.0.0",
        dlm_policy: Optional[IPolicy] = None,
        dlm_interval: float = 5.0,
    ):
        super().__init__(object_id=hub_id, mqtt_service=mqtt_service)

        self.hub_id = hub_id
        self.location = location
        self.max_grid_capacity_kw = max_grid_capacity_kw
        self.firmware_version = firmware_version

        self.current_state: ConnectionState = ConnectionState.OFFLINE
        self.ip_address: str = ip_address
        self.cpu_temp: float = 0.0

        policy = dlm_policy or EqualSharingPolicy(
            max_grid_capacity_kw=max_grid_capacity_kw
        )
        self.dlm_service = DLMService(
            hub_id=hub_id,
            mqtt_service=mqtt_service,
            policy=policy,
            dlm_interval=dlm_interval,
        )

        self.dlm_service.set_get_nodes_state_callback(self._get_nodes_state)
        self.dlm_service.set_apply_allocation_callback(self._apply_allocation)
        self.dlm_service.set_handle_vehicle_assignment_callback(
            self._handle_vehicle_assignment
        )

    def add_node(
        self, node_id: str, max_power_kw: float = 22.0, simulation: bool = True
    ) -> Node:
        """
        Add a charging node to this hub.

        Args:
            node_id: Unique node identifier
            max_power_kw: Maximum power for this node
            simulation: Whether to use simulated sensors/actuators

        Returns:
            The created Node resource
        """
        node = Node(
            node_id=node_id,
            hub_id=self.hub_id,
            max_power_kw=max_power_kw,
            simulation=simulation,
        )

        self.resource_map[node_id] = node
        self.logger.info(f"➕ Added node {node_id} to hub {self.hub_id}")

        return node

    def get_node(self, node_id: str) -> Node:
        """Get a specific node resource."""
        return self.resource_map.get(node_id)  # type: ignore

    def publish_hub_info(self) -> None:
        """Publish hub info message (retained)."""

        info = HubInfo(
            hub_id=self.hub_id,
            location=self.location,
            max_grid_capacity_kw=self.max_grid_capacity_kw,
            ip_address=self.ip_address,
            firmware_version=self.firmware_version,
        )

        topic = f"iot/hubs/{self.hub_id}/info"
        payload = info.model_dump_json()

        self.mqtt_service.publish(topic, payload, qos=1, retain=True)
        self.logger.info(f"📤 Published HubInfo to {topic}")

    def publish_hub_status(self) -> None:
        """Publish hub status message."""

        self.cpu_temp = random.uniform(40.0, 85.0)

        status = HubStatus(
            state=self.current_state,
            cpu_temp=self.cpu_temp,
        )

        topic = f"iot/hubs/{self.hub_id}/status"
        payload = status.model_dump_json()

        self.mqtt_service.publish(topic, payload, qos=1, retain=False)
        self.logger.info(f"📤 Published HubStatus: {self.current_state.value}")

    def set_hub_state(self, new_state: ConnectionState) -> None:
        """Update hub connection state and publish."""
        if self.current_state != new_state:
            old_state = self.current_state
            self.current_state = new_state
            self.logger.info(f"🔄 Hub state: {old_state.value} → {new_state.value}")
            self.publish_hub_status()

    def _register_resource_listeners(self) -> None:
        """
        Register listeners for all node resources.
        Each node gets listeners for: info (on startup), status, telemetry.
        """
        for node_id, node_resource in self.resource_map.items():
            if not isinstance(node_resource, Node):
                continue

            info_listener = self._create_listener(
                message_type="info",
                topic=f"iot/hubs/{self.hub_id}/nodes/{node_id}/info",
                qos=1,
                retain=True,  # Info messages are retained
            )
            node_resource.add_data_listener(info_listener)

            status_listener = self._create_listener(
                message_type="status",
                topic=f"iot/hubs/{self.hub_id}/nodes/{node_id}/status",
                qos=1,
                retain=False,
            )
            node_resource.add_data_listener(status_listener)

            telemetry_listener = self._create_listener(
                message_type="telemetry",
                topic=f"iot/hubs/{self.hub_id}/nodes/{node_id}/telemetry",
                qos=0,
                retain=False,
            )
            node_resource.add_data_listener(telemetry_listener)

            self.logger.info(f"✅ Registered listeners for node {node_id}")

    def _get_nodes_state(self) -> Dict[str, Dict]:
        """Get current state of all nodes for DLM policy."""
        nodes_state = {}

        for node_id, resource in self.resource_map.items():
            if isinstance(resource, Node):
                nodes_state[node_id] = {
                    "max_power_kw": resource.max_power_kw,
                    "current_power_kw": resource.power_sensor.get_value("power")
                    / 1000.0,
                    "state": resource.current_state.value,
                    "vehicle_id": resource.connected_vehicle_id,
                    "vehicle_soc": resource.current_vehicle_soc,
                    "is_occupied": resource.is_occupied,
                }

        return nodes_state

    def _apply_allocation(self, allocation: PowerAllocation) -> None:
        """Apply power allocation to a node."""
        node = self.get_node(allocation.node_id)
        if node:
            node.set_power_limit(allocation.allocated_power_kw)

    def _handle_vehicle_assignment(self, request) -> None:
        """
        Handle vehicle assignment to node.
        Updates node with vehicle info and starts charging.
        """
        node = self.get_node(request.node_id)
        if node:
            node.connected_vehicle_id = request.vehicle_id
            node.current_vehicle_soc = request.soc_percent

            node.measure_sensors()
            if node.is_occupied is False:
                raise ValueError(
                    f"Node {request.node_id} has no vehicle connected for assignment"
                )

            node.set_state(ChargingState.CHARGING)

            self.logger.info(
                f"🔌 Vehicle {request.vehicle_id} assigned to node {request.node_id} "
                f"(SoC: {request.soc_percent}%)"
            )

    def start(self) -> None:
        """Start the hub and all its nodes."""
        self.set_hub_state(ConnectionState.ONLINE)

        self.publish_hub_info()

        self.publish_hub_status()

        super().start()

        for _, node_resource in self.resource_map.items():
            if isinstance(node_resource, Node):
                node_resource.notify_update(message_type="info")
                node_resource.notify_update(message_type="status")

        self.dlm_service.start()

        self.logger.info(
            f"🚀 HubDevice {self.hub_id} started with {len(self.resource_map)} nodes"
        )

    def stop(self) -> None:
        """Stop the hub and all its nodes."""
        self.dlm_service.stop()
        self.set_hub_state(ConnectionState.OFFLINE)
        super().stop()
        self.logger.info(f"🛑 HubDevice {self.hub_id} stopped")

    def __str__(self) -> str:
        return f"HubDevice(id={self.hub_id}, nodes={len(self.resource_map)}, state={self.current_state.value})"
