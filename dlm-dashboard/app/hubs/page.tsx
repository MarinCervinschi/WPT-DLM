"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { StatusBadge } from "@/components/status-badge";
import { HubFormDialog } from "@/components/hub-form-dialog";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import api from "@/lib/api";
import type { Hub, HubCreate, HubUpdate } from "@/lib/types";
import { Plus, Pencil, Trash2, MapPin, Zap } from "lucide-react";

export default function HubsPage() {
  const [hubs, setHubs] = useState<Hub[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [selectedHub, setSelectedHub] = useState<Hub | null>(null);
  const [deleteHub, setDeleteHub] = useState<Hub | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function fetchHubs() {
    setIsLoading(true);
    try {
      const response = await api.listHubs({ limit: 100 });
      setHubs(response.items);
    } catch {
      toast.error("Failed to fetch hubs");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchHubs();
  }, []);

  async function handleCreate(data: HubCreate | HubUpdate) {
    try {
      await api.createHub(data as HubCreate);
      toast.success("Hub created successfully");
      fetchHubs();
    } catch {
      toast.error("Failed to create hub");
      throw new Error("Failed to create hub");
    }
  }

  async function handleUpdate(data: HubCreate | HubUpdate) {
    if (!selectedHub) return;
    try {
      await api.updateHub(selectedHub.hub_id, data as HubUpdate);
      toast.success("Hub updated successfully");
      fetchHubs();
    } catch {
      toast.error("Failed to update hub");
      throw new Error("Failed to update hub");
    }
  }

  async function handleDelete() {
    if (!deleteHub) return;
    setIsDeleting(true);
    try {
      await api.deleteHub(deleteHub.hub_id);
      toast.success("Hub deleted successfully");
      setDeleteHub(null);
      fetchHubs();
    } catch {
      toast.error("Failed to delete hub");
    } finally {
      setIsDeleting(false);
    }
  }

  const columns = [
    {
      key: "hub_id",
      header: "Hub Id",
      cell: (hub: Hub) => (
        <div className="font-medium text-card-foreground">{hub.hub_id}</div>
      ),
    },
    {
      key: "location",
      header: "Location",
      cell: (hub: Hub) => (
        <div className="flex items-center gap-2 text-muted-foreground">
          <MapPin className="h-4 w-4" />
          {hub.lat && hub.lon ? `${hub.lat}, ${hub.lon}` : "N/A"}
        </div>
      ),
    },
    {
      key: "max_capacity_kw",
      header: "Capacity",
      cell: (hub: Hub) => (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Zap className="h-4 w-4" />
          {hub.max_grid_capacity_kw} kW
        </div>
      ),
    },
    {
      key: "is_active",
      header: "Status",
      cell: (hub: Hub) => (
        <StatusBadge status={hub.is_active ? "Active" : "Inactive"} />
      ),
    },
    {
      key: "actions",
      header: "",
      cell: (hub: Hub) => (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedHub(hub);
              setFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              setDeleteHub(hub);
            }}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
      className: "w-24",
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader title="Hubs" description="Manage your charging hub locations">
        <Button
          onClick={() => {
            setSelectedHub(null);
            setFormOpen(true);
          }}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Hub
        </Button>
      </PageHeader>

      <div className="p-6">
        <DataTable
          columns={columns}
          data={hubs}
          isLoading={isLoading}
          emptyMessage="No hubs found. Create one to get started."
        />
      </div>

      <HubFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        hub={selectedHub}
        onSubmit={selectedHub ? handleUpdate : handleCreate}
      />

      <ConfirmDialog
        open={!!deleteHub}
        onOpenChange={(open) => !open && setDeleteHub(null)}
        title="Delete Hub"
        description={`Are you sure you want to delete "${deleteHub?.hub_id}"? This action cannot be undone and will also delete all associated nodes.`}
        onConfirm={handleDelete}
        confirmLabel="Delete"
        variant="destructive"
      />
    </DashboardLayout>
  );
}
