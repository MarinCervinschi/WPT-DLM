from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .enums import ChargingState


class NodeInfo(BaseModel):
    """
    Topic: iot/hubs/<hub_id>/nodes/<node_id>/info (retain=True)
    Published when node is registered or comes online.
    """

    node_id: str = Field(..., max_length=50, description="Unique node identifier")
    hub_id: str = Field(..., max_length=50, description="Parent hub ID")
    name: Optional[str] = Field(default=None, max_length=100, description="Node name")
    max_power_kw: float = Field(..., ge=0, le=350, description="Node max power in kW")


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
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Telemetry timestamp",
    )

    @field_validator("power_kw")
    @classmethod
    def power_must_not_exceed_limit(cls, v: float, info) -> float:
        """Validate that actual power doesn't exceed the limit."""
        if "power_limit_kw" in info.data and v > info.data["power_limit_kw"]:
            raise ValueError("power_kw cannot exceed power_limit_kw")
        return v

    @field_validator("connected_vehicle_id")
    def set_default_if_none(cls, v):
        return v if v is not None else "n/a"
