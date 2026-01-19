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
    hub_id = Column(String(50), primary_key=True, index=True)

    # Geo Location
    lat = Column(Float, nullable=True, comment="Latitude (-90 to 90)")
    lon = Column(Float, nullable=True, comment="Longitude (-180 to 180)")
    alt = Column(Float, nullable=True, default=0.0, comment="Altitude in meters")

    max_grid_capacity_kw = Column(
        Float, nullable=False, default=100.0, comment="Maximum grid capacity in kW"
    )
    ip_address = Column(
        String(45), nullable=False, default="0.0.0.0", comment="IP Address"
    )
    firmware_version = Column(
        String(20), nullable=False, default="1.0.0", comment="Firmware version"
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
        return f"<Hub(id={self.hub_id}, active={self.is_active}, nodes={len(self.nodes or [])})>"
