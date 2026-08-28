"use client";

import React, { useEffect, useState } from "react";
import { IncidentTimeline } from "@/components/dashboard/IncidentTimeline";
import { Incident } from "@/lib/types";
import { api } from "@/lib/api";
import { Filter, RefreshCw } from "lucide-react";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const data = await api.getIncidents(statusFilter || undefined, severityFilter || undefined);
      setIncidents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [severityFilter, statusFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Incident Log & History
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Full repository of physical and operational campus alarms
          </p>
        </div>

        <button
          onClick={fetchIncidents}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filters Bar */}
      <div className="glass-panel rounded-xl p-4 border border-white/10 flex flex-wrap items-center gap-4 text-xs font-mono">
        <div className="flex items-center gap-2 text-slate-400">
          <Filter className="w-4 h-4 text-amber-400" />
          <span>Filter Records:</span>
        </div>

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-navy-950 border border-white/10 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-amber-500"
        >
          <option value="">All Severities</option>
          <option value="P1">P1 Critical</option>
          <option value="P2">P2 High</option>
          <option value="P3">P3 Medium</option>
          <option value="P4">P4 Low</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-navy-950 border border-white/10 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-amber-500"
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="mitigating">Mitigating</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>

      {/* List */}
      <IncidentTimeline incidents={incidents} />
    </div>
  );
}
