from typing import Dict, Any, List, Optional
from datetime import datetime
from data.seed_campus import get_seed_inspections, get_seed_buildings


def check_inspection_schedule(building_id: Optional[str] = None, agency: Optional[str] = None) -> Dict[str, Any]:
    """Cross-references campus locations against regulatory and safety inspection schedules.
    
    Args:
        building_id: Optional building filter (e.g., 'BLDG-D').
        agency: Optional regulatory agency filter (e.g., 'Fire Marshal', 'OSHA', 'EPA').
        
    Returns:
        Matching upcoming audits, deadlines, required proof documents, and prior citations.
    """
    inspections = get_seed_inspections()
    
    filtered = inspections
    if building_id:
        filtered = [i for i in filtered if i["building_id"] == building_id]
    if agency:
        filtered = [i for i in filtered if agency.lower() in i["agency"].lower()]

    return {
        "status": "SUCCESS",
        "total_upcoming_inspections": len(filtered),
        "inspections": filtered,
        "high_priority_deadlines": [i for i in filtered if "Fire" in i["agency"] or "Hospital" in i["inspection_type"]],
    }


def generate_compliance_doc(
    inspection_id: str,
    incident_id: Optional[str] = None,
    document_type: str = "Pre-Inspection Compliance Packet"
) -> Dict[str, Any]:
    """Assembles a formal compliance documentation package with signed verification logs.
    
    Args:
        inspection_id: Target inspection identifier.
        incident_id: Optional related active incident ID.
        document_type: Category of compliance packet.
        
    Returns:
        Generated compliance manifest, verification checklist, and archive reference.
    """
    inspections = get_seed_inspections()
    insp = next((i for i in inspections if i["inspection_id"] == inspection_id), None)
    
    if not insp:
        return {"status": "ERROR", "reason": f"Inspection '{inspection_id}' not found."}

    doc_id = f"DOC-COMP-{datetime.utcnow().strftime('%Y%m%d')}-{insp['building_id']}"
    manifest = {
        "document_id": doc_id,
        "document_type": document_type,
        "inspection_target": insp["inspection_type"],
        "agency": insp["agency"],
        "building_id": insp["building_id"],
        "scheduled_date": insp["scheduled_date"],
        "compiled_at": datetime.utcnow().isoformat(),
        "verified_items": [f"Certified: {doc}" for doc in insp.get("required_documents", [])],
        "resolved_violations": [f"Remediated Proof: {viol}" for viol in insp.get("outstanding_violations", [])],
        "compliance_status": "READY_FOR_SUBMISSION",
        "signoff_authority": "ARCHON Governing Compliance Engine",
    }

    return {
        "status": "SUCCESS",
        "document_id": doc_id,
        "manifest": manifest,
        "summary": f"Generated compliance packet '{doc_id}' for {insp['agency']} audit at {insp['building_id']}.",
    }


def flag_violations(building_id: str, violation_summary: str, severity: str = "HIGH") -> Dict[str, Any]:
    """Logs and flags a regulatory or environmental safety violation requiring urgent remediation.
    
    Args:
        building_id: Building where violation occurred.
        violation_summary: Specific code or safety deficiency description.
        severity: Urgency ('CRITICAL', 'HIGH', 'MEDIUM').
        
    Returns:
        Registered violation record and mandatory remediation timeline.
    """
    buildings = get_seed_buildings()
    bldg = next((b for b in buildings if b["building_id"] == building_id), None)

    flag_id = f"VIOL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    return {
        "status": "SUCCESS",
        "flag_id": flag_id,
        "building_id": building_id,
        "building_name": bldg["name"] if bldg else building_id,
        "violation_summary": violation_summary,
        "severity": severity,
        "remediation_window_hours": 24 if severity == "CRITICAL" else 72,
        "logged_at": datetime.utcnow().isoformat(),
    }
