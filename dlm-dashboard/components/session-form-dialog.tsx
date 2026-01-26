"use client";

import React from "react";

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type {
  ChargingSession,
  ChargingSessionCreate,
  ChargingSessionUpdate,
  Node,
  Vehicle,
} from "@/lib/types";

interface SessionFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  session?: ChargingSession | null;
  nodes: Node[];
  vehicles: Vehicle[];
  onSubmit: (data: ChargingSessionCreate | ChargingSessionUpdate) => Promise<void>;
}

export function SessionFormDialog({
  open,
  onOpenChange,
  session,
  nodes,
  vehicles,
  onSubmit,
}: SessionFormDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    node_id: "",
    vehicle_id: "",
    end_time: "",
    total_energy_kwh: 0,
    avg_power_kw: 0,
  });

  useEffect(() => {
    if (session) {
      setFormData({
        node_id: session.node_id,
        vehicle_id: session.vehicle_id || "",
        end_time: session.end_time ? session.end_time.slice(0, 16) : "",
        total_energy_kwh: session.total_energy_kwh,
        avg_power_kw: session.avg_power_kw,
      });
    } else {
      const availableNodes = nodes.filter((n) => !n.is_maintenance);
      setFormData({
        node_id: availableNodes[0]?.node_id || nodes[0]?.node_id || "",
        vehicle_id: vehicles[0]?.vehicle_id || "",
        end_time: "",
        total_energy_kwh: 0,
        avg_power_kw: 0,
      });
    }
  }, [session, nodes, vehicles, open]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (session) {
        const submitData: ChargingSessionUpdate = {
          vehicle_id: formData.vehicle_id || undefined,
          total_energy_kwh: formData.total_energy_kwh,
          avg_power_kw: formData.avg_power_kw,
        };
        await onSubmit(submitData);
      } else {
        const submitData: ChargingSessionCreate = {
          node_id: formData.node_id,
          vehicle_id: formData.vehicle_id || undefined,
        };
        await onSubmit(submitData);
      }
      onOpenChange(false);
    } finally {
      setIsLoading(false);
    }
  }

  const availableNodes = nodes.filter(
    (n) => !n.is_maintenance || n.node_id === session?.node_id
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-card-foreground">
            {session ? "Edit Session" : "Start Charging Session"}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!session && (
            <>
              <div className="space-y-2">
                <Label htmlFor="node_id" className="text-card-foreground">Charging Node</Label>
                <Select
                  value={formData.node_id}
                  onValueChange={(value) => setFormData({ ...formData, node_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a node" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableNodes.map((node, i) => (
                      <SelectItem key={`${node.node_id}-${i}`} value={node.node_id}>
                        {node.node_id} - {node.max_power_kw}kW
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="vehicle_id" className="text-card-foreground">Vehicle</Label>
                <Select
                  value={formData.vehicle_id}
                  onValueChange={(value) => setFormData({ ...formData, vehicle_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a vehicle" />
                  </SelectTrigger>
                  <SelectContent>
                    {vehicles.map((vehicle, i) => (
                      <SelectItem key={`${vehicle.vehicle_id}-${i}`} value={vehicle.vehicle_id}>
                        {vehicle.manufacturer} {vehicle.model} ({vehicle.driver_id})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </>
          )}

          {session && (
            <>
              <div className="space-y-2">
                <Label htmlFor="end_time" className="text-card-foreground">End Time</Label>
                <Input
                  id="end_time"
                  type="datetime-local"
                  value={formData.end_time}
                  onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="total_energy_kwh" className="text-card-foreground">Energy (kWh)</Label>
                  <Input
                    id="total_energy_kwh"
                    type="number"
                    min="0"
                    step="0.1"
                    value={formData.total_energy_kwh}
                    onChange={(e) =>
                      setFormData({ ...formData, total_energy_kwh: parseFloat(e.target.value) || 0 })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="avg_power_kw" className="text-card-foreground">Avg Power (kW)</Label>
                  <Input
                    id="avg_power_kw"
                    type="number"
                    min="0"
                    step="0.1"
                    value={formData.avg_power_kw}
                    onChange={(e) =>
                      setFormData({ ...formData, avg_power_kw: parseFloat(e.target.value) || 0 })
                    }
                  />
                </div>
              </div>
            </>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || (!session && (!formData.node_id || !formData.vehicle_id))}>
              {isLoading ? "Saving..." : session ? "Update" : "Start Session"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
