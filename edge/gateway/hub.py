"""
Hub management - handles collections of charging nodes.
The hub autonomously manages power distribution based on local policy.
"""

import logging
from typing import Dict, List, Literal, Optional

from nodes import I2CNode, NodeInterface, SimulatedNode
from policies import PolicyManager

logger = logging.getLogger(__name__)


class Hub:
    """
    Represents a charging hub with multiple nodes.
    Manages power distribution autonomously based on configured policy.
    """

    def __init__(
        self,
        hub_id: str,
        hub_type: Literal["physical", "simulated"],
        max_power_kw: float = 50.0,
        policy_name: str = "equal_sharing",
    ):
        self.hub_id = hub_id
        self.hub_type = hub_type
        self.max_power_kw = max_power_kw
        self.nodes: Dict[str, NodeInterface] = {}
        self.policy_manager = PolicyManager(policy_name)
        logger.info(
            f"Created {hub_type} hub: {hub_id} "
            f"(max {max_power_kw}kW, policy: {policy_name})"
        )

    def add_node(self, node: NodeInterface):
        """Add a node to this hub."""
        self.nodes[node.node_id] = node
        logger.info(f"Added node {node.node_id} to hub {self.hub_id}")

    def get_node(self, node_id: str) -> Optional[NodeInterface]:
        """Get a specific node by ID."""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[NodeInterface]:
        """Get all nodes in this hub."""
        return list(self.nodes.values())

    def read_all_telemetry(self) -> Dict[str, Dict]:
        """Read telemetry from all nodes."""
        telemetry_data = {}
        for node_id, node in self.nodes.items():
            telemetry = node.read_telemetry()
            if telemetry:
                telemetry_data[node_id] = telemetry
        return telemetry_data

    def update_vehicle_status(
        self,
        node_id: str,
        vehicle_id: Optional[str],
        vehicle_soc: Optional[int],
        authorized: bool,
    ) -> bool:
        """
        Update vehicle status on a node.
        Called when cloud sends vehicle connection/authorization updates.

        Args:
            node_id: Target node ID
            vehicle_id: Vehicle ID (None if disconnected)
            vehicle_soc: State of charge percentage
            authorized: Whether vehicle is authorized to charge

        Returns:
            True if successful, False otherwise
        """
        node = self.get_node(node_id)
        if not node:
            logger.warning(f"Node {node_id} not found in hub {self.hub_id}")
            return False

        # Update node state
        node.update_vehicle_info(vehicle_id, vehicle_soc)
        node.authorized = authorized

        logger.info(
            f"Vehicle status updated: {self.hub_id}/{node_id} - "
            f"vehicle={vehicle_id}, soc={vehicle_soc}, auth={authorized}"
        )

        # Recalculate power distribution
        self.apply_power_distribution()

        return True

    def update_policy(self, policy_name: str):
        """
        Update the power distribution policy.
        Called when cloud sends policy updates.

        Args:
            policy_name: Name of the new policy to apply
        """
        logger.info(f"Hub {self.hub_id} updating policy to: {policy_name}")
        self.policy_manager.update_policy(policy_name)
        # Recalculate with new policy
        self.apply_power_distribution()

    def apply_power_distribution(self):
        """
        Calculate and apply power distribution to all nodes.
        This is the core DLM logic - hub autonomously manages power.
        """
        # Calculate power limits using current policy
        power_limits = self.policy_manager.calculate_power_distribution(
            self.nodes, self.max_power_kw
        )

        # Apply limits to each node
        for node_id, power_limit_kw in power_limits.items():
            node = self.nodes.get(node_id)
            if node:
                node.write_command(power_limit_kw, node.authorized)

        logger.debug(f"Hub {self.hub_id} power distribution applied: {power_limits}")


def create_hub_from_config(config: Dict) -> Hub:
    """
    Factory function to create a hub from configuration.

    Args:
        config: Hub configuration dictionary with keys:
                - hub_id: str
                - type: "physical" or "simulated"
                - max_power_kw: float (default: 50.0)
                - policy: str (default: "equal_sharing")
                - i2c_bus: int (for physical hubs)
                - nodes: list of node configs

    Returns:
        Configured Hub instance
    """
    hub_id = config["hub_id"]
    hub_type = config["type"]
    max_power_kw = config.get("max_power_kw", 50.0)
    policy_name = config.get("policy", "equal_sharing")

    if not hub_id or not hub_type:
        raise ValueError("Configuration Hub invalid: missing hub_id or type")

    hub = Hub(hub_id, hub_type, max_power_kw, policy_name)

    # Initialize I2C bus for physical hubs
    i2c_bus = None
    if hub_type == "physical":
        try:
            i2c_bus = _initialize_i2c_bus(config.get("i2c_bus", 1), hub_id)
        except Exception:
            return hub

    # Create nodes
    for node_config in config.get("nodes", []):
        try:
            node = _build_node(node_config, hub_type, i2c_bus)
            if node:
                hub.add_node(node)
        except Exception as e:
            logger.error(f"Unable to create node {node_config.get('node_id')}: {e}")

    return hub


def _initialize_i2c_bus(bus_number: int, hub_id: str):
    """Initialize and return an I2C bus."""
    try:
        import smbus2

        bus = smbus2.SMBus(bus_number)
        logger.info(f"I2C bus {bus_number} initialized for hub {hub_id}")
        return bus
    except Exception as e:
        logger.error(f"Failed to initialize I2C bus {bus_number} for hub {hub_id}: {e}")
        logger.warning(f"Hub {hub_id} will not function properly without I2C")
        raise


def _build_node(node_cfg: Dict, hub_type: str, i2c_bus) -> Optional[NodeInterface]:
    """Private sub-factory for creating individual nodes."""
    node_id = node_cfg.get("node_id")
    max_power_kw = node_cfg.get("max_power_kw", 22.0)

    if not node_id:
        logger.error("Node configuration missing required 'node_id'")
        return None

    if hub_type == "physical":
        i2c_address = node_cfg.get("i2c_address")
        if i2c_bus and i2c_address:
            return I2CNode(node_id, max_power_kw, i2c_address, i2c_bus)
        logger.warning(f"Physical node {node_id} missing I2C configuration")
        return None

    if hub_type == "simulated":
        return SimulatedNode(node_id, max_power_kw)

    logger.error(f"Unknown hub type: {hub_type}")
    return None
