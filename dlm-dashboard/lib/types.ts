// Hub Types
export interface Hub {
  hub_id: string;
  lat?: number;
  lon?: number;
  alt?: number;
  max_grid_capacity_kw: number;
  is_active: boolean;
  last_seen?: string;
}

export interface HubCreate {
  hub_id: string;
  lat?: number;
  lon?: number;
  alt?: number;
  max_grid_capacity_kw: number;
  is_active?: boolean;
  ip_address: string;
  firmware_version: string;
}

export interface HubUpdate {
  lat?: number;
  lon?: number;
  alt?: number;
  max_grid_capacity_kw?: number;
  is_active?: boolean;
  ip_address?: string;
  firmware_version?: string;
}

export interface HubDetailResponse extends Hub {
  node_count: number;
  total_node_power_kw: number;
}

export interface HubListResponse {
  items: Hub[];
  total: number;
  skip: number;
  limit: number;
}

// Node Types (charging nodes/points within hubs)
export interface Node {
  node_id: string;
  hub_id: string;
  max_power_kw: number;
  is_maintenance: boolean;
}

export interface NodeCreate {
  node_id: string;
  hub_id: string;
  max_power_kw?: number;
  is_maintenance?: boolean;
}

export interface NodeUpdate {
  max_power_kw?: number;
  is_maintenance?: boolean;
}

export interface NodeDetailResponse extends Node {
  active_session_count: number;
  total_sessions: number;
  total_energy_delivered_kwh: number;
}

export interface NodeListResponse {
  items: Node[];
  total: number;
  skip: number;
  limit: number;
}

// Vehicle Types
export interface Vehicle {
  vehicle_id: string;
  model?: string;
  manufacturer?: string;
  driver_id?: string;
  registered_at: string;
}

export interface VehicleCreate {
  vehicle_id: string;
  model?: string;
  manufacturer?: string;
  driver_id?: string;
}

export interface VehicleUpdate {
  model?: string;
  manufacturer?: string;
  driver_id?: string;
}

export interface VehicleDetailResponse extends Vehicle {
  total_sessions: number;
  total_energy_consumed_kwh: number;
  last_charging_session?: string;
}

export interface VehicleListResponse {
  items: Vehicle[];
  total: number;
  skip: number;
  limit: number;
}

// Charging Session Types
export interface ChargingSession {
  charging_session_id: number;
  node_id: string;
  vehicle_id?: string;
  start_time: string;
  end_time?: string;
  total_energy_kwh: number;
  avg_power_kw: number;
}

export interface ChargingSessionCreate {
  node_id: string;
  vehicle_id?: string;
}

export interface ChargingSessionUpdate {
  vehicle_id?: string;
  total_energy_kwh?: number;
  avg_power_kw?: number;
}

export interface ChargingSessionStart {
  node_id: string;
  vehicle_id?: string;
}

export interface ChargingSessionEnd {
  total_energy_kwh: number;
  avg_power_kw: number;
}

export interface ChargingSessionDetailResponse extends ChargingSession {
  is_active: boolean;
  duration_minutes?: number;
}

export interface ChargingSessionListResponse {
  items: ChargingSession[];
  total: number;
  skip: number;
  limit: number;
}

export interface ChargingSessionStats {
  total_sessions: number;
  active_sessions: number;
  total_energy_kwh: number;
  avg_session_duration_minutes?: number;
}

// DLM Event Types (Dynamic Load Management)
export interface DLMEvent {
  dlm_event_id: number;
  hub_id: string;
  node_id: string;
  trigger_reason: string;
  total_grid_load_kw: number;
  original_limit_kw: number;
  new_limit_kw: number;
  timestamp: string;
  available_capacity_at_trigger?: number;
}

export interface DLMEventCreate {
  hub_id: string;
  node_id: string;
  trigger_reason: string;
  total_grid_load_kw: number;
  original_limit_kw: number;
  new_limit_kw: number;
  available_capacity_at_trigger?: number;
}

export interface DLMEventLog {
  hub_id: string;
  node_id: string;
  trigger_reason: string;
  total_grid_load_kw: number;
  original_limit_kw: number;
  new_limit_kw: number;
  available_capacity_at_trigger?: number;
}

export interface DLMEventDetailResponse extends DLMEvent {
  limit_change_kw: number;
}

export interface DLMEventListResponse {
  items: DLMEvent[];
  total: number;
  skip: number;
  limit: number;
}

export interface DLMEventStats {
  total_events: number;
  events_by_reason: Record<string, number>;
  avg_limit_change_kw?: number;
  time_range_hours: number;
}

// Charging Request Types (POST only - to initiate charging)
export interface ChargingRequestCreate {
  vehicle_id: string;
}

export interface ChargingRequestResponse {
  message: string;
  node_id: string;
  vehicle_id: string;
  hub_id: string;
}

// Recommendation Types
export interface RecommendationRequest {
  latitude: number;
  longitude: number;
  battery_level: number;
}

export interface RecommendationResponse {
  hub_id: string;
  node_id: string;
  hub_latitude: number;
  hub_longitude: number;
  distance_km: number;
  estimated_wait_time_min: number;
  available_power_kw: number;
}

// QR Code Types
export interface QRCodeResponse {
  node_id: string;
  qr_code_url: string;
  qr_code_data: string;
  expires_at: string;
}

export interface QRCodeData {
  node_id: string;
  endpoint_url: string;
}

export interface GenerateQRCodeParams {
  base_url?: string;
  size?: number;
  download?: boolean;
}

// Health Check
export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  service: string;
  dependencies?: Record<string, string>;
}

// API Error
export interface APIError {
  error: string;
  detail?: string;
  code?: string;
}
