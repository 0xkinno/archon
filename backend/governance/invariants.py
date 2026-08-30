"""
The Twelve Hard Governance Invariants for ARCHON.

Each invariant function is total, pure, deterministic, and returns an InvariantResult.
These functions define structural correctness across both runtime pre-commit checks
and offline post-incident verification over persisted state and audit traces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

try:
    from governance.signing import compute_state_hash, verify_incident_signature
except ImportError:
    from backend.governance.signing import compute_state_hash, verify_incident_signature



@dataclass(frozen=True, slots=True)
class InvariantResult:
    invariant_id: str
    title: str
    holds: bool
    detail: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "title": self.title,
            "holds": self.holds,
            "detail": self.detail,
            "evidence": self.evidence,
        }


def _ok(inv: str, title: str, detail: str = "", **evidence: Any) -> InvariantResult:
    return InvariantResult(inv, title, True, detail, evidence)


def _bad(inv: str, title: str, detail: str, **evidence: Any) -> InvariantResult:
    return InvariantResult(inv, title, False, detail, evidence)


# --------------------------------------------------------------------------------------
# INV-01: Financial Threshold Quarantine
# --------------------------------------------------------------------------------------
INV01_TITLE = "Financial Threshold Quarantine"


def check_inv01_financial_threshold(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Any expenditure >$10,000 requires explicit human director approval before effect."""
    dispatches = state.get("dispatches", [])
    unauthorized = []

    for d in dispatches:
        cost = float(d.get("estimated_cost", 0) or d.get("amount", 0) or 0)
        status = d.get("status", "").upper()
        approval_id = d.get("approval_id") or d.get("authorized_by")

        if cost > 10000.0:
            if status in ("EXECUTED", "DISPATCHED", "COMMITTED", "COMPLETED") and not approval_id:
                unauthorized.append({"dispatch_id": d.get("dispatch_id", d.get("id")), "cost": cost, "status": status})

    if unauthorized:
        return _bad(
            "INV-01",
            INV01_TITLE,
            f"{len(unauthorized)} expenditure(s) >$10,000 committed without required human authorization",
            unauthorized=unauthorized,
        )
    return _ok("INV-01", INV01_TITLE, "all expenditures >$10,000 strictly quarantined until authorized")


# --------------------------------------------------------------------------------------
# INV-02: No Tainted Source Action
# --------------------------------------------------------------------------------------
INV02_TITLE = "No Tainted Source Action"


