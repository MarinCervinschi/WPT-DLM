import uvicorn
from shared.simulation.static_vehicle import run_static_vehicle
import threading


def start_vehicle_thread():
    """Start the static vehicle in a separate thread."""
    vehicle_thread = threading.Thread(target=run_static_vehicle, daemon=True)
    vehicle_thread.start()
    return vehicle_thread


if __name__ == "__main__":
    vehicle_thread = start_vehicle_thread()

    uvicorn.run(
        "edge.gateway.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info",
    )
