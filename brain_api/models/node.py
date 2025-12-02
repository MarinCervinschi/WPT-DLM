from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from ..db import Base


class Node(Base):
    """
    The Node (Charging Point) - individual charging station.

    Each node belongs to a hub and can have multiple charging sessions.
    """

    __tablename__ = "nodes"
    __table_args__ = (
        CheckConstraint(
            "max_power_kw > 0 AND max_power_kw <= 350", name="check_max_power_range"
        ),
    )

    node_id = Column(String(50), primary_key=True, index=True)
    hub_id = Column(
        String(50),
        ForeignKey("hubs.hub_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(100), nullable=True, comment="Human-readable name")
    max_power_kw = Column(
        Float,
        nullable=False,
        default=22.0,
        comment="Maximum power output in kW (depending on hub capacity)",
    )

    is_maintenance = Column(Boolean, nullable=False, default=False)

    hub = relationship("Hub", back_populates="nodes")
    sessions = relationship(
        "ChargingSession", back_populates="node", cascade="all, delete-orphan"
    )
    dlm_events = relationship(
        "DLMEvent", back_populates="node", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Node(id={self.node_id}, hub={self.hub_id}, max_power={self.max_power_kw}kW)>"
