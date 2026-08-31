import os
import json
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Ensure environment variables and service account credentials are loaded
env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

cred_file = Path(__file__).resolve().parent.parent / "secrets" / "firebase-service-account.json"
if cred_file.exists() and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_file)

from config import settings
from data.seed_campus import (
    get_seed_buildings,
    get_seed_vendors,
    get_seed_inspections,
    get_seed_playbooks,
)
from models.incident import Incident, RemediationTask, DispatchRecord
from models.agent_models import AgentManifest
from models.audit import AuditEntry, Span, ApprovalRequest

logger = logging.getLogger("archon.firestore")


class FirestoreService:
    """Async Firestore client with thread-safe in-memory fallback for local execution & tests."""

    def __init__(self):
        has_creds = bool(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON") or
            settings.GOOGLE_APPLICATION_CREDENTIALS_JSON or
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or
            (settings.GCP_PROJECT_ID and settings.GOOGLE_API_KEY)
        )
        self.use_live_gcp = has_creds
        self._db = None
        self._initialized = False

        # In-memory storage collections / cache
        self._incidents: Dict[str, Dict[str, Any]] = {}
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._spans: Dict[str, Dict[str, Any]] = {}
        self._approvals: Dict[str, Dict[str, Any]] = {}
        self._dispatches: Dict[str, Dict[str, Any]] = {}
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._buildings: Dict[str, Dict[str, Any]] = {}
        self._vendors: Dict[str, Dict[str, Any]] = {}
        self._inspections: Dict[str, Dict[str, Any]] = {}
        self._playbooks: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        """Initializes database connection and seeds initial catalog if empty."""
        if self._initialized:
            return

        # Attempt live Firestore connection
        if self.use_live_gcp:
            try:
                from google.cloud import firestore
                project_id = settings.GCP_PROJECT_ID or "archon-ece25"
                creds_json_raw = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON") or settings.GOOGLE_APPLICATION_CREDENTIALS_JSON

                if creds_json_raw:
                    try:
                        from google.oauth2 import service_account
                        sa_info = json.loads(creds_json_raw)
                        credentials = service_account.Credentials.from_service_account_info(sa_info)
                        self._db = firestore.Client(project=project_id, credentials=credentials)
                        logger.info(f"Connected live Firestore client using GOOGLE_APPLICATION_CREDENTIALS_JSON for project: {project_id}")
                        
                        # Write to temp file for any dependent libraries requiring file path
                        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                            tmp_file = Path(tempfile.gettempdir()) / "archon-firebase-creds.json"
                            tmp_file.write_text(creds_json_raw, encoding="utf-8")
                            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(tmp_file)
                    except Exception as json_err:
                        logger.warning(f"Failed parsing GOOGLE_APPLICATION_CREDENTIALS_JSON ({json_err}), trying standard credentials.")
                        self._db = firestore.Client(project=project_id)
                else:
                    self._db = firestore.Client(project=project_id)
                    logger.info(f"Connected live Firestore client to project: {project_id}")
            except Exception as e:
                logger.warning(f"Live Firestore connection failed ({e}), operating in in-memory mode.")
                self._db = None

        # Seed catalog data into cache and Firestore if live
        for b in get_seed_buildings():
            self._buildings[b["building_id"]] = b
            if self._db:
                try:
                    self._db.collection("buildings").document(b["building_id"]).set(b)
                except Exception as ex:
                    logger.debug(f"Firestore building seed sync notice: {ex}")

        for v in get_seed_vendors():
            self._vendors[v["vendor_id"]] = v
            if self._db:
                try:
                    self._db.collection("vendors").document(v["vendor_id"]).set(v)
                except Exception as ex:
                    logger.debug(f"Firestore vendor seed sync notice: {ex}")

        for insp in get_seed_inspections():
            self._inspections[insp["inspection_id"]] = insp
            if self._db:
                try:
                    self._db.collection("inspections").document(insp["inspection_id"]).set(insp)
                except Exception as ex:
                    logger.debug(f"Firestore inspection seed sync notice: {ex}")

        for p in get_seed_playbooks():
            self._playbooks[p["playbook_id"]] = p
            if self._db:
                try:
                    self._db.collection("playbooks").document(p["playbook_id"]).set(p)
                except Exception as ex:
                    logger.debug(f"Firestore playbook seed sync notice: {ex}")

        # Seed Active Demo Incidents
        demo_incidents = [
            {
                "id": "INC-STORM-001",
                "title": "Severe Storm & Substation A Flood Warning",
                "description": "Telemetry alert: Heavy rainfall (42mm/hr) detected. Substation A basement water sensor triggered at 18 inches. Risk of 480V switchgear water ingress and campus cooling loop cross-tie loss.",
                "severity": "P1",
                "status": "investigating",
                "incident_type": "water_main_break",
                "affected_buildings": ["SUBSTATION-A", "BLDG-C", "BLDG-H"],
                "assigned_agents": ["incident_commander", "impact_assessor", "vendor_coordinator", "compliance_inspector", "communications_officer", "remediation_tracker", "memory_curator"],
                "playbook_id": "PB-WATER-001",
                "created_at": "2026-08-31T20:00:00",
                "updated_at": "2026-08-31T20:05:00",
            },
            {
                "id": "INC-XFRM-002",
                "title": "Substation B Main Transformer Thermal Anomaly",
                "description": "Telemetry alert: Step-down transformer T-02 oil temperature reached 94.2C with coolant pump stall. Secondary fan banks required.",
                "severity": "P2",
                "status": "mitigating",
                "incident_type": "electrical_failure",
                "affected_buildings": ["SUBSTATION-B", "BLDG-F"],
                "assigned_agents": ["incident_commander", "vendor_coordinator", "remediation_tracker"],
                "playbook_id": "PB-ELEC-002",
                "created_at": "2026-08-31T19:15:00",
                "updated_at": "2026-08-31T19:30:00",
            },
            {
                "id": "INC-ADV-INJ-003",
                "title": "Adversarial Contractor Quote Quarantine & Rollback",
                "description": "Model Armor threat firewall detected and quarantined prompt injection in external quotation webhook. State snapshot restored in 0.62ms.",
                "severity": "P3",
                "status": "resolved",
                "incident_type": "security_quarantine",
                "affected_buildings": ["BLDG-F"],
                "assigned_agents": ["incident_commander", "vendor_coordinator"],
                "playbook_id": "PB-SEC-001",
                "created_at": "2026-08-31T18:00:00",
                "updated_at": "2026-08-31T18:05:00",
            }
        ]
        for inc in demo_incidents:
            self._incidents[inc["id"]] = inc

        # Seed Pending & Historic Approvals
        demo_approvals = [
            {
                "approval_id": "APP-DIR-001",
                "incident_id": "INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/vendor_coordinator",
                "tool_name": "dispatch_vendor",
                "action_type": "Emergency Industrial Dewatering Dispatch",
                "description": "Authorize $14,500 emergency deployment of Apex Dewatering dual 4-inch submersible pump rig for Substation A basement flood.",
                "estimated_cost": 14500.0,
                "status": "pending",
                "required_role": "facilities_director",
                "created_at": "2026-08-31T20:05:00",
            },
            {
                "approval_id": "APP-DIR-002",
                "incident_id": "INC-XFRM-002",
                "agent_id": "spiffe://archon.internal/agent/vendor_coordinator",
                "tool_name": "dispatch_vendor",
                "action_type": "High Voltage Transformer Repair",
                "description": "Authorize Sparks High Voltage emergency radiator backflush and thermal recovery ($6,200).",
                "estimated_cost": 6200.0,
                "status": "approved",
                "required_role": "facilities_director",
                "decision_by": "Director of Campus Facilities",
                "decision_notes": "Approved under emergency equipment preservation authority.",
                "created_at": "2026-08-31T19:20:00",
                "resolved_at": "2026-08-31T19:22:00",
            }
        ]
        for appr in demo_approvals:
            self._approvals[appr["approval_id"]] = appr

        # Seed Dispatches
        demo_dispatches = [
            {
                "dispatch_id": "DSP-PUMP-001",
                "incident_id": "INC-STORM-001",
                "vendor_id": "VND-HYDRO-01",
                "vendor_name": "Apex Dewatering Solutions",
                "specialty": "commercial_pumping",
                "building_id": "SUBSTATION-A",
                "estimated_cost": 14500.0,
                "status": "pending_approval",
                "estimated_arrival_hours": 1.2,
                "description": "Deploy dual 4-inch high-capacity submersible pumps to Substation A basement sump.",
                "po_number": "PO-PENDING-DIR-AUTH",
                "dispatched_at": "2026-08-31T20:05:00",
            },
            {
                "dispatch_id": "DSP-ELEC-002",
                "incident_id": "INC-XFRM-002",
                "vendor_id": "VND-002",
                "vendor_name": "Sparks High Voltage",
                "specialty": "high_voltage_transformer",
                "building_id": "SUBSTATION-B",
                "estimated_cost": 6200.0,
                "status": "dispatched",
                "estimated_arrival_hours": 0.8,
                "description": "Radiator backflush and secondary cooling circuit inspection.",
                "po_number": "PO-2026-0831-ELEC",
                "dispatched_at": "2026-08-31T19:22:00",
            }
        ]
        for d in demo_dispatches:
            self._dispatches[d["dispatch_id"]] = d

        # Seed Remediation Tasks
        demo_tasks = [
            {
                "task_id": "TSK-SUMP-01",
                "incident_id": "INC-STORM-001",
                "title": "Deploy auxiliary submersible pumps to Substation A sump",
                "description": "Position dual 4-inch pumps and connect discharge hoses to stormwater main.",
                "status": "in_progress",
                "assignee": "Apex Dewatering / Cascade",
                "deadline": "2026-08-31T22:00:00",
            },
            {
                "task_id": "TSK-BERM-02",
                "incident_id": "INC-STORM-001",
                "title": "Inspect and reinforce waterproof perimeter berms",
                "description": "Verify sandbag barriers and seal east wall conduit penetrations.",
                "status": "completed",
                "assignee": "Facilities Engineering",
                "deadline": "2026-08-31T20:30:00",
            },
            {
                "task_id": "TSK-NICU-03",
                "incident_id": "INC-STORM-001",
                "title": "Monitor Hospital NICU Zone 3 chiller cross-tie pressure",
                "description": "Ensure manual bypass valve V-104 is operational and loop temperature stays at 68F.",
                "status": "in_progress",
                "assignee": "Clinical Facilities Lead",
                "deadline": "2026-08-31T21:30:00",
            }
        ]
        for t in demo_tasks:
            self._tasks[t["task_id"]] = t

        # Seed Multi-Agent Reasoning Trace Spans for INC-STORM-001
        demo_spans = [
            {
                "span_id": "SPN-01-CMD",
                "trace_id": "TRC-INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/incident_commander",
                "action": "triage_and_classify",
                "tool_name": "classify_incident",
                "status": "completed",
                "start_time": "2026-08-31T20:00:00.100Z",
                "end_time": "2026-08-31T20:00:00.650Z",
                "decision_rationale": "Classified telemetry spike (42mm/hr rainfall, 18in sump level) as P1 Critical. Activated PB-WATER-001.",
            },
            {
                "span_id": "SPN-02-IMP",
                "trace_id": "TRC-INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/impact_assessor",
                "action": "map_blast_radius",
                "tool_name": "map_dependencies",
                "status": "completed",
                "start_time": "2026-08-31T20:00:00.660Z",
                "end_time": "2026-08-31T20:00:01.200Z",
                "decision_rationale": "Mapped topological dependencies: Substation A feeds Building C hydraulic pump room and Hospital NICU chilled water cross-tie.",
            },
            {
                "span_id": "SPN-03-VND",
                "trace_id": "TRC-INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/vendor_coordinator",
                "action": "rank_and_dispatch_contractor",
                "tool_name": "dispatch_vendor",
                "status": "quarantined_approval",
                "start_time": "2026-08-31T20:00:01.210Z",
                "end_time": "2026-08-31T20:00:01.900Z",
                "decision_rationale": "Selected Apex Dewatering ($14,500, ETA 1.2 hrs). Cost > $10k held by Safety Kernel (INV-01) for Director authorization.",
            },
            {
                "span_id": "SPN-04-CMP",
                "trace_id": "TRC-INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/compliance_inspector",
                "action": "verify_environmental_specs",
                "tool_name": "flag_violations",
                "status": "completed",
                "start_time": "2026-08-31T20:00:01.910Z",
                "end_time": "2026-08-31T20:00:02.400Z",
                "decision_rationale": "Cross-referenced EPA 40 CFR 60 stormwater rules and OSHA 1910.303 electrical wet-location clearances. Zero hazardous violations.",
            },
            {
                "span_id": "SPN-05-COM",
                "trace_id": "TRC-INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/communications_officer",
                "action": "draft_emergency_advisory",
                "tool_name": "route_by_severity",
                "status": "completed",
                "start_time": "2026-08-31T20:00:02.410Z",
                "end_time": "2026-08-31T20:00:02.950Z",
                "decision_rationale": "Dispatched targeted SMS and operational push alert to Facilities Director, Hospital Chief Engineer, and On-Call Electricians.",
            },
            {
                "span_id": "SPN-06-REM",
                "trace_id": "TRC-INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/remediation_tracker",
                "action": "track_work_orders",
                "tool_name": "create_task",
                "status": "completed",
                "start_time": "2026-08-31T20:00:02.960Z",
                "end_time": "2026-08-31T20:00:03.500Z",
                "decision_rationale": "Created 3 corrective tasks: sump pump positioning, berm sandbag inspection, and NICU chiller cross-tie monitoring.",
            },
            {
                "span_id": "SPN-07-MEM",
                "trace_id": "TRC-INC-STORM-001",
                "agent_id": "spiffe://archon.internal/agent/memory_curator",
                "action": "curate_institutional_lesson",
                "tool_name": "store_lesson",
                "status": "completed",
                "start_time": "2026-08-31T20:00:03.510Z",
                "end_time": "2026-08-31T20:00:04.100Z",
                "decision_rationale": "Committed precedent MEM-007 to Vertex AI Memory Bank with verified source incident ID and outcome metrics.",
            }
        ]
        for s in demo_spans:
            self._spans[s["span_id"]] = s

        logger.info("Loaded seed datasets into memory store and live Firestore.")
        self._initialized = True


    # ------------------ Incidents ------------------
    async def create_incident(self, incident: Incident) -> Incident:
        data = incident.model_dump()
        data["created_at"] = incident.created_at.isoformat()
        data["updated_at"] = incident.updated_at.isoformat()
        self._incidents[incident.id] = data
        if self._db:
            try:
                self._db.collection("incidents").document(incident.id).set(data)
            except Exception as e:
                logger.warning(f"Firestore create_incident sync error: {e}")
        return incident

    async def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        return self._incidents.get(incident_id)

    async def list_incidents(self, status: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        res = list(self._incidents.values())
        if status:
            res = [i for i in res if i.get("status") == status]
        if severity:
            res = [i for i in res if i.get("severity") == severity]
        # Sort descending by updated_at or created_at
        res.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return res

    async def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if incident_id in self._incidents:
            updates["updated_at"] = datetime.utcnow().isoformat()
            self._incidents[incident_id].update(updates)
            if self._db:
                try:
                    self._db.collection("incidents").document(incident_id).update(updates)
                except Exception as e:
                    logger.warning(f"Firestore update_incident sync error: {e}")
            return self._incidents[incident_id]
        return None

    # ------------------ Agents / Registry ------------------
    async def register_agent(self, manifest: AgentManifest) -> AgentManifest:
        data = manifest.model_dump()
        data["registered_at"] = manifest.registered_at.isoformat()
        data["last_heartbeat"] = manifest.last_heartbeat.isoformat()
        self._agents[manifest.agent_id] = data
        if self._db:
            try:
                self._db.collection("agents").document(manifest.name).set(data)
            except Exception as e:
                logger.warning(f"Firestore register_agent sync error: {e}")
        return manifest

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._agents.get(agent_id)

    async def list_agents(self) -> List[Dict[str, Any]]:
        return list(self._agents.values())

    async def update_agent_heartbeat(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            now_iso = datetime.utcnow().isoformat()
            self._agents[agent_id]["last_heartbeat"] = now_iso
            self._agents[agent_id]["status"] = "active"
            self._agents[agent_id]["missed_heartbeats"] = 0
            if self._db:
                try:
                    agent_name = self._agents[agent_id].get("name", agent_id)
                    self._db.collection("agents").document(agent_name).update({"last_heartbeat": now_iso, "status": "active"})
                except Exception as e:
                    logger.debug(f"Firestore heartbeat sync notice: {e}")
            return True
        return False

    async def deregister_agent(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    # ------------------ Audit & Observability ------------------
    async def log_audit_entry(self, entry: AuditEntry):
        data = entry.model_dump()
        data["timestamp"] = entry.timestamp.isoformat()
        self._audit_log.append(data)
        if self._db:
            try:
                self._db.collection("audit_log").document(entry.entry_id).set(data)
            except Exception as e:
                logger.warning(f"Firestore log_audit_entry sync error: {e}")

    async def save_span(self, span: Span):
        data = span.model_dump()
        data["start_time"] = span.start_time.isoformat()
        if span.end_time:
            data["end_time"] = span.end_time.isoformat()
        self._spans[span.span_id] = data
        if self._db:
            try:
                self._db.collection("spans").document(span.span_id).set(data)
            except Exception as e:
                logger.warning(f"Firestore save_span sync error: {e}")

    async def get_span(self, span_id: str) -> Optional[Dict[str, Any]]:
        return self._spans.get(span_id)

    async def get_trace_spans(self, trace_id: str) -> List[Dict[str, Any]]:
        spans = [s for s in self._spans.values() if s.get("trace_id") == trace_id]
        spans.sort(key=lambda x: x.get("start_time", ""))
        return spans

    async def list_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        # Group spans by trace_id
        traces_map: Dict[str, Dict[str, Any]] = {}
        for s in self._spans.values():
            t_id = s.get("trace_id")
            if t_id not in traces_map:
                traces_map[t_id] = {
                    "trace_id": t_id,
                    "spans_count": 0,
                    "agents": set(),
                    "start_time": s.get("start_time"),
                    "status": s.get("status"),
                }
            traces_map[t_id]["spans_count"] += 1
            traces_map[t_id]["agents"].add(s.get("agent_id"))
        
        result = []
        for t in traces_map.values():
            t["agents"] = list(t["agents"])
            result.append(t)
        result.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        return result[:limit]

    # ------------------ Approvals ------------------
    async def create_approval_request(self, approval: ApprovalRequest) -> ApprovalRequest:
        data = approval.model_dump()
        data["created_at"] = approval.created_at.isoformat()
        self._approvals[approval.approval_id] = data
        if self._db:
            try:
                self._db.collection("approvals").document(approval.approval_id).set(data)
            except Exception as e:
                logger.warning(f"Firestore create_approval_request sync error: {e}")
        return approval

    async def get_approval_request(self, approval_id: str) -> Optional[Dict[str, Any]]:
        return self._approvals.get(approval_id)

    async def list_pending_approvals(self) -> List[Dict[str, Any]]:
        return [a for a in self._approvals.values() if a.get("status") == "pending"]

    async def list_all_approvals(self) -> List[Dict[str, Any]]:
        res = list(self._approvals.values())
        res.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return res

    async def resolve_approval(self, approval_id: str, status: str, decision_by: str, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if approval_id in self._approvals:
            self._approvals[approval_id]["status"] = status
            self._approvals[approval_id]["decision_by"] = decision_by
            self._approvals[approval_id]["decision_notes"] = notes or ""
            self._approvals[approval_id]["resolved_at"] = datetime.utcnow().isoformat()
            if self._db:
                try:
                    self._db.collection("approvals").document(approval_id).update(self._approvals[approval_id])
                except Exception as e:
                    logger.warning(f"Firestore resolve_approval sync error: {e}")
            return self._approvals[approval_id]
        return None

    # ------------------ Dispatches & Tasks ------------------
    async def save_dispatch(self, dispatch: Dict[str, Any]):
        self._dispatches[dispatch["dispatch_id"]] = dispatch
        if self._db:
            try:
                self._db.collection("dispatches").document(dispatch["dispatch_id"]).set(dispatch)
            except Exception as e:
                logger.warning(f"Firestore save_dispatch sync error: {e}")

    async def list_dispatches(self, incident_id: Optional[str] = None) -> List[Dict[str, Any]]:
        res = list(self._dispatches.values())
        if incident_id:
            res = [d for d in res if d.get("incident_id") == incident_id]
        return res

    async def save_task(self, task: Dict[str, Any]):
        self._tasks[task["task_id"]] = task
        if self._db:
            try:
                self._db.collection("tasks").document(task["task_id"]).set(task)
            except Exception as e:
                logger.warning(f"Firestore save_task sync error: {e}")

    async def list_tasks(self, incident_id: Optional[str] = None) -> List[Dict[str, Any]]:
        res = list(self._tasks.values())
        if incident_id:
            res = [t for t in res if t.get("incident_id") == incident_id]
        return res

    # ------------------ Catalogs ------------------
    async def list_buildings(self) -> List[Dict[str, Any]]:
        return list(self._buildings.values())

    async def get_building(self, building_id: str) -> Optional[Dict[str, Any]]:
        return self._buildings.get(building_id)

    async def list_vendors(self, specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        vendors = list(self._vendors.values())
        if specialty:
            vendors = [v for v in vendors if specialty.lower() in [s.lower() for s in v.get("specialties", [])]]
        return vendors

    async def get_vendor(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        return self._vendors.get(vendor_id)

    async def update_vendor(self, vendor_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if vendor_id in self._vendors:
            self._vendors[vendor_id].update(updates)
            return self._vendors[vendor_id]
        return None

    async def list_inspections(self, building_id: Optional[str] = None) -> List[Dict[str, Any]]:
        inspections = list(self._inspections.values())
        if building_id:
            inspections = [i for i in inspections if i.get("building_id") == building_id]
        return inspections

    async def get_playbook(self, playbook_id_or_type: str) -> Optional[Dict[str, Any]]:
        # Match by ID or incident_type
        if playbook_id_or_type in self._playbooks:
            return self._playbooks[playbook_id_or_type]
        for p in self._playbooks.values():
            if p.get("incident_type") == playbook_id_or_type:
                return p
        return None


firestore_service = FirestoreService()
