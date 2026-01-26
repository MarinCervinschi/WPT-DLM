"use client";

import { useEffect, useState, useCallback } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "@/lib/api";
import type { DLMEvent, Hub } from "@/lib/types";
import {
  BarChart3,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  Building2,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const eventTypeConfig: Record<string, { icon: typeof BarChart3; color: string; bgColor: string }> = {
  GRID_OVERLOAD: { icon: TrendingDown, color: "text-warning", bgColor: "bg-warning/10" },
  PRIORITY_SHIFT: { icon: RefreshCw, color: "text-accent", bgColor: "bg-accent/10" },
  SCHEDULE: { icon: BarChart3, color: "text-primary", bgColor: "bg-primary/10" },
  MANUAL: { icon: AlertTriangle, color: "text-destructive", bgColor: "bg-destructive/10" },
  EMERGENCY: { icon: AlertTriangle, color: "text-destructive", bgColor: "bg-destructive/10" },
  REBALANCE: { icon: TrendingUp, color: "text-success", bgColor: "bg-success/10" },
};

export default function DLMEventsPage() {
  const [events, setEvents] = useState<DLMEvent[]>([]);
  const [hubs, setHubs] = useState<Hub[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hubFilter, setHubFilter] = useState<string>("all");
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("all");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [eventsRes, hubsRes] = await Promise.all([
        api.listDLMEvents({
          limit: 100,
          hub_id: hubFilter !== "all" ? hubFilter : undefined,
          event_type: eventTypeFilter !== "all" ? eventTypeFilter : undefined,
        }),
        api.listHubs({ limit: 100 }),
      ]);
      setEvents(eventsRes.items);
      setHubs(hubsRes.items);
    } catch (error) {
      toast.error("Failed to fetch DLM events");
    } finally {
      setIsLoading(false);
    }
  }, [hubFilter, eventTypeFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getHubName = (hubId: string) => {
    const hub = hubs.find((h) => h.hub_id === hubId);
    return hub?.hub_id ?? "Unknown Hub";
  };

  // Calculate stats
  const eventCounts = {
    GRID_OVERLOAD: events.filter((e) => e.trigger_reason === "GRID_OVERLOAD").length,
    PRIORITY_SHIFT: events.filter((e) => e.trigger_reason === "PRIORITY_SHIFT").length,
    SCHEDULE: events.filter((e) => e.trigger_reason === "SCHEDULE").length,
    MANUAL: events.filter((e) => e.trigger_reason === "MANUAL").length,
    EMERGENCY: events.filter((e) => e.trigger_reason === "EMERGENCY").length,
    REBALANCE: events.filter((e) => e.trigger_reason === "REBALANCE").length,
  };

  const columns = [
    {
      key: "trigger_reason",
      header: "Event Type",
      render: (event: DLMEvent) => {
        const config = eventTypeConfig[event.trigger_reason] || eventTypeConfig.MANUAL;
        const Icon = config.icon;
        return (
          <div className="flex items-center gap-3">
            <div className={`rounded-lg p-2 ${config.bgColor}`}>
              <Icon className={`h-4 w-4 ${config.color}`} />
            </div>
            <span className="font-medium capitalize">{event.trigger_reason?.replace("_", " ")}</span>
          </div>
        );
      },
    },
    {
      key: "hub",
      header: "Hub",
      render: (event: DLMEvent) => (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Building2 className="h-4 w-4" />
          {getHubName(event.hub_id)}
        </div>
      ),
    },
    {
      key: "description",
      header: "Description",
      render: (event: DLMEvent) => (
        <span className="text-muted-foreground">{event.trigger_reason}</span>
      ),
    },
    {
      key: "values",
      header: "Change",
      render: (event: DLMEvent) => (
        <div className="flex items-center gap-2">
          {event.original_limit_kw !== undefined && (
            <span className="text-muted-foreground">{event.original_limit_kw?.toFixed(2)} kW</span>
          )}
          {event.original_limit_kw !== undefined && event.new_limit_kw !== undefined && (
            <span className="text-muted-foreground">→</span>
          )}
          {event.new_limit_kw !== undefined && (
            <span className="font-medium text-card-foreground">{event.new_limit_kw?.toFixed(2)} kW</span>
          )}
          {event.original_limit_kw === undefined && event.new_limit_kw === undefined && (
            <span className="text-muted-foreground">-</span>
          )}
        </div>
      ),
    },
    {
      key: "node_id",
      header: "Node",
      render: (event: DLMEvent) => (
        <span className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium">
          {event.node_id}
        </span>
      ),
    },
    {
      key: "timestamp",
      header: "Timestamp",
      render: (event: DLMEvent) => (
        <span className="text-muted-foreground">
          {new Date(event.timestamp).toLocaleString()}
        </span>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="DLM Events"
        description="Dynamic Load Management event history"
      >
        <Button variant="outline" onClick={fetchData} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </PageHeader>

      <div className="p-6 space-y-6">
        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Object.entries(eventCounts).map(([type, count]) => {
            const config = eventTypeConfig[type];
            const Icon = config?.icon ?? BarChart3;
            return (
              <Card key={type}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground capitalize">
                    {type.replace("_", " ")}
                  </CardTitle>
                  <div className={`rounded-lg p-2 ${config?.bgColor ?? "bg-muted"}`}>
                    <Icon className={`h-4 w-4 ${config?.color ?? "text-muted-foreground"}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-card-foreground">{count}</div>
                  <p className="text-xs text-muted-foreground mt-1">events recorded</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm text-muted-foreground">Hub:</label>
            <select
              className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={hubFilter}
              onChange={(e) => setHubFilter(e.target.value)}
            >
              <option value="all">All Hubs</option>
              {hubs.map((hub, i) => (
                <option key={`${hub.hub_id}-${i}`} value={hub.hub_id}>
                  {hub.hub_id}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm text-muted-foreground">Event Type:</label>
            <select
              className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="GRID_OVERLOAD">Grid Overload</option>
              <option value="PRIORITY_SHIFT">Priority Shift</option>
              <option value="SCHEDULE">Schedule</option>
              <option value="MANUAL">Manual</option>
              <option value="EMERGENCY">Emergency</option>
              <option value="REBALANCE">Rebalance</option>
            </select>
          </div>
        </div>

        {/* Events Table */}
        <DataTable
          columns={columns}
          data={events}
          isLoading={isLoading}
          emptyMessage="No DLM events recorded yet."
        />
      </div>
    </DashboardLayout>
  );
}
