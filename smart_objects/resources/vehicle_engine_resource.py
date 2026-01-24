import random
import threading
import time
import json
from typing import List, Optional, ClassVar
import gpxpy
from .smart_object_resource import SmartObjectResource
from shared.mqtt_dtos import (
    VehicleTelemetry,
    GeoLocation,
    NodeStatus,
    NodeTelemetry,
    ChargingState,
)
from shared.services import MQTTService


class VehicleEngineResource(SmartObjectResource):
    """
    A vehicle engine resource that combines GPS and battery simulation,
    updating both in a single thread and notifying with VehicleTelemetry.
    """

    UPDATE_PERIOD: ClassVar[int] = 1  # seconds
    TASK_DELAY_TIME: ClassVar[int] = 5  # seconds

    MIN_BATTERY_LEVEL: ClassVar[float] = 60.0
    MAX_BATTERY_LEVEL: ClassVar[float] = 90.0
    MIN_BATTERY_CONSUMPTION: ClassVar[float] = 0.05
    MAX_BATTERY_CONSUMPTION: ClassVar[float] = 0.1

    def __init__(
        self,
        resource_id: str,
        simulation: bool = True,
        vehicle_id: Optional[str] = None,
        gpx_file_name: Optional[str] = None,
        mqtt_service: Optional[MQTTService] = None,
        static_position: Optional[GeoLocation] = None,
    ):
        super().__init__(resource_id)

        self.gpx_file_name = gpx_file_name
        self.simulation = simulation
        self.mqtt_service = mqtt_service
        self.vehicle_id = vehicle_id

        self.way_point_list: List[GeoLocation] = []
        self.current_location: Optional[GeoLocation] = static_position
        self._way_point_index: int = 0
        self._reverse: bool = False

        self.battery_level: float = self._sample_initial_battery_level()
        self.target_battery_level: Optional[float] = None

        self.speed_kmh: float = 0.0
        self.engine_temp_c: float = 25.0
        self.is_charging: bool = False

        self._update_thread: Optional[threading.Thread] = None
        self._stop_update = threading.Event()

        self._assigned_hub_id: Optional[str] = None
        self._assigned_node_id: Optional[str] = None

        if self.simulation and self.gpx_file_name:
            self._load_gpx_waypoints()

    def _sample_initial_battery_level(self) -> float:
        """Sample initial battery level between min and max."""
        return self.MIN_BATTERY_LEVEL + random.random() * (
            self.MAX_BATTERY_LEVEL - self.MIN_BATTERY_LEVEL
        )

    def _load_gpx_waypoints(self) -> None:
        """Load waypoints from GPX file"""
        assert self.gpx_file_name is not None, "GPX file name must be provided"
        try:
            with open(self.gpx_file_name, "r") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                print(gpx)
                self.way_point_list = [
                    GeoLocation(
                        latitude=point.latitude,
                        longitude=point.longitude,
                        altitude=point.elevation or 0.0,
                    )
                    for track in gpx.tracks
                    for segment in track.segments
                    for point in segment.points
                ]
            self.logger.info(
                f"GPX File loaded with {len(self.way_point_list)} waypoints"
            )
        except Exception as e:
            self.logger.error(f"Error loading GPX file: {e}")
            raise

    def start_periodic_event_update_task(self) -> None:
        """Start the periodic vehicle update task"""
        self.logger.info(
            f"🚗 - Starting vehicle engine update task with period: {self.UPDATE_PERIOD} s"
        )

        if self._update_thread is None or not self._update_thread.is_alive():
            self._stop_update.clear()
            self._update_thread = threading.Thread(
                target=self._update_loop,
                daemon=True,
                name=f"VehicleEngine-{self.resource_id}",
            )
            self._update_thread.start()

    def _update_loop(self) -> None:
        """Background thread for periodic vehicle updates."""
        time.sleep(self.TASK_DELAY_TIME)
        while not self._stop_update.is_set():
            try:
                if not self.is_charging and self.simulation and self.gpx_file_name:
                    current_point = self.way_point_list[self._way_point_index]
                    self.current_location = GeoLocation(
                        latitude=current_point.latitude,
                        longitude=current_point.longitude,
                        altitude=current_point.altitude or 0.0,
                    )

                    self._way_point_index += 1 if not self._reverse else -1

                    if self._way_point_index >= len(self.way_point_list):
                        self._handle_direction_change(reverse=True)
                    elif self._way_point_index < 0:
                        self._handle_direction_change(reverse=False)

                if not self.is_charging:
                    consumption = random.uniform(
                        self.MIN_BATTERY_CONSUMPTION,
                        self.MAX_BATTERY_CONSUMPTION,
                    )
                    self.battery_level = max(0.0, self.battery_level - consumption)

                if self.battery_level <= 0.0:
                    self.logger.info("Vehicle battery depleted!")
                    self.speed_kmh = 0.0
                    self.engine_temp_c = 25.0
                    self.stop_periodic_event_update_task()
                    continue

                if self.is_charging:
                    self.speed_kmh = 0.0
                else:
                    self.speed_kmh = random.uniform(0, 120)
                    self.engine_temp_c = random.uniform(20, 60)

                telemetry = self.get_telemetry()

                self.logger.info(f"Vehicle Telemetry: {telemetry}")
                self.notify_update(message_type="telemetry")

            except Exception as e:
                self.logger.error(f"Error in vehicle engine update: {e}")

            self._stop_update.wait(self.UPDATE_PERIOD)

    def get_telemetry(self) -> VehicleTelemetry:
        """Get telemetry message DTO (for periodic measurements)."""

        assert self.current_location is not None, "Current location is not set"
        return VehicleTelemetry(
            geo_location=self.current_location,
            battery_level=int(self.battery_level),
            speed_kmh=self.speed_kmh,
            engine_temp_c=self.engine_temp_c,
            is_charging=self.is_charging,
        )

    def _handle_direction_change(self, reverse: bool) -> None:
        """Handle reversing direction when reaching end of waypoints"""
        self.way_point_list.reverse()
        self._way_point_index = 0
        self._reverse = not self._reverse
        direction = "backward" if reverse else "forward"
        self.logger.info(f"Vehicle reversing direction, now moving {direction}")

    def stop_periodic_event_update_task(self) -> None:
        """Stop the periodic updates"""
        if self._update_thread and self._update_thread.is_alive():
            self._stop_update.set()
            self._update_thread.join(timeout=5)
            self._update_thread = None

    def handle_charging_request(self, hub_id: str, node_id: str) -> None:
        """Handle charging request by subscribing to charging topics."""
        self._assigned_hub_id = hub_id
        self._assigned_node_id = node_id
        self.logger.info(
            f"Processing charging request for hub {hub_id}, node {node_id}"
        )
        self._subscribe_to_charging_topics(hub_id, node_id)

    def _subscribe_to_charging_topics(self, hub_id: str, node_id: str) -> None:
        """Subscribe to node status and telemetry topics."""
        if not self.mqtt_service:
            return

        status_topic = f"iot/hubs/{hub_id}/nodes/{node_id}/status"
        telemetry_topic = f"iot/hubs/{hub_id}/nodes/{node_id}/telemetry"

        self.mqtt_service.subscribe(status_topic, self._on_node_status_message)
        self.mqtt_service.subscribe(telemetry_topic, self._on_node_telemetry_message)

        self.logger.info(f"Subscribed to {status_topic} and {telemetry_topic}")

    def _unsubscribe_from_charging_topics(self) -> None:
        """Unsubscribe from node topics after charging completes."""
        if (
            not self.mqtt_service
            or not self._assigned_hub_id
            or not self._assigned_node_id
        ):
            return

        status_topic = (
            f"iot/hubs/{self._assigned_hub_id}/nodes/{self._assigned_node_id}/status"
        )
        telemetry_topic = (
            f"iot/hubs/{self._assigned_hub_id}/nodes/{self._assigned_node_id}/telemetry"
        )

        self.mqtt_service.unsubscribe(status_topic)
        self.mqtt_service.unsubscribe(telemetry_topic)

        self.logger.info(f"Unsubscribed from charging topics")

        self._assigned_hub_id = None
        self._assigned_node_id = None

    def _on_node_status_message(self, msg) -> None:
        """Handle node status messages."""
        try:
            data = json.loads(msg.payload.decode())
            status = NodeStatus(**data)

            if status.state == ChargingState.CHARGING and not self.is_charging:
                self.is_charging = True
                self.target_battery_level = random.uniform(80.0, 100.0)
                self.logger.info(
                    f"Charging started! Target: {self.target_battery_level:.1f}%"
                )

            else:
                if self.is_charging and self.battery_level >= (
                    self.target_battery_level or 100
                ):
                    self.logger.info("Charging complete!")
                    self._finish_charging()

        except Exception as e:
            self.logger.error(f"Error processing node status: {e}")

    def _on_node_telemetry_message(self, msg) -> None:
        """Handle node telemetry messages to update battery level."""
        try:
            data = json.loads(msg.payload.decode())
            telemetry = NodeTelemetry(**data)

            if self.is_charging and telemetry.power_kw > 0:
                # TODO: to test realistic charging, consider time delta
                charge_rate_per_second = telemetry.power_kw / 3600 * self.UPDATE_PERIOD
                self.battery_level = min(
                    100.0, self.battery_level + charge_rate_per_second
                )

                if (
                    self.simulation
                    and self.target_battery_level
                    and self.battery_level >= self.target_battery_level
                ):
                    self.logger.info(
                        f"Target battery level reached: {self.battery_level:.1f}%"
                    )
                    self._finish_charging()

        except Exception as e:
            self.logger.error(f"Error processing node telemetry: {e}")

    def _finish_charging(self) -> None:
        """Complete the charging process and resume vehicle operation."""
        self.is_charging = False
        self._unsubscribe_from_charging_topics()
        self.logger.info("Charging complete")
