"""
Simple Equal Sharing DLM Policy.

Distributes available grid capacity equally among all charging nodes.
"""

from typing import Dict, List

from core.mqtt_dtos.dlm_dto import VehicleRequest

from .dlm_policy import DLMPolicy, PowerAllocation


class EqualSharingPolicy(DLMPolicy):
    """
    Equal sharing policy: distribute grid capacity equally among active nodes.
    """

    def __call__(
        self, nodes_state: Dict[str, Dict], vehicle_requests: List[VehicleRequest]
    ) -> List[PowerAllocation]:
        """
        Distribute power equally among charging nodes.

        Args:
            nodes_state: Current state of all nodes
            vehicle_requests: Vehicle charging requests

        Returns:
            Power allocations for each node
        """
        allocations = []

        # Find nodes that are currently charging or have vehicles
        charging_nodes = []
        for node_id, state in nodes_state.items():
            if state.get("is_occupied") and state.get("state") == "CHARGING":
                charging_nodes.append(node_id)

        if not charging_nodes:
            # No nodes charging, allocate max power to all nodes
            for node_id, state in nodes_state.items():
                allocations.append(
                    PowerAllocation(
                        node_id=node_id,
                        allocated_power_kw=state["max_power_kw"],
                        reason="No active charging",
                    )
                )
            return allocations

        # Distribute grid capacity equally among charging nodes
        power_per_node = self.max_grid_capacity_kw / len(charging_nodes)

        for node_id, state in nodes_state.items():
            if node_id in charging_nodes:
                # Limit to node's max capacity
                allocated = min(power_per_node, state["max_power_kw"])
                allocations.append(
                    PowerAllocation(
                        node_id=node_id,
                        allocated_power_kw=allocated,
                        reason=f"Equal share ({len(charging_nodes)} active)",
                    )
                )
            else:
                # Not charging, give full capacity
                allocations.append(
                    PowerAllocation(
                        node_id=node_id,
                        allocated_power_kw=state["max_power_kw"],
                        reason="Idle",
                    )
                )

        return allocations

    def get_policy_name(self) -> str:
        return "EqualSharing"
