"use client";

import { useEffect, useState, useCallback } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { VehicleFormDialog } from "@/components/vehicle-form-dialog";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import api from "@/lib/api";
import type { Vehicle, VehicleCreate, VehicleUpdate } from "@/lib/types";
import { Plus, Pencil, Trash2, Car } from "lucide-react";

export default function VehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [deleteVehicle, setDeleteVehicle] = useState<Vehicle | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await api.listVehicles({ limit: 100 });
      setVehicles(res.items);
    } catch (error) {
      toast.error("Failed to fetch vehicles");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async (data: VehicleCreate | VehicleUpdate) => {
    try {
      await api.createVehicle(data as VehicleCreate);
      toast.success("Vehicle registered successfully");
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to register vehicle");
      throw error;
    }
  };

  const handleUpdate = async (data: VehicleCreate | VehicleUpdate) => {
    if (!editingVehicle) return;
    try {
      await api.updateVehicle(editingVehicle.vehicle_id, data as VehicleUpdate);
      toast.success("Vehicle updated successfully");
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update vehicle");
      throw error;
    }
  };

  const handleDelete = async () => {
    if (!deleteVehicle) return;
    try {
      await api.deleteVehicle(deleteVehicle.vehicle_id);
      toast.success("Vehicle deleted successfully");
      setDeleteVehicle(null);
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to delete vehicle");
    }
  };

  const columns = [
    {
      key: "vehicle",
      header: "Vehicle",
      render: (vehicle: Vehicle) => (
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <Car className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-medium">{vehicle.manufacturer} {vehicle.model}</p>
            <p className="text-sm text-muted-foreground">{vehicle.driver_id}</p>
          </div>
        </div>
      ),
    },
    {
      key: "registered_at",
      header: "Registered",
      render: (vehicle: Vehicle) => (
        <span className="text-muted-foreground">
          {new Date(vehicle.registered_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (vehicle: Vehicle) => (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setEditingVehicle(vehicle);
              setFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDeleteVehicle(vehicle)}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PageHeader
        title="Vehicles"
        description="Manage registered EV vehicles"
      >
        <Button onClick={() => { setEditingVehicle(null); setFormOpen(true); }}>
          <Plus className="mr-2 h-4 w-4" />
          Register Vehicle
        </Button>
      </PageHeader>

      <div className="p-6">
        <DataTable
          columns={columns}
          data={vehicles}
          isLoading={isLoading}
          emptyMessage="No vehicles registered. Add your first vehicle."
        />
      </div>

      <VehicleFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        vehicle={editingVehicle}
        onSubmit={editingVehicle ? handleUpdate : handleCreate}
      />

      <ConfirmDialog
        open={!!deleteVehicle}
        onOpenChange={(open) => !open && setDeleteVehicle(null)}
        title="Delete Vehicle"
        description={`Are you sure you want to delete "${deleteVehicle?.manufacturer} ${deleteVehicle?.model}" (${deleteVehicle?.driver_id})? This action cannot be undone.`}
        onConfirm={handleDelete}
        confirmLabel="Delete"
        variant="destructive"
      />
    </DashboardLayout>
  );
}
