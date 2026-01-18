from typing import ClassVar, List
from smart_objects.models import Actuator


class L298NActuator(Actuator):
    RESOURCE_TYPE = "iot:actuator:l298n"
    VALID_STATUSES: ClassVar[List[str]] = ["ON", "OFF"]
    PWM_LEVELS: ClassVar[tuple[float, float]] = (0.0, 255.0)

    def __init__(self, simulation: bool = False):
        super().__init__(type=self.RESOURCE_TYPE)

        self.state = {
            "status": "OFF",
            "pwm_level": 0.0,
        }

        self.simulation = simulation

    def apply_command(self, command: dict) -> None:
        if self.simulation:
            new_status = command.get("status", self.state["status"])
            new_pwm_level = command.get("pwm_level", self.state["pwm_level"])

            if new_status in self.VALID_STATUSES:
                self.state["status"] = new_status

            if (
                isinstance(new_pwm_level, (int, float))
                and self.PWM_LEVELS[0] <= new_pwm_level <= self.PWM_LEVELS[1]
            ):
                self.state["pwm_level"] = new_pwm_level

            self.logger.info(
                f"Simulated L298N Actuator command applied: status={self.state['status']}, pwm_level={self.state['pwm_level']}"
            )
        else:
            # TODO: Implement actual L298N hardware command application logic here
            pass

    def get_current_state(self) -> dict:
        return self.state.copy()

    def reset(self) -> None:
        self.state = {
            "status": "OFF",
            "pwm_level": 0.0,
        }
        self.logger.info("L298N Actuator state has been reset to default values.")

    def __str__(self) -> str:
        return (
            f"L298NActuator(status={self.state['status']}, "
            f"pwm_level={self.state['pwm_level']}, simulation={self.simulation})"
        )
