from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

from .enums import ConnectionState, GeoLocation


class HubInfo(BaseModel):
    """
    Topic: iot/hubs/<hub_id>/info (retain=True)
    Published when hub comes online for the first time or restarts.
    """

    hub_id: str = Field(..., max_length=50, description="Unique hub identifier")
    location: GeoLocation = Field(..., description="Hub physical location")
    max_grid_capacity_kw: float = Field(
        ..., ge=0, le=1000, description="Hub grid capacity in kW"
    )
    ip_address: str = Field(
        ..., min_length=7, max_length=45, description="Hub IP address"
    )
    firmware_version: str = Field(..., max_length=20, description="Firmware version")

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


class HubStatus(BaseModel):
    """
    Topic: iot/hubs/+/status
    """

    state: ConnectionState = Field(..., description="Hub connection state")
    cpu_temp: float = Field(..., ge=-40, le=125, description="CPU temperature in °C")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Status timestamp",
    )
