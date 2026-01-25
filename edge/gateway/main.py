import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.mqtt_dtos import GeoLocation
from shared.policies import PriorityPolicy
from shared.services.mqtt_service import MQTTService
from smart_objects.hub import Hub

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("DLM_Gateway_Hub")

logging.getLogger("iot:actuator:l298n").setLevel(logging.DEBUG)
logging.getLogger("hw_node").setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Gateway Hub")

    loop = asyncio.get_running_loop()

    mqtt_service = MQTTService(
        broker_host="localhost",
        broker_port=1883,
        client_id="DLM_Gateway_Hub",
    )
    mqtt_service.connect()
    await asyncio.sleep(1)

    if not mqtt_service.is_connected:
        logger.error("Failed to connect to MQTT broker. Exiting.")
        raise RuntimeError("MQTT connection failed")

    HUB_ID = "DLM_Gateway_Hub"
    MAX_GRID_CAPACITY_KW = 200.0

    LOCATION = GeoLocation(latitude=44.62958, longitude=10.94864, altitude=50.0)

    hub = Hub(
        hub_id=HUB_ID,
        mqtt_service=mqtt_service,
        location=LOCATION,
        max_grid_capacity_kw=MAX_GRID_CAPACITY_KW,
        firmware_version="1.0.0",
        dlm_interval=5.0,
        dlm_policy=PriorityPolicy(max_grid_capacity_kw=MAX_GRID_CAPACITY_KW),
    )

    hub.add_node(
        node_id="hw_node",
        max_power_kw=110.0,
        simulation=False,
        serial_port="COM7",
    )
    hub.add_node(node_id="node_02", max_power_kw=110.0, simulation=True)
    hub.add_node(node_id="node_03", max_power_kw=110.0, simulation=True)

    hub.start()

    logger.info("Hub started - listening for vehicle requests")
    logger.info(f"Grid capacity: {MAX_GRID_CAPACITY_KW}kW | DLM Policy: Priority")

    app.state.hub = hub
    app.state.mqtt_service = mqtt_service

    yield

    logger.info("Stopping Gateway Hub")
    hub.stop()
    mqtt_service.disconnect()
    logger.info("Gateway Hub stopped")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Gateway Hub is running"}
