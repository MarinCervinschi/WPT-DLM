from typing import Dict, List

from .base_policy import IPolicy, PowerAllocation


class EqualSharingPolicy(IPolicy):
    """
    Equal sharing policy: distribute grid capacity equally among active nodes.
    """

    def __call__(self, nodes_state: Dict[str, Dict]) -> List[PowerAllocation]:
        """
        Distribute power equally among charging nodes.

        Args:
            nodes_state: Current state of all nodes

        Returns:
            Power allocations for each node
        """
        allocations = []

        charging_nodes = []
        for node_id, state in nodes_state.items():
            if state.get("is_occupied") and state.get("state") == "CHARGING":
                charging_nodes.append(node_id)

        if not charging_nodes:
            return []

        power_per_node = self.max_grid_capacity_kw / len(charging_nodes)

        for node_id, state in nodes_state.items():
            if node_id in charging_nodes:
                allocated = min(power_per_node, state["max_power_kw"])
                allocations.append(
                    PowerAllocation(
                        node_id=node_id,
                        allocated_power_kw=allocated,
                        reason=f"Equal share ({len(charging_nodes)} active)",
                    )
                )

        return allocations

    def get_policy_name(self) -> str:
        return "EqualSharing"
