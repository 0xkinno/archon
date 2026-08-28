import React from "react";
import { MemoryEntry } from "@/lib/types";
import { BrainCircuit, Building2, User, Calendar, Sparkles } from "lucide-react";
import { formatTimeAgo } from "@/lib/utils";

interface MemoryCardProps {
  memory: MemoryEntry;
}

export const MemoryCard: React.FC<MemoryCardProps> = ({ memory }) => {
  return (
    <div className="glass-panel-interactive rounded-xl p-5 border border-white/10 relative overflow-hidden flex flex-col justify-between">
      <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-full blur-xl pointer-events-none" />

      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-400">
              <BrainCircuit className="w-4 h-4" />
            </span>
            <span className="text-xs font-mono font-semibold text-purple-300 uppercase tracking-wider">
              {memory.category.replace("_", " ")}
            </span>
          </div>

          {memory.relevance_score !== undefined && (
            <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <Sparkles className="w-3 h-3" />
              {Math.round(memory.relevance_score * 100)}% Match
            </span>
          )}
        </div>

        <p className="text-sm text-slate-200 leading-relaxed mb-4">
          {memory.content}
        </p>
      </div>

      <div className="pt-3 border-t border-white/5 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2 font-mono">
        <div className="flex items-center gap-3">
          {memory.building_id && (
            <span className="flex items-center gap-1 text-slate-300">
              <Building2 className="w-3.5 h-3.5 text-slate-500" />
              {memory.building_id}
            </span>
          )}
          {memory.vendor_id && (
            <span className="flex items-center gap-1 text-slate-300">
              <User className="w-3.5 h-3.5 text-slate-500" />
              {memory.vendor_id}
            </span>
          )}
        </div>
        <span className="flex items-center gap-1 text-slate-500">
          <Calendar className="w-3.5 h-3.5" />
          {formatTimeAgo(memory.created_at)}
        </span>
      </div>
    </div>
  );
};
