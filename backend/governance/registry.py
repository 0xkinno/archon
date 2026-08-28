import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.agent_models import AgentManifest, AgentStatus, Playbook
from services.firestore_service import firestore_service
from .gateway import DOMAIN_TOOL_REGISTRY

logger = logging.getLogger("archon.registry")


class AgentRegistry:
    """Central catalog for discovering, versioning, and monitoring specialist agents."""

    def __init__(self):
        self._manifests: Dict[str, AgentManifest] = {}
        self._boot_default_agents()

    def _boot_default_agents(self):
        """Initializes default fleet manifests."""
        default_fleet = [
            {
                "name": "incident_commander",
                "domain": "orchestration",
                "version": "1.0.0",
                "description": "Orchestrates incident response by classifying signals, activating playbooks, and delegating to specialists.",
                "capabilities": ["Signal Classification", "Severity Triage", "Playbook Activation", "Fleet Delegation"],
                "tools": ["classify_incident", "activate_playbook", "search_precedent"],
            },
            {
                "name": "impact_assessor",
                "domain": "blast_radius",
                "version": "1.0.0",
                "description": "Maps affected buildings, occupant counts, secondary utility dependencies, and structural risk zones.",
                "capabilities": ["BMS Telemetry Query", "Occupancy Sweeps", "Topological Dependency Mapping"],
                "tools": ["query_building_systems", "check_occupancy", "map_dependencies"],
            },
            {
                "name": "vendor_coordinator",
                "domain": "vendor_management",
                "version": "1.0.0",
                "description": "Evaluates vendor reliability scores, contract SLAs, and handles automated emergency contractor dispatches.",
                "capabilities": ["Vendor Directory Search", "Auto-Dispatching", "Historical SLA Review"],
                "tools": ["search_vendors", "dispatch_vendor", "check_vendor_history"],
            },
            {
                "name": "compliance_inspector",
                "domain": "regulatory",
                "version": "1.0.0",
                "description": "Cross-references active incidents against Fire Marshal, OSHA, and EPA inspection schedules and generates proof packages.",
                "capabilities": ["Audit Schedule Query", "Compliance Doc Assembly", "Violation Tracking"],
                "tools": ["check_inspection_schedule", "generate_compliance_doc", "flag_violations"],
            },
            {
                "name": "communications_officer",
                "domain": "stakeholder_comms",
                "version": "1.0.0",
                "description": "Drafts and dispatches multi-tiered emergency notifications and status updates tailored by severity.",
                "capabilities": ["Severity-Based Routing", "Urgent Alert Drafting", "Contact Directory Lookup"],
                "tools": ["draft_notification", "route_by_severity", "check_contact_directory"],
            },
            {
                "name": "remediation_tracker",
                "domain": "corrective_actions",
                "version": "1.0.0",
                "description": "Creates, monitors, and escalates physical remediation tasks and manages multi-shift operational handoffs.",
                "capabilities": ["Task Lifecycle CRUD", "Overdue Escalation", "Shift Handoff Log Compilation"],
                "tools": ["create_task", "update_task", "escalate_overdue", "shift_handoff"],
            },
            {
                "name": "memory_curator",
                "domain": "institutional_memory",
                "version": "1.0.0",
                "description": "Extracts operational lessons, updates vendor performance scorecards, and encodes permanent campus knowledge.",
                "capabilities": ["Lesson Extraction", "Precedent Semantic Retrieval", "Scorecard Evolution"],
                "tools": ["store_lesson", "search_precedent", "update_vendor_scorecard"],
            },
        ]

        for a in default_fleet:
            spiffe_id = f"spiffe://archon.campus/agent/{a['name']}"
            manifest = AgentManifest(
                agent_id=spiffe_id,
                name=a["name"],
                version=a["version"],
                domain=a["domain"],
                description=a["description"],
                capabilities=a["capabilities"],
                tools=a["tools"],
                status=AgentStatus.ACTIVE,
                registered_at=datetime.utcnow(),
                last_heartbeat=datetime.utcnow(),
            )
            self._manifests[manifest.agent_id] = manifest
            # Also register in firestore service synchronous memory
            firestore_service._agents[manifest.agent_id] = manifest.model_dump()

    def register_agent(self, manifest: AgentManifest) -> AgentManifest:
        """Registers or updates an agent capability manifest."""
        manifest.last_heartbeat = datetime.utcnow()
        self._manifests[manifest.agent_id] = manifest
        firestore_service._agents[manifest.agent_id] = manifest.model_dump()
        logger.info(f"Registered agent '{manifest.name}' ({manifest.agent_id}) in registry.")
        return manifest

    def deregister_agent(self, agent_id: str) -> bool:
        """Removes an agent from the active catalog."""
        if agent_id in self._manifests:
            del self._manifests[agent_id]
            if agent_id in firestore_service._agents:
                del firestore_service._agents[agent_id]
            return True
        return False

    def get_agent(self, agent_id_or_name: str) -> Optional[AgentManifest]:
        """Looks up an agent by SPIFFE URI or short name."""
        if agent_id_or_name in self._manifests:
            return self._manifests[agent_id_or_name]
        for m in self._manifests.values():
            if m.name == agent_id_or_name:
                return m
        return None

    def list_agents(self) -> List[AgentManifest]:
        """Returns all registered agents."""
        return list(self._manifests.values())

    def heartbeat(self, agent_id: str) -> bool:
        """Records a heartbeat from an active agent."""
        agent = self.get_agent(agent_id)
        if agent:
            agent.last_heartbeat = datetime.utcnow()
            agent.missed_heartbeats = 0
            agent.status = AgentStatus.ACTIVE
            return True
        return False

    def check_health(self) -> Dict[str, AgentStatus]:
        """Evaluates health based on heartbeat recency."""
        now = datetime.utcnow()
        statuses = {}
        for aid, manifest in self._manifests.items():
            delta = (now - manifest.last_heartbeat).total_seconds()
            if delta > 300:  # 5 minutes
                manifest.status = AgentStatus.OFFLINE
            elif delta > 120:  # 2 minutes
                manifest.status = AgentStatus.DEGRADED
            else:
                manifest.status = AgentStatus.ACTIVE
            statuses[manifest.name] = manifest.status
        return statuses

    async def discover_agents(self, incident_type: str) -> List[AgentManifest]:
        """Discovers the ordered sequence of agents required for an incident type."""
        playbook_data = await firestore_service.get_playbook(incident_type)
        if not playbook_data:
            # Return full fleet if no specific playbook exists
            return self.list_agents()
        
        required_names = playbook_data.get("required_agents", [])
        discovered = []
        for name in required_names:
            agent = self.get_agent(name)
            if agent:
                discovered.append(agent)
        return discovered


agent_registry = AgentRegistry()
