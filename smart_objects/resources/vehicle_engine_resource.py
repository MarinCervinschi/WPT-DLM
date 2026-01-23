import random
import threading
import time
from typing import List, Optional, ClassVar
import gpxpy
from .smart_object_resource import SmartObjectResource
from shared.mqtt_dtos import GeoLocation
from shared.mqtt_dtos.vehicle_dto import VehicleTelemetry


class VehicleEngineResource(SmartObjectResource):
    """
    A vehicle engine resource that combines GPS and battery simulation,
    updating both in a single thread and notifying with VehicleTelemetry.
    """

    UPDATE_PERIOD: ClassVar[int] = 1  # seconds
    TASK_DELAY_TIME: ClassVar[int] = 5  # seconds

    MIN_BATTERY_LEVEL: ClassVar[float] = 50.0
    MAX_BATTERY_LEVEL: ClassVar[float] = 90.0
    MIN_BATTERY_CONSUMPTION: ClassVar[float] = 0.05
    MAX_BATTERY_CONSUMPTION: ClassVar[float] = 0.0

    def __init__(self, resource_id: str, gpx_file_name: str):
        super().__init__(resource_id)

        self.gpx_file_name = gpx_file_name

        self.way_point_list: List[GeoLocation] = []
        self.current_location: Optional[GeoLocation] = None
        self._way_point_index: int = 0
        self._reverse: bool = False

        self.battery_level: float = self.MIN_BATTERY_LEVEL + random.random() * (
            self.MAX_BATTERY_LEVEL - self.MIN_BATTERY_LEVEL
        )

        self.speed_kmh: float = 0.0
        self.engine_temp_c: float = 25.0
        self.is_charging: bool = False

        self._update_thread: Optional[threading.Thread] = None
        self._stop_update = threading.Event()

        self._load_gpx_waypoints()

    def _load_gpx_waypoints(self) -> None:
        """Load waypoints from GPX file"""
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

                self.speed_kmh = random.uniform(0, 120)
                self.engine_temp_c = random.uniform(20, 60)

                telemetry = VehicleTelemetry(
                    geo_location=self.current_location,
                    battery_level=int(self.battery_level),
                    speed_kmh=self.speed_kmh,
                    engine_temp_c=self.engine_temp_c,
                    is_charging=self.is_charging,
                )

                self.logger.info(f"Vehicle Telemetry: {telemetry}")
                self.notify_update(telemetry)

            except Exception as e:
                self.logger.error(f"Error in vehicle engine update: {e}")

            self._stop_update.wait(self.UPDATE_PERIOD)

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
