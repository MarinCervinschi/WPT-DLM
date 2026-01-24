from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..services import (
    ChargingSessionService,
    DLMService,
    HubService,
    NodeService,
    RecommendationService,
    VehicleService,
)
from ..services.influxdb_service import InfluxDBService

DBSession = Annotated[Session, Depends(get_db)]


_mqtt_service = None
_influx_service = None

def get_mqtt_service():
    """Dependency that provides MQTT service instance."""
    global _mqtt_service
    if _mqtt_service is None:
        raise RuntimeError("MQTT service not initialized")
    return _mqtt_service


def set_mqtt_service(mqtt_service):
    """Set the global MQTT service instance."""
    global _mqtt_service
    _mqtt_service = mqtt_service


def get_influx_service() -> InfluxDBService:
    """Dependency that provides InfluxDB service instance."""
    global _influx_service
    if _influx_service is None:
        _influx_service = InfluxDBService()
    return _influx_service


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


def get_recommendation_service(
    db: DBSession, influx: InfluxDBService = Depends(get_influx_service)
) -> RecommendationService:
    """Dependency that provides RecommendationService instance."""
    return RecommendationService(db, influx)


HubServiceDep = Annotated[HubService, Depends(get_hub_service)]
NodeServiceDep = Annotated[NodeService, Depends(get_node_service)]
VehicleServiceDep = Annotated[VehicleService, Depends(get_vehicle_service)]
ChargingSessionServiceDep = Annotated[
    ChargingSessionService, Depends(get_charging_session_service)
]
DLMServiceDep = Annotated[DLMService, Depends(get_dlm_service)]
RecommendationServiceDep = Annotated[
    RecommendationService, Depends(get_recommendation_service)
]
