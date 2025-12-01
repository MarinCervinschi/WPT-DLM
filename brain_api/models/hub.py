from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, String, func
from sqlalchemy.orm import relationship

from ..db import Base


class Hub(Base):
    """
    The Hub (Edge Gateway) - manages multiple charging nodes.

    Represents a physical location with charging infrastructure.
    """

    __tablename__ = "hubs"
    __table_args__ = (
        CheckConstraint("lat >= -90 AND lat <= 90", name="check_lat_range"),
        CheckConstraint("lon >= -180 AND lon <= 180", name="check_lon_range"),
        CheckConstraint("alt >= -500 AND alt <= 10000", name="check_alt_range"),
        CheckConstraint("max_grid_capacity_kw > 0", name="check_max_grid_positive"),
    )

    hub_id = Column(String(50), primary_key=True, index=True)

    # Geo Location
    lat = Column(Float, nullable=True, comment="Latitude (-90 to 90)")
    lon = Column(Float, nullable=True, comment="Longitude (-180 to 180)")
    alt = Column(Float, nullable=True, default=0.0, comment="Altitude in meters")

    max_grid_capacity_kw = Column(
        Float, nullable=False, default=100.0, comment="Maximum grid capacity in kW"
    )

    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    last_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    nodes = relationship("Node", back_populates="hub", cascade="all, delete-orphan")
    dlm_events = relationship(
        "DLMEvent", back_populates="hub", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Hub(id={self.id}, active={self.is_active}, nodes={len(self.nodes or [])})>"
