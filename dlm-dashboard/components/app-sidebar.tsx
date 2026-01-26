"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  CircuitBoard,
  Car,
  Activity,
  BarChart3,
  QrCode,
  Zap,
  Cloud,
  Cpu,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Hubs", href: "/hubs", icon: Building2 },
  { name: "Nodes", href: "/nodes", icon: CircuitBoard },
  { name: "Vehicles", href: "/vehicles", icon: Car },
  { name: "Sessions", href: "/sessions", icon: Activity },
  { name: "DLM Events", href: "/dlm-events", icon: BarChart3 },
  { name: "QR Codes", href: "/qr-codes", icon: QrCode },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border">
      <div className="flex h-16 items-center gap-3 px-6 border-b border-sidebar-border">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sidebar-primary">
          <Zap className="h-5 w-5 text-sidebar-primary-foreground" />
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold tracking-tight">WPT-DLM</span>
          <span className="text-xs text-sidebar-foreground/60">EV Charging Manager</span>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4">
        <ul className="space-y-1">
          {navigation.map((item, i) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <li key={`${item.name}-${i}`}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-primary text-sidebar-primary-foreground"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="border-t border-sidebar-border p-4">
        <div className="rounded-lg bg-sidebar-accent/50 p-3">
          <div className="flex items-center gap-2 text-xs text-sidebar-foreground/70">
            <Cloud className="h-3.5 w-3.5" />
            <span>Cloud Connected</span>
          </div>
          <div className="mt-2 flex items-center gap-2 text-xs text-sidebar-foreground/70">
            <Cpu className="h-3.5 w-3.5" />
            <span>Digital Twin Active</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
