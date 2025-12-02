"""
Vehicle DTOs - Pydantic schemas for Vehicle entity.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ==================== Base Schema ====================


class VehicleBase(BaseModel):
    """Base schema with common Vehicle fields."""

    model: Optional[str] = Field(None, max_length=100, description="Vehicle model name")
    manufacturer: Optional[str] = Field(
        None, max_length=100, description="Vehicle manufacturer"
    )
    driver_id: Optional[str] = Field(
        None, max_length=50, description="Driver/owner identifier"
    )


# ==================== Create Schema ====================


class VehicleCreate(VehicleBase):
    """Schema for creating a new Vehicle."""

    vehicle_id: str = Field(
        ..., min_length=1, max_length=50, description="Unique vehicle ID"
    )


# ==================== Update Schema ====================


class VehicleUpdate(BaseModel):
    """Schema for updating a Vehicle. All fields are optional."""

    model: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    driver_id: Optional[str] = Field(None, max_length=50)


# ==================== Response Schemas ====================


class VehicleResponse(VehicleBase):
    """Schema for Vehicle response."""

    model_config = ConfigDict(from_attributes=True)

    vehicle_id: str
    registered_at: datetime


class VehicleDetailResponse(VehicleResponse):
    """Schema for detailed Vehicle response with session stats."""

    total_sessions: int = Field(0, description="Total number of charging sessions")
    total_energy_consumed_kwh: float = Field(
        0.0, description="Total energy consumed"
    )
    last_charging_session: Optional[datetime] = Field(
        None, description="Last charging session start time"
    )


class VehicleListResponse(BaseModel):
    """Schema for paginated Vehicle list response."""

    items: list[VehicleResponse]
    total: int
    skip: int
    limit: int
