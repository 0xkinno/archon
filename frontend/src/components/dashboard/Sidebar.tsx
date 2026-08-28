"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  AlertTriangle,
  Users,
  BrainCircuit,
  Activity,
  CheckCircle,
  Building2,
  ShieldAlert,
  Radio,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

const NAV_ITEMS = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Incidents", href: "/dashboard/incidents", icon: AlertTriangle },
  { label: "Agent Fleet", href: "/dashboard/agents", icon: Users },
  { label: "Memory Bank", href: "/dashboard/memory", icon: BrainCircuit },
  { label: "Traces & Audit", href: "/dashboard/traces", icon: Activity },
  { label: "Approvals", href: "/dashboard/approvals", icon: CheckCircle },
  { label: "Campus Map", href: "/dashboard/campus", icon: Building2 },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed = false, onToggle }) => {
  const pathname = usePathname();

  return (
    <aside
      className={`fixed left-0 top-0 bottom-0 z-40 bg-navy-950/95 backdrop-blur-xl border-r border-white/10 flex flex-col justify-between transition-all duration-300 ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      <div>
        {/* Brand Header */}
        <div className="h-16 px-5 border-b border-white/10 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold shrink-0">
              <ShieldAlert className="w-5 h-5" />
            </span>
            {!collapsed && (
              <span className="text-base font-extrabold tracking-wider text-white">
                ARCHON
              </span>
            )}
          </Link>
          {onToggle && (
            <button
              onClick={onToggle}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors hidden lg:block"
            >
              {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          )}
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1.5 mt-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
                }`}
                title={collapsed ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-amber-400" : "text-slate-400"}`} />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Live System Indicator */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3">
          <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-400 pulse-dot-green shrink-0" />
          {!collapsed && (
            <div className="text-[11px] font-mono leading-tight">
              <div className="text-emerald-400 font-bold">GEAP FLEET ONLINE</div>
              <div className="text-slate-500">Zero-Trust Guardrails Active</div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};
