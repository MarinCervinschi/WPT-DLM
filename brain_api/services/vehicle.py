from ..models import VehicleDbo
from ..repositories import VehicleRepository
from ..schemas import VehicleCreate, VehicleListResponse, VehicleResponse, VehicleUpdate
from .base import BaseService


class VehicleService(
    BaseService[
        VehicleDbo,
        VehicleRepository,
        VehicleCreate,
        VehicleUpdate,
        VehicleResponse,
        VehicleListResponse,
    ]
):
    """Service layer for Vehicle operations."""

    repository_class = VehicleRepository
    response_schema = VehicleResponse
    list_response_schema = VehicleListResponse

    def get_or_create(self, vehicle_id: str, data: VehicleCreate) -> VehicleResponse:
        """Get or create a vehicle (auto-registration)."""
        vehicle, created = self.repo.get_or_create(vehicle_id, defaults=data.model_dump())
        if created:
            self.db.commit()
        return VehicleResponse.model_validate(vehicle)
