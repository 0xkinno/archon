"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ShieldAlert, ArrowRight, Play, Sparkles, CheckCircle, Radio } from "lucide-react";
import { AGENT_DOMAINS } from "@/lib/constants";

export const Hero: React.FC = () => {
  const agents = Object.entries(AGENT_DOMAINS);

  return (
    <section className="relative min-h-[92vh] flex items-center justify-center py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Background Gradient & Glow Accents */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[380px] bg-gradient-to-tr from-amber-500/10 via-purple-600/10 to-blue-500/10 blur-[120px] pointer-events-none rounded-full" />

      <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
        {/* Left Column: Headline & Action */}
        <div className="lg:col-span-7 space-y-8 text-center lg:text-left">
          {/* Category Pill */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-panel border-amber-500/30 text-amber-400 text-xs font-semibold uppercase tracking-wider"
          >
            <span className="flex h-2 w-2 rounded-full bg-amber-400 animate-ping" />
            All Things Agentic Hackathon | Fortified Enterprise Fleet Track
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.1]"
          >
            Institutional Intelligence That{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-200 to-amber-500">
              Never Forgets.
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg sm:text-xl text-slate-300 max-w-2xl font-normal leading-relaxed"
          >
            A governed fleet of 7 AI agents that classifies, coordinates, and resolves operational incidents across your entire campus, while preserving decades of institutional knowledge that usually walks out the door when staff retire.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-wrap items-center justify-center lg:justify-start gap-4 pt-2"
          >
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-navy-950 font-bold shadow-lg shadow-amber-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <span>Launch Command Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <a
              href="https://youtube.com/watch?v=placeholder"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl glass-panel text-slate-200 font-semibold hover:border-amber-500/40 hover:text-white transition-all"
            >
              <Play className="w-4 h-4 text-amber-400 fill-amber-400/20" />
              <span>Watch 4-Min Demo</span>
            </a>
          </motion.div>

          {/* Key Trust Pillars */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="pt-6 border-t border-white/10 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-xs text-slate-400"
          >
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Google ADK 2.6.2 Swarm</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Vertex AI Memory Bank</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>7/7 GEAP Subsystems</span>
            </div>
          </motion.div>
        </div>

        {/* Right Column: Floating Fleet Status Monitor */}
        <div className="lg:col-span-5">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="glass-panel rounded-2xl p-6 border border-white/15 relative shadow-2xl"
          >
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
              <div className="flex items-center gap-2.5">
                <span className="h-3 w-3 rounded-full bg-emerald-400 pulse-dot-green" />
                <span className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
                  Active Fleet Status (7/7 Online)
                </span>
              </div>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                GEAP Governed
              </span>
            </div>

            <div className="space-y-2.5">
              {agents.map(([key, info], idx) => (
                <div
                  key={key}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-navy-900/60 border border-white/5 transition-all hover:border-white/20"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: info.color }}
                    />
                    <div>
                      <div className="text-xs font-semibold text-slate-200">{info.name}</div>
                      <div className="text-[10px] font-mono text-slate-400">
                        spiffe://archon.campus/agent/{key}
                      </div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                    ACTIVE
                  </span>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-xs text-slate-400 font-mono">
              <span>Zero-Trust Policy Engine</span>
              <span className="text-amber-400">Active</span>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
