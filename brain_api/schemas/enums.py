from enum import Enum


class ConnectionState(str, Enum):
    """Device connection state."""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class ChargingState(str, Enum):
    """Charging point state."""

    IDLE = "idle"
    CHARGING = "charging"
    OCCUPIED = "occupied"
    FAULTED = "faulted"
