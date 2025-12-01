<p><a target="_blank" href="https://app.eraser.io/workspace/ckMgfMWXETpfMUeeZgOh" id="edit-in-eraser-github-link"><img alt="Edit in Eraser" src="https://firebasestorage.googleapis.com/v0/b/second-petal-295822.appspot.com/o/images%2Fgithub%2FOpen%20in%20Eraser.svg?alt=media&amp;token=968381c8-a7e7-472a-8ed6-4a6626da5501"></a></p>

# WPT-DLM
This project implements a smart energy orchestration system for wireless charging hubs. It utilizes IoT telemetry to monitor State of Charge (SoC) and a Dynamic Load Management logic to shift grid capacity to critical users, maximizing throughput and efficiency.

## MQTT Topics
### Publishers
1. INFO
    - [ ] `iot/hubs/<hub_id>/info` - `retain=True` 
    - [ ] `iot/vehicles/<vehicle_id>/info` - `retain=True` 
    - [ ] `iot/hubs/<hub_id>/nodes/<node_id>/info` - `retain=True` 

2. STATUS
    - [ ] `iot/hubs/<hub_id>/status` 
    - [ ] `iot/hubs/<hub_id>/nodes/<node_id>/status` 

3. TELEMETRY
    - [ ] `iot/vehicles/<vehicle_id>/telemetry` 
    - [ ] `iot/hubs/<hub_id>/nodes/<node_id>/telemetry` 

4. DLM
    - [ ] `iot/hubs/<hub_id>/dlm/events` 

### Subscribers (Cloud)
1. API (brain)
    - [ ] `iot/hubs/+/info` 
    - [ ] `iot/vehicles/+/info` 
    - [ ] `iot/hubs/+/nodes/+/info` 
    - [ ] `iot/hubs/+/dlm/events` 
    - [ ] `iot/vehicles/+/telemetry` 
    - [ ] `iot/hubs/+/nodes/+/status` 

2. Telegraf
    - [ ] `iot/hubs/+/status` 
    - [ ] `iot/hubs/+/nodes/+/status` 
    - [ ] `iot/hubs/+/nodes/+/telemetry` 

## Docker Compose

### Services

| Service | Port | Description |
|---------|------|-------------|
| **mqtt-broker** | 1883 | Eclipse Mosquitto - MQTT message broker |
| **influxdb** | 8086 | Time-series database for telemetry |
| **telegraf** | - | Collects MQTT data → writes to InfluxDB |
| **grafana** | 3000 | Visualization dashboards |
| **postgres** | 5432 | Relational database for entities |

### Quick Start

```bash
# 1. Copy environment file and configure
cp .env.example .env

# 2. Start all services
docker compose up -d

# 3. Check status
docker compose ps
```

### Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | `.env` → `GRAFANA_ADMIN_USER/PASSWORD` |
| InfluxDB | http://localhost:8086 | `.env` → `INFLUXDB_ADMIN_USER/PASSWORD` |

### Commands

```bash
# View logs
docker compose logs -f [service_name]

# Stop all
docker compose down

# Reset (removes volumes)
docker compose down -v
```

### Configuration Files

```
config/
├── mosquitto/mosquitto.conf   # MQTT broker settings
├── telegraf/telegraf.conf     # MQTT → InfluxDB pipeline
└── grafana/provisioning/      # Auto-configured datasources
```

## Brain API

FastAPI service for managing hubs, nodes, vehicles, and DLM events.

### Setup

```bash
# Install dependencies
uv sync

# Start PostgreSQL
docker compose up -d postgres

# Run the API
uv run run_api.py
```

### API Documentation

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc UI |
| http://localhost:8000/openapi.json | OpenAPI schema |

<!-- eraser-additional-content -->
## Diagrams
<!-- eraser-additional-files -->
<a href="/README-WPT-DLM Architecture-1.eraserdiagram" data-element-id="YNlSBabyQ0ELAIbAE9SHY"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----eb832d37f32b2a58ef20c8ea6b04dab1-WPT-DLM-Architecture.png" alt="" data-element-id="YNlSBabyQ0ELAIbAE9SHY" /></a>
<a href="/README-Level 2&3 - Cloud-2.eraserdiagram" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----b2014d803362ff6bace94805e844e310-Level-2-3---Cloud.png" alt="" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm" /></a>
<a href="/README-WPT-DLM Communications-3.eraserdiagram" data-element-id="SzsOyQy3vm1-rzsHEhoXi"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----7002d23aa0eecb839eda355536428af4-WPT-DLM-Communications.png" alt="" data-element-id="SzsOyQy3vm1-rzsHEhoXi" /></a>
<a href="/README-MQTT Communications-4.eraserdiagram" data-element-id="RoUn7RU6jCmdFCRULfX-a"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----1b73e8a12e0807934d8eecc60f00d283-MQTT-Communications.png" alt="" data-element-id="RoUn7RU6jCmdFCRULfX-a" /></a>
<a href="/README-PostgresSQL database-5.eraserdiagram" data-element-id="YiIdFMM5JvimPrVneXaL0"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----fd05d4d02b11bc23c9970eae5da98ee8-PostgresSQL-database.png" alt="" data-element-id="YiIdFMM5JvimPrVneXaL0" /></a>
<a href="/README-Sequence Diagram of /recommendations-6.eraserdiagram" data-element-id="yBDGnZ1tXTITsJNfmO0_R"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----8082d232b4a8361cf473e5e948681704-Sequence-Diagram-of--recommendations.png" alt="" data-element-id="yBDGnZ1tXTITsJNfmO0_R" /></a>
<!-- end-eraser-additional-files -->
<!-- end-eraser-additional-content -->
<!--- Eraser file: https://app.eraser.io/workspace/ckMgfMWXETpfMUeeZgOh --->