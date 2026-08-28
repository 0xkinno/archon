import React from "react";
import { IncidentStatus } from "@/lib/types";

interface StatusPillProps {
  status: IncidentStatus | string;
}

export const StatusPill: React.FC<StatusPillProps> = ({ status }) => {
  const styles: Record<string, string> = {
    open: "bg-red-500/10 text-red-400 border-red-500/30",
    investigating: "bg-blue-500/10 text-blue-400 border-blue-500/30 animate-pulse",
    mitigating: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    resolved: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    pending: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30",
    in_progress: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
    completed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    blocked: "bg-rose-500/10 text-rose-400 border-rose-500/30",
  };

  const style = styles[status.toLowerCase()] || "bg-slate-500/10 text-slate-400 border-slate-500/30";

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize tracking-wide ${style}`}>
      {status.replace("_", " ")}
    </span>
  );
};
