from pydantic import BaseModel, Field


class ChargingRequestCreate(BaseModel):
    """Schema for requesting a charging session via QR code."""

    vehicle_id: str = Field(
        ..., min_length=1, max_length=50, description="Vehicle ID from mobile app"
    )


class ChargingRequestResponse(BaseModel):
    """Schema for charging request response."""

    message: str
    node_id: str
    vehicle_id: str
    hub_id: str
