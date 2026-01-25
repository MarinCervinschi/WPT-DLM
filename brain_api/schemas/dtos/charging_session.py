from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# ==================== Base Schema ====================


class ChargingSessionBase(BaseModel):
    """Base schema with common ChargingSession fields."""

    node_id: str = Field(..., min_length=1, max_length=50, description="Node ID")
    vehicle_id: Optional[str] = Field(
        ..., max_length=50, description="Vehicle ID (optional)"
    )


# ==================== Create Schema ====================


class ChargingSessionCreate(ChargingSessionBase):
    """Schema for creating a new ChargingSession."""

    pass


class ChargingSessionStart(BaseModel):
    """Schema for starting a charging session."""

    node_id: str = Field(..., min_length=1, max_length=50, description="Node ID")
    vehicle_id: Optional[str] = Field(..., max_length=50, description="Vehicle ID")


# ==================== Update Schema ====================


class ChargingSessionUpdate(BaseModel):
    """Schema for updating a ChargingSession. All fields are optional."""

    vehicle_id: Optional[str] = Field(None, max_length=50)
    total_energy_kwh: Optional[float] = Field(None, ge=0)
    avg_power_kw: Optional[float] = Field(None, ge=0)


class ChargingSessionEnd(BaseModel):
    """Schema for ending a charging session."""

    total_energy_kwh: float = Field(..., ge=0, description="Total energy delivered")
    avg_power_kw: float = Field(..., ge=0, description="Average power during session")


# ==================== Response Schemas ====================


class ChargingSessionResponse(ChargingSessionBase):
    """Schema for ChargingSession response."""

    model_config = ConfigDict(from_attributes=True)

    charging_session_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_energy_kwh: float
    avg_power_kw: float


class ChargingSessionDetailResponse(ChargingSessionResponse):
    """Schema for detailed ChargingSession response."""

    is_active: bool = Field(description="Whether session is ongoing")
    duration_minutes: Optional[float] = Field(
        None, description="Session duration in minutes"
    )


class ChargingSessionListResponse(BaseModel):
    """Schema for paginated ChargingSession list response."""

    items: list[ChargingSessionResponse]
    total: int
    skip: int
    limit: int


class ChargingSessionStats(BaseModel):
    """Schema for charging session statistics."""

    total_sessions: int
    active_sessions: int
    total_energy_kwh: float
    avg_session_duration_minutes: Optional[float] = None
