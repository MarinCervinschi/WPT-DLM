from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from ..models import Hub
from .base import BaseRepository
from ..schemas import HubCreate, HubUpdate


class HubRepository(BaseRepository[Hub, HubCreate, HubUpdate]):
    """
    Repository for Hub (Edge Gateway) operations.
    """

    model = Hub
    pk_field = "hub_id"

    def get_active_hubs(self) -> Sequence[Hub]:
        """Get all active hubs."""
        return self.filter_by(is_active=True)

    def get_inactive_hubs(self) -> Sequence[Hub]:
        """Get all inactive hubs."""
        return self.filter_by(is_active=False)

    def get_hubs_by_location(
        self,
        lat: float,
        lon: float,
        radius_km: float = 10.0,
    ) -> Sequence[Hub]:
        """
        Get hubs within a radius of a location (approximate).

        Uses a simple bounding box approach for efficiency.
        For precise distance calculations, use PostGIS.

        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Search radius in kilometers

        Returns:
            List of hubs within radius
        """
        # Approximate degrees per km (varies by latitude)
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(lat * 0.0175))  # cos approximation

        stmt = select(Hub).where(
            and_(
                Hub.lat.isnot(None),
                Hub.lon.isnot(None),
                Hub.lat >= lat - lat_delta,
                Hub.lat <= lat + lat_delta,
                Hub.lon >= lon - lon_delta,
                Hub.lon <= lon + lon_delta,
            )
        )
        return self.db.execute(stmt).scalars().all()

    def update_last_seen(self, hub_id: str) -> Hub | None:
        """Update hub's last_seen timestamp."""
        hub = self.get(hub_id)
        if hub:
            hub.last_seen = datetime.now(timezone.utc)  # type: ignore[assignment]
            self.db.flush()
        return hub

    def set_active(self, hub_id: str, active: bool = True) -> Hub:
        """Set hub active/inactive status."""
        return self.update(hub_id, {"is_active": active})

    def get_hub_with_nodes(self, hub_id: str) -> Hub | None:
        """Get hub with eager-loaded nodes."""
        stmt = select(Hub).where(Hub.hub_id == hub_id).options(selectinload(Hub.nodes))
        return self.db.execute(stmt).scalar_one_or_none()

    def get_total_capacity(self) -> float:
        """Get sum of max_grid_capacity_kw for all active hubs."""
        stmt = select(func.sum(Hub.max_grid_capacity_kw)).where(Hub.is_active == True)
        return self.db.execute(stmt).scalar_one() or 0.0
