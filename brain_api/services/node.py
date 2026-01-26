from sqlalchemy.orm import Session

from ..models import NodeDbo
from ..repositories import HubRepository, NodeRepository
from ..schemas import NodeCreate, NodeListResponse, NodeResponse, NodeUpdate
from .base import BaseService


class NodeService(
    BaseService[
        NodeDbo,
        NodeRepository,
        NodeCreate,
        NodeUpdate,
        NodeResponse,
        NodeListResponse,
    ]
):
    """Service layer for Node operations."""

    repository_class = NodeRepository
    response_schema = NodeResponse
    list_response_schema = NodeListResponse

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.hub_repo = HubRepository(db)

    def list(
        self,
        hub_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> NodeListResponse:
        """List nodes with pagination, optionally filtering by hub."""
        if hub_id:
            nodes = self.repo.get_nodes_by_hub(hub_id)
            total = len(list(nodes))
        else:
            nodes = self.repo.get_all(skip=skip, limit=limit)
            total = self.repo.count()

        return NodeListResponse(
            items=[NodeResponse.model_validate(n) for n in nodes],
            total=total,
            skip=skip,
            limit=limit,
        )

    def create(self, data: NodeCreate) -> NodeResponse:
        """Create a new node (verifies hub exists)."""
        self.hub_repo.get_or_raise(data.hub_id)
        return super().create(data)

    def set_maintenance(self, node_id: str, maintenance: bool) -> NodeResponse:
        """Set node maintenance status."""
        node = self.repo.set_maintenance(node_id, maintenance)
        self.db.commit()
        return NodeResponse.model_validate(node)
