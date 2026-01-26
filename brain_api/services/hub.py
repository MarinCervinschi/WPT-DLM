from ..models import HubDbo
from ..repositories import HubRepository
from ..schemas import HubCreate, HubListResponse, HubResponse, HubUpdate
from .base import BaseService


class HubService(
    BaseService[
        HubDbo,
        HubRepository,
        HubCreate,
        HubUpdate,
        HubResponse,
        HubListResponse,
    ]
):
    """Service layer for Hub operations."""

    repository_class = HubRepository
    response_schema = HubResponse
    list_response_schema = HubListResponse

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> HubListResponse:
        """List hubs with pagination, optionally filtering active only."""
        if active_only:
            hubs = self.repo.get_active_hubs()
            total = len(list(hubs))
        else:
            hubs = self.repo.get_all(skip=skip, limit=limit)
            total = self.repo.count()

        return HubListResponse(
            items=[HubResponse.model_validate(h) for h in hubs],
            total=total,
            skip=skip,
            limit=limit,
        )

    def activate(self, hub_id: str) -> HubResponse:
        """Activate a hub."""
        hub = self.repo.set_active(hub_id, True)
        self.db.commit()
        return HubResponse.model_validate(hub)

    def deactivate(self, hub_id: str) -> HubResponse:
        """Deactivate a hub."""
        hub = self.repo.set_active(hub_id, False)
        self.db.commit()
        return HubResponse.model_validate(hub)
