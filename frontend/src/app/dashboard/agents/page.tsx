"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AgentManifest } from "@/lib/types";
import { AGENT_DOMAINS } from "@/lib/constants";
import { Users, Bot, RefreshCw, Activity, ShieldAlert, CheckCircle2, AlertCircle } from "lucide-react";
import { formatTimeAgo } from "@/lib/utils";

export default function AgentsRegistryPage() {
  const [agents, setAgents] = useState<AgentManifest[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const data = await api.getAgents();
      setAgents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Agent Registry & Lifecycle
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Firestore-backed catalog of specialist agents, capabilities, and health heartbeats
          </p>
        </div>

        <button
          onClick={fetchAgents}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Fleet</span>
        </button>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => {
          const config = AGENT_DOMAINS[agent.name] || {
            color: "#8B5CF6",
            name: agent.name,
          };
          const isActive = agent.status === "active";

          return (
            <div
              key={agent.agent_id}
              className="glass-panel-interactive rounded-2xl p-6 border flex flex-col justify-between"
              style={{
                borderLeftColor: config.color,
                borderLeftWidth: "4px",
              }}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${isActive ? "bg-emerald-400 pulse-dot-green" : "bg-amber-400"}`} />
                    <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                      v{agent.version}
                    </span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${
                    isActive
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                      : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                  }`}>
                    {agent.status}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-white mb-1">{agent.name}</h3>
                <div className="text-[11px] font-mono text-slate-400 mb-3 truncate">
                  {agent.agent_id}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed mb-4">{agent.description}</p>

                {/* Capabilities */}
                <div className="mb-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 block mb-1.5">
                    Operational Capabilities:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {agent.capabilities.map((cap) => (
                      <span
                        key={cap}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-300"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Tools */}
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 block mb-1.5">
                    Domain Tools:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {agent.tools.map((t) => (
                      <span
                        key={t}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-navy-950 border border-white/10 text-slate-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-6 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
                <span>Heartbeat:</span>
                <span className="text-slate-300">{formatTimeAgo(agent.last_heartbeat)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
