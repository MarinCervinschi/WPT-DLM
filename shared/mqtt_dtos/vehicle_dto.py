from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from .enums import GeoLocation


class VehicleTelemetry(BaseModel):
    """
    Topic: iot/vehicles/+/telemetry
    """

    geo_location: GeoLocation = Field(..., description="Vehicle GPS location")
    battery_level: int = Field(
        ..., ge=0, le=100, description="Battery state of charge (%)"
    )
    speed_kmh: Optional[float] = Field(
        default=None, ge=0, le=300, description="Vehicle speed in km/h"
    )
    engine_temp_c: Optional[float] = Field(
        default=None, ge=-40, le=150, description="Engine temperature in Celsius"
    )
    is_charging: bool = Field(..., description="Whether currently charging")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Telemetry timestamp",
    )


class VehicleRequest(BaseModel):
    """
    Vehicle charging request message.
    Sent by Brain API to Hub via MQTT.
    Topic: iot/hubs/+/requests
    """

    vehicle_id: str = Field(
        ..., min_length=1, max_length=50, description="Vehicle identifier"
    )
    node_id: str = Field(
        ..., min_length=1, max_length=50, description="Target node identifier"
    )
    soc_percent: int = Field(
        ..., ge=0, le=100, description="Current state of charge percentage"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Request timestamp",
    )
