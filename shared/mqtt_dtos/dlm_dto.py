import datetime
from datetime import datetime, timezone

from pydantic import BaseModel, Field


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
