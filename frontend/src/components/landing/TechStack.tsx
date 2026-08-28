"use client";

import React from "react";
import { Layers } from "lucide-react";

const STACK_GROUPS = [
  {
    category: "Development & LLM",
    items: [
      { name: "Gemini Antigravity", role: "Agentic Pair Programming & Build IDE" },
      { name: "Google ADK 2.6.2+", role: "Orchestration & Swarm Callbacks" },
      { name: "Gemini 3.5 Flash", role: "Reasoning & Signal Classification" },
      { name: "Vertex AI Memory Bank", role: "Cross-Session Institutional Memory" },
    ],
  },
  {
    category: "Backend & Governance",
    items: [
      { name: "FastAPI 0.115+", role: "REST & Real-Time WebSocket Server" },
      { name: "Google Cloud Firestore", role: "Immutable State & Audit Ledger" },
      { name: "OpenTelemetry SDK", role: "Distributed Tracing & Spans" },
      { name: "PyJWT & SPIFFE", role: "Zero-Trust Agent Identity Scoping" },
    ],
  },
  {
    category: "Frontend & Infrastructure",
    items: [
      { name: "Next.js 14 (App Router)", role: "Server & Client Architecture" },
      { name: "Tailwind CSS 3.4+", role: "Custom Navy & Amber Command Theme" },
      { name: "Framer Motion 11", role: "Fluid 60fps Micro-Interactions" },
      { name: "Google Cloud Run", role: "Containerized Production Hosting" },
    ],
  },
];

export const TechStack: React.FC = () => {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 border-t border-white/5 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-slate-500/10 border border-slate-500/30 text-slate-300 text-xs font-semibold uppercase tracking-wider">
            <Layers className="w-3.5 h-3.5" />
            Engineering Foundation
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            Built With Google's Production Ecosystem
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Architected specifically for Google Cloud enterprise standards with zero throwaway mocks.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {STACK_GROUPS.map((group, idx) => (
            <div key={idx} className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
              <h3 className="text-sm font-mono uppercase tracking-wider text-amber-400 font-bold pb-3 border-b border-white/10">
                {group.category}
              </h3>
              <div className="space-y-3">
                {group.items.map((item, iIdx) => (
                  <div key={iIdx} className="p-3 rounded-lg bg-navy-950/60 border border-white/5">
                    <div className="text-xs font-bold text-white mb-0.5">{item.name}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{item.role}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
