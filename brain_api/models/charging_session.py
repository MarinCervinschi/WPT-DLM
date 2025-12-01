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


class ChargingSession(Base):
    """
    Charging Session - represents a single charging event.

    Tracks energy delivered, duration, and links vehicle to node.
    """

    __tablename__ = "charging_sessions"
    __table_args__ = (
        CheckConstraint("total_energy_kwh >= 0", name="check_energy_non_negative"),
        CheckConstraint("avg_power_kw >= 0", name="check_avg_power_non_negative"),
        CheckConstraint(
            "end_time IS NULL OR end_time >= start_time", name="check_end_after_start"
        ),
    )

    charging_session_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    node_id = Column(
        String(50),
        ForeignKey("nodes.node_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_id = Column(
        String(50),
        ForeignKey("vehicles.vehicle_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )
    end_time = Column(DateTime(timezone=True), nullable=True)

    total_energy_kwh = Column(
        Float, nullable=False, default=0.0, comment="Total energy delivered in kWh"
    )
    avg_power_kw = Column(
        Float, nullable=False, default=0.0, comment="Average power during session in kW"
    )

    node = relationship("Node", back_populates="sessions")
    vehicle = relationship("Vehicle", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<ChargingSession(id={self.id}, node={self.node_id}, energy={self.total_energy_kwh}kWh)>"

    @property
    def is_active(self) -> bool:
        """Check if session is still ongoing."""
        return self.end_time is None

    @property
    def duration_minutes(self) -> float | None:
        """Calculate session duration in minutes."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds() / 60  # type: ignore[union-attr]
