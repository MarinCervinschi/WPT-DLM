import threading
import time
from typing import Optional

from pydantic import BaseModel

from shared.mqtt_dtos.enums import ChargingState
from shared.mqtt_dtos.node_dto import NodeInfo, NodeStatus, NodeTelemetry
from smart_objects.actuators.l298n import L298NActuator
from smart_objects.sensors.hc_sr04 import HC_SR04
from smart_objects.sensors.ina_219 import INA219Sensor

from .smart_object_resource import SmartObjectResource


class Node(SmartObjectResource):
    """
    Node smart object resource representing a charging point within a hub.

    The Hub (SmartObject) contains multiple Node resources.
    Publishing is handled by listeners registered in the Hub.

    Components:
    - INA219 sensor: measures voltage, current, power
    - HC-SR04 sensor: detects vehicle presence (distance)
    - L298N actuator: controls charging on/off and PWM level
    """

    # Distance threshold for vehicle detection (cm)
    VEHICLE_DETECTION_THRESHOLD = 50.0  # Vehicle present if distance < 50cm

    def __init__(
        self,
        node_id: str,
        hub_id: str,
        max_power_kw: float = 22.0,
        simulation: bool = True,
    ):
        super().__init__(resource_id=node_id)
        self.node_id = node_id
        self.hub_id = hub_id
        self.max_power_kw = max_power_kw

        # Sensors and actuators
        self.power_sensor = INA219Sensor(simulation=simulation)
        self.distance_sensor = HC_SR04(simulation=simulation)
        self.charging_actuator = L298NActuator(simulation=simulation)

        # Current state
        self.current_state: ChargingState = ChargingState.IDLE
        self.error_code: int = 0

        # Additional telemetry data
        self.power_limit_kw: float = max_power_kw
        self.is_occupied: bool = False
        self.connected_vehicle_id: Optional[str] = None
        self.current_vehicle_soc: Optional[int] = None

        # Periodic update control
        self._telemetry_thread: Optional[threading.Thread] = None
        self._stop_telemetry = threading.Event()
        self._telemetry_interval: float = 2.0  # seconds

    def set_state(self, new_state: ChargingState, error_code: int = 0) -> None:
        """
        Update node state and notify listeners (which will publish status).
        Also controls the charging actuator.

        Args:
            new_state: New charging state
            error_code: Error code (0 = no error)
        """
        if self.current_state != new_state or self.error_code != error_code:
            old_state = self.current_state
            self.current_state = new_state
            self.error_code = error_code

            self.logger.info(f"🔄 State change: {old_state.value} → {new_state.value}")

            # Control actuator based on state
            if new_state == ChargingState.CHARGING:
                self._start_charging()
            elif new_state in (
                ChargingState.IDLE,
                ChargingState.FULL,
                ChargingState.FAULTED,
            ):
                self._stop_charging()

            # Notify listeners (they will call get_status() and publish)
            self.notify_update(updated_value=self.get_status())

    def _start_charging(self) -> None:
        """Start charging by activating the actuator."""
        command = {"status": "ON", "pwm_level": 255.0}  # Full power
        self.charging_actuator.apply_command(command)
        self.logger.info("⚡ Charging started (actuator ON)")

    def _stop_charging(self) -> None:
        """Stop charging by deactivating the actuator."""
        command = {"status": "OFF", "pwm_level": 0.0}
        self.charging_actuator.apply_command(command)
        self.logger.info("🔌 Charging stopped (actuator OFF)")

    def set_power_limit(self, limit_kw: float) -> None:
        """
        Set DLM power limit and adjust actuator PWM accordingly.

        Args:
            limit_kw: New power limit in kW
        """
        self.power_limit_kw = limit_kw

        if self.current_state == ChargingState.CHARGING:
            # Calculate PWM level based on power limit
            pwm_ratio = min(limit_kw / self.max_power_kw, 1.0)
            pwm_level = pwm_ratio * 255.0

            command = {"status": "ON", "pwm_level": pwm_level}
            self.charging_actuator.apply_command(command)
            self.logger.info(
                f"⚙️ DLM limit set to {limit_kw:.2f}kW (PWM: {pwm_level:.0f})"
            )

    def measure_sensors(self) -> None:
        """Read all sensor values and update telemetry."""
        # Measure power sensor (INA219)
        self.power_sensor.measure()

        # Measure distance sensor (HC-SR04)
        self.distance_sensor.measure()
        distance = self.distance_sensor.get_value("distance")

        # Detect vehicle presence based on distance
        self.is_occupied = distance < self.VEHICLE_DETECTION_THRESHOLD

        # Sensor values are in Watts, convert to kW
        power_w = self.power_sensor.get_value("power")
        self.logger.debug(
            f"📊 Sensor readings: "
            f"V={self.power_sensor.get_value('voltage'):.2f}V, "
            f"I={self.power_sensor.get_value('current'):.3f}A, "
            f"P={power_w:.2f}W, "
            f"Distance={distance:.1f}cm, "
            f"Occupied={self.is_occupied}"
        )

    def update_vehicle_info(
        self,
        is_occupied: bool,
        connected_vehicle_id: Optional[str] = None,
        current_vehicle_soc: Optional[int] = None,
    ) -> None:
        """
        Update vehicle connection information.

        Args:
            is_occupied: Whether a vehicle is connected
            connected_vehicle_id: ID of connected vehicle
            current_vehicle_soc: Vehicle state of charge %
        """
        self.is_occupied = is_occupied
        self.connected_vehicle_id = connected_vehicle_id
        self.current_vehicle_soc = current_vehicle_soc

    def get_info(self) -> NodeInfo:
        """Get info message DTO (for retained info messages)."""
        return NodeInfo(
            node_id=self.node_id,
            hub_id=self.hub_id,
            max_power_kw=self.max_power_kw,
        )

    def get_status(self) -> NodeStatus:
        """Get status message DTO (for state change messages)."""
        return NodeStatus(state=self.current_state, error_code=self.error_code)

    def get_telemetry(self) -> NodeTelemetry:
        """Get telemetry message DTO (for periodic measurements)."""
        return NodeTelemetry(
            voltage=self.power_sensor.get_value("voltage"),
            current=self.power_sensor.get_value("current"),
            power_kw=self.power_sensor.get_value("power") / 1000.0,  # W to kW
            power_limit_kw=self.power_limit_kw,
            is_occupied=self.is_occupied,
            connected_vehicle_id=self.connected_vehicle_id,
            current_vehicle_soc=self.current_vehicle_soc,
        )

    def _telemetry_loop(self) -> None:
        """Background thread for periodic telemetry updates."""
        while not self._stop_telemetry.is_set():
            try:
                # Measure sensors first
                self.measure_sensors()

                # Then notify listeners with updated telemetry
                self.notify_update(
                    updated_value=self.get_telemetry(), message_type="telemetry"
                )
            except Exception as e:
                self.logger.error(f"Error in telemetry loop: {e}")

            self._stop_telemetry.wait(self._telemetry_interval)

    def start_periodic_event_update_task(self) -> None:
        """Start periodic telemetry updates."""
        if self._telemetry_thread is None or not self._telemetry_thread.is_alive():
            self._stop_telemetry.clear()
            self._telemetry_thread = threading.Thread(
                target=self._telemetry_loop,
                daemon=True,
                name=f"NodeTelemetry-{self.node_id}",
            )
            self._telemetry_thread.start()
            self.logger.info(
                f"🟢 Started telemetry updates (every {self._telemetry_interval}s)"
            )

    def stop_periodic_event_update_task(self) -> None:
        """Stop periodic telemetry updates."""
        if self._telemetry_thread and self._telemetry_thread.is_alive():
            self._stop_telemetry.set()
            self._telemetry_thread.join(timeout=5)
            self.logger.info("🔴 Stopped telemetry updates")

    def __str__(self) -> str:
        actuator_state = self.charging_actuator.get_current_state()
        return (
            f"Node(id={self.node_id}, hub={self.hub_id}, "
            f"state={self.current_state.value}, "
            f"power={self.power_sensor.get_value('power'):.2f}W, "
            f"actuator={actuator_state['status']})"
        )
