"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Incident, RemediationTask, DispatchRecord, Span } from "@/lib/types";
import { SeverityIndicator } from "@/components/shared/SeverityIndicator";
import { StatusPill } from "@/components/shared/StatusPill";
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
  CheckCircle2,
  KeyRound,
  FileCheck,
} from "lucide-react";
import { formatTimeAgo, formatCurrency } from "@/lib/utils";

export default function IncidentDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [incident, setIncident] = useState<Incident | null>(null);
  const [tasks, setTasks] = useState<RemediationTask[]>([]);
  const [dispatches, setDispatches] = useState<DispatchRecord[]>([]);
  const [spans, setSpans] = useState<Span[]>([]);
  const [verifierData, setVerifierData] = useState<any>(null);
  const [verifying, setVerifying] = useState(false);
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

  const handleRunVerifier = async () => {
    setVerifying(true);
    try {
      const vResult = await api.verifyIncidentInvariants(id);
      setVerifierData(vResult);
    } catch (e) {
      console.error(e);
    } finally {
      setVerifying(false);
    }
  };

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

      {/* Main Grid: Left Column = Governance & Operations, Right Column = Swarm Trace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: 7 cols */}
        <div className="lg:col-span-7 space-y-6">
          {/* Live Governance Invariant Verification Card */}
          <div className="glass-panel rounded-2xl p-6 border border-emerald-500/30 bg-emerald-950/10 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                  Governance Invariant Verifier &amp; Ed25519 State Proof
                </h3>
              </div>
              <button
                onClick={handleRunVerifier}
                disabled={verifying}
                className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-mono text-xs font-bold border border-emerald-500/40 transition-colors flex items-center gap-1.5"
              >
                <FileCheck className="w-3.5 h-3.5" />
                <span>{verifying ? "Auditing..." : "Run Invariant Verifier"}</span>
              </button>
            </div>

            <p className="text-xs text-slate-300 font-mono leading-relaxed">
              Deterministic Safety Kernel verifies financial thresholds, least-privilege domain scope, exactly-once dispatch, and cryptographic state hash integrity independently of live LLM inference.
            </p>

            {verifierData ? (
              <div className="space-y-3 pt-2">
                <div className="p-3 rounded-xl bg-black/40 border border-emerald-500/30 text-xs font-mono space-y-1.5">
                  <div className="flex items-center justify-between text-emerald-300 font-bold">
                    <span>STATUS: {verifierData.verified_pass ? "ALL INVARIANTS SATISFIED (PASS)" : "VIOLATION DETECTED"}</span>
                    <span>{verifierData.passed_invariants_count} / {verifierData.total_invariants_count}</span>
                  </div>
                  <div className="text-slate-400 truncate text-[11px]">
                    <span className="text-slate-500">State Hash:</span> {verifierData.state_hash}
                  </div>
                  <div className="text-slate-400 truncate text-[11px] flex items-center gap-1">
                    <KeyRound className="w-3 h-3 text-amber-400" />
                    <span className="text-slate-500">Ed25519 Sig:</span> {verifierData.signature?.slice(0, 32)}...
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono max-h-48 overflow-y-auto pr-1">
                  {verifierData.results?.map((r: any) => (
                    <div
                      key={r.invariant_id}
                      className={`p-2 rounded-lg border flex items-center justify-between ${
                        r.holds
                          ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-200"
                          : "bg-rose-950/20 border-rose-500/30 text-rose-200"
                      }`}
                    >
                      <span>{r.invariant_id}: {r.title}</span>
                      <span className="font-bold">{r.holds ? "PASS" : "FAIL"}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px] font-mono">
                <div className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200">INV-01: &gt;$10k Gated</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200">INV-02: Zero Taint</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200">INV-03: Scope Bound</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200">INV-04: No Dup Dispatch</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200">INV-05: P1 Escalation</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-slate-200">INV-10: Ed25519 Signed</span>
                </div>
              </div>
            )}
          </div>

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

        {/* Right Column: 5 cols — Reasoning Chain Traces */}
        <div className="lg:col-span-5 space-y-4">
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