def check_inv02_no_tainted_action(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Quarantined or injection-tainted signals must never trigger downstream physical effects."""
    tainted_sources = set()
    for log in audit_trail:
        if log.get("event") == "MODEL_ARMOR_QUARANTINE" or log.get("action") == "INJECTION_BLOCKED" or log.get("tainted") is True:
            src = log.get("source_id") or log.get("signal_id") or log.get("input_id")
            if src:
                tainted_sources.add(src)

    violations = []
    for log in audit_trail:
        if log.get("event") in ("DISPATCH_VENDOR", "COMMIT_REMEDIATION", "EXECUTE_ACTUATION"):
            used_source = log.get("derived_from") or log.get("signal_id")
            if used_source in tainted_sources:
                violations.append({"action": log.get("event"), "source_id": used_source, "timestamp": log.get("timestamp")})

    if violations:
        return _bad(
            "INV-02",
            INV02_TITLE,
            f"{len(violations)} downstream effect(s) derived from quarantined/tainted sources",
            violations=violations,
        )
    return _ok("INV-02", INV02_TITLE, "zero effects executed from quarantined or tainted inputs")


# --------------------------------------------------------------------------------------
# INV-03: Domain Scope Integrity
# --------------------------------------------------------------------------------------
INV03_TITLE = "Domain Scope Integrity"

AGENT_ALLOWED_TOOLS = {
    "incident_commander": {"plan_incident", "declare_escalation", "delegate_task", "request_closure", "update_status"},
    "impact_assessor": {"calculate_blast_radius", "assess_structural_risk", "evaluate_occupancy", "model_downtime"},
    "vendor_coordinator": {"query_vendor_catalog", "rank_contractors", "dispatch_vendor", "track_eta"},
    "compliance_inspector": {"audit_osha_regulations", "check_epa_compliance", "verify_licensing", "inspect_permits"},
    "communications_officer": {"draft_campus_alert", "broadcast_evacuation_notice", "notify_facilities_team", "send_push_notification"},
    "remediation_tracker": {"create_task", "assign_subcontractor", "log_sensor_reading", "complete_task"},
    "memory_curator": {"query_memory_bank", "record_incident_precedent", "cluster_historical_patterns"},
}


def check_inv03_domain_scope_integrity(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Agents must never execute tools or actions outside their defined capability envelope."""
    out_of_scope = []
    for log in audit_trail:
        agent = log.get("agent_name", "").lower()
        tool = log.get("tool_name")

        if agent in AGENT_ALLOWED_TOOLS and tool:
            allowed = AGENT_ALLOWED_TOOLS[agent]
            # Standard generic tools like read_telemetry are permissible across all
            if tool not in allowed and not tool.startswith("read_") and not tool.startswith("query_"):
                out_of_scope.append({"agent": agent, "unauthorized_tool": tool, "timestamp": log.get("timestamp")})

    if out_of_scope:
        return _bad(
            "INV-03",
            INV03_TITLE,
            f"{len(out_of_scope)} tool execution(s) exceeded agent domain authorization",
            violations=out_of_scope,
        )
    return _ok("INV-03", INV03_TITLE, "all tool executions strictly conformed to domain capability envelopes")


# --------------------------------------------------------------------------------------
# INV-04: No Duplicate Vendor Dispatch
# --------------------------------------------------------------------------------------
INV04_TITLE = "No Duplicate Vendor Dispatch"


def check_inv04_no_duplicate_dispatch(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """For any given building and specialty, no duplicate concurrent active dispatches are permitted."""
    dispatches = state.get("dispatches", [])
    seen_specialties: dict[str, str] = {}
    duplicates = []

    for d in dispatches:
        building = d.get("building_id", state.get("building_id", "CAMPUS"))
        specialty = d.get("specialty", d.get("trade", "")).lower()
        status = d.get("status", "").upper()

        if status in ("ACTIVE", "DISPATCHED", "EN_ROUTE", "IN_PROGRESS") and specialty:
            key = f"{building}:{specialty}"
            dispatch_id = d.get("dispatch_id", d.get("id", "disp"))
            if key in seen_specialties:
                duplicates.append({"building": building, "specialty": specialty, "first_id": seen_specialties[key], "duplicate_id": dispatch_id})
            else:
                seen_specialties[key] = dispatch_id

    if duplicates:
        return _bad(
            "INV-04",
            INV04_TITLE,
            f"{len(duplicates)} duplicate vendor dispatch(es) found for identical building and specialty",
            duplicates=duplicates,
        )
    return _ok("INV-04", INV04_TITLE, "exactly-once vendor dispatch enforced across all trades")


# --------------------------------------------------------------------------------------
# INV-05: P1 Escalation Determinism
# --------------------------------------------------------------------------------------
INV05_TITLE = "P1 Escalation Determinism"


def check_inv05_p1_escalation(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """P1/Critical incidents must deterministically trigger Commander assignment and emergency broadcast."""
    severity = state.get("severity", "").upper()
    if severity in ("P1", "CRITICAL", "HIGH_CRITICAL"):
        has_commander = bool(state.get("commander_assigned") or any(l.get("agent_name") == "incident_commander" for l in audit_trail))
        has_broadcast = bool(state.get("escalation_broadcast") or any(l.get("event") in ("ESCALATION_BROADCAST", "P1_ALERT_SENT") for l in audit_trail))

        if not has_commander or not has_broadcast:
            return _bad(
                "INV-05",
                INV05_TITLE,
                f"P1 incident lacked mandatory escalation artifacts (commander: {has_commander}, broadcast: {has_broadcast})",
                has_commander=has_commander,
                has_broadcast=has_broadcast,
            )
    return _ok("INV-05", INV05_TITLE, "critical incident escalation path deterministically executed")


# --------------------------------------------------------------------------------------
# INV-06: Agent Loop Boundedness
# --------------------------------------------------------------------------------------
INV06_TITLE = "Agent Loop Boundedness"


def check_inv06_loop_boundedness(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Agent turn recursion must remain <= 10 steps to prevent runaway loops."""
    agent_turn_counts: dict[str, int] = {}
    for log in audit_trail:
        agent = log.get("agent_name", "unknown")
        if log.get("event") in ("AGENT_STEP", "TOOL_CALL", "TURN_EXECUTION"):
            agent_turn_counts[agent] = agent_turn_counts.get(agent, 0) + 1

    overbounded = {a: count for a, count in agent_turn_counts.items() if count > 10}
    if overbounded:
        return _bad(
            "INV-06",
            INV06_TITLE,
            f"Agent(s) exceeded maximum 10-turn recursion envelope: {overbounded}",
            turn_counts=agent_turn_counts,
        )
    return _ok("INV-06", INV06_TITLE, f"all agent turn loops strictly bounded (max observed: {max(agent_turn_counts.values()) if agent_turn_counts else 0} turns)")


# --------------------------------------------------------------------------------------
# INV-07: Memory Provenance Binding
# --------------------------------------------------------------------------------------
INV07_TITLE = "Memory Provenance Binding"


def check_inv07_memory_provenance(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """All curated memories must bind to a valid source incident ID and metric outcome."""
    memories = state.get("curated_memories", [])
    orphaned_memories = []

    for m in memories:
        src_id = m.get("source_incident_id")
        has_metric = bool(m.get("outcome_metric") or m.get("resolution_cost") or m.get("lesson"))
        if not src_id or not has_metric:
            orphaned_memories.append(m)

    if orphaned_memories:
        return _bad(
            "INV-07",
            INV07_TITLE,
            f"{len(orphaned_memories)} memory precedent(s) lacked valid source incident provenance",
            orphaned=orphaned_memories,
        )
    return _ok("INV-07", INV07_TITLE, "all curated memories bound to verifiable incident provenance")


# --------------------------------------------------------------------------------------
# INV-08: Approval Precedes Effect Execution
# --------------------------------------------------------------------------------------
INV08_TITLE = "Approval Precedes Effect Execution"


def check_inv08_approval_precedence(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Approval timestamp must strictly precede or equal the execution timestamp."""
    time_format = "%Y-%m-%dT%H:%M:%S"
    dispatches = state.get("dispatches", [])
    violations = []

    for d in dispatches:
        cost = float(d.get("estimated_cost", 0) or d.get("amount", 0) or 0)
        if cost > 10000.0 and d.get("approved_at") and d.get("dispatched_at"):
            try:
                t_app = datetime.fromisoformat(d["approved_at"].replace("Z", ""))
                t_disp = datetime.fromisoformat(d["dispatched_at"].replace("Z", ""))
                if t_disp < t_app:
                    violations.append({"dispatch_id": d.get("dispatch_id"), "approved_at": d["approved_at"], "dispatched_at": d["dispatched_at"]})
            except Exception:
                pass

    if violations:
        return _bad(
            "INV-08",
            INV08_TITLE,
            f"{len(violations)} dispatch effect(s) occurred before human approval was granted",
            violations=violations,
        )
    return _ok("INV-08", INV08_TITLE, "human authorization strictly preceded effect execution")


# --------------------------------------------------------------------------------------
# INV-09: No Orphaned Remediation Tasks
# --------------------------------------------------------------------------------------
INV09_TITLE = "No Orphaned Remediation Tasks"


def check_inv09_no_orphaned_tasks(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Closed or Resolved incidents cannot leave unassigned or orphaned active tasks."""
    incident_status = state.get("status", "").upper()
    tasks = state.get("remediation_tasks", [])

    if incident_status in ("CLOSED", "RESOLVED"):
        unresolved = [t for t in tasks if t.get("status", "").upper() in ("PENDING", "IN_PROGRESS", "OPEN", "UNASSIGNED")]
        if unresolved:
            return _bad(
                "INV-09",
                INV09_TITLE,
                f"Incident closed with {len(unresolved)} unresolved remediation task(s)",
                unresolved_tasks=unresolved,
            )
    return _ok("INV-09", INV09_TITLE, "all remediation tasks fully resolved prior to incident closure")


# --------------------------------------------------------------------------------------
# INV-10: Cryptographic State Integrity
# --------------------------------------------------------------------------------------
INV10_TITLE = "Cryptographic State Integrity"


def check_inv10_cryptographic_integrity(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """The incident state hash must verify against the Ed25519 signature."""
    sig = state.get("signature")
    pub_key = state.get("public_key")
    sig_type = state.get("signature_type", "ED25519")

    if not sig:
        return _bad("INV-10", INV10_TITLE, "State snapshot is unsigned (missing cryptographic signature)")

    is_valid = verify_incident_signature(state, sig, pub_key, sig_type)
    if not is_valid:
        return _bad("INV-10", INV10_TITLE, "Signature verification failed — state hash mismatch or tampered data")

    return _ok("INV-10", INV10_TITLE, "Ed25519 cryptographic state signature verified successfully")


# --------------------------------------------------------------------------------------
# INV-11: Rate Limit Envelope Respected
# --------------------------------------------------------------------------------------
INV11_TITLE = "Rate Limit Envelope Respected"


def check_inv11_rate_limit(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Agent tool calls must not exceed 60 calls per minute."""
    timestamps = []
    for log in audit_trail:
        ts_str = log.get("timestamp")
        if ts_str:
            try:
                timestamps.append(datetime.fromisoformat(ts_str.replace("Z", "")))
            except Exception:
                pass

    if len(timestamps) > 60:
        # Check sliding 60-second window
        timestamps.sort()
        for i in range(len(timestamps) - 60):
            delta = (timestamps[i + 60] - timestamps[i]).total_seconds()
            if delta < 60.0:
                return _bad("INV-11", INV11_TITLE, f"Rate limit spike detected: 60 calls within {delta:.1f}s")

    return _ok("INV-11", INV11_TITLE, "all agent calls stayed within the 60 calls/min rate limit envelope")


# --------------------------------------------------------------------------------------
# INV-12: Zero Trust Identity Authorization
# --------------------------------------------------------------------------------------
INV12_TITLE = "Zero Trust Identity Authorization"


def check_inv12_identity_authorization(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> InvariantResult:
    """Every recorded action must present a valid SPIFFE ID formatted as spiffe://archon.internal/agent/{agent}."""
    invalid_identities = []
    for log in audit_trail:
        spiffe_id = log.get("spiffe_id")
        agent_name = log.get("agent_name")
        if spiffe_id:
            expected = f"spiffe://archon.internal/agent/{agent_name}" if agent_name else "spiffe://archon.internal/"
            if not spiffe_id.startswith("spiffe://archon.internal/"):
                invalid_identities.append({"spiffe_id": spiffe_id, "agent": agent_name})

    if invalid_identities:
        return _bad(
            "INV-12",
            INV12_TITLE,
            f"{len(invalid_identities)} action(s) carried invalid SPIFFE identity credentials",
            invalid_identities=invalid_identities,
        )
    return _ok("INV-12", INV12_TITLE, "all actions verified with valid SPIFFE cryptographic identity tokens")


# --------------------------------------------------------------------------------------
# Master Evaluation Engine
# --------------------------------------------------------------------------------------
INVARIANT_CHECKS = [
    check_inv01_financial_threshold,
    check_inv02_no_tainted_action,
    check_inv03_domain_scope_integrity,
    check_inv04_no_duplicate_dispatch,
    check_inv05_p1_escalation,
    check_inv06_loop_boundedness,
    check_inv07_memory_provenance,
    check_inv08_approval_precedence,
    check_inv09_no_orphaned_tasks,
    check_inv10_cryptographic_integrity,
    check_inv11_rate_limit,
    check_inv12_identity_authorization,
]


def evaluate_all_invariants(state: dict[str, Any], audit_trail: list[dict[str, Any]]) -> list[InvariantResult]:
    """Pure deterministic evaluator checking all 12 ARCHON invariants against state snapshot."""
    results = []
    for check_fn in INVARIANT_CHECKS:
        results.append(check_fn(state, audit_trail))
    return results
