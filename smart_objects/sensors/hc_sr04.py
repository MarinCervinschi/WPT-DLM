import random
import time
from typing import Optional

from edge.gateway.bridge.serial_bridge import ArduinoSerialBridge
from smart_objects.models import Sensor


class HC_SR04(Sensor):

    RESOURCE_TYPE = "iot:sensor:hc_sr04"
    UNIT_DISTANCE = "cm"
    DATA_TYPE = float
    MEASUREMENT_PRECISION = 2

    def __init__(
        self, bridge: Optional[ArduinoSerialBridge] = None, simulation: bool = False
    ):
        super().__init__(
            type=self.RESOURCE_TYPE,
            values={
                "distance": 0.0,
            },
            units={
                "distance": self.UNIT_DISTANCE,
            },
            ranges={
                "distance": (2.0, 400.0),
            },
            timestamp=0,
        )
        self.bridge = bridge
        self.simulation = simulation

    def measure(self) -> None:
        if self.simulation:
            distance = random.uniform(2.0, 50.0)
            self.simulate_measurement(distance)
        else:
            if self.bridge:
                try:
                    distance = self.bridge.get_distance()
                    self.values.update(distance=distance)
                    self.timestamp = int(time.time() * 1000)
                except Exception as e:
                    raise RuntimeError(f"Failed to read distance from HC-SR04: {e}")

    def simulate_measurement(self, distance: float) -> None:
        self.values.update(
            {
                "distance": round(distance, self.MEASUREMENT_PRECISION),
            }
        )

        self.timestamp = int(time.time() * 1000)  # Current time in milliseconds

    def __str__(self) -> str:
        return (
            f"HC_SR04Sensor(distance={self.values['distance']} {self.UNIT_DISTANCE}, "
            f"timestamp={self.timestamp}, simulation={self.simulation})"
        )
