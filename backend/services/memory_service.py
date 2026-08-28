import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from config import settings

logger = logging.getLogger("archon.memory")


class ArchonMemoryService:
    """Institutional memory service backed by Vertex AI Memory Bank with local semantic fallback."""

    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self.location = location or settings.GCP_LOCATION
        self.use_vertex = settings.USE_MEMORY_BANK and bool(settings.GOOGLE_API_KEY)
        
        # Local semantic store
        self._memories: List[Dict[str, Any]] = []
        self._seed_initial_memories()

    def _seed_initial_memories(self):
        """Seeds 20 years of campus institutional wisdom and incident precedents."""
        initial_seeds = [
            {
                "memory_id": "MEM-001",
                "building_id": "BLDG-F",
                "category": "electrical_quirk",
                "content": "Building F electrical panel B3 has tripped 5 times in the past year, always during high-humidity periods above 80%. Root cause identified as moisture infiltration through the east wall conduit penetration. Temporary fix: industrial dehumidifier in panel room. Permanent fix: re-seal conduit penetration with silicone mastic and replace affected thermal breakers. Estimated cost: $12,000. Last vendor used: Sparks Electric (VND-002), response time was 1.8 hours.",
                "created_at": "2025-11-14T08:30:00",
                "importance": 0.95,
                "tags": ["panel_b3", "humidity", "electrical", "sparks", "BLDG-F"]
            },
            {
                "memory_id": "MEM-002",
                "building_id": "BLDG-C",
                "category": "plumbing_water_loop",
                "content": "Building C sub-basement hydraulic pump room contains the primary chiller return cross-tie for Building H (Hospital NICU). In the event of a water main rupture in Building C, manual bypass valve V-104 must be actuated within 20 minutes to preserve chilled water circulation to Hospital Zone 3.",
                "created_at": "2025-06-20T14:15:00",
                "importance": 0.98,
                "tags": ["water_main", "chiller_bypass", "valve_v104", "nicu", "BLDG-C", "BLDG-H"]
            },
            {
                "memory_id": "MEM-003",
                "vendor_id": "VND-005",
                "category": "vendor_performance",
                "content": "Atlas Elevator Services (VND-005) recorded 3 maintenance no-shows in Q3 2026. Elevator shafts in Building A require certified state inspection slips. When Atlas fails to respond within 2 hours, automatically trigger contractual liquidated damages clause and notify secondary contractor.",
                "created_at": "2026-07-10T11:00:00",
                "importance": 0.88,
                "tags": ["atlas_elevator", "no_show", "sla_penalty", "BLDG-A", "VND-005"]
            },
            {
                "memory_id": "MEM-004",
                "building_id": "BLDG-D",
                "category": "compliance_inspection",
                "content": "State Fire Marshal inspection team in 2025 flagged Vivarium halon-substitute bottle hydrostatic tags. Inspector Captain Reynolds specifically checks emergency egress lighting battery discharge logs first before proceeding to chemical fume hoods.",
                "created_at": "2025-08-30T16:00:00",
                "importance": 0.92,
                "tags": ["fire_marshal", "reynolds", "vivarium", "battery_log", "BLDG-D"]
            },
            {
                "memory_id": "MEM-005",
                "building_id": "BLDG-H",
                "category": "critical_infrastructure",
                "content": "Hospital NICU (Zone 3) requires ambient temperature maintained at 68F (+-1.5F). If cooling loop supply drops below 42F or ambient rises above 74F, immediate life-safety escalation to charge nurse and clinical engineering is mandatory.",
                "created_at": "2026-01-15T09:00:00",
                "importance": 1.0,
                "tags": ["nicu", "temperature_critical", "life_safety", "BLDG-H"]
            },
            {
                "memory_id": "MEM-006",
                "vendor_id": "VND-001",
                "category": "vendor_excellence",
                "content": "Cascade Industrial Plumbing (VND-001) maintains high-pressure dewatering rigs on 24/7 standby. Average arrival time on P1 water breaches is 1.2 hours. Dispatcher Sarah Jenkins possesses direct access codes to Building C basement mechanical gates.",
                "created_at": "2026-03-01T10:00:00",
                "importance": 0.90,
                "tags": ["cascade", "plumbing", "p1_response", "VND-001"]
            }
        ]
        self._memories.extend(initial_seeds)

    async def store_incident_lesson(
        self,
        incident_id: str,
        lesson: str,
        building_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        category: str = "incident_lesson",
        importance: float = 0.8
    ) -> Dict[str, Any]:
        """Stores a lesson learned from an incident into persistent institutional memory."""
        memory_id = f"MEM-{len(self._memories) + 1:03d}"
        entry = {
            "memory_id": memory_id,
            "incident_id": incident_id,
            "building_id": building_id,
            "vendor_id": vendor_id,
            "category": category,
            "content": lesson,
            "created_at": datetime.utcnow().isoformat(),
            "importance": importance,
            "tags": [t.lower() for t in re.findall(r"\b[A-Za-z0-9_-]{3,}\b", f"{lesson} {building_id or ''} {vendor_id or ''}")]
        }
        self._memories.append(entry)
        logger.info(f"Stored institutional memory: {memory_id} for incident: {incident_id}")
        return entry

    async def search_precedent(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches institutional memory for relevant precedents using keyword & semantic scoring."""
        query_words = set(re.findall(r"\b[A-Za-z0-9_-]{2,}\b", query.lower()))
        scored_results = []

        for mem in self._memories:
            content_words = set(re.findall(r"\b[A-Za-z0-9_-]{2,}\b", mem["content"].lower()))
            tag_words = set(mem.get("tags", []))
            
            # Match intersection
            overlap = query_words.intersection(content_words.union(tag_words))
            if overlap:
                score = (len(overlap) / max(len(query_words), 1)) * mem.get("importance", 0.8)
                scored_results.append((score, mem))
            elif any(w in mem["content"].lower() for w in query_words):
                scored_results.append((0.5 * mem.get("importance", 0.8), mem))

        # Sort by relevance score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        results = [dict(item[1], relevance_score=round(item[0], 3)) for item in scored_results[:limit]]
        
        # If no specific keyword matched, return highest importance general memories
        if not results:
            general = sorted(self._memories, key=lambda x: x.get("importance", 0), reverse=True)[:limit]
            results = [dict(m, relevance_score=0.4) for m in general]

        return results

    async def update_vendor_scorecard(self, vendor_id: str, incident_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a vendor's performance scorecard in institutional memory."""
        note = f"Scorecard update for vendor {vendor_id} on incident {incident_id}: {metrics}"
        return await self.store_incident_lesson(
            incident_id=incident_id,
            lesson=note,
            vendor_id=vendor_id,
            category="vendor_scorecard",
            importance=0.85
        )

    async def get_building_history(self, building_id: str) -> List[Dict[str, Any]]:
        """Retrieves known issues and quirks for a specific campus building."""
        return [m for m in self._memories if m.get("building_id") == building_id]

    async def get_vendor_history(self, vendor_id: str) -> List[Dict[str, Any]]:
        """Retrieves institutional memory notes for a specific vendor."""
        return [m for m in self._memories if m.get("vendor_id") == vendor_id]

    async def list_all_memories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns all institutional memories."""
        return sorted(self._memories, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]


memory_service = ArchonMemoryService()
