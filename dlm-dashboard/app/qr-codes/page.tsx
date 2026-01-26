"use client";

import { useEffect, useState, useCallback } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StatusBadge } from "@/components/status-badge";
import { toast } from "sonner";
import api from "@/lib/api";
import type { Node, Hub } from "@/lib/types";
import { QrCode, CircuitBoard, Download, RefreshCw, Clock, Building2 } from "lucide-react";

export default function QRCodesPage() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [hubs, setHubs] = useState<Hub[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string>("");
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [nodesRes, hubsRes] = await Promise.all([
        api.listNodes({ limit: 100 }),
        api.listHubs({ limit: 100 }),
      ]);
      setNodes(nodesRes.items);
      setHubs(hubsRes.items);

      if (nodesRes.items.length > 0 && !selectedNodeId) {
        setSelectedNodeId(nodesRes.items[0].node_id);
      }
    } catch (error) {
      toast.error("Failed to fetch nodes");
    } finally {
      setIsLoading(false);
    }
  }, [selectedNodeId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const generateQRCode = async () => {
    if (!selectedNodeId) return;

    setIsGenerating(true);
    try {
      const result = await api.getQRCode(selectedNodeId);
      setQrCode(result);
      toast.success("QR code generated successfully");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to generate QR code");
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadQRCode = () => {
    if (!qrCode) return;

    const link = document.createElement("a");
    link.href = qrCode;
    link.download = `qr-code-${selectedNodeId}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("QR code downloaded");
  };

  const selectedNode = nodes.find((n) => n.node_id === selectedNodeId);

  const getHubName = (hubId: string) => {
    const hub = hubs.find((h) => h.hub_id === hubId);
    return hub ? hub.hub_id : hubId;
  };

  return (
    <DashboardLayout>
      <PageHeader
        title="QR Codes"
        description="Generate QR codes for charging nodes"
      />

      <div className="p-6">
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Node Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-card-foreground">
                <CircuitBoard className="h-5 w-5 text-primary" />
                Select Node
              </CardTitle>
              <CardDescription>
                Choose a charging node to generate its QR code
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex h-40 items-center justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : nodes.length === 0 ? (
                <div className="rounded-lg border border-border bg-muted/50 p-6 text-center">
                  <CircuitBoard className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 text-lg font-medium text-card-foreground">No Nodes Available</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Create charging nodes first to generate QR codes.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <Select value={selectedNodeId} onValueChange={setSelectedNodeId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a node" />
                    </SelectTrigger>
                    <SelectContent>
                      {nodes.map((node, i) => (
                        <SelectItem key={`${node.node_id}-${i}`} value={node.node_id}>
                          <div className="flex items-center gap-2">
                            <CircuitBoard className="h-4 w-4" />
                            {node.node_id}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {selectedNode && (
                    <div className="rounded-lg border border-border p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Node ID</span>
                        <span className="font-medium text-card-foreground">{selectedNode.node_id}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Hub</span>
                        <div className="flex items-center gap-1">
                          <Building2 className="h-3 w-3 text-muted-foreground" />
                          <span className="text-sm text-card-foreground">{getHubName(selectedNode.hub_id)}</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Maintenance</span>
                        <span className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium">
                          {selectedNode.is_maintenance ? "Yes" : "No"}
                        </span>
                      </div>
                    </div>
                  )}

                  <Button
                    className="w-full"
                    onClick={generateQRCode}
                    disabled={!selectedNodeId || isGenerating}
                  >
                    {isGenerating ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <QrCode className="mr-2 h-4 w-4" />
                        Generate QR Code
                      </>
                    )}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* QR Code Display */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-card-foreground">
                <QrCode className="h-5 w-5 text-primary" />
                QR Code
              </CardTitle>
              <CardDescription>
                Scan this code to start charging at the selected node
              </CardDescription>
            </CardHeader>
            <CardContent>
              {qrCode ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-center rounded-lg border border-border bg-white p-6">
                    <img
                      src={qrCode}
                      alt="QR Code"
                      className="h-64 w-64"
                    />
                  </div>

                  <div className="rounded-lg border border-border p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Node ID</span>
                      <span className="font-mono text-sm text-card-foreground">{selectedNodeId.slice(0, 12)}...</span>
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    className="w-full bg-transparent"
                    onClick={downloadQRCode}
                    disabled={!qrCode}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download QR Code
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="rounded-full bg-muted p-6">
                    <QrCode className="h-16 w-16 text-muted-foreground" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-card-foreground">No QR Code Generated</h3>
                  <p className="mt-2 text-center text-sm text-muted-foreground">
                    Select a node and click "Generate QR Code" to create a scannable code
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
