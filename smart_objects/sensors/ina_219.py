import random
import time
from typing import Optional

from edge.gateway.bridge.serial_bridge import ArduinoSerialBridge
from smart_objects.models import Sensor


class INA219Sensor(Sensor):
    RESOURCE_TYPE = "iot:sensor:ina_219"
    UNIT_VOLTAGE = "V"
    UNIT_CURRENT = "A"
    UNIT_POWER = "W"
    DATA_TYPE = float
    MEASUREMENT_PRECISION = 3

    def __init__(
        self, bridge: Optional[ArduinoSerialBridge] = None, simulation: bool = False
    ):
        super().__init__(
            type=self.RESOURCE_TYPE,
            values={
                "voltage": 0.0,
                "current": 0.0,
                "power": 0.0,
            },
            units={
                "voltage": self.UNIT_VOLTAGE,
                "current": self.UNIT_CURRENT,
                "power": self.UNIT_POWER,
            },
            ranges={
                "voltage": (0.0, 26.0),
                "current": (0.0, 3.2),
                "power": (0.0, 78.4),
            },
            timestamp=0,
        )

        self.simulation = simulation
        self.bridge = bridge

    def measure(self) -> None:
        if self.simulation:
            voltage = random.uniform(0.0, 26.0)
            current = random.uniform(0.0, 3.2)
            self.simulate_measurement(voltage, current)
        else:
            if self.bridge:
                try:
                    v, i, p = self.bridge.get_power_data()
                    self.values.update(voltage=v, current=i, power=p)
                    self.timestamp = int(time.time() * 1000)
                except Exception as e:
                    raise RuntimeError(f"Failed to read power data from INA219: {e}")

    def simulate_measurement(self, voltage: float, current: float) -> None:
        power = voltage * current

        self.values.update(
            {
                "voltage": round(voltage, self.MEASUREMENT_PRECISION),
                "current": round(current, self.MEASUREMENT_PRECISION),
                "power": round(power, self.MEASUREMENT_PRECISION),
            }
        )

        self.timestamp = int(time.time() * 1000)  # Current time in milliseconds

    def __str__(self) -> str:
        return (
            f"INA219Sensor(voltage={self.values['voltage']} {self.UNIT_VOLTAGE}, "
            f"current={self.values['current']} {self.UNIT_CURRENT}, "
            f"power={self.values['power']} {self.UNIT_POWER}, "
            f"timestamp={self.timestamp}, "
            f"simulation={self.simulation}"
        )
