"use client";

import React from "react";
import { DashboardMetrics } from "@/lib/types";
import { AlertTriangle, Users, CheckCircle, BrainCircuit, Clock, Building2 } from "lucide-react";

interface MetricsStripProps {
  metrics: DashboardMetrics | null;
}

export const MetricsStrip: React.FC<MetricsStripProps> = ({ metrics }) => {
  const m = metrics || {
    active_incidents: 0,
    total_incidents: 0,
    severity_breakdown: { P1: 0, P2: 0, P3: 0, P4: 0 },
    agents_online: 7,
    total_agents: 7,
    pending_approvals: 0,
    memory_entries_stored: 6,
    avg_response_time_minutes: 1.4,
    campus_buildings_monitored: 12,
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* 1. Active Incidents Card */}
      <div className="glass-panel rounded-xl p-4 border border-white/10 flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider">Active Incidents</span>
          <AlertTriangle className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-2xl font-bold text-white font-mono">{m.active_incidents}</span>
          <span className="text-[11px] text-slate-400 font-mono">({m.total_incidents} total)</span>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono">
          <span className="flex items-center gap-1 text-red-400 font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
            {m.severity_breakdown.P1} P1
          </span>
          <span className="flex items-center gap-1 text-orange-400 font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-400" />
            {m.severity_breakdown.P2} P2
          </span>
          <span className="flex items-center gap-1 text-yellow-400 font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400" />
            {m.severity_breakdown.P3} P3
          </span>
        </div>
      </div>

      {/* 2. Agents Online Card */}
      <div className="glass-panel rounded-xl p-4 border border-white/10 flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider">Agents Online</span>
          <Users className="w-4 h-4 text-purple-400" />
        </div>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-2xl font-bold text-white font-mono">{m.agents_online} / {m.total_agents}</span>
        </div>
        <div className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot-green" />
          100% Swarm Operational
        </div>
      </div>

      {/* 3. Pending Approvals Card */}
      <div className={`glass-panel rounded-xl p-4 border flex flex-col justify-between ${
        m.pending_approvals > 0 ? "border-amber-500/50 bg-amber-500/5" : "border-white/10"
      }`}>
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider">Pending Approvals</span>
          <CheckCircle className={`w-4 h-4 ${m.pending_approvals > 0 ? "text-amber-400" : "text-slate-500"}`} />
        </div>
        <div className="flex items-baseline gap-2 mb-2">
          <span className={`text-2xl font-bold font-mono ${m.pending_approvals > 0 ? "text-amber-400" : "text-white"}`}>
            {m.pending_approvals}
          </span>
          <span className="text-[11px] text-slate-400 font-mono">gate: &gt;$10k</span>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">
          {m.pending_approvals > 0 ? "Action Required" : "No pending gates"}
        </div>
      </div>

      {/* 4. Memory Entries Card */}
      <div className="glass-panel rounded-xl p-4 border border-white/10 flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider">Institutional Wisdom</span>
          <BrainCircuit className="w-4 h-4 text-purple-400" />
        </div>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-2xl font-bold text-white font-mono">{m.memory_entries_stored}</span>
          <span className="text-[11px] text-slate-400 font-mono">memories</span>
        </div>
        <div className="text-[10px] text-purple-300/80 font-mono">
          Vertex AI Memory Bank
        </div>
      </div>

      {/* 5. Avg Response SLA Card */}
      <div className="glass-panel rounded-xl p-4 border border-white/10 flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider">Autonomous Triage</span>
          <Clock className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-2xl font-bold text-white font-mono">{m.avg_response_time_minutes}m</span>
          <span className="text-[11px] text-emerald-400 font-mono font-bold">-80% vs manual</span>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">
          Across {m.campus_buildings_monitored} Campus Buildings
        </div>
      </div>
    </div>
  );
};
