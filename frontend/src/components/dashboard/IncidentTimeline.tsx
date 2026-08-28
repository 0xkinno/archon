"use client";

import React from "react";
import Link from "next/link";
import { Incident } from "@/lib/types";
import { SeverityIndicator } from "../shared/SeverityIndicator";
import { StatusPill } from "../shared/StatusPill";
import { AgentBadge } from "../shared/AgentBadge";
import { Building2, Clock, ChevronRight, AlertCircle } from "lucide-react";
import { formatTimeAgo } from "@/lib/utils";

interface IncidentTimelineProps {
  incidents: Incident[];
  onSelectIncident?: (incident: Incident) => void;
}

export const IncidentTimeline: React.FC<IncidentTimelineProps> = ({ incidents, onSelectIncident }) => {
  if (!incidents || incidents.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-500">
        <AlertCircle className="w-8 h-8 mx-auto mb-3 text-slate-600" />
        <div className="text-sm font-semibold text-slate-400 mb-1">No Active Incidents</div>
        <div className="text-xs">All campus building systems operating within standard baseline parameters.</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {incidents.map((inc) => (
        <div
          key={inc.id}
          onClick={() => onSelectIncident && onSelectIncident(inc)}
          className="glass-panel-interactive rounded-xl p-5 border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer group"
        >
          <div className="space-y-2 flex-1">
            <div className="flex flex-wrap items-center gap-2.5">
              <SeverityIndicator severity={inc.severity} size="sm" withPulse={inc.status !== "resolved"} />
              <StatusPill status={inc.status} />
              <span className="text-xs font-mono text-slate-400">{inc.id}</span>
              <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatTimeAgo(inc.created_at)}
              </span>
            </div>

            <h4 className="text-base font-bold text-white group-hover:text-amber-300 transition-colors">
              {inc.title}
            </h4>

            <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
              {inc.description}
            </p>

            <div className="flex flex-wrap items-center gap-3 pt-2 text-xs text-slate-400">
              {inc.affected_buildings && inc.affected_buildings.length > 0 && (
                <div className="flex items-center gap-1 text-slate-300 font-mono">
                  <Building2 className="w-3.5 h-3.5 text-slate-500" />
                  <span>{inc.affected_buildings.join(", ")}</span>
                </div>
              )}

              {inc.assigned_agents && inc.assigned_agents.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5">
                  {inc.assigned_agents.slice(0, 3).map((agent) => (
                    <AgentBadge key={agent} agentName={agent} size="sm" />
                  ))}
                  {inc.assigned_agents.length > 3 && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-400 border border-white/10">
                      +{inc.assigned_agents.length - 3} more
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
            <Link
              href={`/dashboard/incidents/${inc.id}`}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-semibold text-slate-200 group-hover:text-amber-400 transition-colors"
            >
              <span>Inspect</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      ))}
    </div>
  );
};
