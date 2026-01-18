import logging
from abc import ABC, abstractmethod
from typing import Any, Dict


class Actuator(ABC):

    def __init__(self, type: str) -> None:

        self.type = type
        self.state: Dict[str, Any] = {}

        self.logger = logging.getLogger(f"{type}")

    @abstractmethod
    def apply_command(self, command: Dict[str, Any]) -> None:
        """
        Apply the command to the actuator.
        This method should be implemented by subclasses to handle specific command logic.

        Args:
            command: Dictionary containing the command parameters

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_current_state(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass