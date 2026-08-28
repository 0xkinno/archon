"use client";

import React from "react";
import { motion } from "framer-motion";
import { XCircle, CheckCircle2, ArrowRight, ShieldCheck, Zap, Sparkles } from "lucide-react";

export const Solution: React.FC = () => {
  const comparison = [
    {
      title: "Before ARCHON",
      subtitle: "Fragmented & Chaotic Operations",
      color: "border-red-500/20 bg-red-500/5",
      badgeColor: "bg-red-500/20 text-red-400 border-red-500/30",
      points: [
        "Frantic midnight phone calls across 10 vendor hotlines",
        "Blind dispatching without understanding chilled water inter-ties",
        "Missed regulatory audits resulting in code violations and fines",
        "20 years of building failure history lost every retirement cycle",
      ],
    },
    {
      title: "The ARCHON Platform",
      subtitle: "Governed Multi-Agent Intelligence",
      color: "border-amber-500/40 bg-amber-500/10 shadow-lg shadow-amber-500/10",
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold",
      points: [
        "Automated triage and classification of IoT alerts in sub-seconds",
        "Topological dependency mapping to protect critical hospital wards",
        "Zero-trust tool execution governed by Model Armor and Gateway",
        "Continuous memory synthesis powered by Vertex AI Memory Bank",
      ],
    },
    {
      title: "After ARCHON",
      subtitle: "Resilient & Auditable Command",
      color: "border-emerald-500/20 bg-emerald-500/5",
      badgeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
      points: [
        "80% faster incident response and emergency contractor arrival",
        "Zero institutional knowledge loss across shifts and years",
        "Automated pre-audit compliance packets for Fire Marshals & OSHA",
        "Immutable OpenTelemetry audit trail for insurance and leadership",
      ],
    },
  ];

  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 border-t border-white/5 relative bg-navy-900/30">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <Zap className="w-3.5 h-3.5" />
            The Architectural Shift
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            ARCHON Replaces Chaos With Command
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Transform manual panic into deterministic, observable, and governed execution across all campus facilities.
          </p>
        </div>

        {/* 3 Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative items-stretch">
          {comparison.map((col, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.15 }}
              className={`rounded-2xl p-8 border flex flex-col justify-between ${col.color}`}
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className={`text-xs uppercase tracking-wider px-3 py-1 rounded-full border ${col.badgeColor}`}>
                    {col.title}
                  </span>
                  {idx === 1 && <Sparkles className="w-5 h-5 text-amber-400 animate-spin" style={{ animationDuration: "8s" }} />}
                </div>
                <h3 className="text-xl font-bold text-white mb-6">{col.subtitle}</h3>

                <ul className="space-y-4">
                  {col.points.map((pt, pIdx) => (
                    <li key={pIdx} className="flex items-start gap-3 text-sm text-slate-300 leading-relaxed">
                      {idx === 0 ? (
                        <XCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      )}
                      <span>{pt}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {idx === 1 && (
                <div className="mt-8 pt-4 border-t border-amber-500/20 text-xs text-amber-300/90 font-mono text-center">
                  Protected by 7 GEAP Governance Subsystems
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
