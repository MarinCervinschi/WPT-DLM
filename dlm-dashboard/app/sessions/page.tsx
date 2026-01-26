"use client";

import { useEffect, useState, useCallback } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { StatusBadge } from "@/components/status-badge";
import { SessionFormDialog } from "@/components/session-form-dialog";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import api from "@/lib/api";
import type {
  ChargingSession,
  ChargingSessionCreate,
  ChargingSessionUpdate,
  Node,
  Vehicle,
} from "@/lib/types";
import { Plus, Pencil, Trash2, CircuitBoard, Car, Clock, Zap } from "lucide-react";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<ChargingSession[]>([]);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [nodeMap, setNodeMap] = useState<Record<string, Node>>({});
  const [vehicleMap, setVehicleMap] = useState<Record<string, Vehicle>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<ChargingSession | null>(null);
  const [deleteSession, setDeleteSession] = useState<ChargingSession | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [sessionsRes, nodesRes, vehiclesRes] = await Promise.all([
        api.listChargingSessions({ limit: 100 }),
        api.listNodes({ limit: 100 }),
        api.listVehicles({ limit: 100 }),
      ]);
      setSessions(sessionsRes.items);
      setNodes(nodesRes.items);
      setVehicles(vehiclesRes.items);

      const nMap: Record<string, Node> = {};
      for (const node of nodesRes.items) {
        nMap[node.node_id] = node;
      }
      setNodeMap(nMap);

      const vMap: Record<string, Vehicle> = {};
      for (const vehicle of vehiclesRes.items) {
        vMap[vehicle.vehicle_id] = vehicle;
      }
      setVehicleMap(vMap);
    } catch {
      toast.error("Failed to fetch data");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleCreate(data: ChargingSessionCreate | ChargingSessionUpdate) {
    try {
      await api.createChargingSession(data as ChargingSessionCreate);
      toast.success("Charging session started");
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to start session");
      throw error;
    }
  }

  async function handleUpdate(data: ChargingSessionCreate | ChargingSessionUpdate) {
    if (!selectedSession) return;
    try {
      await api.updateChargingSession(String(selectedSession.charging_session_id), data as ChargingSessionUpdate);
      toast.success("Session updated successfully");
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update session");
      throw error;
    }
  }

  async function handleDelete() {
    if (!deleteSession) return;
    setIsDeleting(true);
    try {
      await api.deleteChargingSession(String(deleteSession.charging_session_id));
      toast.success("Session deleted successfully");
      setDeleteSession(null);
      fetchData();
    } catch {
      toast.error("Failed to delete session");
    } finally {
      setIsDeleting(false);
    }
  }

  function formatDuration(start: string, end: string | null): string {
    if (!end) return "Ongoing";
    const startDate = new Date(start);
    const endDate = new Date(end);
    const diffMs = endDate.getTime() - startDate.getTime();
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  }

  const columns = [
    {
      key: "vehicle",
      header: "Vehicle",
      render: (session: ChargingSession) => {
        const vehicle = vehicleMap[session.vehicle_id || ""];
        return (
          <div className="flex items-center gap-2">
            <Car className="h-4 w-4 text-muted-foreground" />
            <div>
              <span className="font-medium text-card-foreground">
                {vehicle ? `${vehicle.manufacturer} ${vehicle.model}` : "Unknown"}
              </span>
              <p className="text-xs text-muted-foreground">
                {vehicle?.driver_id || session?.vehicle_id?.slice(0, 8)}
              </p>
            </div>
          </div>
        );
      },
    },
    {
      key: "node",
      header: "Node",
      render: (session: ChargingSession) => {
        const node = nodeMap[session.node_id];
        return (
          <div className="flex items-center gap-2 text-muted-foreground">
            <CircuitBoard className="h-4 w-4" />
            {node ? node.node_id : "Unknown"}
          </div>
        );
      },
    },
    {
      key: "start_time",
      header: "Started",
      render: (session: ChargingSession) => (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Clock className="h-4 w-4" />
          {new Date(session.start_time).toLocaleString()}
        </div>
      ),
    },
    {
      key: "duration",
      header: "Duration",
      render: (session: ChargingSession) => (
        <span className="text-muted-foreground">
          {formatDuration(session.start_time, session.end_time || null)}
        </span>
      ),
    },
    {
      key: "energy",
      header: "Energy",
      render: (session: ChargingSession) => (
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-primary" />
          <span className="font-medium text-card-foreground">{session.total_energy_kwh.toFixed(1)} kWh</span>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (session: ChargingSession) => <StatusBadge status={session.end_time ? "completed" : "active"} />,
    },
    {
      key: "actions",
      header: "",
      render: (session: ChargingSession) => (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedSession(session);
              setFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDeleteSession(session)}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  const availableNodes = nodes.filter((n) => !n.is_maintenance);

  return (
    <DashboardLayout>
      <PageHeader
        title="Charging Sessions"
        description="Monitor and manage charging sessions"
      >
        <Button
          onClick={() => {
            setSelectedSession(null);
            setFormOpen(true);
          }}
          disabled={availableNodes.length === 0 || vehicles.length === 0}
        >
          <Plus className="mr-2 h-4 w-4" />
          Start Session
        </Button>
      </PageHeader>

      <div className="p-6">
        {nodes.length === 0 && !isLoading ? (
          <div className="rounded-lg border border-border bg-card p-8 text-center">
            <CircuitBoard className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-medium text-card-foreground">No nodes available</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Create charging nodes first before starting sessions.
            </p>
          </div>
        ) : vehicles.length === 0 && !isLoading ? (
          <div className="rounded-lg border border-border bg-card p-8 text-center">
            <Car className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-medium text-card-foreground">No vehicles registered</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Register vehicles first before starting sessions.
            </p>
          </div>
        ) : availableNodes.length === 0 && nodes.length > 0 && !isLoading ? (
          <div className="mb-4 rounded-lg border border-warning/20 bg-warning/10 p-4">
            <p className="text-sm text-warning-foreground">
              All nodes are currently occupied. Sessions can only be started on available nodes.
            </p>
          </div>
        ) : null}

        {(nodes.length > 0 && vehicles.length > 0 || isLoading) && (
          <DataTable
            columns={columns}
            data={sessions}
            isLoading={isLoading}
            emptyMessage="No charging sessions found."
          />
        )}
      </div>

      <SessionFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        session={selectedSession}
        nodes={nodes}
        vehicles={vehicles}
        onSubmit={selectedSession ? handleUpdate : handleCreate}
      />

      <ConfirmDialog
        open={!!deleteSession}
        onOpenChange={(open) => !open && setDeleteSession(null)}
        title="Delete Session"
        description="Are you sure you want to delete this charging session? This action cannot be undone."
        onConfirm={handleDelete}
        confirmLabel="Delete"
        variant="destructive"
      />
    </DashboardLayout>
  );
}
