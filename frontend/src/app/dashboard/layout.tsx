"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/dashboard/Sidebar";
import Link from "next/link";
import { Zap, ShieldCheck, Search, Bell, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simMessage, setSimMessage] = useState<string | null>(null);

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const res = await api.simulateStormResponse();
      setSimMessage(res.message || "Simulating Storm Response Protocol...");
      setTimeout(() => setSimMessage(null), 8000);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-navy-950 flex">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Shell */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          sidebarCollapsed ? "lg:pl-20" : "lg:pl-64"
        }`}
      >
        {/* Top Command Bar */}
        <header className="sticky top-0 z-30 h-16 glass-panel border-b border-white/10 px-4 sm:px-8 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono font-bold text-amber-400/90 uppercase tracking-wider hidden sm:inline-block">
              Campus Command Center
            </span>
            <span className="text-xs font-mono text-slate-500 hidden sm:inline-block">|</span>
            <span className="text-xs font-mono text-slate-400 truncate">
              University & Hospital Multi-Facility Fleet
            </span>
          </div>

          <div className="flex items-center gap-3">
            {simMessage && (
              <span className="text-xs font-mono text-amber-300 bg-amber-500/10 px-3 py-1 rounded border border-amber-500/30 animate-pulse hidden md:inline-block">
                {simMessage}
              </span>
            )}

            {/* Quick Simulate Button */}
            <button
              onClick={handleSimulate}
              disabled={isSimulating}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-navy-950 text-xs font-bold shadow-md shadow-amber-500/20 transition-all active:scale-95 disabled:opacity-50"
            >
              <Zap className="w-3.5 h-3.5 fill-navy-950" />
              <span>{isSimulating ? "Simulating..." : "Simulate Storm"}</span>
            </button>

            <Link
              href="/"
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
              title="Return to Public Landing Page"
            >
              <ExternalLink className="w-4 h-4" />
            </Link>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="p-4 sm:p-8 flex-1 max-w-7xl w-full mx-auto space-y-8">
          {children}
        </main>
      </div>
    </div>
  );
}
