from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import and_, func, select

from ..models import ChargingSession
from ..schemas import ChargingSessionCreate, ChargingSessionUpdate
from .base import BaseRepository


class ChargingSessionRepository(
    BaseRepository[ChargingSession, ChargingSessionCreate, ChargingSessionUpdate]
):
    """
    Repository for ChargingSession operations.
    """

    model = ChargingSession
    pk_field = "charging_session_id"

    def get_active_sessions(
        self, node_id: str | None = None
    ) -> Sequence[ChargingSession]:
        """
        Get sessions that haven't ended yet.

        Args:
            node_id: Optional node filter

        Returns:
            List of active sessions
        """
        stmt = select(ChargingSession).where(ChargingSession.end_time.is_(None))
        if node_id:
            stmt = stmt.where(ChargingSession.node_id == node_id)
        return self.db.execute(stmt).scalars().all()

    def get_sessions_by_node(self, node_id: str) -> Sequence[ChargingSession]:
        """Get all sessions for a node."""
        return self.filter_by(node_id=node_id)

    def get_sessions_by_vehicle(self, vehicle_id: str) -> Sequence[ChargingSession]:
        """Get all sessions for a vehicle."""
        return self.filter_by(vehicle_id=vehicle_id)

    def get_sessions_in_range(
        self,
        start: datetime,
        end: datetime,
        node_id: str | None = None,
    ) -> Sequence[ChargingSession]:
        """
        Get sessions within a time range.

        Args:
            start: Start of range
            end: End of range
            node_id: Optional node filter

        Returns:
            List of sessions
        """
        stmt = select(ChargingSession).where(
            and_(
                ChargingSession.start_time >= start,
                ChargingSession.start_time <= end,
            )
        )
        if node_id:
            stmt = stmt.where(ChargingSession.node_id == node_id)
        return self.db.execute(stmt).scalars().all()

    def start_session(
        self,
        node_id: str,
        vehicle_id: str | None = None,
    ) -> ChargingSession:
        """
        Start a new charging session.

        Args:
            node_id: Node ID
            vehicle_id: Optional vehicle ID

        Returns:
            New session
        """
        return self.create(
            {
                "node_id": node_id,
                "vehicle_id": vehicle_id,
                "start_time": datetime.now(timezone.utc),
                "total_energy_kwh": 0.0,
                "avg_power_kw": 0.0,
            }
        )

    def end_session(
        self,
        session_id: int,
        total_energy_kwh: float,
        avg_power_kw: float,
    ) -> ChargingSession:
        """
        End a charging session.

        Args:
            session_id: Session ID
            total_energy_kwh: Total energy delivered
            avg_power_kw: Average power during session

        Returns:
            Updated session
        """
        return self.update(
            session_id,
            {
                "end_time": datetime.now(timezone.utc),
                "total_energy_kwh": total_energy_kwh,
                "avg_power_kw": avg_power_kw,
            },
        )

    def get_total_energy(
        self,
        node_id: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> float:
        """
        Get total energy delivered.

        Args:
            node_id: Optional node filter
            start: Optional start time filter
            end: Optional end time filter

        Returns:
            Total energy in kWh
        """
        stmt = select(func.sum(ChargingSession.total_energy_kwh))

        if node_id:
            stmt = stmt.where(ChargingSession.node_id == node_id)
        if start:
            stmt = stmt.where(ChargingSession.start_time >= start)
        if end:
            stmt = stmt.where(ChargingSession.start_time <= end)

        return self.db.execute(stmt).scalar_one() or 0.0
