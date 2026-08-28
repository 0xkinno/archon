"use client";

import React from "react";
import { motion } from "framer-motion";
import { AGENT_DOMAINS } from "@/lib/constants";
import { ShieldAlert, Network, Truck, FileCheck, Radio, CheckSquare, BrainCircuit, Bot } from "lucide-react";

const FLEET_DETAILS = [
  {
    key: "incident_commander",
    role: "The Orchestrator",
    domain: "Orchestration & Triage",
    desc: "Ingests multi-source signals, determines severity (P1-P4), searches memory for precedent, and orchestrates playbooks via Google ADK.",
    tools: ["classify_incident", "activate_playbook", "search_precedent"],
    icon: ShieldAlert,
  },
  {
    key: "impact_assessor",
    role: "Spatial Cartographer",
    domain: "Blast Radius & Topology",
    desc: "Traverses campus topological graph to map affected buildings, occupancy headcounts, and secondary utility dependencies like hospital chilled water loops.",
    tools: ["query_building_systems", "check_occupancy", "map_dependencies"],
    icon: Network,
  },
  {
    key: "vendor_coordinator",
    role: "Logistics Dispatcher",
    domain: "Vendor Management",
    desc: "Audits contractor reliability scorecards, verifies SLA response guarantees, and executes emergency dispatches with financial gate enforcement.",
    tools: ["search_vendors", "dispatch_vendor", "check_vendor_history"],
    icon: Truck,
  },
  {
    key: "compliance_inspector",
    role: "Regulatory Guardian",
    domain: "Audits & EHS Standards",
    desc: "Cross-references active repairs against Fire Marshal, OSHA, and EPA calendars; generates complete pre-audit proof documentation packages.",
    tools: ["check_inspection_schedule", "generate_compliance_doc", "flag_violations"],
    icon: FileCheck,
  },
  {
    key: "communications_officer",
    role: "Public Information Officer",
    domain: "Stakeholder Notifications",
    desc: "Formulates multi-channel emergency alerts and updates tailored to incident severity, routing via SMS, email, radio, and dashboard feeds.",
    tools: ["draft_notification", "route_by_severity", "check_contact_directory"],
    icon: Radio,
  },
  {
    key: "remediation_tracker",
    role: "Field Action Supervisor",
    domain: "Corrective Action Tasks",
    desc: "Creates structured work orders, tracks repair SLA deadlines, automatically escalates overdue items, and compiles shift transition handoff logs.",
    tools: ["create_task", "update_task", "escalate_overdue", "shift_handoff"],
    icon: CheckSquare,
  },
  {
    key: "memory_curator",
    role: "Institutional Archivist",
    domain: "Institutional Memory",
    desc: "Extracts operational findings, updates long-term vendor scorecards, and encodes permanent campus quirks into Vertex AI Memory Bank.",
    tools: ["store_lesson", "search_precedent", "update_vendor_scorecard"],
    icon: BrainCircuit,
  },
];

export const AgentFleet: React.FC = () => {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 border-t border-white/5 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-semibold uppercase tracking-wider">
            <Bot className="w-3.5 h-3.5" />
            Google ADK Fleet
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Seven Specialists. One Governing Intelligence.
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Each agent owns a single operational domain with zero overlap. Every action is gated by zero-trust identity and real-time observability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {FLEET_DETAILS.map((agent, idx) => {
            const config = AGENT_DOMAINS[agent.key] || { color: "#8B5CF6" };
            const Icon = agent.icon;

            return (
              <motion.div
                key={agent.key}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.08 }}
                className="glass-panel-interactive rounded-xl p-6 border flex flex-col justify-between relative overflow-hidden group"
                style={{
                  borderLeftColor: config.color,
                  borderLeftWidth: "4px",
                }}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className="p-2.5 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${config.color}20`, color: config.color }}
                    >
                      <Icon className="w-5 h-5" />
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-400 border border-white/10">
                      ADK Agent
                    </span>
                  </div>

                  <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold mb-1">
                    {agent.domain}
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">
                    {agent.key}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed mb-6">
                    {agent.desc}
                  </p>
                </div>

                <div className="pt-4 border-t border-white/5 space-y-2">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 block">
                    Domain Tools:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {agent.tools.map((t) => (
                      <span
                        key={t}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-navy-950/80 border border-white/10 text-slate-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
