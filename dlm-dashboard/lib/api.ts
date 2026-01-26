import type {
  Hub,
  HubCreate,
  HubUpdate,
  HubListResponse,
  Node,
  NodeCreate,
  NodeUpdate,
  NodeListResponse,
  Vehicle,
  VehicleCreate,
  VehicleUpdate,
  VehicleListResponse,
  ChargingSession,
  ChargingSessionCreate,
  ChargingSessionUpdate,
  ChargingSessionListResponse,
  DLMEventListResponse,
  ChargingRequestCreate,
  ChargingRequestResponse,
  QRCodeResponse,
  HealthResponse,
} from "./types";

const API_BASE_URL = "http://localhost:8000";

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {

    try {

      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      // Handle empty responses (like 204 No Content)
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return undefined as T;
      }

      return response.json();
    } catch (error) {
      throw new Error(`Network error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  // Health Check
  async healthCheck(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health");
  }

  // Hubs
  async listHubs(params?: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
  }): Promise<HubListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit !== undefined) searchParams.set("limit", String(params.limit));
    if (params?.active_only !== undefined) searchParams.set("active_only", String(params.active_only));
    const query = searchParams.toString();
    return this.request<HubListResponse>(`/hubs${query ? `?${query}` : ""}`);
  }

  async getHub(hubId: string): Promise<Hub> {
    return this.request<Hub>(`/hubs/${hubId}`);
  }

  async createHub(data: HubCreate): Promise<Hub> {
    return this.request<Hub>("/hubs", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateHub(hubId: string, data: HubUpdate): Promise<Hub> {
    return this.request<Hub>(`/hubs/${hubId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteHub(hubId: string): Promise<void> {
    await this.request(`/hubs/${hubId}`, { method: "DELETE" });
  }

  // Nodes
  async listNodes(params?: {
    skip?: number;
    limit?: number;
    hub_id?: string;
    status?: string;
    active_only?: boolean;
  }): Promise<NodeListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit !== undefined) searchParams.set("limit", String(params.limit));
    if (params?.hub_id) searchParams.set("hub_id", params.hub_id);
    if (params?.status) searchParams.set("status", params.status);
    if (params?.active_only !== undefined) searchParams.set("active_only", String(params.active_only));
    const query = searchParams.toString();
    return this.request<NodeListResponse>(`/nodes${query ? `?${query}` : ""}`);
  }

  async getNode(nodeId: string): Promise<Node> {
    return this.request<Node>(`/nodes/${nodeId}`);
  }

  async createNode(data: NodeCreate): Promise<Node> {
    return this.request<Node>("/nodes", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateNode(nodeId: string, data: NodeUpdate): Promise<Node> {
    return this.request<Node>(`/nodes/${nodeId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteNode(nodeId: string): Promise<void> {
    await this.request(`/nodes/${nodeId}`, { method: "DELETE" });
  }

  // Vehicles
  async listVehicles(params?: {
    skip?: number;
    limit?: number;
  }): Promise<VehicleListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit !== undefined) searchParams.set("limit", String(params.limit));
    const query = searchParams.toString();
    return this.request<VehicleListResponse>(`/vehicles${query ? `?${query}` : ""}`);
  }

  async getVehicle(vehicleId: string): Promise<Vehicle> {
    return this.request<Vehicle>(`/vehicles/${vehicleId}`);
  }

  async createVehicle(data: VehicleCreate): Promise<Vehicle> {
    return this.request<Vehicle>("/vehicles", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateVehicle(vehicleId: string, data: VehicleUpdate): Promise<Vehicle> {
    return this.request<Vehicle>(`/vehicles/${vehicleId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteVehicle(vehicleId: string): Promise<void> {
    await this.request(`/vehicles/${vehicleId}`, { method: "DELETE" });
  }

  // Charging Sessions
  async listChargingSessions(params?: {
    skip?: number;
    limit?: number;
    node_id?: string;
    vehicle_id?: string;
    status?: string;
  }): Promise<ChargingSessionListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit !== undefined) searchParams.set("limit", String(params.limit));
    if (params?.node_id) searchParams.set("node_id", params.node_id);
    if (params?.vehicle_id) searchParams.set("vehicle_id", params.vehicle_id);
    if (params?.status) searchParams.set("status", params.status);
    const query = searchParams.toString();
    return this.request<ChargingSessionListResponse>(`/sessions${query ? `?${query}` : ""}`);
  }

  async getChargingSession(sessionId: string): Promise<ChargingSession> {
    return this.request<ChargingSession>(`/sessions/${sessionId}`);
  }

  async createChargingSession(data: ChargingSessionCreate): Promise<ChargingSession> {
    return this.request<ChargingSession>("/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateChargingSession(sessionId: string, data: ChargingSessionUpdate): Promise<ChargingSession> {
    return this.request<ChargingSession>(`/sessions/${sessionId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteChargingSession(sessionId: string): Promise<void> {
    await this.request(`/sessions/${sessionId}`, { method: "DELETE" });
  }

  // DLM Events (Read only)
  async listDLMEvents(params?: {
    skip?: number;
    limit?: number;
    hub_id?: string;
    event_type?: string;
  }): Promise<DLMEventListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set("skip", String(params.skip));
    if (params?.limit !== undefined) searchParams.set("limit", String(params.limit));
    if (params?.hub_id) searchParams.set("hub_id", params.hub_id);
    if (params?.event_type) searchParams.set("event_type", params.event_type);
    const query = searchParams.toString();
    return this.request<DLMEventListResponse>(`/dlm/events${query ? `?${query}` : ""}`);
  }

  private getHeaders() {
    return {
      "Content-Type": "application/json",
    };
  }

  // QR Codes
  async getQRCode(nodeId: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/qr/node/${nodeId}`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch QR code: ${response.statusText}`);
    }
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  }
}

export const api = new APIClient();
export default api;
