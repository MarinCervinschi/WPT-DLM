from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request schema for charging recommendations."""

    latitude: float = Field(..., ge=-90, le=90, description="Vehicle latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Vehicle longitude")
    battery_level: int = Field(
        ..., ge=0, le=100, description="Current battery level (%)"
    )


class RecommendationResponse(BaseModel):
    """Response schema for charging recommendations."""

    hub_id: str = Field(..., description="Recommended hub ID")
    node_id: str = Field(..., description="Recommended node ID")
    hub_latitude: float = Field(..., description="Hub latitude")
    hub_longitude: float = Field(..., description="Hub longitude")
    distance_km: float = Field(..., description="Distance from vehicle to hub in km")
    estimated_wait_time_min: int = Field(
        ..., description="Estimated wait time in minutes"
    )
    available_power_kw: float = Field(..., description="Available charging power in kW")
