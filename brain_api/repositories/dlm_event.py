from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

from sqlalchemy import and_, func, select

from ..models import DLMEventDbo as DLMEvent
from ..schemas import DLMEventCreate
from .base import BaseRepository


class DLMEventRepository(BaseRepository[DLMEvent, DLMEventCreate, dict[str, Any]]):
    """
    Repository for DLMEvent (Dynamic Load Management) operations.
    """

    model = DLMEvent
    pk_field = "dlm_event_id"

    def get_events_by_hub(self, hub_id: str) -> Sequence[DLMEvent]:
        """Get all DLM events for a hub."""
        return self.filter_by(hub_id=hub_id)

    def get_events_by_node(self, node_id: str) -> Sequence[DLMEvent]:
        """Get all DLM events for a node."""
        return self.filter_by(node_id=node_id)

    def get_events_by_reason(self, trigger_reason: str) -> Sequence[DLMEvent]:
        """Get events by trigger reason."""
        return self.filter_by(trigger_reason=trigger_reason)

    def get_events_in_range(
        self,
        start: datetime,
        end: datetime,
        hub_id: str | None = None,
    ) -> Sequence[DLMEvent]:
        """
        Get DLM events within a time range.

        Args:
            start: Start of range
            end: End of range
            hub_id: Optional hub filter

        Returns:
            List of events
        """
        stmt = select(DLMEvent).where(
            and_(
                DLMEvent.timestamp >= start,
                DLMEvent.timestamp <= end,
            )
        )
        if hub_id:
            stmt = stmt.where(DLMEvent.hub_id == hub_id)
        return self.db.execute(stmt).scalars().all()

    def log_event(
        self,
        hub_id: str,
        node_id: str,
        trigger_reason: str,
        total_grid_load_kw: float,
        original_limit_kw: float,
        new_limit_kw: float,
        available_capacity: float | None = None,
    ) -> DLMEvent:
        """
        Log a new DLM event.

        Args:
            hub_id: Hub ID
            node_id: Node ID
            trigger_reason: Reason for the event
            total_grid_load_kw: Total grid load
            original_limit_kw: Original power limit
            new_limit_kw: New power limit
            available_capacity: Available capacity at trigger

        Returns:
            Created event
        """
        return self.create(
            {
                "hub_id": hub_id,
                "node_id": node_id,
                "trigger_reason": trigger_reason,
                "total_grid_load_kw": total_grid_load_kw,
                "original_limit_kw": original_limit_kw,
                "new_limit_kw": new_limit_kw,
                "available_capacity_at_trigger": available_capacity,
                "timestamp": datetime.now(timezone.utc),
            }
        )

    def get_recent_events(
        self, hours: int = 24, limit: int = 100
    ) -> Sequence[DLMEvent]:
        """Get events from the last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (
            select(DLMEvent)
            .where(DLMEvent.timestamp >= cutoff)
            .order_by(DLMEvent.timestamp.desc())
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def get_event_stats(
        self,
        hub_id: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dict[str, int]:
        """
        Get statistics about DLM events.

        Returns:
            Dictionary with event counts by reason
        """
        stmt = select(DLMEvent.trigger_reason, func.count(DLMEvent.dlm_event_id))

        if hub_id:
            stmt = stmt.where(DLMEvent.hub_id == hub_id)
        if start:
            stmt = stmt.where(DLMEvent.timestamp >= start)
        if end:
            stmt = stmt.where(DLMEvent.timestamp <= end)

        stmt = stmt.group_by(DLMEvent.trigger_reason)
        results = self.db.execute(stmt).all()

        return {reason: count for reason, count in results}
