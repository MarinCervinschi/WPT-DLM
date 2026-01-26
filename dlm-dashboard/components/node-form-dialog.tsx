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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import type { Node, NodeCreate, NodeUpdate, Hub } from "@/lib/types";

interface NodeFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  node?: Node | null;
  hubs: Hub[];
  onSubmit: (data: NodeCreate | NodeUpdate) => Promise<void>;
}

export function NodeFormDialog({
  open,
  onOpenChange,
  node,
  hubs,
  onSubmit,
}: NodeFormDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    node_id: "",
    hub_id: "",
    max_power_kw: 50,
    is_maintenance: false,
  });

  useEffect(() => {
    if (node) {
      setFormData({
        node_id: node.node_id,
        hub_id: node.hub_id,
        max_power_kw: node.max_power_kw,
        is_maintenance: node.is_maintenance,
      });
    } else {
      setFormData({
        node_id: "",
        hub_id: hubs[0]?.hub_id ?? "",
        max_power_kw: 50,
        is_maintenance: false,
      });
    }
  }, [node, hubs, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (node) {
        const updateData: NodeUpdate = {
          max_power_kw: formData.max_power_kw,
          is_maintenance: formData.is_maintenance,
        };
        await onSubmit(updateData);
      } else {
        const createData: NodeCreate = {
          node_id: formData.node_id,
          hub_id: formData.hub_id,
          max_power_kw: formData.max_power_kw,
          is_maintenance: formData.is_maintenance,
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
            {node ? "Edit Node" : "Create New Node"}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!node && (
            <>
              <div className="space-y-2">
                <Label htmlFor="hub_id" className="text-card-foreground">Hub</Label>
                <Select
                  value={formData.hub_id}
                  onValueChange={(value) => setFormData({ ...formData, hub_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a hub" />
                  </SelectTrigger>
                  <SelectContent>
                    {hubs.map((hub, i) => (
                      <SelectItem key={`${hub.hub_id}-${i}`} value={hub.hub_id}>
                        {hub.hub_id}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="node_id" className="text-card-foreground">Node ID</Label>
                <Input
                  id="node_id"
                  value={formData.node_id}
                  onChange={(e) => setFormData({ ...formData, node_id: e.target.value })}
                  placeholder="e.g., NODE_001"
                  required
                />
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="max_power_kw" className="text-card-foreground">Max Power (kW)</Label>
            <Input
              id="max_power_kw"
              type="number"
              value={formData.max_power_kw}
              onChange={(e) => setFormData({ ...formData, max_power_kw: Number(e.target.value) })}
              min={1}
              required
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="is_maintenance" className="text-card-foreground">Maintenance Mode</Label>
            <Switch
              id="is_maintenance"
              checked={formData.is_maintenance}
              onCheckedChange={(checked) => setFormData({ ...formData, is_maintenance: checked })}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || (!node && (!formData.node_id || !formData.hub_id))}>
              {isSubmitting ? "Saving..." : node ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
