from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import relationship

from ..db import Base


class VehicleDbo(Base):
    """
    The Vehicle (Guest) - electric vehicle that uses charging infrastructure.
    """

    __tablename__ = "vehicles"

    vehicle_id = Column(String(50), primary_key=True, index=True)

    model = Column(String(100), nullable=True, comment="Vehicle model name")
    manufacturer = Column(String(100), nullable=True, comment="Vehicle manufacturer")

    driver_id = Column(
        String(50), nullable=True, index=True, comment="Driver/owner identifier"
    )

    registered_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    sessions = relationship("ChargingSessionDbo", back_populates="vehicle")

    def __repr__(self) -> str:
        return f"<VehicleDbo(id={self.vehicle_id}, model={self.model}, manufacturer={self.manufacturer})>"
