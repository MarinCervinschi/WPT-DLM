"""
Priority-based DLM Policy.

Allocates power based on vehicle priority and SoC.
"""
from typing import Dict, List
from .dlm_policy import DLMPolicy, PowerAllocation
from core.mqtt_dtos.dlm_dto import VehicleRequest


class PriorityPolicy(DLMPolicy):
    """
    Priority policy: allocate power based on vehicle priority and low SoC first.
    """
    
    def __call__(
        self,
        nodes_state: Dict[str, Dict],
        vehicle_requests: List[VehicleRequest]
    ) -> List[PowerAllocation]:
        """
        Allocate power based on priority and SoC.
        
        Priority order:
        1. Highest priority vehicles
        2. Lowest SoC vehicles (among same priority)
        
        Args:
            nodes_state: Current state of all nodes
            vehicle_requests: Vehicle charging requests
        
        Returns:
            Power allocations for each node
        """
        allocations = []
        
        # Create mapping of node_id to vehicle request
        node_to_request = {req.node_id: req for req in vehicle_requests}
        
        # Get charging nodes with their priorities
        charging_nodes = []
        for node_id, state in nodes_state.items():
            if state.get("is_occupied") and state.get("state") == "CHARGING":
                request = node_to_request.get(node_id)
                priority = request.priority if request else 0
                soc = state.get("vehicle_soc", 100)
                charging_nodes.append((node_id, priority, soc, state))
        
        if not charging_nodes:
            # No active charging
            for node_id, state in nodes_state.items():
                allocations.append(PowerAllocation(
                    node_id=node_id,
                    allocated_power_kw=state["max_power_kw"],
                    reason="No active charging"
                ))
            return allocations
        
        # Sort by priority (desc) then by SoC (asc)
        charging_nodes.sort(key=lambda x: (-x[1], x[2]))
        
        remaining_capacity = self.max_grid_capacity_kw
        
        # Allocate power to nodes in priority order
        for node_id, priority, soc, state in charging_nodes:
            max_node_power = state["max_power_kw"]
            allocated = min(remaining_capacity, max_node_power)
            
            allocations.append(PowerAllocation(
                node_id=node_id,
                allocated_power_kw=allocated,
                reason=f"Priority={priority}, SoC={soc}%"
            ))
            
            remaining_capacity -= allocated
            
            if remaining_capacity <= 0:
                break
        
        # Allocate remaining nodes (not charging)
        allocated_nodes = {alloc.node_id for alloc in allocations}
        for node_id, state in nodes_state.items():
            if node_id not in allocated_nodes:
                allocations.append(PowerAllocation(
                    node_id=node_id,
                    allocated_power_kw=state["max_power_kw"],
                    reason="Idle"
                ))
        
        return allocations
    
    def get_policy_name(self) -> str:
        return "Priority"
