"use client";

import React from "react"

import { AppSidebar } from "./app-sidebar";
import { Toaster } from "@/components/ui/sonner";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex h-screen bg-background">
      <AppSidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
      <Toaster position="top-right" />
    </div>
  );
}
