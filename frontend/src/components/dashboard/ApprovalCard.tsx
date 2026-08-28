"use client";

import React, { useState } from "react";
import { ApprovalRequest } from "@/lib/types";
import { formatCurrency, formatTimeAgo } from "@/lib/utils";
import { ShieldAlert, Check, X, Clock, DollarSign } from "lucide-react";

interface ApprovalCardProps {
  approval: ApprovalRequest;
  onApprove: (id: string, notes?: string) => Promise<void>;
  onReject: (id: string, notes?: string) => Promise<void>;
}

export const ApprovalCard: React.FC<ApprovalCardProps> = ({ approval, onApprove, onReject }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notes, setNotes] = useState("");

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      await onApprove(approval.approval_id, notes);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    try {
      await onReject(approval.approval_id, notes);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isPending = approval.status === "pending";

  return (
    <div className={`glass-panel rounded-2xl p-6 border transition-all ${
      isPending ? "border-amber-500/40 bg-amber-500/5 shadow-lg shadow-amber-500/5" : "border-white/10 opacity-70"
    }`}>
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <ShieldAlert className="w-4 h-4" />
          </span>
          <span className="text-xs font-mono font-bold text-amber-300">
            {approval.approval_id}
          </span>
        </div>

        <span className={`text-[11px] font-mono px-2.5 py-0.5 rounded-full border uppercase tracking-wider ${
          approval.status === "approved"
            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
            : approval.status === "rejected"
            ? "bg-red-500/10 text-red-400 border-red-500/30"
            : "bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold"
        }`}>
          {approval.status}
        </span>
      </div>

      <h4 className="text-base font-bold text-white mb-2">{approval.description}</h4>

      <div className="bg-navy-950/80 p-3.5 rounded-xl border border-white/5 space-y-2 mb-4 text-xs font-mono">
        <div className="text-amber-400 font-semibold flex items-center gap-1.5">
          <span>Reason:</span>
          <span className="text-slate-200">{approval.reason}</span>
        </div>

        {approval.estimated_cost && (
          <div className="flex items-center gap-2 text-slate-300">
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
            <span>Estimated Financial Impact:</span>
            <span className="text-emerald-400 font-bold">
              {formatCurrency(approval.estimated_cost)}
            </span>
          </div>
        )}

        <div className="flex items-center justify-between text-slate-400 pt-1 text-[11px]">
          <span>Incident: {approval.incident_id}</span>
          <span>{formatTimeAgo(approval.created_at)}</span>
        </div>
      </div>

      {isPending && (
        <div className="space-y-3 pt-2">
          <input
            type="text"
            placeholder="Decision sign-off notes (optional)..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full bg-navy-950/90 border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
          />

          <div className="flex items-center gap-3">
            <button
              onClick={handleApprove}
              disabled={isSubmitting}
              className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-xs font-bold transition-all disabled:opacity-50"
            >
              <Check className="w-4 h-4" />
              <span>Approve Action</span>
            </button>
            <button
              onClick={handleReject}
              disabled={isSubmitting}
              className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-300 text-xs font-bold transition-all disabled:opacity-50"
            >
              <X className="w-4 h-4" />
              <span>Reject</span>
            </button>
          </div>
        </div>
      )}

      {approval.decision_by && (
        <div className="mt-3 pt-3 border-t border-white/5 text-[11px] font-mono text-slate-400 flex items-center justify-between">
          <span>Decided By: {approval.decision_by}</span>
          {approval.resolved_at && <span>{formatTimeAgo(approval.resolved_at)}</span>}
        </div>
      )}
    </div>
  );
};
