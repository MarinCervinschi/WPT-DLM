import logging
import random
import threading
from typing import Optional, Dict, Any
import requests

from shared.mqtt_dtos import GeoLocation, VehicleRequest
from shared.services import MQTTService


class ChargingRequestEmulator:
    """
    Service that monitors vehicle battery level and automatically requests
    charging when needed. Only active in simulation mode.
    """

    CHECK_INTERVAL: int = 5

    def __init__(
        self,
        vehicle_id: str,
        mqtt_service: MQTTService,
        get_battery_level_callback,
        get_location_callback,
        api_url: str = "http://localhost:8000",
    ):
        self.vehicle_id = vehicle_id
        self.mqtt_service = mqtt_service
        self.get_battery_level = get_battery_level_callback
        self.get_location = get_location_callback
        self.api_url = api_url

        
        self.logger = logging.getLogger(f"ChargingRequestEmulator-{vehicle_id}")
        
        self._battery_threshold = self._sample_battery_threshold()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = threading.Event()
        self._charging_requested = False

    def start(self) -> None:
        """Start monitoring battery level."""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_monitor.clear()
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name=f"ChargingMonitor-{self.vehicle_id}",
            )
            self._monitor_thread.start()
            self.logger.info("Started charging request service")

    def stop(self) -> None:
        """Stop monitoring."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_monitor.set()
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
            self.logger.info("Stopped charging request service")

    def _monitor_loop(self) -> None:
        """Monitor battery level and request charging when needed."""
        while not self._stop_monitor.is_set():
            try:
                battery_level = self.get_battery_level()

                if (
                    battery_level <= self._battery_threshold
                    and not self._charging_requested
                ):
                    self.logger.info(
                        f"Battery below threshold ({self._battery_threshold:.1f}%), requesting charge"
                    )
                    self._request_charging()
                    self._battery_threshold = self._sample_battery_threshold()
                elif battery_level > self._battery_threshold:
                    self._charging_requested = False

            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")

            self._stop_monitor.wait(self.CHECK_INTERVAL)

    def _sample_battery_threshold(self) -> int:
        """Sample battery threshold with slight random variation."""

        new_threshold = int(random.uniform(10, 40))
        self.logger.info(f"New battery threshold set to {new_threshold}%")
        return new_threshold

    def _request_charging(self) -> None:
        """Request charging from the recommendation API."""
        try:
            location = self.get_location()
            if not location:
                self.logger.error("No location available for charging request")
                return

            recommendation = self._get_charging_recommendation(location)

            if not recommendation:
                self.logger.warning("No charging recommendation available")
                return

            hub_id = recommendation["hub_id"]
            node_id = recommendation["node_id"]

            self.logger.info(
                f"Sending charging request to hub {hub_id}, node {node_id}"
            )

            request = VehicleRequest(
                vehicle_id=self.vehicle_id,
                node_id=node_id,
                soc_percent=int(self.get_battery_level()),
            )

            request_topic = f"iot/hubs/{hub_id}/requests"
            self.mqtt_service.publish(request_topic, request.model_dump_json(), qos=1)

            self._charging_requested = True

        except Exception as e:
            self.logger.error(f"Error requesting charging: {e}")

    def _get_charging_recommendation(
        self, location: GeoLocation
    ) -> Optional[Dict[str, Any]]:
        """Get charging recommendation from API or return mock data."""
        try:
            response = requests.post(
                f"{self.api_url}/recommendations",
                json={
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                },
                timeout=5,
            )

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(
                    f"API returned status {response.status_code}, using mock data"
                )
                return self._get_mock_recommendation()

        except requests.RequestException as e:
            self.logger.warning(f"API request failed: {e}, using mock data")
            return self._get_mock_recommendation()

    def _get_mock_recommendation(self) -> Dict[str, Any]:
        """Return mock recommendation data for testing."""
        return {
            "hub_id": "hub_01",
            "node_id": "node_01",
            "distance_km": 0.5,
            "estimated_wait_time_min": 0,
        }
