from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .enums import ChargingState, ConnectionState


class GeoLocation(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    alt: float = Field(default=0.0, ge=-500, le=10000, description="Altitude in meters")


class NodeTelemetry(BaseModel):
    """
    Topic: iot/hubs/+/nodes/+/telemetry
    """

    voltage: float = Field(..., ge=0, le=1000, description="Voltage in Volts")
    current: float = Field(..., ge=0, le=500, description="Current in Amps")
    power_kw: float = Field(
        ..., ge=0, le=350, description="Actual power consumption in kW"
    )
    power_limit_kw: float = Field(
        ..., ge=0, le=350, description="DLM enforced limit in kW"
    )
    is_occupied: bool = Field(..., description="Whether a vehicle is connected")

    connected_vehicle_id: Optional[str] = Field(
        default=None, max_length=50, description="ID of connected vehicle"
    )
    current_vehicle_soc: Optional[int] = Field(
        default=None, ge=0, le=100, description="Vehicle state of charge (%)"
    )

    @field_validator("power_kw")
    @classmethod
    def power_must_not_exceed_limit(cls, v: float, info) -> float:
        """Validate that actual power doesn't exceed the limit."""
        if "power_limit_kw" in info.data and v > info.data["power_limit_kw"]:
            raise ValueError("power_kw cannot exceed power_limit_kw")
        return v


class VehicleTelemetry(BaseModel):
    """
    Topic: iot/vehicles/+/telemetry
    """

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    alt: float = Field(default=0.0, ge=-500, le=10000, description="Altitude in meters")
    battery_level: int = Field(
        ..., ge=0, le=100, description="Battery state of charge (%)"
    )
    is_charging: bool = Field(..., description="Whether currently charging")


class NodeStatus(BaseModel):
    """
    Topic: iot/hubs/+/nodes/+/status
    """

    state: ChargingState = Field(..., description="Current charging state")
    error_code: int = Field(
        default=0, ge=0, le=9999, description="Error code (0 = no error)"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Status timestamp",
    )


class HubStatus(BaseModel):
    """
    Topic: iot/hubs/+/status
    """

    state: ConnectionState = Field(..., description="Hub connection state")
    ip_address: str = Field(
        ..., min_length=7, max_length=45, description="Hub IP address"
    )
    cpu_temp: float = Field(..., ge=-40, le=125, description="CPU temperature in °C")

    @field_validator("ip_address")
    @classmethod
    def validate_ip_format(cls, v: str) -> str:
        """Basic IP address format validation."""
        import ipaddress

        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("Invalid IP address format")
        return v


class DLMNotification(BaseModel):
    """
    Topic: iot/hubs/+/dlm/events
    """

    trigger_reason: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Reason for DLM action (e.g., GRID_OVERLOAD)",
    )
    original_limit: float = Field(
        ..., ge=0, le=350, description="Previous power limit in kW"
    )
    new_limit: float = Field(..., ge=0, le=350, description="New power limit in kW")
    affected_node_id: str = Field(..., max_length=50, description="ID of affected node")
    total_grid_load: float = Field(
        ..., ge=0, description="Total grid load at trigger time in kW"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp",
    )
