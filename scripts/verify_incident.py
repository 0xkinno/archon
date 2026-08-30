#!/usr/bin/env python3
"""
ARCHON Offline Incident Invariant Verifier.

Pulls stored incident state and audit traces independently of the live API/Gemini,
evaluates all 12 ARCHON governance invariants deterministically in pure Python,
and outputs a per-invariant PASS/FAIL evidence audit.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Tuple

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.governance.invariants import evaluate_all_invariants, InvariantResult
from backend.governance.signing import compute_state_hash, sign_incident_state


def load_from_manifest_file(path: Path) -> Tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load incident state and audit trail from a local JSON manifest file."""
    content = json.loads(path.read_text(encoding="utf-8"))
    state = content.get("state", content)
    audit_trail = content.get("audit_trail", state.get("audit_trail", []))
    return state, audit_trail


def load_from_firestore_or_local(incident_id: str) -> Tuple[dict[str, Any], list[dict[str, Any]]]:
    """Attempt to load from Firestore, fallback to local evidence store."""
    # Check local evidence first
    evidence_dir = REPO_ROOT / "evidence" / "incidents"
    local_manifest = evidence_dir / f"{incident_id}.manifest.json"
    if local_manifest.exists():
        return load_from_manifest_file(local_manifest)

    # Check data/incidents
    data_manifest = REPO_ROOT / "backend" / "data" / f"{incident_id}.json"
    if data_manifest.exists():
        return load_from_manifest_file(data_manifest)

    # Attempt Firestore fetch
    try:
        from backend.services.firestore_service import get_firestore_client
        db = get_firestore_client()
        if db:
            doc = db.collection("incidents").document(incident_id).get()
            if doc.exists:
                state = doc.to_dict()
                # Fetch audit logs subcollection or query
                logs_query = db.collection("audit_logs").where("incident_id", "==", incident_id).stream()
                audit_trail = [l.to_dict() for l in logs_query]
                return state, audit_trail
    except Exception as e:
        print(f"[NOTE] Firestore fetch bypassed ({e}), relying on local snapshot store.")

    raise FileNotFoundError(f"Could not locate incident manifest for ID: {incident_id}")


def format_table(results: list[InvariantResult], incident_id: str, state_hash: str) -> str:
    """Format invariant verification results as an institutional audit table."""
    lines = []
    lines.append("=" * 80)
    lines.append(f" ARCHON GOVERNANCE INVARIANT VERIFIER -- INCIDENT {incident_id}")
    lines.append(f" Canonical State Hash: {state_hash}")
    lines.append("=" * 80)
    lines.append(f"{'INVARIANT':<10} | {'TITLE':<38} | {'VERDICT':<6} | {'EVIDENCE / DETAIL'}")
    lines.append("-" * 80)

    all_passed = True
    for r in results:
        verdict = "PASS" if r.holds else "FAIL"
        if not r.holds:
            all_passed = False
        detail_snippet = (r.detail[:60] + "...") if len(r.detail) > 60 else r.detail
        lines.append(f"{r.invariant_id:<10} | {r.title:<38} | {verdict:<6} | {detail_snippet}")

    lines.append("=" * 80)
    summary_verdict = "ALL INVARIANTS SATISFIED (PASS)" if all_passed else "GOVERNANCE VIOLATION DETECTED (FAIL)"
    lines.append(f"FINAL AUDIT RESULT: {summary_verdict}")
    lines.append("=" * 80)
    return "\n".join(lines), all_passed


def main():
    parser = argparse.ArgumentParser(description="ARCHON Offline Invariant Verifier")
    parser.add_argument("--incident-id", "-i", help="Incident ID to verify")
    parser.add_argument("--manifest", "-m", help="Path to local incident manifest JSON")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if not args.incident_id and not args.manifest:
        # Default to a seeded demo incident if none specified
        evidence_dir = REPO_ROOT / "evidence" / "incidents"
        if evidence_dir.exists():
            manifests = list(evidence_dir.glob("*.manifest.json"))
            if manifests:
                args.manifest = str(manifests[0])
            else:
                args.incident_id = "INC-STORM-2026-08"
        else:
            args.incident_id = "INC-STORM-2026-08"

    try:
        if args.manifest:
            manifest_path = Path(args.manifest)
            state, audit_trail = load_from_manifest_file(manifest_path)
            inc_id = state.get("incident_id", manifest_path.stem.replace(".manifest", ""))
        else:
            state, audit_trail = load_from_firestore_or_local(args.incident_id)
            inc_id = args.incident_id

        # Compute hash
        state_hash = compute_state_hash(state)
        results = evaluate_all_invariants(state, audit_trail)

        if args.json:
            out = {
                "incident_id": inc_id,
                "state_hash": state_hash,
                "overall_pass": all(r.holds for r in results),
                "invariants": [r.as_dict() for r in results],
            }
            print(json.dumps(out, indent=2))
        else:
            table_str, all_passed = format_table(results, inc_id, state_hash)
            print(table_str)

        sys.exit(0 if all(r.holds for r in results) else 1)

    except Exception as e:
        print(f"ERROR: Verifier failed execution: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
