import datetime
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


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
    available_capacity: float = Field(
        ..., description="Available grid capacity at trigger time in kW"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp",
    )

    @field_validator("available_capacity")
    def capacity_must_be_non_negative(cls, v: float):
        if v is None or v < 0:
            return 0.0
        return v

    @field_validator("total_grid_load")
    def load_must_be_non_negative(cls, v: float):
        if v is None or v < 0:
            return 0.0
        return v
