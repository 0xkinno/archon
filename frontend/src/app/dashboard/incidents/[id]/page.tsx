"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Incident, RemediationTask, DispatchRecord, Span } from "@/lib/types";
import { SeverityIndicator } from "@/components/shared/SeverityIndicator";
import { StatusPill } from "@/components/shared/StatusPill";
import { AgentBadge } from "@/components/shared/AgentBadge";
import { TraceTimeline } from "@/components/shared/TraceTimeline";
import {
  ArrowLeft,
  Building2,
  Clock,
  Truck,
  CheckSquare,
  Activity,
  Layers,
  ShieldCheck,
} from "lucide-react";
import { formatTimeAgo, formatCurrency } from "@/lib/utils";

export default function IncidentDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [incident, setIncident] = useState<Incident | null>(null);
  const [tasks, setTasks] = useState<RemediationTask[]>([]);
  const [dispatches, setDispatches] = useState<DispatchRecord[]>([]);
  const [spans, setSpans] = useState<Span[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getIncidentDetail(id);
        if (data.incident) setIncident(data.incident);
        if (data.tasks) setTasks(data.tasks);
        if (data.dispatches) setDispatches(data.dispatches);
        if (data.spans) setSpans(data.spans);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return <div className="py-20 text-center text-slate-500 font-mono text-xs">Loading incident record...</div>;
  }

  if (!incident) {
    return (
      <div className="py-20 text-center space-y-3">
        <div className="text-white text-lg font-bold">Incident Not Found</div>
        <Link href="/dashboard/incidents" className="text-amber-400 text-xs font-mono underline">
          Return to Incident Stream
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Back Link */}
      <Link
        href="/dashboard/incidents"
        className="inline-flex items-center gap-2 text-xs font-mono text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Incident Stream</span>
      </Link>

      {/* Incident Header Card */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <SeverityIndicator severity={incident.severity} size="md" withPulse={incident.status !== "resolved"} />
            <StatusPill status={incident.status} />
            <span className="text-xs font-mono text-slate-400">{incident.id}</span>
          </div>
          <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            Created {formatTimeAgo(incident.created_at)}
          </span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          {incident.title}
        </h1>

        <p className="text-sm text-slate-200 leading-relaxed max-w-4xl bg-navy-950/70 p-4 rounded-xl border border-white/5 font-mono">
          {incident.description}
        </p>

        <div className="flex flex-wrap items-center gap-6 pt-2 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-1.5">
            <Building2 className="w-4 h-4 text-amber-400" />
            <span>Affected Buildings:</span>
            <span className="text-white font-bold">
              {incident.affected_buildings?.join(", ") || "Campus Wide"}
            </span>
          </div>

          {incident.playbook_id && (
            <div className="flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-purple-400" />
              <span>Active Playbook:</span>
              <span className="text-purple-300 font-bold">{incident.playbook_id}</span>
            </div>
          )}
        </div>
      </div>

      {/* Grid: Tasks & Dispatches vs Observability Trace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Work Orders & Contractor Dispatches */}
        <div className="lg:col-span-6 space-y-6">
          {/* Dispatches Card */}
          <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-teal-400" />
                <h3 className="text-sm font-bold text-white uppercase font-mono">
                  Contractor Dispatches ({dispatches.length})
                </h3>
              </div>
              <span className="text-[11px] font-mono text-teal-400">Auto-Dispatched</span>
            </div>

            {dispatches.length === 0 ? (
              <div className="py-6 text-center text-xs text-slate-500 font-mono">
                No external contractors dispatched for this event.
              </div>
            ) : (
              <div className="space-y-3">
                {dispatches.map((d) => (
                  <div key={d.dispatch_id} className="p-4 rounded-xl bg-navy-950/80 border border-white/5 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{d.vendor_name}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/30">
                        {d.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 font-mono">{d.description}</p>
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1">
                      <span>ETA: {d.estimated_arrival_hours} hours</span>
                      <span className="text-emerald-400 font-bold">{formatCurrency(d.estimated_cost)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Remediation Tasks Card */}
          <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <CheckSquare className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white uppercase font-mono">
                  Corrective Work Orders ({tasks.length})
                </h3>
              </div>
              <span className="text-[11px] font-mono text-emerald-400">Remediation Tracker</span>
            </div>

            {tasks.length === 0 ? (
              <div className="py-6 text-center text-xs text-slate-500 font-mono">
                No open work orders recorded.
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.map((t) => (
                  <div key={t.task_id} className="p-4 rounded-xl bg-navy-950/80 border border-white/5 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{t.title}</span>
                      <StatusPill status={t.status} />
                    </div>
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                      <span>Assignee: {t.assignee}</span>
                      {t.deadline && <span>Due: {formatTimeAgo(t.deadline)}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Reasoning Chain Traces */}
        <div className="lg:col-span-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white uppercase font-mono">
                Distributed Reasoning Trace
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-500">
              OpenTelemetry Verified
            </span>
          </div>

          <div className="glass-panel rounded-2xl p-6 border border-white/10">
            <TraceTimeline spans={spans} />
          </div>
        </div>
      </div>
    </div>
  );
}
