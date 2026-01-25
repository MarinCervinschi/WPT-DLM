import logging
from typing import Dict, List

from .base_policy import IPolicy, PowerAllocation

logger = logging.getLogger(__name__)


class PriorityPolicy(IPolicy):
    """
    Priority-based policy: Lower SoC vehicles get more power.
    Helps vehicles with lower battery charge first.
    """

    def __call__(self, nodes_state: Dict[str, Dict]) -> List[PowerAllocation]:
        """
        Distribute power prioritizing vehicles with lower SoC.

        Args:
            nodes_state: Current state of all nodes
                {
                    "node_01": {
                        "max_power_kw": 22.0,
                        "current_power_kw": 15.0,
                        "state": "CHARGING",
                        "vehicle_id": "vehicle_123",
                        "vehicle_soc": 50,
                        "is_occupied": True
                    }
                }

        Returns:
            List of power allocations for each node
        """
        allocations = []

        charging_nodes = []
        for node_id, state in nodes_state.items():
            if (
                state.get("is_occupied")
                and state.get("state") == "charging"
                and state.get("vehicle_id")
            ):
                charging_nodes.append((node_id, state))

        if not charging_nodes:
            return []

        priorities = []
        for node_id, state in charging_nodes:
            soc = state.get("vehicle_soc")
            if soc is None:
                soc = 50  # Default to 50% if SoC unknown

            priority = max(1, 100 - soc)
            priorities.append((node_id, state, priority, soc))

        total_priority = sum(p[2] for p in priorities)

        for node_id, state, priority, soc in priorities:
            proportional_power = (priority / total_priority) * self.max_grid_capacity_kw
            allocated = min(proportional_power, state["max_power_kw"])

            allocations.append(
                PowerAllocation(
                    node_id=node_id,
                    allocated_power_kw=allocated,
                    reason=f"Priority-based (SoC: {soc}%, {len(charging_nodes)} active)",
                )
            )

        logger.debug(
            f"Priority policy: distributed {self.max_grid_capacity_kw:.1f}kW "
            f"across {len(charging_nodes)} nodes based on SoC priorities"
        )

        return allocations

    def get_policy_name(self) -> str:
        return "Priority"
