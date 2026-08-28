import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from data.seed_campus import get_seed_vendors, get_seed_buildings
from services.firestore_service import firestore_service
from services.memory_service import memory_service


def search_vendors(specialty: str, urgency: str = "urgent") -> Dict[str, Any]:
    """Searches vendor directory for verified campus contractors matching the required specialty.
    
    Args:
        specialty: Trade specialty (e.g., 'plumbing', 'electrical', 'hvac', 'elevator', 'fire', 'hazmat').
        urgency: Urgency rating ('emergency', 'urgent', 'routine').
        
    Returns:
        Ranked contractor options with calculated response times, reliability metrics, and rates.
    """
    vendors = get_seed_vendors()
    matches = [v for v in vendors if any(specialty.lower() in s.lower() for s in v["specialties"])]

    if urgency == "emergency":
        matches.sort(key=lambda v: (v["avg_response_time_hours"], -v["reliability_score"]))
    else:
        matches.sort(key=lambda v: (-v["reliability_score"], v["avg_response_time_hours"]))

    ranked_list = []
    for v in matches[:3]:
        terms = v.get("contract_terms", {})
        rate = terms.get("emergency_rate" if urgency == "emergency" else "standard_rate", 150.0)
        ranked_list.append({
            "vendor_id": v["vendor_id"],
            "name": v["name"],
            "avg_response_time_hours": v["avg_response_time_hours"],
            "reliability_score": v["reliability_score"],
            "contract_status": terms.get("status", "ACTIVE"),
            "hourly_rate": rate,
            "sla_hours": terms.get("sla_hours", 4.0),
            "contact_phone": v.get("contact_info", {}).get("emergency_hotline"),
        })

    return {
        "status": "SUCCESS",
        "specialty": specialty,
        "urgency": urgency,
        "total_matched_vendors": len(matches),
        "recommended_vendors": ranked_list,
    }


def dispatch_vendor(
    vendor_id: str,
    incident_id: str,
    description: str,
    building_id: str,
    estimated_hours: float = 4.0
) -> Dict[str, Any]:
    """Dispatches a contractor to an active campus incident.
    
    Args:
        vendor_id: Identifier of the vendor (e.g., 'VND-001').
        incident_id: Active incident ID.
        description: Work order description.
        building_id: Target building.
        estimated_hours: Anticipated job duration in hours.
        
    Returns:
        Dispatch confirmation, tracking ID, ETA, and financial estimate.
    """
    vendors = get_seed_vendors()
    vendor = next((v for v in vendors if v["vendor_id"] == vendor_id), None)
    
    buildings = get_seed_buildings()
    bldg = next((b for b in buildings if b["building_id"] == building_id), None)

    if not vendor:
        return {"status": "ERROR", "reason": f"Vendor '{vendor_id}' not found in directory."}

    terms = vendor.get("contract_terms", {})
    rate = terms.get("emergency_rate", 200.0)
    cost = float(rate * estimated_hours)

    dispatch_id = f"DSP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    dispatch_record = {
        "dispatch_id": dispatch_id,
        "vendor_id": vendor_id,
        "vendor_name": vendor["name"],
        "incident_id": incident_id or "INC-GENERAL",
        "building_id": building_id,
        "building_name": bldg["name"] if bldg else building_id,
        "description": description,
        "status": "DISPATCHED",
        "estimated_arrival_hours": vendor["avg_response_time_hours"],
        "hourly_rate": rate,
        "estimated_hours": estimated_hours,
        "estimated_cost": cost,
        "dispatched_at": datetime.utcnow().isoformat(),
    }

    # Store dispatch in synchronous firestore map
    firestore_service._dispatches[dispatch_id] = dispatch_record

    return {
        "status": "SUCCESS",
        "dispatch_id": dispatch_id,
        "vendor_name": vendor["name"],
        "building": bldg["name"] if bldg else building_id,
        "estimated_arrival_hours": vendor["avg_response_time_hours"],
        "estimated_cost": cost,
        "dispatch_timestamp": dispatch_record["dispatched_at"],
        "confirmation": f"Dispatched {vendor['name']} to {bldg['name'] if bldg else building_id} (ETA: {vendor['avg_response_time_hours']} hrs, Est: ${cost:,.2f})",
    }


def check_vendor_history(vendor_id: str) -> Dict[str, Any]:
    """Retrieves vendor performance scorecard and institutional memory records.
    
    Args:
        vendor_id: The vendor to audit.
        
    Returns:
        Reliability history, prior incidents served, contract status, and institutional memory warnings.
    """
    vendors = get_seed_vendors()
    vendor = next((v for v in vendors if v["vendor_id"] == vendor_id), None)
    
    if not vendor:
        return {"status": "ERROR", "reason": f"Vendor '{vendor_id}' not found."}

    memories = [m for m in memory_service._memories if m.get("vendor_id") == vendor_id]

    return {
        "status": "SUCCESS",
        "vendor_id": vendor_id,
        "name": vendor["name"],
        "reliability_score": vendor["reliability_score"],
        "contract_status": vendor.get("contract_terms", {}).get("status", "ACTIVE"),
        "incidents_served_count": len(vendor.get("incidents_served", [])),
        "notes": vendor.get("notes", []),
        "institutional_memories": [m["content"] for m in memories],
        "is_under_review": vendor.get("contract_terms", {}).get("status") in ("UNDER_REVIEW", "PROBATIONARY"),
    }
