from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# ==================== Base Schema ====================


class HubBase(BaseModel):
    """Base schema with common Hub fields."""

    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    alt: Optional[float] = Field(
        0.0, ge=-500, le=10000, description="Altitude in meters"
    )
    max_grid_capacity_kw: float = Field(
        100.0, gt=0, description="Maximum grid capacity in kW"
    )


# ==================== Create Schema ====================


class HubCreate(HubBase):
    """Schema for creating a new Hub."""

    hub_id: str = Field(..., min_length=1, max_length=50, description="Unique hub ID")
    is_active: bool = Field(True, description="Whether the hub is active")
    ip_address: str = Field(
        ..., min_length=7, max_length=45, description="Hub IP address"
    )
    firmware_version: str = Field(..., max_length=20, description="Firmware version")


# ==================== Update Schema ====================


class HubUpdate(BaseModel):
    """Schema for updating a Hub. All fields are optional."""

    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    alt: Optional[float] = Field(None, ge=-500, le=10000)
    max_grid_capacity_kw: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    ip_address: Optional[str] = Field(None, min_length=7, max_length=45)
    firmware_version: Optional[str] = Field(None, max_length=20)


# ==================== Response Schemas ====================


class HubResponse(HubBase):
    """Schema for Hub response."""

    model_config = ConfigDict(from_attributes=True)

    hub_id: str
    is_active: bool
    last_seen: Optional[datetime] = None


class HubDetailResponse(HubResponse):
    """Schema for detailed Hub response with node count."""

    node_count: int = Field(0, description="Number of nodes in this hub")
    total_node_power_kw: float = Field(
        0.0, description="Total power capacity of all nodes"
    )


class HubListResponse(BaseModel):
    """Schema for paginated Hub list response."""

    items: list[HubResponse]
    total: int
    skip: int
    limit: int
