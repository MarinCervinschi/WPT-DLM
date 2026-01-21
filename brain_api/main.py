import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import charging_request, dlm, health, hubs, nodes, sessions, vehicles
from .api import dependencies
from .core.config import settings
from .core.logging import setup_logging
from .db import init_db
from .schemas import ErrorResponse
from shared.services import MQTTService

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")

    mqtt_service = MQTTService(
        broker_host=settings.MQTT_BROKER_HOST,
        broker_port=settings.MQTT_BROKER_PORT,
        client_id="brain_api",
    )
    mqtt_service.connect()
    
    dependencies.set_mqtt_service(mqtt_service)
    logger.info("MQTT service initialized successfully")

    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    # Cleanup
    mqtt_service.disconnect()
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error", detail=str(exc.errors()), code="VALIDATION_ERROR"
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error", detail=str(exc), code="INTERNAL_ERROR"
        ).model_dump(),
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(hubs.router, tags=["Hubs"])
app.include_router(nodes.router, tags=["Nodes"])
app.include_router(vehicles.router, tags=["Vehicles"])
app.include_router(sessions.router, tags=["Charging Sessions"])
app.include_router(dlm.router, tags=["Dynamic Load Management"])
app.include_router(charging_request.router, tags=["Charging Requests"])


@app.get("/", summary="Root Endpoint", description="Get basic API information")
async def root() -> dict:
    """
    Root endpoint providing basic API information.

    Returns:
        dict: API information and documentation links
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }
