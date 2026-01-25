import json
import threading
from typing import ClassVar, Optional

from edge.gateway import ArduinoSerialBridge
from shared.mqtt_dtos import ChargingState, NodeInfo, NodeStatus, NodeTelemetry
from shared.mqtt_dtos.vehicle_dto import VehicleTelemetry
from shared.services import MQTTService
from smart_objects.actuators import L298NActuator
from smart_objects.sensors import HC_SR04, INA219Sensor

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

    VEHICLE_DETECTION_THRESHOLD: ClassVar[int] = (
        50  # Vehicle present if distance < 50cm
    )
    TELEMETRY_INTERVAL: ClassVar[float] = 2.0  # seconds

    def __init__(
        self,
        node_id: str,
        hub_id: str,
        mqtt_service: Optional[MQTTService] = None,
        max_power_kw: float = 78.0,
        simulation: bool = True,
        serial_port: str = "COM3",
    ):
        super().__init__(resource_id=node_id)
        self.node_id = node_id
        self.hub_id = hub_id
        self.mqtt_service = mqtt_service
        self.max_power_kw = max_power_kw

        self.simulation = simulation

        self.bridge = None
        if not simulation:
            try:
                # Creiamo l'istanza e connettiamo
                self.bridge = ArduinoSerialBridge(port=serial_port)
                self.bridge.connect()
                self.logger.info(f"Bridge initialized on {serial_port}")
            except Exception as e:
                self.logger.error(
                    f"Failed to init bridge: {e}. Fallback to simulation."
                )
                simulation = True

        self.power_sensor = INA219Sensor(bridge=self.bridge, simulation=simulation)
        self.distance_sensor = HC_SR04(bridge=self.bridge, simulation=simulation)
        self.charging_actuator = L298NActuator(
            bridge=self.bridge, simulation=simulation
        )

        self.current_state: ChargingState = ChargingState.IDLE
        self.error_code: int = 0

        self.power_limit_kw: float = 0.0
        self.is_occupied: bool = False
        self.connected_vehicle_id: Optional[str] = None
        self.current_vehicle_soc: Optional[int] = None

        self._telemetry_thread: Optional[threading.Thread] = None
        self._stop_telemetry = threading.Event()

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

            if new_state == ChargingState.CHARGING:
                self._start_charging()
            elif new_state in (
                ChargingState.IDLE,
                ChargingState.FULL,
                ChargingState.FAULTED,
            ):
                self._stop_charging()
                self.unsubscribe_from_vehicle_telemetry(self.connected_vehicle_id)  # type: ignore

            self.notify_update(message_type="status")

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
            pwm_ratio = min(limit_kw / self.max_power_kw, 1.0)
            pwm_level = pwm_ratio * 255.0

            command = {"status": "ON", "pwm_level": pwm_level}
            self.charging_actuator.apply_command(command)
            self.logger.info(
                f"⚙️ DLM limit set to {limit_kw:.2f}kW (PWM: {pwm_level:.0f})"
            )

    def measure_sensors(self) -> None:
        """Read all sensor values and update telemetry."""
        self.power_sensor.measure()

        self.distance_sensor.measure()
        distance = self.distance_sensor.get_value("distance")

        if not self.simulation:
            self.is_occupied = distance < self.VEHICLE_DETECTION_THRESHOLD

        power_w = self.power_sensor.get_value("power")
        self.logger.debug(
            f"📊 Sensor readings: "
            f"V={self.power_sensor.get_value('voltage'):.2f}V, "
            f"I={self.power_sensor.get_value('current'):.3f}A, "
            f"P={power_w:.2f}W, "
            f"Distance={distance:.1f}cm, "
            f"Occupied={self.is_occupied}"
        )

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
            power_kw=self.power_sensor.get_value("power"),
            power_limit_kw=self.power_limit_kw,
            is_occupied=self.is_occupied,
            connected_vehicle_id=self.connected_vehicle_id,
            current_vehicle_soc=self.current_vehicle_soc,
        )

    def _telemetry_loop(self) -> None:
        """Background thread for periodic telemetry updates."""
        while not self._stop_telemetry.is_set():
            try:
                self.measure_sensors()

                if self.current_state == ChargingState.FULL and not self.is_occupied:
                    self.set_state(ChargingState.IDLE)

                self.notify_update(message_type="telemetry")
            except Exception as e:
                self.logger.error(f"Error in telemetry loop: {e}")

            self._stop_telemetry.wait(self.TELEMETRY_INTERVAL)

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
                f"🟢 Started telemetry updates (every {self.TELEMETRY_INTERVAL}s)"
            )

    def stop_periodic_event_update_task(self) -> None:
        """Stop periodic telemetry updates."""
        if self._telemetry_thread and self._telemetry_thread.is_alive():
            self._stop_telemetry.set()
            self._telemetry_thread.join(timeout=5)
            self.logger.info("🔴 Stopped telemetry updates")

        if self.bridge:
            self.bridge.disconnect()
            self.logger.info("Bridge disconnected.")

    def subscribe_to_vehicle_telemetry(self, vehicle_id: str) -> None:
        """Subscribe to vehicle telemetry topic."""
        if not self.mqtt_service:
            self.logger.warning("No MQTT service available for subscription")
            return

        telemetry_topic = f"iot/vehicles/{vehicle_id}/telemetry"

        def _on_vehicle_telemetry_message(msg) -> None:
            """Handle vehicle telemetry messages during charging."""
            try:
                data = json.loads(msg.payload.decode())
                telemetry = VehicleTelemetry(**data)

                if telemetry.battery_level is not None:
                    self.current_vehicle_soc = telemetry.battery_level

                if (
                    not telemetry.is_charging
                    and self.is_occupied
                    and self.current_state == ChargingState.CHARGING
                ):
                    self.set_state(ChargingState.FULL)
                    if self.simulation:
                        self.is_occupied = False

                self.logger.debug(
                    f"📊 Received telemetry from vehicle {vehicle_id}: "
                    f"SoC={telemetry.battery_level}%"
                )

            except Exception as e:
                self.logger.error(f"Error processing vehicle telemetry message: {e}")

        self.mqtt_service.subscribe(telemetry_topic, _on_vehicle_telemetry_message)
        self.logger.info(f"🔔 Subscribed to {telemetry_topic}")

    def unsubscribe_from_vehicle_telemetry(self, vehicle_id: str) -> None:
        """Unsubscribe from vehicle telemetry topic."""
        if (
            not self.mqtt_service
            or not self.connected_vehicle_id
            or not self.current_vehicle_soc
        ):
            return

        telemetry_topic = f"iot/vehicles/{vehicle_id}/telemetry"

        self.mqtt_service.unsubscribe(telemetry_topic)

        self.logger.info(f"🔕 Unsubscribed from {telemetry_topic}")

        self.connected_vehicle_id = None
        self.current_vehicle_soc = None

    def __str__(self) -> str:
        actuator_state = self.charging_actuator.get_current_state()
        return (
            f"Node(id={self.node_id}, hub={self.hub_id}, "
            f"state={self.current_state.value}, "
            f"power={self.power_sensor.get_value('power'):.2f}W, "
            f"actuator={actuator_state['status']})"
        )
