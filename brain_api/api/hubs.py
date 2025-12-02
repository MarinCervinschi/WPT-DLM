from fastapi import APIRouter, HTTPException, status

from ..repositories.base import NotFoundError
from ..schemas import HubCreate, HubListResponse, HubResponse, HubUpdate
from .dependencies import HubServiceDep

router = APIRouter(prefix="/hubs", tags=["Hubs"])


@router.get(
    "",
    response_model=HubListResponse,
    summary="List all hubs",
)
def list_hubs(
    service: HubServiceDep,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> HubListResponse:
    """List all hubs with optional pagination and filtering."""
    return service.list(skip=skip, limit=limit, active_only=active_only)


@router.get(
    "/{hub_id}",
    response_model=HubResponse,
    summary="Get a hub by ID",
)
def get_hub(hub_id: str, service: HubServiceDep) -> HubResponse:
    """Get a specific hub by its ID."""
    try:
        return service.get(hub_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "",
    response_model=HubResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hub",
)
def create_hub(data: HubCreate, service: HubServiceDep) -> HubResponse:
    """Create a new hub."""
    return service.create(data)


@router.patch(
    "/{hub_id}",
    response_model=HubResponse,
    summary="Update a hub",
)
def update_hub(hub_id: str, data: HubUpdate, service: HubServiceDep) -> HubResponse:
    """Update an existing hub."""
    try:
        return service.update(hub_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{hub_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hub",
)
def delete_hub(hub_id: str, service: HubServiceDep) -> None:
    """Delete a hub by its ID."""
    if not service.delete(hub_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hub {hub_id} not found",
        )


@router.post(
    "/{hub_id}/activate",
    response_model=HubResponse,
    summary="Activate a hub",
)
def activate_hub(hub_id: str, service: HubServiceDep) -> HubResponse:
    """Activate a hub."""
    try:
        return service.activate(hub_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{hub_id}/deactivate",
    response_model=HubResponse,
    summary="Deactivate a hub",
)
def deactivate_hub(hub_id: str, service: HubServiceDep) -> HubResponse:
    """Deactivate a hub."""
    try:
        return service.deactivate(hub_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
