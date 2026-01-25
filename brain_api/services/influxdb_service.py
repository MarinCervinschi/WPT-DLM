import logging
from datetime import datetime, timezone
from typing import Optional

from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi

from ..core.config import settings


class InfluxDBService:
    """Service for querying InfluxDB telemetry data."""

    def __init__(self):
        """Initialize InfluxDB client."""
        self.client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG,
        )
        self.query_api: QueryApi = self.client.query_api()
        self.bucket = settings.INFLUXDB_BUCKET

        self.logger = logging.getLogger("InfluxDBService")

    def get_session_metrics(
        self, node_id: str, start_time: datetime, end_time: Optional[datetime] = None
    ) -> dict[str, float]:
        """
        Get aggregated metrics for a charging session.

        Args:
            node_id: Node identifier
            start_time: Session start time
            end_time: Session end time (None for ongoing sessions)

        Returns:
            Dictionary with total_energy_kwh and avg_power_kw
        """
        # Use current time if end_time is None
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")

        now_utc = datetime.now(timezone.utc)
        end_time_val = end_time if end_time else now_utc
        end_time_str = end_time_val.strftime("%Y-%m-%dT%H:%M:%S")

        # Flux query to calculate total energy and average power
        # Energy is calculated by integrating power over time
        query = f"""
        data = from(bucket: "{self.bucket}")
          |> range(start: {start_time_str}Z, stop: {end_time_str}Z)
          |> filter(fn: (r) => r["_measurement"] == "node_telemetry")
          |> filter(fn: (r) => r["node_id"] == "{node_id}")
          |> filter(fn: (r) => r["_field"] == "power_kw")
        
        data |> mean() |> yield(name: "avg")
        data |> integral(unit: 1h) |> yield(name: "energy")
        """

        try:
            result = self.query_api.query(query=query, org=settings.INFLUXDB_ORG)

            metrics = {"total_energy_kwh": 0.0, "avg_power_kw": 0.0}
            # Parse results
            for table in result:
                for record in table.records:
                    if record["result"] == "avg":
                        metrics["avg_power_kw"] = round(float(record.get_value()), 3)
                    elif record["result"] == "energy":
                        metrics["total_energy_kwh"] = round(
                            float(record.get_value()), 3
                        )

            self.logger.debug(
                f"Session metrics for node {node_id}: "
                f"{metrics['total_energy_kwh']:.2f} kWh, {metrics['avg_power_kw']:.2f} kW avg"
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Error querying InfluxDB for session metrics: {e}")
            # Return zeros if query fails
            return {"total_energy_kwh": 0.0, "avg_power_kw": 0.0}

    def get_latest_node_telemetry(self, node_id: str) -> Optional[dict]:
        """
        Get the latest telemetry data for a specific node.

        Args:
            node_id: Node identifier

        Returns:
            Dictionary with latest telemetry data or None if not found
        """
        query = f"""
        from(bucket: "{self.bucket}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "node_telemetry")
          |> filter(fn: (r) => r["node_id"] == "{node_id}")
          |> last()
        """

        try:
            result = self.query_api.query(query=query, org=settings.INFLUXDB_ORG)

            telemetry = {}
            for table in result:
                for record in table.records:
                    field = record.get_field()
                    value = record.get_value()
                    telemetry[field] = value

            if telemetry:
                self.logger.debug(f"Latest telemetry for node {node_id}: {telemetry}")
                return telemetry

            return None

        except Exception as e:
            self.logger.error(f"Error querying InfluxDB for node telemetry: {e}")
            return None

    def get_nodes_current_state(self, node_ids: list[str]) -> dict[str, dict]:
        """
        Get current state for multiple nodes.

        Args:
            node_ids: List of node identifiers

        Returns:
            Dictionary mapping node_id to telemetry data
        """
        if not node_ids:
            return {}

        node_filter = " or ".join([f'r["node_id"] == "{nid}"' for nid in node_ids])

        query = f"""
        from(bucket: "{self.bucket}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "node_telemetry")
          |> filter(fn: (r) => {node_filter})
          |> last()
        """

        try:
            result = self.query_api.query(query=query, org=settings.INFLUXDB_ORG)

            nodes_state = {}
            for table in result:
                for record in table.records:
                    node_id = record.values.get("node_id")
                    if node_id not in nodes_state:
                        nodes_state[node_id] = {}

                    field = record.get_field()
                    value = record.get_value()
                    nodes_state[node_id][field] = value

            self.logger.debug(f"Retrieved state for {len(nodes_state)} nodes")
            return nodes_state

        except Exception as e:
            self.logger.error(f"Error querying InfluxDB for nodes state: {e}")
            return {}

    def get_latest_vehicle_telemetry(self, vehicle_id: str) -> Optional[dict]:
        """
        Get the latest telemetry data for a specific vehicle.

        Args:
            vehicle_id: Vehicle identifier

        Returns:
            Dictionary with latest telemetry data (including battery_level) or None if not found
        """
        query = f"""
        from(bucket: "{self.bucket}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "vehicle_telemetry")
          |> filter(fn: (r) => r["vehicle_id"] == "{vehicle_id}")
          |> last()
        """

        try:
            result = self.query_api.query(query=query, org=settings.INFLUXDB_ORG)

            telemetry = {}
            for table in result:
                for record in table.records:
                    field = record.get_field()
                    value = record.get_value()
                    telemetry[field] = value

            if telemetry:
                self.logger.debug(
                    f"Latest telemetry for vehicle {vehicle_id}: {telemetry}"
                )
                return telemetry
            else:
                self.logger.warning(f"No telemetry found for vehicle {vehicle_id}")
                return None

        except Exception as e:
            self.logger.error(f"Error querying InfluxDB for vehicle telemetry: {e}")
            return None

    def close(self):
        """Close InfluxDB client connection."""
        if self.client:
            self.client.close()
