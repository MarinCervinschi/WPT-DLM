import asyncio
import logging
from contextlib import asynccontextmanager
import json

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import charging_request, dlm, health, hubs, nodes, sessions, vehicles, ws_telemetry
from .api import dependencies
from .core.config import settings
from .core.logging import setup_logging
from .core.websocket_manager import ws_manager
from .data_collector import MQTTDataCollector
from .db import init_db
from .db.session import SessionLocal
from .schemas import ErrorResponse
from shared.services import MQTTService
from shared.mqtt_dtos import VehicleTelemetry

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    loop = asyncio.get_running_loop()

    mqtt_service = MQTTService(
        broker_host=settings.MQTT_BROKER_HOST,
        broker_port=settings.MQTT_BROKER_PORT,
        client_id="brain_api",
    )
    mqtt_service.connect()
    
    # Subscribe to vehicle telemetry topic
    def on_telemetry_message(msg):
        """Callback per messaggi di telemetria dai veicoli."""
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 4 and topic_parts[0] == 'iot' and topic_parts[1] == 'vehicles' and topic_parts[3] == 'telemetry':
                vehicle_id = topic_parts[2]
                payload = json.loads(msg.payload.decode())
                
                telemetry = VehicleTelemetry(**payload)
                data_to_send = telemetry.model_dump(mode='json')

                # 2. USA call_soon_threadsafe per pianificare la coroutine nel loop di FastAPI
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        ws_manager.send_to_vehicle_clients(vehicle_id, data_to_send)
                    )
                )
                
                logger.debug(f"Telemetry forwarded for vehicle {vehicle_id}")
        except Exception as e:
            # Importante: usa loop.call_soon_threadsafe anche per i log se necessario, 
            # ma il logger standard di python di solito è thread-safe.
            logger.error(f"Error processing telemetry message: {e}")
    
    mqtt_service.subscribe("iot/vehicles/+/telemetry", on_telemetry_message, qos=0)
    
    dependencies.set_mqtt_service(mqtt_service)
    logger.info("MQTT service initialized successfully")

    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Initialize and start MQTT Data Collector
    db = SessionLocal()
    try:
        data_collector = MQTTDataCollector(mqtt_service, db)
        data_collector.subscribe()
        logger.info("MQTT Data Collector initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MQTT Data Collector: {e}")
        db.close()
        raise

    yield

    # Stop data collector
    try:
        data_collector.unsubscribe()
    except Exception as e:
        logger.error(f"Error stopping data collector: {e}")
    finally:
        db.close()
    
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
app.include_router(ws_telemetry.router, tags=["WebSocket Telemetry"])


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
