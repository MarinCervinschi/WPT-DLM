from dataclasses import Field
from enum import Enum

from pydantic import BaseModel, Field


class ConnectionState(str, Enum):
    """Device connection state."""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class ChargingState(str, Enum):
    """Charging point state."""

    IDLE = "idle"
    CHARGING = "charging"
    FULL = "full"
    FAULTED = "faulted"


class GeoLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    altitude: float = Field(
        default=0.0, ge=-500, le=10000, description="Altitude in meters"
    )
