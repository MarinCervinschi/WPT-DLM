from fastapi import APIRouter, HTTPException, status

from ..repositories.base import NotFoundError
from ..schemas import VehicleCreate, VehicleListResponse, VehicleResponse, VehicleUpdate
from .dependencies import VehicleServiceDep

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get(
    "",
    response_model=VehicleListResponse,
    summary="List all vehicles",
)
def list_vehicles(
    service: VehicleServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> VehicleListResponse:
    """List all registered vehicles with pagination."""
    return service.list(skip=skip, limit=limit)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Get a vehicle by ID",
)
def get_vehicle(vehicle_id: str, service: VehicleServiceDep) -> VehicleResponse:
    """Get a specific vehicle by its ID."""
    try:
        return service.get(vehicle_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vehicle",
)
def create_vehicle(data: VehicleCreate, service: VehicleServiceDep) -> VehicleResponse:
    """Register a new vehicle."""
    return service.create(data)


@router.post(
    "/{vehicle_id}/register",
    response_model=VehicleResponse,
    summary="Get or register a vehicle",
)
def register_vehicle(vehicle_id: str, service: VehicleServiceDep) -> VehicleResponse:
    """Get existing vehicle or auto-register if not found."""
    return service.get_or_create(vehicle_id)


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Update a vehicle",
)
def update_vehicle(
    vehicle_id: str,
    data: VehicleUpdate,
    service: VehicleServiceDep,
) -> VehicleResponse:
    """Update an existing vehicle."""
    try:
        return service.update(vehicle_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vehicle",
)
def delete_vehicle(vehicle_id: str, service: VehicleServiceDep) -> None:
    """Delete a vehicle by its ID."""
    if not service.delete(vehicle_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found",
        )
