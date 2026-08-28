"use client";

import React from "react";
import Link from "next/link";
import { AGENT_DOMAINS } from "@/lib/constants";
import { AgentManifest } from "@/lib/types";
import { ShieldAlert, Network, Truck, FileCheck, Radio, CheckSquare, BrainCircuit, Bot } from "lucide-react";

interface AgentStatusGridProps {
  agents?: AgentManifest[];
}

const ICONS: Record<string, any> = {
  incident_commander: ShieldAlert,
  impact_assessor: Network,
  vendor_coordinator: Truck,
  compliance_inspector: FileCheck,
  communications_officer: Radio,
  remediation_tracker: CheckSquare,
  memory_curator: BrainCircuit,
};

export const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({ agents }) => {
  const agentKeys = Object.keys(AGENT_DOMAINS);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
      {agentKeys.map((key) => {
        const info = AGENT_DOMAINS[key];
        const Icon = ICONS[key] || Bot;
        const liveManifest = agents?.find((a) => a.name === key);
        const status = liveManifest?.status || "active";

        return (
          <Link
            key={key}
            href="/dashboard/agents"
            className="glass-panel-interactive rounded-xl p-3.5 border border-white/10 flex flex-col justify-between group text-left"
            style={{
              borderTopColor: info.color,
              borderTopWidth: "3px",
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <span
                className="p-1.5 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${info.color}20`, color: info.color }}
              >
                <Icon className="w-4 h-4" />
              </span>
              <span className="flex h-2 w-2 rounded-full bg-emerald-400 pulse-dot-green" />
            </div>

            <div>
              <div className="text-xs font-bold text-white group-hover:text-amber-300 transition-colors truncate">
                {info.name}
              </div>
              <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                {status}
              </div>
            </div>
          </Link>
        );
      })}
    </div>
  );
};
