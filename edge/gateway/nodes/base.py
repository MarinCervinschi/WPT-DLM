from abc import ABC, abstractmethod
from typing import Dict, Optional


class NodeInterface(ABC):
    """Abstract base class for charging station nodes."""

    def __init__(self, node_id: str, max_power_kw: float):
        self.node_id = node_id
        self.max_power_kw = max_power_kw
        self.power_limit_kw = 0.0
        self.authorized = False
        self.connected_vehicle_id: Optional[str] = None
        self.vehicle_soc: Optional[int] = None

    @abstractmethod
    def read_telemetry(self) -> Optional[Dict]:
        """
        Read telemetry from the node.

        Returns:
            Dict with keys: voltage, current, power_kw, power_limit_kw,
                           is_occupied, connected_vehicle_id (optional),
                           current_vehicle_soc (optional)
        """
        pass

    @abstractmethod
    def write_command(self, power_limit_kw: float, authorized: bool):
        """
        Send command to the node.

        Args:
            power_limit_kw: Power limit in kW
            authorized: Authorization flag
        """
        pass

    def update_vehicle_info(self, vehicle_id: Optional[str], soc: Optional[int]):
        """Update connected vehicle information."""
        self.connected_vehicle_id = vehicle_id
        self.vehicle_soc = soc
        self.is_occupied = True if vehicle_id else False
