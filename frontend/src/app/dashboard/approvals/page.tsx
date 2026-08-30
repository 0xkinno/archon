"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ApprovalRequest } from "@/lib/types";
import { ApprovalCard } from "@/components/dashboard/ApprovalCard";
import {
  CheckCircle,
  ShieldAlert,
  RefreshCw,
  ShieldCheck,
  Lock,
  FileCheck2,
  Cpu,
} from "lucide-react";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("pending");
  const [loading, setLoading] = useState(true);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const data = await api.getApprovals(statusFilter || undefined);
      setApprovals(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [statusFilter]);

  const handleApprove = async (id: string, notes?: string) => {
    await api.approveAction(id, notes);
    await fetchApprovals();
  };

  const handleReject = async (id: string, notes?: string) => {
    await api.rejectAction(id, notes);
    await fetchApprovals();
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Human Governance &amp; Approval Gateway
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Deterministic Safety Kernel gates for high-cost expenditures (&gt;$10,000) and Model Armor taint-isolation verification
          </p>
        </div>

        <button
          onClick={fetchApprovals}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 transition-colors border border-white/10"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Institutional Defense Layer Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-amber-500/30 bg-amber-950/10 space-y-2">
          <div className="flex items-center gap-2 text-amber-400 text-xs font-mono font-bold uppercase">
            <Lock className="w-4 h-4" />
            <span>INV-01: Financial Gating</span>
          </div>
          <div className="text-xl font-extrabold text-white font-mono">$10,000.00 Limit</div>
          <p className="text-[11px] text-slate-300 font-mono">
            Autonomous agent dispatches &gt;$10k are held in pending quarantine until signed by a Facilities Director.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-emerald-500/30 bg-emerald-950/10 space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono font-bold uppercase">
            <ShieldCheck className="w-4 h-4" />
            <span>Model Armor &amp; TPSI</span>
          </div>
          <div className="text-xl font-extrabold text-white font-mono">Zero Taint Active</div>
          <p className="text-[11px] text-slate-300 font-mono">
            Taint-Propagated State Isolation invalidates poisoned context and triggers deterministic snapshot rollback.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-blue-500/30 bg-blue-950/10 space-y-2">
          <div className="flex items-center gap-2 text-blue-400 text-xs font-mono font-bold uppercase">
            <Cpu className="w-4 h-4" />
            <span>Ed25519 State Proof</span>
          </div>
          <div className="text-xl font-extrabold text-white font-mono">100% Signed</div>
          <p className="text-[11px] text-slate-300 font-mono">
            Canonical SHA-256 state hashes signed on closure and independently verified by the offline Python verifier.
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-4 text-xs font-mono">
        <button
          onClick={() => setStatusFilter("pending")}
          className={`px-4 py-2 rounded-xl transition-all font-bold ${
            statusFilter === "pending"
              ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Pending Authorization Gates ({approvals.filter((a) => a.status === "pending").length})
        </button>
        <button
          onClick={() => setStatusFilter("")}
          className={`px-4 py-2 rounded-xl transition-all font-bold ${
            statusFilter === ""
              ? "bg-white/10 text-white border border-white/20"
              : "text-slate-400 hover:text-white"
          }`}
        >
          All Approval History
        </button>
      </div>

      {/* List */}
      {approvals.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center text-slate-500 text-xs font-mono border border-white/5">
          <CheckCircle className="w-8 h-8 mx-auto mb-3 text-emerald-400/60" />
          <div className="text-sm font-semibold text-slate-300 mb-1">Queue Clear</div>
          <div>No pending agent actions exceed the $10,000 threshold or require manual authorization.</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {approvals.map((appr) => (
            <ApprovalCard
              key={appr.approval_id}
              approval={appr}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}
    </div>
  );
}
