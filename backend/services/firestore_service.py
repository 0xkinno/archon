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
