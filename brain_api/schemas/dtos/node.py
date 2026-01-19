"""
Node DTOs - Pydantic schemas for Node entity.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# ==================== Base Schema ====================


class NodeBase(BaseModel):
    """Base schema with common Node fields."""

    max_power_kw: float = Field(
        22.0, gt=0, le=350, description="Maximum power output in kW"
    )


# ==================== Create Schema ====================


class NodeCreate(NodeBase):
    """Schema for creating a new Node."""

    node_id: str = Field(..., min_length=1, max_length=50, description="Unique node ID")
    hub_id: str = Field(..., min_length=1, max_length=50, description="Parent hub ID")
    is_maintenance: bool = Field(False, description="Whether node is in maintenance")


# ==================== Update Schema ====================


class NodeUpdate(BaseModel):
    """Schema for updating a Node. All fields are optional."""

    name: Optional[str] = Field(None, max_length=100)
    max_power_kw: Optional[float] = Field(None, gt=0, le=350)
    is_maintenance: Optional[bool] = None


# ==================== Response Schemas ====================


class NodeResponse(NodeBase):
    """Schema for Node response."""

    model_config = ConfigDict(from_attributes=True)

    node_id: str
    hub_id: str
    is_maintenance: bool


class NodeDetailResponse(NodeResponse):
    """Schema for detailed Node response with session info."""

    active_session_count: int = Field(0, description="Number of active sessions")
    total_sessions: int = Field(0, description="Total number of sessions")
    total_energy_delivered_kwh: float = Field(0.0, description="Total energy delivered")


class NodeListResponse(BaseModel):
    """Schema for paginated Node list response."""

    items: list[NodeResponse]
    total: int
    skip: int
    limit: int
