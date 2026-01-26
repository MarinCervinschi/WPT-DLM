"use client";

import React from "react"

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Vehicle, VehicleCreate, VehicleUpdate } from "@/lib/types";

interface VehicleFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  vehicle?: Vehicle | null;
  onSubmit: (data: VehicleCreate | VehicleUpdate) => Promise<void>;
}

export function VehicleFormDialog({
  open,
  onOpenChange,
  vehicle,
  onSubmit,
}: VehicleFormDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    vehicle_id: "",
    model: "",
    manufacturer: "",
    driver_id: "",
  });

  useEffect(() => {
    if (vehicle) {
      setFormData({
        vehicle_id: vehicle.vehicle_id,
        model: vehicle.model || "",
        manufacturer: vehicle.manufacturer || "",
        driver_id: vehicle.driver_id || "",
      });
    } else {
      setFormData({
        vehicle_id: "",
        model: "",
        manufacturer: "",
        driver_id: "",
      });
    }
  }, [vehicle, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (vehicle) {
        const updateData: VehicleUpdate = {
          model: formData.model,
          manufacturer: formData.manufacturer,
          driver_id: formData.driver_id,
        };
        await onSubmit(updateData);
      } else {
        const createData: VehicleCreate = {
          vehicle_id: formData.vehicle_id,
          model: formData.model,
          manufacturer: formData.manufacturer,
          driver_id: formData.driver_id,
        };
        await onSubmit(createData);
      }
      onOpenChange(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-card-foreground">
            {vehicle ? "Edit Vehicle" : "Register New Vehicle"}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!vehicle && (
            <div className="space-y-2">
              <Label htmlFor="vehicle_id" className="text-card-foreground">Vehicle ID</Label>
              <Input
                id="vehicle_id"
                value={formData.vehicle_id}
                onChange={(e) => setFormData({ ...formData, vehicle_id: e.target.value })}
                placeholder="e.g., VEH-001"
                required
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="manufacturer" className="text-card-foreground">Manufacturer</Label>
              <Input
                id="manufacturer"
                value={formData.manufacturer}
                onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                placeholder="e.g., Tesla"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="model" className="text-card-foreground">Model</Label>
              <Input
                id="model"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                placeholder="e.g., Model 3"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="driver_id" className="text-card-foreground">Driver ID</Label>
            <Input
              id="driver_id"
              value={formData.driver_id}
              onChange={(e) => setFormData({ ...formData, driver_id: e.target.value })}
              placeholder="e.g., DRIVER-001"
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || (!vehicle && !formData.vehicle_id)}>
              {isSubmitting ? "Saving..." : vehicle ? "Update" : "Register"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
