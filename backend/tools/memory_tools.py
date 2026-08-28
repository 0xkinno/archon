import asyncio
from typing import Dict, Any, List, Optional
from services.memory_service import memory_service


def store_lesson(
    incident_id: str,
    lesson: str,
    building_id: Optional[str] = None,
    vendor_id: Optional[str] = None,
    category: str = "incident_lesson"
) -> Dict[str, Any]:
    """Encodes an operational finding, equipment quirk, or response retrospective into institutional memory.
    
    Args:
        incident_id: Incident that generated this insight.
        lesson: Clear summary of the discovery or permanent corrective protocol.
        building_id: Optional campus building identifier.
        vendor_id: Optional contractor identifier.
        category: Knowledge category.
        
    Returns:
        Stored memory manifest and retention confirmation.
    """
    try:
        # Run async store_incident_lesson synchronously in current event loop or via helper
        loop = asyncio.get_event_loop()
        if loop.is_running():
            entry = loop.create_task(
                memory_service.store_incident_lesson(
                    incident_id=incident_id,
                    lesson=lesson,
                    building_id=building_id,
                    vendor_id=vendor_id,
                    category=category
                )
            )
        else:
            entry = loop.run_until_complete(
                memory_service.store_incident_lesson(
                    incident_id=incident_id,
                    lesson=lesson,
                    building_id=building_id,
                    vendor_id=vendor_id,
                    category=category
                )
            )
    except Exception:
        # Direct synchronous fallback
        memory_id = f"MEM-{len(memory_service._memories) + 1:03d}"
        entry = {
            "memory_id": memory_id,
            "incident_id": incident_id,
            "building_id": building_id,
            "vendor_id": vendor_id,
            "category": category,
            "content": lesson,
            "importance": 0.9,
        }
        memory_service._memories.append(entry)

    return {
        "status": "SUCCESS",
        "message": f"Encoded institutional memory for incident '{incident_id}'.",
        "lesson": lesson,
        "building_id": building_id,
    }


def search_precedent(query: str, limit: int = 5) -> Dict[str, Any]:
    """Searches 20 years of campus institutional wisdom for matching historical precedents.
    
    Args:
        query: Operational query string (e.g., 'Building F panel B3', 'chilled water loop failure', 'Atlas elevator').
        limit: Max precedents to return.
        
    Returns:
        Ranked historical incidents, root causes, permanent solutions, and relevance scores.
    """
    # Synchronous query from memory_service._memories
    query_lower = query.lower()
    matches = []
    
    for mem in memory_service._memories:
        content_lower = mem["content"].lower()
        score = 0.0
        
        # Keyword matching
        words = [w for w in query_lower.split() if len(w) > 2]
        matched_words = [w for w in words if w in content_lower]
        if matched_words:
            score = len(matched_words) / max(len(words), 1)
        elif any(w in content_lower for w in words):
            score = 0.5

        if mem.get("building_id") and mem["building_id"].lower() in query_lower:
            score += 0.4
        if mem.get("vendor_id") and mem["vendor_id"].lower() in query_lower:
            score += 0.4

        if score > 0.2:
            matches.append((score, mem))

    matches.sort(key=lambda x: x[0], reverse=True)
    results = [dict(item[1], relevance_score=round(min(item[0], 1.0), 3)) for item in matches[:limit]]

    if not results:
        # Fallback to top institutional memories
        results = [dict(m, relevance_score=0.5) for m in memory_service._memories[:limit]]

    return {
        "status": "SUCCESS",
        "query": query,
        "precedents_found": len(results),
        "precedents": results,
    }


def update_vendor_scorecard(vendor_id: str, incident_id: str, reliability_adjustment: float = -5.0, note: str = "") -> Dict[str, Any]:
    """Updates contractor reliability metrics and appends performance documentation into memory.
    
    Args:
        vendor_id: Contractor identifier.
        incident_id: Related incident.
        reliability_adjustment: Score delta (+/- points).
        note: Incident performance note.
        
    Returns:
        Updated score and scorecard status.
    """
    from data.seed_campus import get_seed_vendors
    vendors = get_seed_vendors()
    vendor = next((v for v in vendors if v["vendor_id"] == vendor_id), None)

    if not vendor:
        return {"status": "ERROR", "reason": f"Vendor '{vendor_id}' not found."}

    old_score = vendor["reliability_score"]
    new_score = max(0.0, min(100.0, old_score + reliability_adjustment))
    vendor["reliability_score"] = round(new_score, 1)

    lesson_text = f"Vendor scorecard update for {vendor['name']} (ID: {vendor_id}): Score adjusted by {reliability_adjustment:+.1f} (New: {new_score:.1f}). Reason: {note}"
    memory_service._memories.append({
        "memory_id": f"MEM-{len(memory_service._memories) + 1:03d}",
        "vendor_id": vendor_id,
        "incident_id": incident_id,
        "category": "vendor_scorecard",
        "content": lesson_text,
        "importance": 0.85,
    })

    return {
        "status": "SUCCESS",
        "vendor_id": vendor_id,
        "vendor_name": vendor["name"],
        "previous_score": old_score,
        "new_reliability_score": new_score,
        "adjustment": reliability_adjustment,
        "status_note": note,
    }
