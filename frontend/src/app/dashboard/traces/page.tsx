"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { TraceSummary } from "@/lib/types";
import { Activity, Clock, Download, ChevronRight, RefreshCw } from "lucide-react";
import { formatTimeAgo } from "@/lib/utils";

export default function TracesObservabilityPage() {
  const [traces, setTraces] = useState<TraceSummary[]>([]);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [reasoningChain, setReasoningChain] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchTraces = async () => {
    setLoading(true);
    try {
      const data = await api.getTraces();
      setTraces(data);
      if (data.length > 0 && !selectedTraceId) {
        handleSelectTrace(data[0].trace_id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTrace = async (traceId: string) => {
    setSelectedTraceId(traceId);
    try {
      const chain = await api.getTraceReasoningChain(traceId);
      setReasoningChain(chain);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchTraces();
  }, []);

  const handleExportJson = () => {
    if (!reasoningChain) return;
    const blob = new Blob([JSON.stringify(reasoningChain, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selectedTraceId || "trace"}_opentelemetry.json`;
    a.click();
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Distributed Traces & Observability
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            OpenTelemetry-compatible span hierarchy and autonomous decision audit ledger
          </p>
        </div>

        <div className="flex items-center gap-3">
          {selectedTraceId && (
            <button
              onClick={handleExportJson}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export OpenTelemetry JSON</span>
            </button>
          )}
          <button
            onClick={fetchTraces}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Trace List */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
            Recorded Traces ({traces.length})
          </h3>

          {traces.length === 0 ? (
            <div className="glass-panel rounded-xl p-8 text-center text-xs text-slate-500 font-mono">
              No distributed traces recorded yet.
            </div>
          ) : (
            traces.map((t) => {
              const isSelected = selectedTraceId === t.trace_id;
              return (
                <div
                  key={t.trace_id}
                  onClick={() => handleSelectTrace(t.trace_id)}
                  className={`glass-panel-interactive rounded-xl p-4 border cursor-pointer transition-all ${
                    isSelected
                      ? "border-amber-500/50 bg-amber-500/10 shadow-md shadow-amber-500/5"
                      : "border-white/10"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-mono font-bold text-white truncate">
                      {t.trace_id}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                      {t.spans_count} Spans
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span className="truncate">{t.agents?.length || 0} Agents Active</span>
                    <span className="flex items-center gap-1 text-slate-500">
                      <Clock className="w-3 h-3" />
                      {formatTimeAgo(t.start_time)}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Reasoning Hierarchy Tree */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
              Reasoning Chain Hierarchy
            </h3>
            {selectedTraceId && (
              <span className="text-xs font-mono text-amber-400 truncate">{selectedTraceId}</span>
            )}
          </div>

          <div className="glass-panel rounded-2xl p-6 border border-white/10 overflow-x-auto min-h-[400px]">
            {reasoningChain ? (
              <div className="space-y-4">
                <div className="text-xs font-mono text-slate-400 mb-2">
                  Total Tree Spans: {reasoningChain.total_spans}
                </div>
                <pre className="text-xs font-mono text-slate-200 bg-navy-950/80 p-4 rounded-xl border border-white/5 whitespace-pre-wrap leading-relaxed">
                  {JSON.stringify(reasoningChain.hierarchy, null, 2)}
                </pre>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-xs font-mono text-slate-500 py-20">
                Select a trace from the left panel to inspect its reasoning tree.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
