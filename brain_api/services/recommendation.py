import logging
import math
from typing import Optional, List

from sqlalchemy.orm import Session

from ..repositories import HubRepository, NodeRepository
from ..schemas import RecommendationRequest, RecommendationResponse
from .influxdb_service import InfluxDBService

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating charging station recommendations."""

    def __init__(self, db: Session, influx_service: InfluxDBService):
        self.db = db
        self.hub_repo = HubRepository(db)
        self.node_repo = NodeRepository(db)
        self.influx_service = influx_service

    def get_recommendation(
        self, request: RecommendationRequest
    ) -> Optional[RecommendationResponse]:
        """
        Generate charging recommendation based on vehicle status and node availability.

        Args:
            request: Vehicle status (position and battery level)

        Returns:
            Recommended hub and node or None if no suitable option found
        """
        active_hubs = list(self.hub_repo.get_active_hubs())

        if not active_hubs:
            logger.warning("No active hubs available for recommendation")
            return None

        best_recommendation = None
        best_score = float("-inf")

        for hub in active_hubs:
            if hub.lat is None or hub.lon is None:
                continue

            hub_lat: float = hub.lat  # type: ignore
            hub_lon: float = hub.lon  # type: ignore

            distance_km = self._calculate_distance(
                request.latitude, request.longitude, hub_lat, hub_lon
            )

            nodes = list(self.node_repo.get_nodes_by_hub(hub.hub_id))  # type: ignore
            if not nodes:
                continue

            node_ids: List[str] = [node.node_id for node in nodes]  # type: ignore
            nodes_state = self.influx_service.get_nodes_current_state(node_ids) 

            for node in nodes:
                is_occupied = False
                available_power: float = node.max_power_kw  # type: ignore

                node_id_str = str(node.node_id)
                if node_id_str in nodes_state:
                    state = nodes_state[node_id_str]
                    is_occupied = state.get("is_occupied", False)
                    available_power = float(
                        state.get("power_limit_kw", node.max_power_kw)
                    )

                if is_occupied:
                    continue

                score = self._calculate_score(
                    distance_km, available_power, request.battery_level
                )

                if score > best_score:
                    best_score = score
                    best_recommendation = {
                        "hub": hub,
                        "node": node,
                        "distance_km": distance_km,
                        "available_power_kw": available_power,
                    }

        if not best_recommendation:
            logger.warning("No available nodes found for recommendation")
            return None

        estimated_wait_time = self._estimate_wait_time(
            best_recommendation["distance_km"]
        )

        return RecommendationResponse(
            hub_id=best_recommendation["hub"].hub_id,  # type: ignore
            node_id=best_recommendation["node"].node_id,  # type: ignore
            hub_latitude=best_recommendation["hub"].lat,  # type: ignore
            hub_longitude=best_recommendation["hub"].lon,  # type: ignore
            distance_km=round(best_recommendation["distance_km"], 2),
            estimated_wait_time_min=estimated_wait_time,
            available_power_kw=round(best_recommendation["available_power_kw"], 2),
        )

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula."""
        R = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _calculate_score(
        self, distance_km: float, available_power_kw: float, battery_level: int
    ) -> float:
        """
        Calculate recommendation score.
        Higher score means better recommendation.
        """
        distance_score = 1 / (1 + distance_km)
        power_score = available_power_kw / 50.0
        urgency_score = (100 - battery_level) / 100.0

        return distance_score * 0.6 + power_score * 0.3 + urgency_score * 0.1

    def _estimate_wait_time(self, distance_km: float) -> int:
        """Estimate wait time in minutes based on distance."""
        avg_speed_kmh = 30.0
        travel_time_hours = distance_km / avg_speed_kmh
        return max(1, int(travel_time_hours * 60))
