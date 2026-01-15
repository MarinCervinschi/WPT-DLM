import logging

from fastapi import APIRouter

from ..core.config import settings
from ..db import check_db_health
from ..schemas import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and its dependencies",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint that verifies API and database connectivity.

    Returns:
        HealthResponse: Health status of the service and dependencies
    """
    db_health = check_db_health()

    all_healthy = db_health["status"] == "healthy"
    overall_status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        service=settings.PROJECT_NAME,
        dependencies={
            "database": db_health["status"],
        },
    )
