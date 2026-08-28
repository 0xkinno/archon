"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { CloudLightning, ArrowRight, Clock, AlertTriangle, Building2, Flame, Bot } from "lucide-react";
import { SeverityIndicator } from "../shared/SeverityIndicator";

const SIGNALS = [
  {
    time: "T+0s",
    title: "Water Sensor Rupture in Building C Basement",
    source: "IoT BMS Water Telemetry",
    location: "Building C - Science Facility",
    severity: "P1",
    desc: "Flow rate exceeding 200 GPM in sub-basement mechanical room. Primary water main rupture detected.",
    activeAgents: ["incident_commander", "impact_assessor", "vendor_coordinator"],
    badge: "Plumbing Failure",
  },
  {
    time: "T+3s",
    title: "Hospital NICU Climate Excursion Alert",
    source: "Hospital Chilled Water Loop Sensor",
    location: "Building H - Hospital NICU Zone 3",
    severity: "P1",
    desc: "Chilled water loop from Building C disrupted. Ambient temperature rising (78F vs 68F setpoint). Life-safety hazard.",
    activeAgents: ["impact_assessor", "communications_officer", "vendor_coordinator"],
    badge: "Secondary Cascade",
  },
  {
    time: "T+5s",
    title: "Contractor Maintenance No-Show",
    source: "Atlas Elevator Dispatch Feed",
    location: "Building A - Administration Hub",
    severity: "P3",
    desc: "Contractor missed third maintenance window this quarter. Trapped occupancy sweeps initiated.",
    activeAgents: ["vendor_coordinator", "remediation_tracker", "memory_curator"],
    badge: "Contractor Default",
  },
  {
    time: "T+8s",
    title: "Pre-Inspection Audit Documentation Alert",
    source: "State Regulatory Calendar",
    location: "Building D - Medical Wing",
    severity: "P2",
    desc: "State Fire Marshal audit scheduled tomorrow at 0900. Automated pre-inspection compliance binder assembled.",
    activeAgents: ["compliance_inspector", "remediation_tracker"],
    badge: "Regulatory Exposure",
  },
];

export const DemoScenario: React.FC = () => {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 border-t border-white/5 bg-navy-900/40 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <CloudLightning className="w-3.5 h-3.5" />
            Live Demo Simulation
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Watch Seven Agents Coordinate a Campus-Wide Storm Response
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Experience how ARCHON autonomously handles cascading multi-building failures in real time with zero human latency.
          </p>
        </div>

        {/* 4 Cascading Signal Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {SIGNALS.map((sig, idx) => (
            <motion.div
              key={sig.time}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              className="glass-panel rounded-2xl p-6 border border-white/10 relative overflow-hidden"
            >
              <div className="flex items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    {sig.time}
                  </span>
                  <span className="text-xs font-mono text-slate-400">{sig.badge}</span>
                </div>
                <SeverityIndicator severity={sig.severity as any} size="sm" />
              </div>

              <h3 className="text-base font-bold text-white mb-1.5">{sig.title}</h3>
              <p className="text-xs text-slate-300 mb-4 leading-relaxed">{sig.desc}</p>

              <div className="pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">{sig.location}</span>
                <div className="flex items-center gap-1">
                  <Bot className="w-3 h-3 text-purple-400" />
                  <span className="text-[11px] font-mono text-purple-300">
                    {sig.activeAgents.length} Agents Engaged
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* CTA Banner */}
        <div className="text-center">
          <Link
            href="/dashboard?simulate=true"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-navy-950 font-bold shadow-lg shadow-amber-500/20 text-sm transition-all hover:scale-105"
          >
            <span>Simulate Live Storm Response in Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </section>
  );
};
