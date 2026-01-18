"""
Policy Manager for Dynamic Load Management.
"""

import logging
from typing import Dict, List, Optional

from core.mqtt_dtos.dlm_dto import VehicleRequest

from .dlm_policy import DLMPolicy, PowerAllocation


class PolicyManager:
    """
    Manages DLM policy execution and power limit application.
    """

    def __init__(self, policy: DLMPolicy):
        """
        Initialize policy manager.

        Args:
            policy: The DLM policy to use
        """
        self.policy = policy
        self.vehicle_requests: List[VehicleRequest] = []
        self.logger = logging.getLogger("PolicyManager")

    def add_vehicle_request(self, request: VehicleRequest) -> None:
        """
        Add a new vehicle charging request.

        Args:
            request: Vehicle charging request
        """
        # Remove any existing request for the same vehicle
        self.vehicle_requests = [
            r for r in self.vehicle_requests if r.vehicle_id != request.vehicle_id
        ]

        self.vehicle_requests.append(request)
        self.logger.info(
            f"➕ Added vehicle request: {request.vehicle_id} → {request.node_id} "
            f"(SoC: {request.soc_percent}%)"
        )

    def remove_vehicle_request(self, vehicle_id: str) -> None:
        """
        Remove a vehicle request (when charging completes or vehicle leaves).

        Args:
            vehicle_id: ID of the vehicle to remove
        """
        self.vehicle_requests = [
            r for r in self.vehicle_requests if r.vehicle_id != vehicle_id
        ]
        self.logger.info(f"➖ Removed vehicle request: {vehicle_id}")

    def apply_policy(self, nodes_state: Dict[str, Dict]) -> List[PowerAllocation]:
        """
        Apply the DLM policy and return power allocations.

        Args:
            nodes_state: Current state of all nodes

        Returns:
            List of power allocations
        """
        self.logger.debug(
            f"🔄 Applying policy '{self.policy.get_policy_name()}' "
            f"with {len(self.vehicle_requests)} requests"
        )

        allocations = self.policy(nodes_state, self.vehicle_requests)

        # Log allocations
        for alloc in allocations:
            self.logger.debug(
                f"⚡ {alloc.node_id}: {alloc.allocated_power_kw:.2f}kW "
                f"({alloc.reason})"
            )

        return allocations

    def get_active_requests(self) -> List[VehicleRequest]:
        """Get all active vehicle requests."""
        return self.vehicle_requests.copy()
