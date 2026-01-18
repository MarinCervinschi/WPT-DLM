import logging
from abc import ABC, abstractmethod
from typing import Dict, Type

logger = logging.getLogger(__name__)

# Registry for auto-discovered policies
_policy_registry: Dict[str, Type["PowerPolicy"]] = {}


class PowerPolicy(ABC):
    """Abstract base class for power distribution policies."""

    @abstractmethod
    def calculate_power_limits(
        self, nodes: Dict, max_hub_power_kw: float  # node_id -> NodeInterface
    ) -> Dict[str, float]:
        """
        Calculate power limits for all nodes based on policy.

        Args:
            nodes: Dictionary of node_id -> NodeInterface
            max_hub_power_kw: Maximum power available for this hub

        Returns:
            Dictionary of node_id -> power_limit_kw
        """
        pass


def register_policy(name: str):
    """
    Decorator to automatically register a policy.

    Usage:
        @register_policy("my_policy_name")
        class MyPolicy(PowerPolicy):
            ...

    Args:
        name: The name to register the policy under
    """

    def decorator(cls: Type["PowerPolicy"]) -> Type["PowerPolicy"]:
        _policy_registry[name] = cls
        logger.debug(f"Registered policy: {name} -> {cls.__name__}")
        return cls

    return decorator


def get_registered_policies() -> Dict[str, Type["PowerPolicy"]]:
    """Get all registered policies."""
    return _policy_registry.copy()
