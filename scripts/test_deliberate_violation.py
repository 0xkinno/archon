import json
import sys
from pathlib import Path

# Add backend and repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "backend"))

from backend.governance.signing import sign_incident_state

def create_broken_manifests():
    evidence_dir = REPO_ROOT / "evidence" / "incidents"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # 1. Deliberate INV-08 Violation: Approval timestamp strictly AFTER dispatch timestamp
    inv08_state = {
        "incident_id": "INC-BROKEN-INV08",
        "title": "Deliberate INV-08 Timing Violation Test",
        "building_id": "BUILDING-E",
        "severity": "P1",
        "status": "RESOLVED",
        "commander_assigned": "incident_commander",
        "escalation_broadcast": True,
        "dispatches": [
            {
                "dispatch_id": "DSP-BROKEN-01",
                "vendor_id": "VND-HYDRO-01",
                "vendor_name": "Apex Dewatering Solutions",
                "specialty": "commercial_pumping",
                "building_id": "BUILDING-E",
                "estimated_cost": 14500.0,
                "status": "COMPLETED",
                "approval_id": "APP-DIR-LATE-01",
                "authorized_by": "Director of Facilities",
                # VIOLATION: Dispatched at 04:12:00Z, but approval occurred LATER at 04:25:00Z!
                "approved_at": "2026-08-30T04:25:00Z",
                "dispatched_at": "2026-08-30T04:12:00Z",
            }
        ],
        "remediation_tasks": [
            {"task_id": "TSK-01", "description": "Verify flood pumps", "status": "COMPLETED"}
        ],
        "curated_memories": [
            {
                "memory_id": "MEM-01",
                "source_incident_id": "INC-BROKEN-INV08",
                "lesson": "Pumping deployment test lesson",
                "outcome_metric": "Verified timing constraint violation",
                "resolution_cost": 14500.0
            }
        ]
    }
    # Sign state cleanly so INV-10 passes and isolates ONLY the INV-08 failure
    sig_meta = sign_incident_state(inv08_state)
    inv08_state.update(sig_meta)

    inv08_audit = [
        {"event": "SIGNAL_INGEST", "agent_name": "incident_commander", "spiffe_id": "spiffe://archon.internal/agent/incident_commander"},
        {"event": "ESCALATION_BROADCAST", "severity": "P1", "agent_name": "communications_officer", "spiffe_id": "spiffe://archon.internal/agent/communications_officer"},
        {"event": "DISPATCH_VENDOR", "dispatch_id": "DSP-BROKEN-01", "timestamp": "2026-08-30T04:12:00Z", "agent_name": "vendor_coordinator", "spiffe_id": "spiffe://archon.internal/agent/vendor_coordinator"},
        {"event": "HUMAN_APPROVAL_GRANTED", "approval_id": "APP-DIR-LATE-01", "timestamp": "2026-08-30T04:25:00Z", "authorized_by": "Director of Facilities"},
    ]

    manifest_inv08 = {
        "manifest_version": "1.0",
        "incident_id": "INC-BROKEN-INV08",
        "state": inv08_state,
        "audit_trail": inv08_audit
    }
    p08 = evidence_dir / "INC-BROKEN-INV08.manifest.json"
    p08.write_text(json.dumps(manifest_inv08, indent=2), encoding="utf-8")
    print(f"Wrote broken INV-08 manifest to {p08}")

    # 2. Deliberate INV-07 Violation: Memory entry with missing/unanchored source incident ID
    inv07_state = {
        "incident_id": "INC-BROKEN-INV07",
        "title": "Deliberate INV-07 Memory Provenance Violation Test",
        "building_id": "BUILDING-C",
        "severity": "P2",
        "status": "RESOLVED",
        "dispatches": [],
        "remediation_tasks": [
            {"task_id": "TSK-01", "description": "Chiller sensor recalibration", "status": "COMPLETED"}
        ],
        "curated_memories": [
            {
                "memory_id": "MEM-ORPHAN-01",
                # VIOLATION: Empty source incident ID!
                "source_incident_id": "",
                "lesson": "Floating unanchored tribal knowledge lesson",
                "outcome_metric": "Undefined",
                "resolution_cost": 0.0
            }
        ]
    }
    sig_meta7 = sign_incident_state(inv07_state)
    inv07_state.update(sig_meta7)

    inv07_audit = [
        {"event": "SIGNAL_INGEST", "agent_name": "incident_commander", "spiffe_id": "spiffe://archon.internal/agent/incident_commander"},
        {"event": "MEMORY_RECORDED", "memory_id": "MEM-ORPHAN-01", "agent_name": "memory_curator", "spiffe_id": "spiffe://archon.internal/agent/memory_curator"},
    ]
    manifest_inv07 = {
        "manifest_version": "1.0",
        "incident_id": "INC-BROKEN-INV07",
        "state": inv07_state,
        "audit_trail": inv07_audit
    }
    p07 = evidence_dir / "INC-BROKEN-INV07.manifest.json"
    p07.write_text(json.dumps(manifest_inv07, indent=2), encoding="utf-8")
    print(f"Wrote broken INV-07 manifest to {p07}")

if __name__ == "__main__":
    create_broken_manifests()
