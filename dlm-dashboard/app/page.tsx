"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/status-badge";
import api from "@/lib/api";
import type { Hub, Node, Vehicle, ChargingSession, DLMEvent, HealthResponse } from "@/lib/types";
import {
  Building2,
  CircuitBoard,
  Car,
  Activity,
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  Battery,
  BarChart3,
} from "lucide-react";

interface DashboardStats {
  totalHubs: number;
  activeHubs: number;
  totalNodes: number;
  availableNodes: number;
  occupiedNodes: number;
  totalVehicles: number;
  activeSessions: number;
  totalEnergy: number;
}

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentSessions, setRecentSessions] = useState<ChargingSession[]>([]);
  const [recentDLMEvents, setRecentDLMEvents] = useState<DLMEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      setError(null);

      try {
        const [healthRes, hubsRes, nodesRes, vehiclesRes, sessionsRes, dlmRes] = await Promise.all([
          api.healthCheck().catch(() => null),
          api.listHubs({ limit: 100 }),
          api.listNodes({ limit: 100 }),
          api.listVehicles({ limit: 100 }),
          api.listChargingSessions({ limit: 10 }),
          api.listDLMEvents({ limit: 5 }),
        ]);

        setHealth(healthRes);

        const hubs = hubsRes.items;
        const nodes = nodesRes.items;
        const sessions = sessionsRes.items;

        setStats({
          totalHubs: hubsRes.total,
          activeHubs: hubs.filter((h: Hub) => h.is_active).length,
          totalNodes: nodesRes.total,
          availableNodes: nodes.filter((n: Node) => !n.is_maintenance).length,
          occupiedNodes: sessions.filter((s: ChargingSession) => s.end_time === null).length,
          totalVehicles: vehiclesRes.total,
          activeSessions: sessions.filter((s: ChargingSession) => s.end_time === null).length,
          totalEnergy: sessions.reduce((acc: number, s: ChargingSession) => acc + s.total_energy_kwh, 0),
        });

        setRecentSessions(sessions.slice(0, 5));
        setRecentDLMEvents(dlmRes.items.slice(0, 5));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch dashboard data");
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, []);

  const statCards = [
    {
      title: "Total Hubs",
      value: stats?.totalHubs ?? 0,
      subtitle: `${stats?.activeHubs ?? 0} active`,
      icon: Building2,
      color: "text-chart-1",
      bgColor: "bg-chart-1/10",
    },
    {
      title: "Charging Nodes",
      value: stats?.totalNodes ?? 0,
      subtitle: `${stats?.availableNodes ?? 0} available`,
      icon: CircuitBoard,
      color: "text-chart-2",
      bgColor: "bg-chart-2/10",
    },
    {
      title: "Registered Vehicles",
      value: stats?.totalVehicles ?? 0,
      subtitle: "In system",
      icon: Car,
      color: "text-chart-3",
      bgColor: "bg-chart-3/10",
    },
    {
      title: "Active Sessions",
      value: stats?.activeSessions ?? 0,
      subtitle: `${stats?.occupiedNodes ?? 0} nodes occupied`,
      icon: Activity,
      color: "text-chart-4",
      bgColor: "bg-chart-4/10",
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Dashboard"
        description="Overview of your EV charging infrastructure"
      />

      <div className="p-6 space-y-6">
        {/* Health Status */}
        <Card>
          <CardContent className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              {health?.status === "healthy" ? (
                <CheckCircle2 className="h-5 w-5 text-success" />
              ) : (
                <AlertCircle className="h-5 w-5 text-destructive" />
              )}
              <div>
                <p className="text-sm font-medium text-card-foreground">
                  API Status: {health?.status ?? (error ? "Error" : "Checking...")}
                </p>
                <p className="text-xs text-muted-foreground">
                  Database: {health?.dependencies?.database ?? "Unknown"}
                </p>
              </div>
            </div>
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </CardContent>
        </Card>

        {/* Stats Grid */}
        {isLoading ? (
          <div className="flex h-40 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {statCards.map((stat, i) => (
              <Card key={`${stat.title}-${i}`}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <div className={`rounded-lg p-2 ${stat.bgColor}`}>
                    <stat.icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-card-foreground">{stat.value}</div>
                  <p className="text-xs text-muted-foreground mt-1">{stat.subtitle}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Energy & Node Status */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Energy Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-card-foreground">
                <TrendingUp className="h-4 w-4" />
                Energy Delivered
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-card-foreground">
                  {stats?.totalEnergy.toFixed(1) ?? "0"}
                </span>
                <span className="text-lg text-muted-foreground">kWh</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                Total energy delivered across all sessions
              </p>
            </CardContent>
          </Card>

          {/* Node Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-card-foreground">
                <Battery className="h-4 w-4" />
                Node Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Available</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 rounded-full bg-muted">
                      <div
                        className="h-2 rounded-full bg-success"
                        style={{
                          width: `${stats?.totalNodes ? (stats.availableNodes / stats.totalNodes) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-card-foreground">{stats?.availableNodes ?? 0}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Occupied</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 rounded-full bg-muted">
                      <div
                        className="h-2 rounded-full bg-warning"
                        style={{
                          width: `${stats?.totalNodes ? (stats.occupiedNodes / stats.totalNodes) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-card-foreground">{stats?.occupiedNodes ?? 0}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Sessions & DLM Events */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recent Sessions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-card-foreground">Recent Charging Sessions</CardTitle>
            </CardHeader>
            <CardContent>
              {recentSessions.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No recent sessions</p>
              ) : (
                <div className="space-y-3">
                  {recentSessions.map((session, i) => (
                    <div
                      key={session.charging_session_id + '-' + i}
                      className="flex items-center justify-between rounded-lg border border-border p-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="rounded-lg bg-accent/10 p-2">
                          <Activity className="h-4 w-4 text-accent" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-card-foreground">
                            Vehicle: {session.vehicle_id?.slice(0, 8)}...
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(session.start_time).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-sm font-medium text-card-foreground">
                            {session.total_energy_kwh.toFixed(1)} kWh
                          </p>
                        </div>
                        <StatusBadge status={session.end_time ? "completed" : "active"} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent DLM Events */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-card-foreground">
                <BarChart3 className="h-4 w-4" />
                Recent DLM Events
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recentDLMEvents.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No DLM events</p>
              ) : (
                <div className="space-y-3">
                  {recentDLMEvents.map((event, i) => (
                    <div
                      key={event.dlm_event_id + '-' + i}
                      className="flex items-center justify-between rounded-lg border border-border p-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="rounded-lg bg-chart-2/10 p-2">
                          <BarChart3 className="h-4 w-4 text-chart-2" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-card-foreground">
                            {event.trigger_reason?.replace("_", " ")?.toUpperCase()}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(event.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-muted-foreground">
                          {event.trigger_reason}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
