from fastapi import APIRouter, Depends, HTTPException, status
from brain_api.schemas import ChargingRequestCreate, ChargingRequestResponse
from brain_api.services import ChargingRequestService
from brain_api.api.dependencies import get_db, get_mqtt_service

router = APIRouter()


@router.post(
    "/nodes/{node_id}/charge",
    response_model=ChargingRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request charging session",
    description="Initiates a charging session request by publishing to MQTT topic",
)

async def request_charging(
    node_id: str,
    request_data: ChargingRequestCreate,
    db=Depends(get_db),
    mqtt_service=Depends(get_mqtt_service),
):
    """
    Request a charging session for a vehicle at a specific node.
    
    The QR code scan provides the node ID, and the app provides the vehicle ID.
    This publishes a message to the MQTT topic for the hub to process.
    """
    service = ChargingRequestService(db, mqtt_service)
    return service.request_charging(node_id=node_id, vehicle_id=request_data.vehicle_id)
