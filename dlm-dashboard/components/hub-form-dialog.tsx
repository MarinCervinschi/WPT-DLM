"use client";

import React from "react"

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import type { Hub, HubCreate, HubUpdate } from "@/lib/types";

interface HubFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  hub?: Hub | null;
  onSubmit: (data: HubCreate | HubUpdate) => Promise<void>;
}

export function HubFormDialog({
  open,
  onOpenChange,
  hub,
  onSubmit,
}: HubFormDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    hub_id: "",
    lat: 0,
    lon: 0,
    alt: 0,
    max_grid_capacity_kw: 0,
    is_active: true,
    ip_address: "",
    firmware_version: "",
  });

  useEffect(() => {
    if (hub) {
      setFormData({
        hub_id: hub.hub_id,
        lat: hub.lat || 0,
        lon: hub.lon || 0,
        alt: hub.alt || 0,
        max_grid_capacity_kw: hub.max_grid_capacity_kw,
        is_active: hub.is_active,
        ip_address: "",
        firmware_version: "",
      });
    } else {
      setFormData({
        hub_id: "",
        lat: 0,
        lon: 0,
        alt: 0,
        max_grid_capacity_kw: 0,
        is_active: true,
        ip_address: "",
        firmware_version: "",
      });
    }
  }, [hub, open]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (hub) {
        const updateData: HubUpdate = {
          lat: formData.lat,
          lon: formData.lon,
          alt: formData.alt,
          max_grid_capacity_kw: formData.max_grid_capacity_kw,
          is_active: formData.is_active,
          ip_address: formData.ip_address,
          firmware_version: formData.firmware_version,
        };
        await onSubmit(updateData);
      } else {
        const createData: HubCreate = {
          hub_id: formData.hub_id,
          lat: formData.lat,
          lon: formData.lon,
          alt: formData.alt,
          max_grid_capacity_kw: formData.max_grid_capacity_kw,
          is_active: formData.is_active,
          ip_address: formData.ip_address,
          firmware_version: formData.firmware_version,
        };
        await onSubmit(createData);
      }
      onOpenChange(false);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{hub ? "Edit Hub" : "Create Hub"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!hub && (
            <div className="space-y-2">
              <Label htmlFor="hub_id">Hub ID</Label>
              <Input
                id="hub_id"
                value={formData.hub_id}
                onChange={(e) => setFormData({ ...formData, hub_id: e.target.value })}
                placeholder="Enter hub ID"
                required
              />
            </div>
          )}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="lat">Latitude</Label>
              <Input
                id="lat"
                type="number"
                step="0.000001"
                value={formData.lat}
                onChange={(e) => setFormData({ ...formData, lat: parseFloat(e.target.value) || 0 })}
                placeholder="Latitude"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lon">Longitude</Label>
              <Input
                id="lon"
                type="number"
                step="0.000001"
                value={formData.lon}
                onChange={(e) => setFormData({ ...formData, lon: parseFloat(e.target.value) || 0 })}
                placeholder="Longitude"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="alt">Altitude</Label>
              <Input
                id="alt"
                type="number"
                step="0.1"
                value={formData.alt}
                onChange={(e) => setFormData({ ...formData, alt: parseFloat(e.target.value) || 0 })}
                placeholder="Altitude"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="max_grid_capacity_kw">Max Grid Capacity (kW)</Label>
            <Input
              id="max_grid_capacity_kw"
              type="number"
              min="0"
              step="0.1"
              value={formData.max_grid_capacity_kw}
              onChange={(e) =>
                setFormData({ ...formData, max_grid_capacity_kw: parseFloat(e.target.value) || 0 })
              }
              placeholder="Enter max grid capacity"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="ip_address">IP Address</Label>
              <Input
                id="ip_address"
                value={formData.ip_address}
                onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                placeholder="192.168.1.100"
                required={!hub}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="firmware_version">Firmware Version</Label>
              <Input
                id="firmware_version"
                value={formData.firmware_version}
                onChange={(e) => setFormData({ ...formData, firmware_version: e.target.value })}
                placeholder="1.0.0"
                required={!hub}
              />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="is_active">Active</Label>
            <Switch
              id="is_active"
              checked={formData.is_active}
              onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || (!hub && (!formData.hub_id || !formData.ip_address || !formData.firmware_version))}>
              {isLoading ? "Saving..." : hub ? "Update" : "Create"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
