from typing import List

from sqlalchemy.orm import Session

from ..models import ChargingSessionDbo
from ..repositories import ChargingSessionRepository, NodeRepository, VehicleRepository
from ..schemas import (
    ChargingSessionCreate,
    ChargingSessionEnd,
    ChargingSessionListResponse,
    ChargingSessionResponse,
    ChargingSessionStart,
    ChargingSessionUpdate,
)
from .base import BaseService


class ChargingSessionService(
    BaseService[
        ChargingSessionDbo,
        ChargingSessionRepository,
        ChargingSessionCreate,
        ChargingSessionUpdate,
        ChargingSessionResponse,
        ChargingSessionListResponse,
    ]
):
    """Service layer for ChargingSession operations."""

    repository_class = ChargingSessionRepository
    response_schema = ChargingSessionResponse
    list_response_schema = ChargingSessionListResponse

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.node_repo = NodeRepository(db)
        self.vehicle_repo = VehicleRepository(db)

    def list(
        self,
        node_id: str | None = None,
        vehicle_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> ChargingSessionListResponse:
        """List charging sessions with pagination, optionally filtering by node or vehicle."""
        if node_id:
            sessions = self.repo.get_sessions_by_node(node_id)
            total = len(list(sessions))
        elif vehicle_id:
            sessions = self.repo.get_sessions_by_vehicle(vehicle_id)
            total = len(list(sessions))
        else:
            sessions = self.repo.get_all(skip=skip, limit=limit)
            total = self.repo.count()

        return ChargingSessionListResponse(
            items=[ChargingSessionResponse.model_validate(s) for s in sessions],
            total=total,
            skip=skip,
            limit=limit,
        )

    def get_active(self, node_id: str | None = None) -> List[ChargingSessionResponse]:
        """Get active charging sessions."""
        sessions = self.repo.get_active_sessions(node_id)
        return [ChargingSessionResponse.model_validate(s) for s in sessions]

    def start(self, data: ChargingSessionStart) -> ChargingSessionResponse:
        """Start a new charging session."""
        self.node_repo.get_or_raise(data.node_id)

        if data.vehicle_id:
            self.vehicle_repo.get_or_create(data.vehicle_id)

        session = self.repo.start_session(data.node_id, data.vehicle_id)
        self.db.commit()
        self.logger.info(
            f"Started session {session.charging_session_id} on node {data.node_id}"
        )
        return ChargingSessionResponse.model_validate(session)

    def end(self, session_id: int, data: ChargingSessionEnd) -> ChargingSessionResponse:
        """End a charging session."""
        session = self.repo.end_session(
            session_id,
            data.total_energy_kwh,
            data.avg_power_kw,
        )
        self.db.commit()
        self.logger.info(f"Ended session {session_id}: {data.total_energy_kwh} kWh")
        return ChargingSessionResponse.model_validate(session)
