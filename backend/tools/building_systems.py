from typing import Dict, Any, List, Optional
from services.firestore_service import firestore_service
from data.seed_campus import get_seed_buildings


def query_building_systems(building_id: str, system_type: Optional[str] = None) -> Dict[str, Any]:
    """Queries campus building telemetry, active systems, and critical environmental zones.
    
    Args:
        building_id: Canonical identifier of the building (e.g., 'BLDG-C', 'BLDG-H').
        system_type: Optional filter for specific system (e.g., 'hvac', 'plumbing', 'electrical').
    
    Returns:
        Structured dictionary containing building name, address, active systems, critical zones, and special operational rules.
    """
    buildings = get_seed_buildings()
    bldg = next((b for b in buildings if b["building_id"] == building_id), None)
    
    if not bldg:
        return {"status": "ERROR", "reason": f"Building '{building_id}' not found in campus topology."}

    matched_systems = bldg["systems"]
    if system_type:
        matched_systems = [s for s in bldg["systems"] if system_type.lower() in s.lower()]

    return {
        "status": "SUCCESS",
        "building_id": bldg["building_id"],
        "name": bldg["name"],
        "address": bldg["address"],
        "floors": bldg["floors"],
        "systems_queried": matched_systems,
        "all_systems": bldg["systems"],
        "critical_zones": bldg["critical_zones"],
        "special_requirements": bldg["special_requirements"],
        "telemetry_health": "NORMAL" if not matched_systems else "ALERT_ACTIVE",
    }


def check_occupancy(building_id: str) -> Dict[str, Any]:
    """Calculates current headcount, capacity percentage, and life-safety evacuation priority.
    
    Args:
        building_id: Target building identifier.
        
    Returns:
        Occupancy details, capacity headroom, and high-density risk flag.
    """
    buildings = get_seed_buildings()
    bldg = next((b for b in buildings if b["building_id"] == building_id), None)
    
    if not bldg:
        return {"status": "ERROR", "reason": f"Building '{building_id}' not found."}

    capacity = bldg.get("occupancy_capacity", 100)
    current = bldg.get("current_occupancy", int(capacity * 0.7))
    pct = round((current / capacity) * 100, 1)

    return {
        "status": "SUCCESS",
        "building_id": building_id,
        "name": bldg["name"],
        "current_occupancy": current,
        "occupancy_capacity": capacity,
        "capacity_utilization_pct": pct,
        "high_density_hazard": pct > 75.0,
        "evacuation_priority": "CRITICAL" if pct > 80.0 or "Hospital" in bldg["name"] else "STANDARD",
    }


def map_dependencies(building_id: str, system: Optional[str] = None) -> Dict[str, Any]:
    """Traverses campus topological graph to identify all upstream and downstream dependencies.
    
    Args:
        building_id: Source building experiencing an incident.
        system: The impaired utility or service (e.g., 'plumbing', 'chilled_water', 'electrical').
        
    Returns:
        List of cascadingly affected dependent buildings, critical ward exposure, and blast radius tier.
    """
    buildings = get_seed_buildings()
    source_bldg = next((b for b in buildings if b["building_id"] == building_id), None)
    
    if not source_bldg:
        return {"status": "ERROR", "reason": f"Building '{building_id}' not found."}

    # Find downstream buildings that list this building in their dependencies
    downstream = [
        {
            "building_id": b["building_id"],
            "name": b["name"],
            "critical_zones": b["critical_zones"],
            "special_requirements": b["special_requirements"]
        }
        for b in buildings
        if building_id in b.get("dependencies", [])
    ]

    has_hospital = any(b["building_id"] == "BLDG-H" for b in downstream)
    severity_boost = "P1_LIFE_SAFETY" if has_hospital else "P2_MULTI_BUILDING" if downstream else "P3_ISOLATED"

    return {
        "status": "SUCCESS",
        "source_building": {
            "building_id": source_bldg["building_id"],
            "name": source_bldg["name"],
            "special_requirements": source_bldg["special_requirements"]
        },
        "impaired_system": system or "all_utilities",
        "upstream_providers": source_bldg.get("dependencies", []),
        "downstream_dependent_buildings": downstream,
        "total_secondary_buildings_affected": len(downstream),
        "critical_ward_exposed": has_hospital,
        "blast_radius_classification": severity_boost,
    }
