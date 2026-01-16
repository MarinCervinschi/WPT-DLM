from .base import PowerPolicy, register_policy
from typing import Dict
import logging

logger = logging.getLogger(__name__)


@register_policy("priority")
class PriorityPolicy(PowerPolicy):
    """
    Priority-based policy: Lower SoC vehicles get more power.
    Helps vehicles with lower battery charge first.
    """
    
    def calculate_power_limits(
        self, 
        nodes: Dict, 
        max_hub_power_kw: float
    ) -> Dict[str, float]:
        """Distribute power prioritizing vehicles with lower SoC."""
        power_limits = {}
        
        # Find all authorized nodes with connected vehicles and SoC info
        authorized_nodes = [
            (node_id, node) 
            for node_id, node in nodes.items() 
            if node.authorized and node.connected_vehicle_id
        ]
        
        if not authorized_nodes:
            return {node_id: 0.0 for node_id in nodes.keys()}
        
        # Calculate priority weights (inverse of SoC)
        # Vehicles with lower SoC get higher weight
        priorities = []
        for node_id, node in authorized_nodes:
            soc = node.vehicle_soc if node.vehicle_soc is not None else 50
            # Invert priority: 100% SoC = low priority, 0% SoC = high priority
            priority = max(1, 100 - soc)  # Ensure minimum priority of 1
            priorities.append((node_id, node, priority))
        
        total_priority = sum(p[2] for p in priorities)
        
        # Distribute power proportionally to priority
        for node_id, node in nodes.items():
            power_limits[node_id] = 0.0
        
        for node_id, node, priority in priorities:
            proportional_power = (priority / total_priority) * max_hub_power_kw
            power_limits[node_id] = min(proportional_power, node.max_power_kw)
        
        logger.debug(f"Priority policy: power distributed based on SoC priorities")
        
        return power_limits