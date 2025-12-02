from typing import List

from fastapi import APIRouter, HTTPException, status

from ..repositories.base import NotFoundError
from ..schemas import (
    ChargingSessionEnd,
    ChargingSessionListResponse,
    ChargingSessionResponse,
    ChargingSessionStart,
)
from .dependencies import ChargingSessionServiceDep

router = APIRouter(prefix="/sessions", tags=["Charging Sessions"])


@router.get(
    "",
    response_model=ChargingSessionListResponse,
    summary="List charging sessions",
)
def list_sessions(
    service: ChargingSessionServiceDep,
    node_id: str | None = None,
    vehicle_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> ChargingSessionListResponse:
    """List charging sessions with optional filtering by node or vehicle."""
    return service.list(node_id=node_id, vehicle_id=vehicle_id, skip=skip, limit=limit)


@router.get(
    "/active",
    response_model=List[ChargingSessionResponse],
    summary="Get active sessions",
)
def get_active_sessions(
    service: ChargingSessionServiceDep,
    node_id: str | None = None,
) -> List[ChargingSessionResponse]:
    """Get all currently active charging sessions."""
    return service.get_active(node_id)


@router.get(
    "/{session_id}",
    response_model=ChargingSessionResponse,
    summary="Get a session by ID",
)
def get_session(
    session_id: int,
    service: ChargingSessionServiceDep,
) -> ChargingSessionResponse:
    """Get a specific charging session by its ID."""
    try:
        return service.get(session_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/start",
    response_model=ChargingSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a charging session",
)
def start_session(
    data: ChargingSessionStart,
    service: ChargingSessionServiceDep,
) -> ChargingSessionResponse:
    """Start a new charging session on a node."""
    try:
        return service.start(data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{session_id}/end",
    response_model=ChargingSessionResponse,
    summary="End a charging session",
)
def end_session(
    session_id: int,
    data: ChargingSessionEnd,
    service: ChargingSessionServiceDep,
) -> ChargingSessionResponse:
    """End an active charging session with final metrics."""
    try:
        return service.end(session_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
