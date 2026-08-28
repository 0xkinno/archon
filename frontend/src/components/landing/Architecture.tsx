"use client";

import React from "react";
import { motion } from "framer-motion";
import { Layers, ArrowDown, Shield, Server, Cpu, Database } from "lucide-react";

export const Architecture: React.FC = () => {
  const steps = [
    {
      num: 1,
      title: "Signal Ingestion",
      desc: "IoT BMS webhooks, vendor emails, operator logs, and inspection calendar triggers arrive at the platform perimeter.",
    },
    {
      num: 2,
      title: "Model Armor Firewall",
      desc: "Screens for 16 prompt injection patterns, redacts 5 PII types, and isolates tool poisoning payload attempts.",
    },
    {
      num: 3,
      title: "Agent Gateway Policy Engine",
      desc: "Authenticates SPIFFE IDs, evaluates domain boundaries, checks rate limits, and flags high-cost dispatches ($10k+).",
    },
    {
      num: 4,
      title: "Dynamic Playbook & Fleet Swarm",
      desc: "Incident Commander selects specialized playbook and delegates to Impact, Vendor, Compliance, Comms, and Remediation agents.",
    },
    {
      num: 5,
      title: "Persistent State & Memory Bank",
      desc: "All state persists to Firestore and permanent operational wisdom is retained in Google Vertex AI Memory Bank.",
    },
    {
      num: 6,
      title: "OpenTelemetry Observability",
      desc: "Distributed traces and hierarchical reasoning chains are broadcast live over WebSockets to the Operations Dashboard.",
    },
  ];

  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 border-t border-white/5 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <Layers className="w-3.5 h-3.5" />
            System Architecture
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Built on Google's Enterprise Agent Platform
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            A deterministic pipeline connecting real-world physical telemetry to governed AI specialist agents.
          </p>
        </div>

        {/* ASCII/Visual Request Flow Diagram */}
        <div className="glass-panel rounded-2xl p-8 mb-16 border border-white/10 overflow-x-auto">
          <div className="min-w-[650px] font-mono text-xs text-slate-300 leading-relaxed bg-navy-950/80 p-6 rounded-xl border border-white/5 space-y-2">
            <div className="text-amber-400 font-bold">SIGNAL ARRIVAL (IoT Webhooks | Vendor Emails | Operator Logs | Inspection Feeds)</div>
            <div className="text-slate-600">       │</div>
            <div className="text-slate-600">       ▼</div>
            <div className="text-red-400 font-bold">[ 1. MODEL ARMOR FIREWALL ] ── Scans 16 Injections | Redacts 5 PII Types | Quarantines Poisoning</div>
            <div className="text-slate-600">       │</div>
            <div className="text-slate-600">       ▼</div>
            <div className="text-blue-400 font-bold">[ 2. AGENT GATEWAY ] ──────── Enforces Zero-Trust SPIFFE Identity | $10k Gate | Domain Scoping</div>
            <div className="text-slate-600">       │</div>
            <div className="text-slate-600">       ▼</div>
            <div className="text-purple-400 font-bold">[ 3. AGENT REGISTRY ] ─────── Discovers Dynamic Playbook & Ordered Specialist Fleet Sequence</div>
            <div className="text-slate-600">       │</div>
            <div className="text-slate-600">       ▼</div>
            <div className="text-emerald-400 font-bold">[ 4. INCIDENT COMMANDER ] ─── Severity Triage (P1-P4) & Google ADK transfer_to_agent Swarm</div>
            <div className="text-slate-600">       ├──► [ impact_assessor ] ──────── Topological Dependency Graph & Chilled Water Loops</div>
            <div className="text-slate-600">       ├──► [ vendor_coordinator ] ──── Contract SLA Auditing & Emergency Auto-Dispatch</div>
            <div className="text-slate-600">       ├──► [ compliance_inspector ] ── Fire Marshal & OSHA Pre-Audit Packet Assembly</div>
            <div className="text-slate-600">       ├──► [ communications_officer ]  Multi-Tier Alert Broadcasting (SMS, Email, Radio)</div>
            <div className="text-slate-600">       ├──► [ remediation_tracker ] ─── Work Orders, Deadlines & Shift Handoff Logs</div>
            <div className="text-slate-600">       └──► [ memory_curator ] ──────── Vertex AI Memory Bank Permanent Wisdom Retention</div>
            <div className="text-slate-600">       │</div>
            <div className="text-slate-600">       ▼</div>
            <div className="text-cyan-400 font-bold">[ 5. OBSERVABILITY & AUDIT ] ─ OpenTelemetry Traces | WebSocket Stream | Next.js Command UI</div>
          </div>
        </div>

        {/* Step by Step Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {steps.map((step) => (
            <div key={step.num} className="glass-panel rounded-xl p-6 border border-white/10 space-y-3">
              <span className="h-8 w-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-sm font-mono font-bold text-amber-400">
                {step.num}
              </span>
              <h3 className="text-base font-bold text-white">{step.title}</h3>
              <p className="text-xs text-slate-300 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
