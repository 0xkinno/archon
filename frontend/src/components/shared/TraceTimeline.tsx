import React from "react";
import { Span } from "@/lib/types";
import { AgentBadge } from "./AgentBadge";
import { CheckCircle2, AlertTriangle, Clock, ArrowRight } from "lucide-react";
import { formatTimeAgo } from "@/lib/utils";

interface TraceTimelineProps {
  spans: Span[];
}

export const TraceTimeline: React.FC<TraceTimelineProps> = ({ spans }) => {
  if (!spans || spans.length === 0) {
    return (
      <div className="py-8 text-center text-slate-500 text-sm">
        No active execution spans recorded for this trace yet.
      </div>
    );
  }

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
      {spans.map((span, idx) => {
        const isSuccess = span.status === "completed";
        const isRunning = span.status === "running";

        return (
          <div key={span.span_id || idx} className="relative group">
            {/* Timeline Node */}
            <span className="absolute -left-6 top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-navy-950 ring-4 ring-navy-950">
              {isSuccess ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : isRunning ? (
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-red-400" />
              )}
            </span>

            {/* Span Card */}
            <div className="glass-panel rounded-lg p-4 transition-all hover:border-slate-700">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <AgentBadge agentName={span.agent_id} size="sm" />
                  <span className="text-xs font-mono text-slate-400">
                    {span.tool_name ? `tool:${span.tool_name}` : span.action}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-500">
                  {span.duration_ms !== undefined && (
                    <span className="flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3" />
                      {span.duration_ms}ms
                    </span>
                  )}
                  <span>{formatTimeAgo(span.start_time)}</span>
                </div>
              </div>

              {span.decision_rationale && (
                <p className="text-sm text-slate-300 mb-2 leading-relaxed bg-navy-900/50 p-2.5 rounded border border-white/5">
                  <span className="text-amber-400/80 font-semibold text-xs uppercase tracking-wider block mb-1">
                    Decision Rationale:
                  </span>
                  {span.decision_rationale}
                </p>
              )}

              {span.tool_result && (
                <div className="mt-2 text-xs font-mono bg-black/40 p-2 rounded overflow-x-auto border border-white/5 text-emerald-300/90">
                  {typeof span.tool_result === "object" ? (
                    <pre className="whitespace-pre-wrap font-mono">{JSON.stringify(span.tool_result, null, 2)}</pre>
                  ) : (
                    String(span.tool_result)
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
