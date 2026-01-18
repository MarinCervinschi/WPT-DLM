import logging
import random
from typing import Dict, Optional

from .base import NodeInterface

logger = logging.getLogger(__name__)


class SimulatedNode(NodeInterface):
    """
    Simulated node for testing without hardware.

    This node simulates electrical behavior (voltage/current) but does NOT
    simulate vehicle connections. Vehicle status comes from cloud via MQTT.
    """

    def __init__(self, node_id: str, max_power_kw: float):
        super().__init__(node_id, max_power_kw)
        self.simulated_voltage = 230.0
        self.simulated_current = 0.0
        logger.info(f"Initialized simulated node {node_id} (max {max_power_kw}kW)")

    def read_telemetry(self) -> Optional[Dict]:
        """Generate simulated telemetry data based on current state."""
        try:
            # Determine if node is occupied (has a connected vehicle)
            is_occupied = self.connected_vehicle_id is not None

            # Simulate charging current based on authorization and power limit
            if is_occupied and self.authorized and self.power_limit_kw > 0:
                # Simulate realistic current draw (with some noise for realism)
                max_current = (self.power_limit_kw * 1000) / self.simulated_voltage
                self.simulated_current = max_current * random.uniform(0.90, 0.98)
            else:
                # Not charging - no current
                self.simulated_current = 0.0

            # Calculate power from voltage and current
            power_kw = (self.simulated_voltage * self.simulated_current) / 1000.0

            # Build telemetry message
            telemetry = {
                "voltage": self.simulated_voltage,
                "current": round(self.simulated_current, 2),
                "power_kw": round(power_kw, 2),
                "power_limit_kw": self.power_limit_kw,
                "is_occupied": is_occupied,
            }

            # Add vehicle info if present
            if is_occupied:
                telemetry["connected_vehicle_id"] = self.connected_vehicle_id
                if self.vehicle_soc is not None:
                    telemetry["current_vehicle_soc"] = self.vehicle_soc

            return telemetry

        except Exception as e:
            logger.error(
                f"Error generating telemetry for simulated node {self.node_id}: {e}"
            )
            return None

    def write_command(self, power_limit_kw: float, authorized: bool):
        """Accept command for simulated node."""
        self.power_limit_kw = power_limit_kw
        self.authorized = authorized
        logger.debug(
            f"Command received for {self.node_id}: "
            f"power_limit={power_limit_kw:.2f}kW, auth={authorized}"
        )
