from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# ==================== Base Schema ====================


class DLMEventBase(BaseModel):
    """Base schema with common DLMEvent fields."""

    hub_id: str = Field(..., min_length=1, max_length=50, description="Hub ID")
    node_id: str = Field(..., min_length=1, max_length=50, description="Node ID")
    trigger_reason: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Trigger reason (e.g., GRID_OVERLOAD)",
    )
    total_grid_load_kw: float = Field(..., ge=0, description="Total grid load in kW")
    original_limit_kw: float = Field(
        ..., ge=0, description="Original power limit in kW"
    )
    new_limit_kw: float = Field(..., ge=0, description="New power limit in kW")


# ==================== Create Schema ====================


class DLMEventCreate(DLMEventBase):
    """Schema for creating a new DLMEvent."""

    available_capacity_at_trigger: Optional[float] = Field(
        None, ge=0, description="Available capacity at trigger time"
    )


class DLMEventLog(BaseModel):
    """Schema for logging a DLM event (simplified)."""

    hub_id: str = Field(..., min_length=1, max_length=50)
    node_id: str = Field(..., min_length=1, max_length=50)
    trigger_reason: str = Field(..., min_length=1, max_length=50)
    total_grid_load_kw: float = Field(..., ge=0)
    original_limit_kw: float = Field(..., ge=0)
    new_limit_kw: float = Field(..., ge=0)
    available_capacity_at_trigger: Optional[float] = Field(None, ge=0)


# ==================== Response Schemas ====================


class DLMEventResponse(DLMEventBase):
    """Schema for DLMEvent response."""

    model_config = ConfigDict(from_attributes=True)

    dlm_event_id: int
    timestamp: datetime
    available_capacity_at_trigger: Optional[float] = None


class DLMEventDetailResponse(DLMEventResponse):
    """Schema for detailed DLMEvent response."""

    limit_change_kw: float = Field(description="Power limit change (+ = increase)")


class DLMEventListResponse(BaseModel):
    """Schema for paginated DLMEvent list response."""

    items: list[DLMEventResponse]
    total: int
    skip: int
    limit: int


class DLMEventStats(BaseModel):
    """Schema for DLM event statistics."""

    total_events: int
    events_by_reason: dict[str, int] = Field(
        default_factory=dict, description="Event counts by trigger reason"
    )
    avg_limit_change_kw: Optional[float] = None
    time_range_hours: int = Field(24, description="Time range for statistics")


# ==================== Trigger Reasons ====================


class DLMTriggerReason:
    """Constants for DLM trigger reasons."""

    GRID_OVERLOAD = "GRID_OVERLOAD"
    PRIORITY_SHIFT = "PRIORITY_SHIFT"
    SCHEDULE = "SCHEDULE"
    MANUAL = "MANUAL"
    EMERGENCY = "EMERGENCY"
    REBALANCE = "REBALANCE"
