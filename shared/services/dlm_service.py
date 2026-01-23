import json
import logging
import threading
from typing import Callable, Dict, List, Optional

from shared.mqtt_dtos import DLMNotification, VehicleRequest
from shared.policies import IPolicy, PowerAllocation
from shared.services import MQTTService


class DLMService:
    """
    Service for Dynamic Load Management.

    Responsibilities:
    - Manage PolicyManager
    - Subscribe to vehicle requests
    - Apply DLM policy (event-driven + periodic)
    - Publish DLM notifications when allocations change
    - Provide power allocations to nodes
    """

    def __init__(
        self,
        hub_id: str,
        mqtt_service: MQTTService,
        policy: IPolicy,
        dlm_interval: float = 5.0,
    ):
        """
        Initialize DLM service.

        Args:
            hub_id: Hub identifier
            mqtt_service: MQTT service for pub/sub
            policy: IPolicy to use
            dlm_interval: Interval for periodic policy execution (seconds)
        """
        self.hub_id = hub_id
        self.mqtt_service = mqtt_service
        self.dlm_interval = dlm_interval
        self.policy = policy

        self.logger = logging.getLogger(f"DLMService-{hub_id}")

        # Track current allocations to detect changes
        self._current_allocations: Dict[str, float] = {}

        # Callback to get nodes state (provided by Hub)
        self._get_nodes_state_callback: Optional[Callable[[], Dict[str, Dict]]] = None

        # Callback to apply allocations (provided by Hub)
        self._apply_allocation_callback: Optional[Callable[[PowerAllocation], None]] = (
            None
        )

        # Callback to handle vehicle assignment (provided by Hub)
        self._handle_vehicle_assignment_callback: Optional[
            Callable[[VehicleRequest], None]
        ] = None

        # Periodic DLM thread
        self._dlm_thread: Optional[threading.Thread] = None
        self._stop_dlm = threading.Event()

    def set_get_nodes_state_callback(
        self, callback: Callable[[], Dict[str, Dict]]
    ) -> None:
        """
        Set callback to get current nodes state.

        Args:
            callback: Function that returns nodes state dict
        """
        self._get_nodes_state_callback = callback

    def set_apply_allocation_callback(
        self, callback: Callable[[PowerAllocation], None]
    ) -> None:
        """
        Set callback to apply power allocation to a node.

        Args:
            callback: Function that applies allocation to a node
        """
        self._apply_allocation_callback = callback

    def set_handle_vehicle_assignment_callback(
        self, callback: Callable[[VehicleRequest], None]
    ) -> None:
        """
        Set callback to handle vehicle assignment to a node.

        Args:
            callback: Function that assigns vehicle to node and starts charging
        """
        self._handle_vehicle_assignment_callback = callback

    def subscribe_to_requests(self) -> None:
        """Subscribe to vehicle request topic from cloud/brain API."""
        request_topic = f"iot/hubs/{self.hub_id}/requests"

        def on_vehicle_request(msg):
            """Handle incoming vehicle request."""
            try:
                payload = json.loads(msg.payload.decode())

                request = VehicleRequest(**payload)

                self.logger.info(
                    f"📨 Received vehicle request: {request.vehicle_id} → "
                    f"{request.node_id} (SoC: {request.soc_percent}%)"
                )

                if self._handle_vehicle_assignment_callback:
                    self._handle_vehicle_assignment_callback(request)

                self.apply_policy()

            except Exception as e:
                self.logger.error(f"Error handling vehicle request: {e}")

        self.mqtt_service.subscribe(request_topic, callback=on_vehicle_request, qos=1)
        self.logger.info(f"🔔 Subscribed to {request_topic}")

    def apply_policy(self) -> List[PowerAllocation]:
        """
        Apply DLM policy and update node power limits.

        Returns:
            List of power allocations
        """
        if not self._get_nodes_state_callback or not self._apply_allocation_callback:
            self.logger.warning("Callbacks not set, cannot apply policy")
            return []

        nodes_state = self._get_nodes_state_callback()

        allocations = self.policy(nodes_state)

        # Apply allocations and publish notifications for changes
        for alloc in allocations:
            old_limit = self._current_allocations.get(alloc.node_id)
            new_limit = alloc.allocated_power_kw

            # Apply allocation
            self._apply_allocation_callback(alloc)

            # Publish DLM notification if limit changed significantly
            if old_limit is None or abs(old_limit - new_limit) > 0.1:
                self._publish_dlm_notification(
                    node_id=alloc.node_id,
                    old_limit=old_limit or new_limit,
                    new_limit=new_limit,
                    reason=alloc.reason,
                    total_grid_load=sum(
                        nodes_state[n]["current_power_kw"] for n in nodes_state
                    ),
                )

                # Update tracked allocation
                self._current_allocations[alloc.node_id] = new_limit

        return allocations

    def _publish_dlm_notification(
        self,
        node_id: str,
        old_limit: float,
        new_limit: float,
        reason: str,
        total_grid_load: float,
    ) -> None:
        """
        Publish DLM event notification.

        Args:
            node_id: Affected node ID
            old_limit: Previous power limit
            new_limit: New power limit
            reason: Reason for DLM action
            total_grid_load: Total grid load at trigger time
        """
        notification = DLMNotification(
            trigger_reason=reason,
            original_limit=old_limit,
            new_limit=new_limit,
            affected_node_id=node_id,
            total_grid_load=total_grid_load,
        )

        topic = f"iot/hubs/{self.hub_id}/dlm/events"
        payload = notification.model_dump_json()

        self.mqtt_service.publish(topic, payload, qos=1, retain=False)

        self.logger.info(
            f"📢 DLM Event: {node_id} | {old_limit:.1f}kW → {new_limit:.1f}kW | {reason}"
        )

    def _dlm_loop(self) -> None:
        """Background thread for periodic DLM policy execution."""
        while not self._stop_dlm.is_set():
            try:
                self.apply_policy()
            except Exception as e:
                self.logger.error(f"Error in DLM loop: {e}")

            self._stop_dlm.wait(self.dlm_interval)

    def start(self) -> None:
        """Start DLM service (subscribe to requests and start periodic thread)."""
        # Subscribe to vehicle requests
        self.subscribe_to_requests()

        # Start periodic DLM thread
        if self._dlm_thread is None or not self._dlm_thread.is_alive():
            self._stop_dlm.clear()
            self._dlm_thread = threading.Thread(
                target=self._dlm_loop, daemon=True, name=f"DLM-{self.hub_id}"
            )
            self._dlm_thread.start()
            self.logger.info(
                f"🟢 Started DLM service (policy: {self.policy.get_policy_name()}, "
                f"interval: {self.dlm_interval}s)"
            )

    def stop(self) -> None:
        """Stop DLM service."""
        if self._dlm_thread and self._dlm_thread.is_alive():
            self._stop_dlm.set()
            self._dlm_thread.join(timeout=5)
            self.logger.info("🔴 Stopped DLM service")
