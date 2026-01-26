import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  className?: string;
}

const statusStyles: Record<string, string> = {
  // Active/Available states
  active: "bg-success/10 text-success border-success/20",
  available: "bg-success/10 text-success border-success/20",
  completed: "bg-success/10 text-success border-success/20",
  
  // Warning states
  occupied: "bg-warning/10 text-warning-foreground border-warning/20",
  reserved: "bg-warning/10 text-warning-foreground border-warning/20",
  
  // Error states
  faulted: "bg-destructive/10 text-destructive border-destructive/20",
  failed: "bg-destructive/10 text-destructive border-destructive/20",
  
  // Inactive states
  inactive: "bg-muted text-muted-foreground border-muted",
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const normalizedStatus = status?.toLowerCase();
  const style = statusStyles[normalizedStatus] || "bg-muted text-muted-foreground border-muted";

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize",
        style,
        className
      )}
    >
      {status}
    </span>
  );
}
