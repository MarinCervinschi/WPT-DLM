-- Seed data for WPT-DLM
-- Run with: uv run python seed_db.py

-- Hubs
INSERT INTO hubs (hub_id, lat, lon, alt, max_grid_capacity_kw, ip_address, firmware_version, is_active)
VALUES
    ('hub_01', 44.6294, 10.9481, 50.0, 150.0, '192.168.1.1', '1.0.0', true),
    ('hub_02', 44.6468, 10.9254, 45.0, 100.0, '192.168.1.2', '1.0.0', true);

-- Nodes
INSERT INTO nodes (node_id, hub_id, max_power_kw, is_maintenance)
VALUES
    ('node_01', 'hub_01', 22.0, false),
    ('node_02', 'hub_01', 22.0, false),
    ('node_03', 'hub_01', 50.0, false),
    ('node_04', 'hub_02', 11.0, false),
    ('node_05', 'hub_02', 22.0, true);

-- Vehicles
INSERT INTO vehicles (vehicle_id, model, manufacturer, driver_id)
VALUES
    ('vehicle_01', 'Model 3', 'Tesla', 'driver_001'),
    ('vehicle_02', 'ID.4', 'Volkswagen', 'driver_002'),
    ('vehicle_03', 'e-208', 'Peugeot', 'driver_003');
