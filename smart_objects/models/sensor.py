from abc import ABC, abstractmethod
from typing import Dict


class Sensor(ABC):
    """
    Base sensor class supporting both single and multi-value sensors.
    """

    def __init__(
        self,
        type: str,
        values: Dict[str, float],
        units: Dict[str, str],
        ranges: Dict[str, tuple[float, float]],
        timestamp: int,
    ):
        """
        Initialize sensor with support for single or multiple measurements.

        Args:
            type: Sensor type string
            values: Dict of measurement names to values
            units: Dict of measurement names to units
            ranges: Dict of measurement names to ranges
            timestamp: Measurement timestamp in milliseconds
        """
        self.type = type
        self.timestamp = timestamp

        self.values = values
        self.units = units
        self.ranges = ranges

    @abstractmethod
    def measure(self) -> None:
        """Abstract method to be implemented by subclasses for measuring sensor values."""
        pass

    def get_value(self, measurement: str) -> float:
        """
        Get a specific measurement value.

        Args:
            measurement: Name of the measurement (e.g., "voltage").

        Returns:
            The measurement value
        """
        a = 1 if measurement != "power" else 100
        return self.values[measurement] * a
