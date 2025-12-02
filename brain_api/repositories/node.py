from typing import Any, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..models import Node
from .base import BaseRepository
from ..schemas import NodeCreate, NodeUpdate


class NodeRepository(BaseRepository[Node, NodeCreate, NodeUpdate]):
    """
    Repository for Node (Charging Point) operations.
    """

    model = Node
    pk_field = "node_id"

    def get_nodes_by_hub(self, hub_id: str) -> Sequence[Node]:
        """Get all nodes belonging to a hub."""
        return self.filter_by(hub_id=hub_id)

    def get_available_nodes(self, hub_id: str | None = None) -> Sequence[Node]:
        """
        Get nodes that are not in maintenance.

        Args:
            hub_id: Optional hub filter

        Returns:
            List of available nodes
        """
        if hub_id:
            return self.filter_by(hub_id=hub_id, is_maintenance=False)
        return self.filter_by(is_maintenance=False)

    def get_nodes_in_maintenance(self) -> Sequence[Node]:
        """Get all nodes currently in maintenance."""
        return self.filter_by(is_maintenance=True)

    def set_maintenance(self, node_id: str, maintenance: bool = True) -> Node:
        """Set node maintenance status."""
        return self.update(node_id, {"is_maintenance": maintenance})

    def get_total_power_capacity(self, hub_id: str | None = None) -> float:
        """
        Get sum of max_power_kw for nodes.

        Args:
            hub_id: Optional hub filter

        Returns:
            Total power capacity in kW
        """
        stmt = select(func.sum(Node.max_power_kw)).where(Node.is_maintenance == False)
        if hub_id:
            stmt = stmt.where(Node.hub_id == hub_id)
        return self.db.execute(stmt).scalar_one() or 0.0

    def get_node_with_sessions(self, node_id: str) -> Node | None:
        """Get node with eager-loaded sessions."""
        stmt = (
            select(Node)
            .where(Node.node_id == node_id)
            .options(selectinload(Node.sessions))
        )
        return self.db.execute(stmt).scalar_one_or_none()
