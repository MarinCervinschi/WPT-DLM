from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..services import (
    ChargingSessionService,
    DLMService,
    HubService,
    NodeService,
    VehicleService,
)

DBSession = Annotated[Session, Depends(get_db)]


def get_hub_service(db: DBSession) -> HubService:
    """Dependency that provides HubService instance."""
    return HubService(db)


def get_node_service(db: DBSession) -> NodeService:
    """Dependency that provides NodeService instance."""
    return NodeService(db)


def get_vehicle_service(db: DBSession) -> VehicleService:
    """Dependency that provides VehicleService instance."""
    return VehicleService(db)


def get_charging_session_service(db: DBSession) -> ChargingSessionService:
    """Dependency that provides ChargingSessionService instance."""
    return ChargingSessionService(db)


def get_dlm_service(db: DBSession) -> DLMService:
    """Dependency that provides DLMService instance."""
    return DLMService(db)


HubServiceDep = Annotated[HubService, Depends(get_hub_service)]
NodeServiceDep = Annotated[NodeService, Depends(get_node_service)]
VehicleServiceDep = Annotated[VehicleService, Depends(get_vehicle_service)]
ChargingSessionServiceDep = Annotated[
    ChargingSessionService, Depends(get_charging_session_service)
]
DLMServiceDep = Annotated[DLMService, Depends(get_dlm_service)]
