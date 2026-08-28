"use client";

import React, { useEffect, useState } from "react";
import { MetricsStrip } from "@/components/dashboard/MetricsStrip";
import { AgentStatusGrid } from "@/components/dashboard/AgentStatusGrid";
import { IncidentTimeline } from "@/components/dashboard/IncidentTimeline";
import { LiveEventFeed } from "@/components/dashboard/LiveEventFeed";
import { Incident, AgentManifest, DashboardMetrics } from "@/lib/types";
import { api } from "@/lib/api";
import { AlertTriangle, Plus, Zap, RefreshCw } from "lucide-react";

export default function DashboardOverviewPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [agents, setAgents] = useState<AgentManifest[]>([]);
  const [loading, setLoading] = useState(true);
  const [intakeText, setIntakeText] = useState("");
  const [isIntaking, setIsIntaking] = useState(false);

  const loadData = async () => {
    try {
      const [m, incs, ags] = await Promise.all([
        api.getMetrics().catch(() => null),
        api.getIncidents().catch(() => []),
        api.getAgents().catch(() => []),
      ]);
      if (m) setMetrics(m);
      if (incs) setIncidents(incs);
      if (ags) setAgents(ags);
    } catch (err) {
      console.error("Dashboard load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleManualIntake = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!intakeText.trim()) return;
    setIsIntaking(true);
    try {
      await api.createIncident({
        title: "Manual Operator Report",
        description: intakeText,
        building_id: "BLDG-C",
      });
      setIntakeText("");
      await loadData();
    } catch (err) {
      console.error("Failed to create incident:", err);
    } finally {
      setIsIntaking(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Header & Fast Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Operational Overview
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Autonomous Triage, Interdependency Mapping & Governance
          </p>
        </div>

        <button
          onClick={loadData}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 hover:text-white transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh State</span>
        </button>
      </div>

      {/* Metrics Strip */}
      <MetricsStrip metrics={metrics} />

      {/* Agent Status Fleet Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
            Governed Agent Swarm
          </h3>
          <span className="text-[11px] font-mono text-purple-400">
            Google ADK 2.6.2 Orchestrated
          </span>
        </div>
        <AgentStatusGrid agents={agents} />
      </div>

      {/* Manual Intake Box */}
      <form
        onSubmit={handleManualIntake}
        className="glass-panel rounded-2xl p-4 border border-white/10 flex flex-col sm:flex-row items-center gap-3"
      >
        <input
          type="text"
          placeholder="Inject real-time signal (e.g. 'Chilled water pressure dropped 40 PSI in Building C basement')..."
          value={intakeText}
          onChange={(e) => setIntakeText(e.target.value)}
          className="flex-1 w-full bg-navy-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500/50 font-mono"
        />
        <button
          type="submit"
          disabled={isIntaking || !intakeText.trim()}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-navy-950 text-xs font-bold transition-all disabled:opacity-50 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>{isIntaking ? "Dispatching..." : "Inject Signal"}</span>
        </button>
      </form>

      {/* Two Column Layout: Timeline vs Live Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Incidents Timeline */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
              Campus Incident Stream
            </h3>
            <span className="text-xs font-mono text-slate-500">
              {incidents.length} Records
            </span>
          </div>
          <IncidentTimeline incidents={incidents} />
        </div>

        {/* Right Column: Live Event Stream Feed */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
              Real-Time Telemetry & Audits
            </h3>
            <span className="text-xs font-mono text-emerald-400">WebSocket Connected</span>
          </div>
          <LiveEventFeed onNewEvent={() => loadData()} />
        </div>
      </div>
    </div>
  );
}
