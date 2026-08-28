"use client";

import React from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Cpu, Database, Fingerprint, Lock, ShieldAlert, Activity } from "lucide-react";

const GEAP_SUBSYSTEMS = [
  {
    number: "01",
    name: "Agent Registry",
    icon: Database,
    tech: "Firestore-Backed Manifest Catalog",
    desc: "Central repository publishing capabilities, semantic versioning, and heartbeat monitoring. Agents self-register on boot and playbooks are discovered dynamically.",
  },
  {
    number: "02",
    name: "Agent Runtime",
    icon: Cpu,
    tech: "Vertex AI Agent Platform (AdkApp)",
    desc: "Long-running async background execution with automated crash recovery and multi-day shift persistence across campus-wide disaster lifecycles.",
  },
  {
    number: "03",
    name: "Memory Bank",
    icon: Activity,
    tech: "VertexAiMemoryBankService",
    desc: "Persistent cross-session institutional memory retaining decades of incident retrospectives, vendor performance scores, and building mechanical quirks.",
  },
  {
    number: "04",
    name: "Agent Identity",
    icon: Fingerprint,
    tech: "Zero-Trust SPIFFE URIs + Scoped JWTs",
    desc: "Every agent possesses a cryptographic SPIFFE identity. Short-lived scoped JWT tokens enforce least-privilege tool execution per domain.",
  },
  {
    number: "05",
    name: "Agent Gateway",
    icon: Lock,
    tech: "Policy Enforcement Engine",
    desc: "Enforces tainted source quarantine, $10,000 financial threshold approvals, domain tool boundaries, and 20-call anti-loop limits in before_tool_callback.",
  },
  {
    number: "06",
    name: "Model Armor",
    icon: ShieldAlert,
    tech: "Multi-Layer Security Firewall",
    desc: "Screens all external IoT webhooks and vendor emails against 16 prompt injection patterns, redacts 5 PII categories, and neutralizes tool parameter poisoning.",
  },
  {
    number: "07",
    name: "Agent Observability",
    icon: ShieldCheck,
    tech: "OpenTelemetry Distributed Tracing",
    desc: "Immutable append-only Firestore audit ledger with parent-child span hierarchy and full reasoning tree reconstruction for insurance and legal compliance.",
  },
];

export const GovernanceLayer: React.FC = () => {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 border-t border-white/5 bg-navy-900/40 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5" />
            Fortified Enterprise Fleet
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Enterprise Governance, Not Guardrail Theater
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            ARCHON fully implements all seven Gemini Enterprise Agent Platform (GEAP) subsystems with real enforcement logic at the tool boundary.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {GEAP_SUBSYSTEMS.map((sub, idx) => {
            const Icon = sub.icon;
            return (
              <motion.div
                key={sub.number}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.08 }}
                className="glass-panel rounded-xl p-6 border border-white/10 hover:border-amber-500/30 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-mono text-xl font-extrabold text-amber-400/70">
                      {sub.number}
                    </span>
                    <span className="p-2 rounded-lg bg-white/5 border border-white/10 text-amber-400">
                      <Icon className="w-5 h-5" />
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-white mb-1">{sub.name}</h3>
                  <div className="text-xs font-mono text-amber-300/80 mb-3">{sub.tech}</div>
                  <p className="text-xs text-slate-300 leading-relaxed">{sub.desc}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
