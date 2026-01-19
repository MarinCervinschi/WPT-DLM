from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PowerAllocation:
    """Power allocation decision for a node."""

    node_id: str
    allocated_power_kw: float
    reason: str


class IPolicy(ABC):
    """
    Abstract base class for Dynamic Load Management policies.

    Policies are callable and take the current system state to compute
    power allocations for all nodes.
    """

    def __init__(self, max_grid_capacity_kw: float):
        """
        Initialize policy with grid capacity.

        Args:
            max_grid_capacity_kw: Maximum total grid capacity
        """
        self.max_grid_capacity_kw = max_grid_capacity_kw

    @abstractmethod
    def __call__(self, nodes_state: Dict[str, Dict]) -> List[PowerAllocation]:
        """
        Compute power allocation for all nodes.

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
        pass

    @abstractmethod
    def get_policy_name(self) -> str:
        """Get the policy name for logging."""
        pass
