"use client";

import { useEffect, useState, useCallback } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { StatusBadge } from "@/components/status-badge";
import { NodeFormDialog } from "@/components/node-form-dialog";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import api from "@/lib/api";
import type { Node, NodeCreate, NodeUpdate, Hub } from "@/lib/types";
import { Plus, Pencil, Trash2, CircuitBoard } from "lucide-react";

export default function NodesPage() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [hubs, setHubs] = useState<Hub[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [editingNode, setEditingNode] = useState<Node | null>(null);
  const [deleteNode, setDeleteNode] = useState<Node | null>(null);
  const [hubFilter, setHubFilter] = useState<string>("all");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [nodesRes, hubsRes] = await Promise.all([
        api.listNodes({ limit: 100, hub_id: hubFilter !== "all" ? hubFilter : undefined }),
        api.listHubs({ limit: 100 }),
      ]);
      setNodes(nodesRes.items);
      setHubs(hubsRes.items);
    } catch (error) {
      toast.error("Failed to fetch nodes");
    } finally {
      setIsLoading(false);
    }
  }, [hubFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async (data: NodeCreate | NodeUpdate) => {
    try {
      await api.createNode(data as NodeCreate);
      toast.success("Node created successfully");
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create node");
      throw error;
    }
  };

  const handleUpdate = async (data: NodeCreate | NodeUpdate) => {
    if (!editingNode) return;
    try {
      await api.updateNode(editingNode.node_id, data as NodeUpdate);
      toast.success("Node updated successfully");
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update node");
      throw error;
    }
  };

  const handleDelete = async () => {
    if (!deleteNode) return;
    try {
      await api.deleteNode(deleteNode.node_id);
      toast.success("Node deleted successfully");
      setDeleteNode(null);
      fetchData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to delete node");
    }
  };

  const getHubName = (hubId: string) => {
    const hub = hubs.find((h) => h.hub_id === hubId);
    return hub?.hub_id ?? "Unknown Hub";
  };

  const columns = [
    {
      key: "node_id",
      header: "Node ID",
      render: (node: Node) => (
        <div className="flex items-center gap-2">
          <CircuitBoard className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">{node.node_id}</span>
        </div>
      ),
    },
    {
      key: "hub",
      header: "Hub",
      render: (node: Node) => (
        <span className="text-muted-foreground">{getHubName(node.hub_id)}</span>
      ),
    },
    {
      key: "max_power_kw",
      header: "Max Power",
      render: (node: Node) => <span>{node.max_power_kw} kW</span>,
    },
    {
      key: "maintenance",
      header: "Status",
      render: (node: Node) => <StatusBadge status={node.is_maintenance ? "maintenance" : "available"} />,
    },
    {
      key: "actions",
      header: "",
      render: (node: Node) => (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setEditingNode(node);
              setFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDeleteNode(node)}
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
        title="Charging Nodes"
        description="Manage charging nodes across your hubs"
      >
        <Button onClick={() => { setEditingNode(null); setFormOpen(true); }}>
          <Plus className="mr-2 h-4 w-4" />
          Add Node
        </Button>
      </PageHeader>

      <div className="p-6">
        <div className="mb-4 flex items-center gap-4">
          <label className="text-sm text-muted-foreground">Filter by Hub:</label>
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

        <DataTable
          columns={columns}
          data={nodes}
          isLoading={isLoading}
          emptyMessage="No nodes found. Create your first charging node."
        />
      </div>

      <NodeFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        node={editingNode}
        hubs={hubs}
        onSubmit={editingNode ? handleUpdate : handleCreate}
      />

      <ConfirmDialog
        open={!!deleteNode}
        onOpenChange={(open) => !open && setDeleteNode(null)}
        title="Delete Node"
        description={`Are you sure you want to delete "${deleteNode?.node_id}"? This action cannot be undone.`}
        onConfirm={handleDelete}
        confirmLabel="Delete"
        variant="destructive"
      />
    </DashboardLayout>
  );
}
