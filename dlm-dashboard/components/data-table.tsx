"use client";

import React from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

interface Column<T> {
  key: string;
  header: string;
  cell?: (item: T) => React.ReactNode;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (item: T) => void;
  getRowKey?: (item: T, index: number) => string;
}

export function DataTable<T>({
  columns,
  data,
  isLoading,
  emptyMessage = "No data found",
  onRowClick,
  getRowKey = (item: any, index: number) => `${item.id || item.node_id || item.hub_id || item.vehicle_id || item.charging_session_id || item.dlm_event_id || 'item'}-${index}`,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const renderCell = (column: Column<T>, item: T) => {
    if (column.render) return column.render(item);
    if (column.cell) return column.cell(item);
    return null;
  };

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent border-b border-border">
            {columns.map((column, i) => (
              <TableHead
                key={`${column.key}-${i}`}
                className={cn(
                  "text-xs font-medium uppercase tracking-wide text-muted-foreground bg-muted/30",
                  column.className
                )}
              >
                {column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-32 text-center text-muted-foreground">
                {emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            data.map((item, i) => (
              <TableRow
                key={getRowKey(item, i)}
                onClick={() => onRowClick?.(item)}
                className={cn(
                  "transition-colors border-b border-border last:border-0",
                  onRowClick && "cursor-pointer hover:bg-muted/50"
                )}
              >
                {columns.map((column, i) => (
                  <TableCell key={`${column.key}-${i}`} className={cn("text-card-foreground", column.className)}>
                    {renderCell(column, item)}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
