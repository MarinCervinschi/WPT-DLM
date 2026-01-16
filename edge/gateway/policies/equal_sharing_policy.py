from .base import PowerPolicy, register_policy
from typing import Dict
import logging

logger = logging.getLogger(__name__)


@register_policy("equal_sharing")
class EqualSharingPolicy(PowerPolicy):
    """
    Default policy: Equal power distribution among authorized vehicles.
    Simple and fair - each connected and authorized vehicle gets equal share.
    """
    
    def calculate_power_limits(
        self, 
        nodes: Dict, 
        max_hub_power_kw: float
    ) -> Dict[str, float]:
        """Distribute power equally among authorized connected vehicles."""
        power_limits = {}
        
        # Find all authorized nodes with connected vehicles
        authorized_nodes = [
            (node_id, node) 
            for node_id, node in nodes.items() 
            if node.authorized and node.connected_vehicle_id
        ]
        
        if not authorized_nodes:
            # No authorized vehicles - all nodes get 0
            return {node_id: 0.0 for node_id in nodes.keys()}
        
        # Equal distribution
        power_per_node = max_hub_power_kw / len(authorized_nodes)
        
        for node_id, node in nodes.items():
            if node.authorized and node.connected_vehicle_id:
                # Don't exceed node's maximum capacity
                power_limits[node_id] = min(power_per_node, node.max_power_kw)
            else:
                power_limits[node_id] = 0.0
        
        logger.debug(
            f"Equal sharing: {len(authorized_nodes)} nodes, "
            f"{power_per_node:.2f}kW each"
        )
        
        return power_limits