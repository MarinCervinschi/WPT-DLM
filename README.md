# WPT-DLM

This project implements a smart energy orchestration system for wireless charging hubs. It utilizes IoT telemetry to monitor State of Charge (SoC) and a Dynamic Load Management logic to shift grid capacity to critical users, maximizing throughput and efficiency.

## MQTT Topics

### Publishers

1. INFO
   - [x] `iot/hubs/{hub_id}/info` - `retain=True`
   - [x] `iot/hubs/{hub_id}/nodes/{node_id}/info` - `retain=True`

2. STATUS
   - [x] `iot/hubs/{hub_id}/status`
   - [x] `iot/hubs/{hub_id}/nodes/{node_id}/status`

3. TELEMETRY
   - [x] `iot/vehicles/{vehicle_id}/telemetry`
   - [x] `iot/hubs/{hub_id}/nodes/{node_id}/telemetry`

4. DLM
   - [x] `iot/hubs/{hub_id}/dlm/events`

5. Charging Request
   - [x] `iot/hubs/{hub_id}/requests`

### Subscribers (Cloud)

1. API (brain)
   - [x] `iot/hubs/+/info`
   - [x] `iot/hubs/+/nodes/+/info`
   - [x] `iot/hubs/+/dlm/events`
   - [x] `iot/hubs/+/nodes/+/status`
   - [x] `iot/vehicles/+/telemetry`

2. Telegraf
   - [x] `iot/hubs/+/status`
   - [x] `iot/hubs/+/nodes/+/status`
   - [x] `iot/hubs/+/nodes/+/telemetry`
   - [x] `iot/vehicles/+/telemetry`

## Docker Compose

### Services

| Service         | Port | Description                             |
| --------------- | ---- | --------------------------------------- |
| **mqtt-broker** | 1883 | Eclipse Mosquitto - MQTT message broker |
| **influxdb**    | 8086 | Time-series database for telemetry      |
| **telegraf**    | -    | Collects MQTT data → writes to InfluxDB |
| **grafana**     | 3000 | Visualization dashboards                |
| **postgres**    | 5432 | Relational database for entities        |

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

| Service  | URL                   | Credentials                             |
| -------- | --------------------- | --------------------------------------- |
| Grafana  | http://localhost:3000 | `.env` → `GRAFANA_ADMIN_USER/PASSWORD`  |
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

# Seed some data in the database
uv run scripts/db/seed_db.py --reset
```

### API Documentation

| URL                                | Description    |
| ---------------------------------- | -------------- |
| http://localhost:8000/docs         | Swagger UI     |
| http://localhost:8000/redoc        | ReDoc UI       |
| http://localhost:8000/openapi.json | OpenAPI schema |

## 🔨 Development

### Adding Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

### Configuration

- All settings for the docker compose services are in [config](config/) directory.
- All the Brain API settings are in [brain_api/core/config.py](brain_api/core/config.py) and can be overridden with environment variables.

### Code Quality

```bash
# Format code
uv run black app/
uv run isort app/
```

<!-- eraser-additional-content -->

## Diagrams

<!-- eraser-additional-files -->

<a href="/docs/diagrams/README-WPT-DLM Architecture-1.eraserdiagram" data-element-id="YNlSBabyQ0ELAIbAE9SHY"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----c7b53ce45e51530a9d0f2df98907719f-WPT-DLM-Architecture.png" alt="" data-element-id="YNlSBabyQ0ELAIbAE9SHY" /></a>
<a href="/docs/diagrams/README-Level 2&3 - Cloud-2.eraserdiagram" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----fc3d3360f393d538327fa60917831005-Level-2-3---Cloud.png" alt="" data-element-id="z1fLtN1Pi2Ed9TSYLy_mm" /></a>
<a href="/docs/diagrams/README-WPT-DLM Communications-3.eraserdiagram" data-element-id="SzsOyQy3vm1-rzsHEhoXi"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----e17c675359ba1183ef18528c9b05777b-WPT-DLM-Communications.png" alt="" data-element-id="SzsOyQy3vm1-rzsHEhoXi" /></a>
<a href="/docs/diagrams/README-PostgresSQL database-4.eraserdiagram" data-element-id="YiIdFMM5JvimPrVneXaL0"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----e633655e840814ac865956cccfdd9c54-PostgresSQL-database.png" alt="" data-element-id="YiIdFMM5JvimPrVneXaL0" /></a>
<a href="/docs/diagrams/README-Sequence Diagram of /recommendations-5.eraserdiagram" data-element-id="yBDGnZ1tXTITsJNfmO0_R"><img src="/.eraser/ckMgfMWXETpfMUeeZgOh___4SCKNyJL8SMwR7QrXqo5OfS44bQ2___---diagram----fe55e0517ccdb9bc18d00ddf9ff2faff-Sequence-Diagram-of--recommendations.png" alt="" data-element-id="yBDGnZ1tXTITsJNfmO0_R" /></a>
