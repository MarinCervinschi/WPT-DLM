from typing import List

from fastapi import APIRouter, HTTPException, status

from ..repositories.base import NotFoundError
from ..schemas import DLMEventListResponse, DLMEventLog, DLMEventResponse
from .dependencies import DLMServiceDep

router = APIRouter(prefix="/dlm", tags=["Dynamic Load Management"])


@router.get(
    "/events",
    response_model=DLMEventListResponse,
    summary="List DLM events",
)
def list_events(
    service: DLMServiceDep,
    hub_id: str | None = None,
    node_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> DLMEventListResponse:
    """List DLM events with optional filtering by hub or node."""
    return service.list(hub_id=hub_id, node_id=node_id, skip=skip, limit=limit)


@router.get(
    "/events/recent",
    response_model=List[DLMEventResponse],
    summary="Get recent DLM events",
)
def get_recent_events(
    service: DLMServiceDep,
    hours: int = 24,
    limit: int = 100,
) -> List[DLMEventResponse]:
    """Get DLM events from the last N hours."""
    return service.get_recent(hours=hours, limit=limit)


@router.get(
    "/events/{event_id}",
    response_model=DLMEventResponse,
    summary="Get a DLM event by ID",
)
def get_event(event_id: int, service: DLMServiceDep) -> DLMEventResponse:
    """Get a specific DLM event by its ID."""
    try:
        return service.get(event_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/events",
    response_model=DLMEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a DLM event",
)
def log_event(data: DLMEventLog, service: DLMServiceDep) -> DLMEventResponse:
    """Log a new DLM event (power limit change)."""
    try:
        return service.log(data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
