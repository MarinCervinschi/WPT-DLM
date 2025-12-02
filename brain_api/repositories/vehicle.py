from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import Vehicle
from .base import BaseRepository
from ..schemas import VehicleCreate, VehicleUpdate


class VehicleRepository(BaseRepository[Vehicle, VehicleCreate, VehicleUpdate]):
    """
    Repository for Vehicle operations.
    """

    model = Vehicle
    pk_field = "vehicle_id"

    def get_vehicles_by_driver(self, driver_id: str) -> Sequence[Vehicle]:
        """Get all vehicles owned by a driver."""
        return self.filter_by(driver_id=driver_id)

    def get_vehicles_by_manufacturer(self, manufacturer: str) -> Sequence[Vehicle]:
        """Get all vehicles by manufacturer."""
        return self.filter_by(manufacturer=manufacturer)

    def get_recently_registered(
        self, days: int = 30, limit: int = 100
    ) -> Sequence[Vehicle]:
        """Get vehicles registered in the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(Vehicle)
            .where(Vehicle.registered_at >= cutoff)
            .order_by(Vehicle.registered_at.desc())
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def get_vehicle_with_sessions(self, vehicle_id: str) -> Vehicle | None:
        """Get vehicle with eager-loaded charging sessions."""
        stmt = (
            select(Vehicle)
            .where(Vehicle.vehicle_id == vehicle_id)
            .options(selectinload(Vehicle.sessions))
        )
        return self.db.execute(stmt).scalar_one_or_none()
