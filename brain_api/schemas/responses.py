from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(..., description="API version")
    service: str = Field(..., description="Service name")
    dependencies: Optional[Dict[str, str]] = Field(
        None, description="Dependency statuses"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
