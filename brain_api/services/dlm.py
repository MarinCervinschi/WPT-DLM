import logging
from typing import List

from sqlalchemy.orm import Session

from ..models import DLMEvent
from ..repositories import DLMEventRepository, HubRepository, NodeRepository
from ..schemas import (
    DLMEventCreate,
    DLMEventListResponse,
    DLMEventLog,
    DLMEventResponse,
)
from .base import BaseService

logger = logging.getLogger(__name__)


class DLMService(
    BaseService[
        DLMEvent,
        DLMEventRepository,
        DLMEventCreate,
        DLMEventCreate,  # No update for events
        DLMEventResponse,
        DLMEventListResponse,
    ]
):
    """Service layer for Dynamic Load Management operations."""

    repository_class = DLMEventRepository
    response_schema = DLMEventResponse
    list_response_schema = DLMEventListResponse

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.hub_repo = HubRepository(db)
        self.node_repo = NodeRepository(db)

    def list(
        self,
        hub_id: str | None = None,
        node_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> DLMEventListResponse:
        """List DLM events with pagination, optionally filtering by hub or node."""
        if hub_id:
            events = self.repo.get_events_by_hub(hub_id)
            total = len(list(events))
        elif node_id:
            events = self.repo.get_events_by_node(node_id)
            total = len(list(events))
        else:
            events = self.repo.get_all(skip=skip, limit=limit)
            total = self.repo.count()

        return DLMEventListResponse(
            items=[DLMEventResponse.model_validate(e) for e in events],
            total=total,
            skip=skip,
            limit=limit,
        )

    def get_recent(self, hours: int = 24, limit: int = 100) -> List[DLMEventResponse]:
        """Get recent DLM events."""
        events = self.repo.get_recent_events(hours, limit)
        return [DLMEventResponse.model_validate(e) for e in events]

    def log(self, data: DLMEventLog) -> DLMEventResponse:
        """Log a new DLM event."""
        self.hub_repo.get_or_raise(data.hub_id)
        self.node_repo.get_or_raise(data.node_id)

        event = self.repo.log_event(
            hub_id=data.hub_id,
            node_id=data.node_id,
            trigger_reason=data.trigger_reason,
            total_grid_load_kw=data.total_grid_load_kw,
            original_limit_kw=data.original_limit_kw,
            new_limit_kw=data.new_limit_kw,
            available_capacity=data.available_capacity_at_trigger,
        )
        self.db.commit()
        logger.info(f"DLM Event: {data.trigger_reason} on {data.node_id}")
        return DLMEventResponse.model_validate(event)
