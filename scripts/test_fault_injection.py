#!/usr/bin/env python3
"""
Deliberate Fault Injection Test for ARCHON Invariant Verifier.

Generates an invalid incident state with deliberate invariant violations:
1. INV-01: $28,000 emergency chiller repair executed with NO human director approval.
2. INV-04: Duplicate plumbing dispatches for the same building zone.
3. INV-09: Incident marked RESOLVED with an orphaned OPEN remediation task.
4. INV-10: Cryptographic signature mismatch / tampering.

Runs the verifier to prove it catches and isolates each failure deterministically.
"""

import json
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

faulted_manifest = {
    "incident_id": "INC-FAULT-INJECTED",
    "scenario": "DELIBERATE_CORRUPTION_TEST",
    "state": {
        "incident_id": "INC-FAULT-INJECTED",
        "title": "Deliberately Tampered Facility Incident",
        "building_id": "BUILDING-TAMPERED",
        "severity": "P1",
        "status": "RESOLVED",
        "commander_assigned": "incident_commander",
        "escalation_broadcast": True,
        "dispatches": [
            {
                "dispatch_id": "DSP-UNAUTHORIZED-01",
                "vendor_id": "VND-ROGUE-01",
                "vendor_name": "Rogue Mechanical",
                "specialty": "hvac_chiller",
                "building_id": "BUILDING-TAMPERED",
                "estimated_cost": 28000.0,
                "status": "EXECUTED",  # VIOLATION: >$10k executed with no approval_id
                "dispatched_at": "2026-08-30T05:00:00Z",
            },
            {
                "dispatch_id": "DSP-PLUMB-A",
                "vendor_id": "VND-PLUMB-01",
                "specialty": "emergency_plumbing",
                "building_id": "BUILDING-TAMPERED",
                "status": "ACTIVE",
            },
            {
                "dispatch_id": "DSP-PLUMB-B",
                "vendor_id": "VND-PLUMB-02",
                "specialty": "emergency_plumbing",
                "building_id": "BUILDING-TAMPERED",
                "status": "ACTIVE",  # VIOLATION: Duplicate active dispatch for same building & trade
            }
        ],
        "remediation_tasks": [
            {
                "task_id": "TSK-ORPHAN-01",
                "description": "Unattended high-pressure valve replacement",
                "status": "OPEN",  # VIOLATION: Orphaned task on RESOLVED incident
            }
        ],
        "curated_memories": [],
        "state_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "signature": "INVALID_SIGNATURE_TAMPERED_PAYLOAD_BASE64",
        "signature_type": "ED25519",
        "public_key": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAUUdWObXL2yamVVATqa5eSj9IxzTCIdmS49VjBNH0Tsc=\n-----END PUBLIC KEY-----\n"
    },
    "audit_trail": [
        {
            "event": "DISPATCH_VENDOR",
            "dispatch_id": "DSP-UNAUTHORIZED-01",
            "timestamp": "2026-08-30T05:00:00Z",
            "agent_name": "vendor_coordinator",
            "spiffe_id": "spiffe://archon.internal/agent/vendor_coordinator",
            "tool_name": "dispatch_vendor"
        }
    ]
}

fault_file = REPO_ROOT / "evidence" / "incidents" / "INC-FAULT-INJECTED.manifest.json"
fault_file.write_text(json.dumps(faulted_manifest, indent=2), encoding="utf-8")
print(f"Wrote faulted manifest to {fault_file}")

# Run verifier against the faulted manifest
print("\nRunning verifier against faulted manifest (Expecting FAIL)...")
res = subprocess.run([
    sys.executable,
    str(REPO_ROOT / "scripts" / "verify_incident.py"),
    "--manifest", str(fault_file)
], capture_output=True, text=True)

print(res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)
print(f"Process Exit Code: {res.returncode} (Expected 1)")
