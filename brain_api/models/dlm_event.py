from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from ..db import Base


class DLMEvent(Base):
    """
    DLM Event - Dynamic Load Management decision log.

    Records load balancing decisions for ML training and auditing.
    Each event captures the state before/after a power limit adjustment.
    """

    __tablename__ = "dlm_events"
    __table_args__ = (
        CheckConstraint("total_grid_load_kw >= 0", name="check_load_non_negative"),
        CheckConstraint(
            "original_limit_kw >= 0", name="check_original_limit_non_negative"
        ),
        CheckConstraint("new_limit_kw >= 0", name="check_new_limit_non_negative"),
    )

    dlm_event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )

    hub_id = Column(
        String(50),
        ForeignKey("hubs.hub_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id = Column(
        String(50),
        ForeignKey("nodes.node_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    trigger_reason = Column(
        String(50),
        nullable=False,
        comment="e.g., GRID_OVERLOAD, PRIORITY_SHIFT, SCHEDULE",
    )
    total_grid_load_kw = Column(
        Float, nullable=False, comment="Total load on hub at trigger time"
    )
    available_capacity_at_trigger = Column(
        Float, nullable=True, comment="Hub.max_grid_capacity_kw - total_grid_load_kw"
    )

    original_limit_kw = Column(
        Float, nullable=False, comment="Power limit before adjustment"
    )
    new_limit_kw = Column(Float, nullable=False, comment="Power limit after adjustment")

    hub = relationship("Hub", back_populates="dlm_events")
    node = relationship("Node", back_populates="dlm_events")

    def __repr__(self) -> str:
        return f"<DLMEvent(id={self.dlm_event_id}, reason={self.trigger_reason}, {self.original_limit_kw}->{self.new_limit_kw}kW)>"

    @property
    def limit_change_kw(self) -> float:
        """Calculate the power limit change (positive = increase, negative = decrease)."""
        return self.new_limit_kw - self.original_limit_kw  # type: ignore[return-value]
