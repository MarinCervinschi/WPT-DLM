import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.websocket_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])
logger = logging.getLogger(__name__)


@router.websocket("/telemetry/{vehicle_id}")
async def telemetry_websocket(websocket: WebSocket, vehicle_id: str):
    """
    WebSocket endpoint for receiving real-time telemetry data for a specific vehicle.
    
    Args:
        websocket: WebSocket connection
        vehicle_id: ID of the vehicle to receive telemetry for
    """
    await ws_manager.connect(websocket, vehicle_id)
    try:
        # Keep the connection alive and wait for messages
        while True:
            # We don't expect messages from the client, just keep alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, vehicle_id)
        logger.info(f"Client disconnected from vehicle {vehicle_id} telemetry")
    except Exception as e:
        logger.error(f"Error in telemetry websocket for vehicle {vehicle_id}: {e}")
        ws_manager.disconnect(websocket, vehicle_id)
