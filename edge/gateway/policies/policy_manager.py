
from typing import Dict
from .base import PowerPolicy, get_registered_policies
import logging

logger = logging.getLogger(__name__)


class PolicyManager:
    """
    Manages power distribution policy for a hub.
    Can switch between different policies based on cloud configuration.
    
    Automatically discovers all registered policies via @register_policy decorator.
    """
    
    def __init__(self, policy_name: str = "equal_sharing"):
        """
        Initialize with a policy.
        
        Args:
            policy_name: Name of the policy to use (default: "equal_sharing")
        """
        self.policy_name = policy_name
        self.policy = self._create_policy(policy_name)
        logger.info(f"Policy manager initialized with: {policy_name}")
    
    def _create_policy(self, policy_name: str) -> PowerPolicy:
        """Create policy instance from name using auto-discovered policies."""
        available_policies = get_registered_policies()
        
        policy_class = available_policies.get(policy_name)
        if not policy_class:
            logger.warning(
                f"Unknown policy '{policy_name}', using default 'equal_sharing'. "
                f"Available: {list(available_policies.keys())}"
            )
            policy_class = available_policies.get("equal_sharing")
            
        if not policy_class:
            raise RuntimeError("No policies registered! Check policy imports.")
            
        return policy_class()
    
    def update_policy(self, policy_name: str):
        """
        Update the active policy.
        Called when cloud sends a policy update.
        
        Args:
            policy_name: New policy name
        """
        if policy_name != self.policy_name:
            logger.info(f"Updating policy: {self.policy_name} -> {policy_name}")
            self.policy_name = policy_name
            self.policy = self._create_policy(policy_name)
        else:
            logger.debug(f"Policy unchanged: {policy_name}")
    
    def calculate_power_distribution(
        self, 
        nodes: Dict, 
        max_hub_power_kw: float
    ) -> Dict[str, float]:
        """
        Calculate power limits for all nodes using current policy.
        
        Args:
            nodes: Dictionary of node_id -> NodeInterface
            max_hub_power_kw: Maximum power available for this hub
            
        Returns:
            Dictionary of node_id -> power_limit_kw
        """
        return self.policy.calculate_power_limits(nodes, max_hub_power_kw)
