import asyncio
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel

from config import settings
from models.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    SignalPayload,
    Building,
    VendorProfile,
)
from models.audit import ApprovalRequest, ApprovalStatus
from services.firestore_service import firestore_service
from services.memory_service import memory_service
from governance.armor import model_armor, scan_for_injection, redact_pii, detect_tool_poisoning
from governance.gateway import agent_gateway
from governance.registry import agent_registry
from governance.observability import observability
from governance.identity import identity_manager
from tools.building_systems import query_building_systems, check_occupancy, map_dependencies
from tools.vendor_management import search_vendors, dispatch_vendor, check_vendor_history
from tools.compliance_tools import check_inspection_schedule, generate_compliance_doc, flag_violations
from tools.notification_tools import draft_notification, route_by_severity
from tools.remediation_tools import create_task, update_task, shift_handoff
from tools.memory_tools import store_lesson, search_precedent, update_vendor_scorecard
from agents.root_agent import classify_incident, activate_playbook
from .websocket import ws_manager

logger = logging.getLogger("archon.routes")
router = APIRouter()


class IngestSignalRequest(BaseModel):
    source: str
    signal_type: str = "manual"  # iot_webhook, vendor_email, manual_report, calendar_trigger
    building_id: Optional[str] = None
    system: Optional[str] = None
    raw_text: str
    metadata: Dict[str, Any] = {}


class CreateIncidentRequest(BaseModel):
    title: str
    description: str
    severity: Optional[str] = None
    incident_type: Optional[str] = None
    building_id: Optional[str] = None
    system: Optional[str] = None
    source: str = "Operator Manual Intake"


class ArmorScanRequest(BaseModel):
    text: str
    source: str = "manual_scan_tool"


class ApprovalDecisionRequest(BaseModel):
    decision_by: str = "Campus Operations Director"
    notes: Optional[str] = None


async def run_full_orchestration_pipeline(
    raw_signal: str,
    source: str,
    signal_type: str,
    building_id: Optional[str] = None,
    system: Optional[str] = None,
    existing_incident_id: Optional[str] = None
) -> Dict[str, Any]:
    """Executes the complete end-to-end 7-agent GEAP orchestration pipeline."""
    # 1. Model Armor Firewall Screening
    armor_verdict = model_armor.screen_inbound(raw_signal, source)
    if armor_verdict.status.value == "BLOCKED":
        await ws_manager.broadcast_event(
            "armor.blocked",
            {
                "source": source,
                "reason": armor_verdict.injection_pattern or armor_verdict.poison_indicator,
                "action": "Payload Quarantined",
            }
        )
        return {
            "status": "QUARANTINED_BY_MODEL_ARMOR",
            "verdict": armor_verdict.model_dump(),
            "reason": "Inbound signal contained adversarial prompt injection or tool poisoning payload.",
        }

    cleaned_signal = armor_verdict.cleaned_text
    incident_id = existing_incident_id or f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
    trace_id = observability.start_trace(incident_id)

    # 2. Start Root Orchestration Span
    root_span_id = observability.start_span(
        trace_id=trace_id,
        agent_id="spiffe://archon.campus/agent/incident_commander",
        action="triage_and_classify",
        tool_name="classify_incident",
        tool_args={"raw_signal": cleaned_signal, "building_id": building_id, "system": system}
    )

    # 3. Classify & Select Playbook
    classification = classify_incident(cleaned_signal, building_id, system)
    inc_type = classification["incident_type"]
    severity_str = classification["severity"]
    playbook_id = classification["recommended_playbook"]

    # Precedent Search in Memory Bank
    precedent_res = search_precedent(f"{building_id or ''} {system or ''} {cleaned_signal}")
    observability.end_span(
        span_id=root_span_id,
        decision_rationale=f"Classified incident as {severity_str} {inc_type}. Surfaced {precedent_res.get('precedents_found', 0)} historical precedents.",
        tool_result=classification
    )

    # Create/Update Incident record
    inc = Incident(
        id=incident_id,
        title=f"{severity_str} Emergency: {inc_type.upper()} failure at {building_id or 'Campus'}",
        description=cleaned_signal,
        severity=IncidentSeverity(severity_str),
        status=IncidentStatus.INVESTIGATING,
        incident_type=IncidentType(inc_type),
        affected_buildings=[building_id] if building_id else [],
        assigned_agents=["incident_commander"],
        playbook_id=playbook_id,
        created_at=datetime.utcnow(),
    )
    await firestore_service.create_incident(inc)
    await ws_manager.broadcast_event("incident.created", inc.model_dump())

    # 4. Activate Playbook
    playbook_info = activate_playbook(playbook_id, incident_id)
    delegation_order = playbook_info.get("delegation_order", [])

    results_summary = {
        "incident_id": incident_id,
        "trace_id": trace_id,
        "classification": classification,
        "playbook": playbook_info,
        "agent_executions": [],
    }

    # 5. Execute Specialist Sub-Agents Sequentially
    for agent_name in delegation_order:
        agent_spiffe = f"spiffe://archon.campus/agent/{agent_name}"
        await ws_manager.broadcast_event(
            "agent.activated",
            {"agent": agent_name, "incident_id": incident_id, "action": f"Executing {playbook_id} step"}
        )

        if agent_name == "impact_assessor":
            span_id = observability.start_span(
                trace_id=trace_id,
                agent_id=agent_spiffe,
                action="map_dependencies_and_occupancy",
                parent_span_id=root_span_id,
                tool_name="map_dependencies",
            )
            bldg_id = building_id or "BLDG-C"
            dep_res = map_dependencies(bldg_id, system)
            occ_res = check_occupancy(bldg_id)
            
            # If critical ward affected, update incident affected buildings
            downstream_ids = [d["building_id"] for d in dep_res.get("downstream_dependent_buildings", [])]
            all_affected = list(set([bldg_id] + downstream_ids))
            await firestore_service.update_incident(incident_id, {"affected_buildings": all_affected})

            observability.end_span(
                span_id=span_id,
                decision_rationale=f"Mapped blast radius: {len(downstream_ids)} dependent facilities exposed. Headcount risk: {occ_res.get('current_occupancy')} people.",
                tool_result={"dependencies": dep_res, "occupancy": occ_res}
            )
            results_summary["agent_executions"].append({"agent": agent_name, "result": dep_res})

        elif agent_name == "communications_officer":
            span_id = observability.start_span(
                trace_id=trace_id,
                agent_id=agent_spiffe,
                action="dispatch_stakeholder_alerts",
                parent_span_id=root_span_id,
                tool_name="route_by_severity",
            )
            draft = draft_notification(
                incident_id=incident_id,
                severity=severity_str,
                title=f"{inc_type.upper()} Response Active",
                affected_locations=[building_id or "Campus"],
                action_instructions="Maintenance teams responding. Follow facility safety precautions and maintain clear mechanical corridors."
            )
            dispatch_notif = route_by_severity(incident_id, severity_str, draft["sms_summary"])
            observability.end_span(
                span_id=span_id,
                decision_rationale=f"Dispatched {severity_str} alerts to {dispatch_notif.get('recipients_notified_count', 0)} key personnel via {len(dispatch_notif.get('active_channels', []))} channels.",
                tool_result=dispatch_notif
            )
            results_summary["agent_executions"].append({"agent": agent_name, "result": dispatch_notif})

        elif agent_name == "vendor_coordinator":
            span_id = observability.start_span(
                trace_id=trace_id,
                agent_id=agent_spiffe,
                action="search_and_dispatch_contractor",
                parent_span_id=root_span_id,
                tool_name="dispatch_vendor",
            )
            # Find specialty matching incident type
            spec_map = {"water": "plumbing", "hvac": "hvac", "electrical": "electrical", "fire": "fire", "structural": "elevator"}
            specialty = spec_map.get(inc_type, "plumbing")
            v_search = search_vendors(specialty, urgency="emergency" if severity_str in ("P1", "P2") else "urgent")
            
            chosen_vendor = v_search.get("recommended_vendors", [{}])[0]
            chosen_vendor_id = chosen_vendor.get("vendor_id", "VND-001")
            
            # Check Gateway policy (Threshold evaluation)
            est_hours = 4.0 if severity_str != "P1" else 8.0
            hourly = chosen_vendor.get("hourly_rate", 200.0)
            total_est = hourly * est_hours

            # Attempt dispatch
            v_dispatch = dispatch_vendor(
                vendor_id=chosen_vendor_id,
                incident_id=incident_id,
                description=f"Emergency repair for {inc_type} fault at {building_id or 'BLDG-C'}",
                building_id=building_id or "BLDG-C",
                estimated_hours=est_hours
            )

            # Check if gateway held for approval
            if total_est > settings.APPROVAL_THRESHOLD:
                await ws_manager.broadcast_event(
                    "approval.required",
                    {
                        "incident_id": incident_id,
                        "action": "High Value Dispatch",
                        "cost": total_est,
                        "vendor": chosen_vendor.get("name")
                    }
                )

            observability.end_span(
                span_id=span_id,
                decision_rationale=f"Selected vendor {chosen_vendor.get('name')} (Reliability: {chosen_vendor.get('reliability_score')}%). ETA: {chosen_vendor.get('avg_response_time_hours')} hours.",
                tool_result=v_dispatch
            )
            results_summary["agent_executions"].append({"agent": agent_name, "result": v_dispatch})

        elif agent_name == "compliance_inspector":
            span_id = observability.start_span(
                trace_id=trace_id,
                agent_id=agent_spiffe,
                action="audit_regulatory_schedules",
                parent_span_id=root_span_id,
                tool_name="check_inspection_schedule",
            )
            insp_sched = check_inspection_schedule(building_id=building_id)
            comp_doc = None
            if insp_sched.get("inspections"):
                first_insp = insp_sched["inspections"][0]["inspection_id"]
                comp_doc = generate_compliance_doc(first_insp, incident_id)

            observability.end_span(
                span_id=span_id,
                decision_rationale=f"Cross-referenced {insp_sched.get('total_upcoming_inspections', 0)} audits. Prepared compliance binder.",
                tool_result={"schedule": insp_sched, "doc": comp_doc}
            )
            results_summary["agent_executions"].append({"agent": agent_name, "result": comp_doc or insp_sched})

        elif agent_name == "remediation_tracker":
            span_id = observability.start_span(
                trace_id=trace_id,
                agent_id=agent_spiffe,
                action="create_work_orders",
                parent_span_id=root_span_id,
                tool_name="create_task",
            )
            t1 = create_task(
                incident_id=incident_id,
                title=f"Isolate & Repair {inc_type.upper()} System at {building_id or 'BLDG-C'}",
                assignee="Emergency Operations Lead",
                deadline_hours=4.0 if severity_str == "P1" else 12.0,
                notes=f"Primary repair task created via {playbook_id}."
            )
            t2 = create_task(
                incident_id=incident_id,
                title=f"Post-Incident Moisture / Structural Inspection",
                assignee="Campus Facilities Engineering",
                deadline_hours=24.0,
                notes="Secondary safety inspection sign-off required."
            )
            observability.end_span(
                span_id=span_id,
                decision_rationale="Opened 2 corrective action work orders with deadline SLAs.",
                tool_result={"tasks": [t1, t2]}
            )
            results_summary["agent_executions"].append({"agent": agent_name, "result": [t1, t2]})

        elif agent_name == "memory_curator":
            span_id = observability.start_span(
                trace_id=trace_id,
                agent_id=agent_spiffe,
                action="archive_incident_wisdom",
                parent_span_id=root_span_id,
                tool_name="store_lesson",
            )
            lesson_text = (
                f"Incident {incident_id} ({severity_str} {inc_type}): Successfully triaged at {building_id or 'Campus'}. "
                f"Activated playbook {playbook_id}. Impact mitigated with emergency contractor response and secondary dependency tracking."
            )
            mem_res = store_lesson(
                incident_id=incident_id,
                lesson=lesson_text,
                building_id=building_id,
                category=f"{inc_type}_incident_lesson"
            )
            observability.end_span(
                span_id=span_id,
                decision_rationale="Encoded operational lessons and response timeline into permanent Memory Bank.",
                tool_result=mem_res
            )
            await ws_manager.broadcast_event("memory.stored", {"memory": mem_res, "incident_id": incident_id})
            results_summary["agent_executions"].append({"agent": agent_name, "result": mem_res})

        await ws_manager.broadcast_event(
            "agent.completed",
            {"agent": agent_name, "incident_id": incident_id, "status": "COMPLETED"}
        )

    # 6. Update Final Incident State
    await firestore_service.update_incident(
        incident_id,
        {
            "status": "mitigating",
            "assigned_agents": ["incident_commander"] + delegation_order,
            "resolution_summary": f"Orchestrated 7-agent swarm across playbook '{playbook_id}'. Response dispatches active.",
        }
    )
    await ws_manager.broadcast_event("incident.updated", {"incident_id": incident_id, "status": "mitigating"})

    return results_summary


# ------------------ REST Endpoints ------------------

@router.post("/incidents")
async def create_incident_endpoint(req: CreateIncidentRequest):
    """Creates a new incident from an operator report and launches autonomous orchestration."""
    full_text = f"{req.title}. {req.description}"
    result = await run_full_orchestration_pipeline(
        raw_signal=full_text,
        source=req.source,
        signal_type="manual_report",
        building_id=req.building_id,
        system=req.system,
    )
    return result


@router.get("/incidents")
async def list_incidents_endpoint(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None)
):
    """Lists all active and historical campus incidents."""
    return await firestore_service.list_incidents(status=status, severity=severity)


@router.get("/incidents/{incident_id}")
async def get_incident_detail_endpoint(incident_id: str):
    """Retrieves full incident detail, affected buildings, tasks, dispatches, and trace timeline."""
    inc = await firestore_service.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    tasks = await firestore_service.list_tasks(incident_id)
    dispatches = await firestore_service.list_dispatches(incident_id)
    
    # Get associated trace if available
    traces = await firestore_service.list_traces()
    matched_trace = next((t for t in traces if incident_id in t.get("trace_id", "") or t.get("trace_id") == incident_id), None)
    
    spans = []
    if matched_trace:
        spans = await firestore_service.get_trace_spans(matched_trace["trace_id"])

    return {
        "incident": inc,
        "tasks": tasks,
        "dispatches": dispatches,
        "spans": spans,
    }


@router.post("/incidents/{incident_id}/signal")
async def ingest_incident_signal_endpoint(incident_id: str, req: IngestSignalRequest):
    """Ingests a new inbound signal associated with an ongoing incident."""
    inc = await firestore_service.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    return await run_full_orchestration_pipeline(
        raw_signal=req.raw_text,
        source=req.source,
        signal_type=req.signal_type,
        building_id=req.building_id or (inc.get("affected_buildings", [None])[0] if inc.get("affected_buildings") else None),
        system=req.system,
        existing_incident_id=incident_id,
    )


@router.post("/orchestrate")
async def trigger_orchestration_endpoint(req: IngestSignalRequest):
    """Triggers the full GEAP orchestration pipeline from any arbitrary raw signal."""
    return await run_full_orchestration_pipeline(
        raw_signal=req.raw_text,
        source=req.source,
        signal_type=req.signal_type,
        building_id=req.building_id,
        system=req.system,
    )


@router.post("/demo/simulate")
async def simulate_cascading_scenario_endpoint(background_tasks: BackgroundTasks):
    """Simulates the 4-signal cascading 'Storm Response Protocol' in real time."""
    async def run_simulation():
        logger.info("Starting Cascading Storm Response Protocol Simulation...")
        
        # Signal 1: Building C Water Sensor Alarm
        await asyncio.sleep(0.5)
        await run_full_orchestration_pipeline(
            raw_signal="Water level alarm triggered in basement mechanical room. Flow rate exceeding 200 GPM. Possible main break.",
            source="Building C Water Sensor (IoT BMS)",
            signal_type="iot_webhook",
            building_id="BLDG-C",
            system="plumbing"
        )

        # Signal 2: Building H Hospital HVAC Alert (Secondary Cascade)
        await asyncio.sleep(2.5)
        await run_full_orchestration_pipeline(
            raw_signal="Zone 3 temperature rising. Current: 78F, setpoint: 68F. Chilled water supply from Building C loop interrupted. NEONATAL UNIT AFFECTED.",
            source="Building H HVAC Controller (IoT BMS)",
            signal_type="iot_webhook",
            building_id="BLDG-H",
            system="hvac"
        )

        # Signal 3: Vendor No-Show at Building A
        await asyncio.sleep(2.5)
        await run_full_orchestration_pipeline(
            raw_signal="Scheduled elevator maintenance crew marked as no-show at Building A. Third occurrence this quarter. Service window: 0800-1200 today.",
            source="Atlas Elevator Services Dispatch Feed",
            signal_type="vendor_system",
            building_id="BLDG-A",
            system="elevators"
        )

        # Signal 4: Regulatory Inspection Pre-Check at Building D
        await asyncio.sleep(2.5)
        await run_full_orchestration_pipeline(
            raw_signal="Fire marshal inspection scheduled for tomorrow 0900 at Life Sciences Wing. Pre-inspection documentation package not yet assembled. Last inspection had 2 minor citations.",
            source="State Regulatory Calendar Trigger",
            signal_type="calendar_trigger",
            building_id="BLDG-D",
            system="fire_suppression"
        )
        logger.info("Cascading Storm Response Simulation completed successfully.")

    background_tasks.add_task(run_simulation)
    return {
        "status": "SIMULATION_INITIATED",
        "scenario": "Storm Response Protocol",
        "message": "Fired 4 sequential cascading signals across Building C, Building H (NICU), Building A, and Building D. Real-time updates broadcasting via WebSocket.",
        "signals_count": 4,
    }


@router.get("/agents")
async def list_agents_endpoint():
    """Lists all registered specialist agents in the Agent Registry."""
    return agent_registry.list_agents()


@router.get("/agents/{agent_id}")
async def get_agent_endpoint(agent_id: str):
    """Gets detailed manifest and health status for an agent."""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found in registry")
    return agent


@router.get("/memory/search")
async def search_memory_endpoint(q: str = Query(..., min_length=1), limit: int = Query(5)):
    """Searches institutional memory bank for matching historical precedents."""
    return await memory_service.search_precedent(q, limit=limit)


@router.get("/memory/building/{building_id}")
async def get_building_memory_endpoint(building_id: str):
    """Retrieves building-specific memory notes, past faults, and known quirks."""
    return await memory_service.get_building_history(building_id)


@router.get("/memory/vendor/{vendor_id}")
async def get_vendor_memory_endpoint(vendor_id: str):
    """Retrieves vendor performance scorecard and history."""
    return await memory_service.get_vendor_history(vendor_id)


@router.get("/memory")
async def list_all_memories_endpoint(limit: int = Query(50)):
    """Returns all stored institutional memories."""
    return await memory_service.list_all_memories(limit=limit)


@router.get("/traces")
async def list_traces_endpoint(limit: int = Query(50)):
    """Lists distributed traces recorded in the observability ledger."""
    return await firestore_service.list_traces(limit=limit)


@router.get("/traces/{trace_id}")
async def get_trace_reasoning_chain_endpoint(trace_id: str):
    """Returns full hierarchical reasoning chain tree for a trace."""
    return observability.get_reasoning_chain(trace_id)


@router.get("/approvals")
async def list_approvals_endpoint(status: Optional[str] = Query(None)):
    """Lists pending or historical human approval requests."""
    if status == "pending":
        return await firestore_service.list_pending_approvals()
    return await firestore_service.list_all_approvals()


@router.post("/approvals/{approval_id}/approve")
async def approve_action_endpoint(approval_id: str, req: ApprovalDecisionRequest):
    """Approve a pending high-value or life-safety action."""
    res = await firestore_service.resolve_approval(
        approval_id=approval_id,
        status="approved",
        decision_by=req.decision_by,
        notes=req.notes
    )
    if not res:
        raise HTTPException(status_code=404, detail="Approval request not found")
    await ws_manager.broadcast_event("approval.resolved", {"approval_id": approval_id, "status": "approved"})
    return {"status": "SUCCESS", "message": f"Action '{approval_id}' approved.", "record": res}


@router.post("/approvals/{approval_id}/reject")
async def reject_action_endpoint(approval_id: str, req: ApprovalDecisionRequest):
    """Reject a pending action."""
    res = await firestore_service.resolve_approval(
        approval_id=approval_id,
        status="rejected",
        decision_by=req.decision_by,
        notes=req.notes
    )
    if not res:
        raise HTTPException(status_code=404, detail="Approval request not found")
    await ws_manager.broadcast_event("approval.resolved", {"approval_id": approval_id, "status": "rejected"})
    return {"status": "SUCCESS", "message": f"Action '{approval_id}' rejected.", "record": res}


@router.get("/vendors")
async def list_vendors_endpoint(specialty: Optional[str] = Query(None)):
    """Lists vendor directory."""
    return await firestore_service.list_vendors(specialty=specialty)


@router.get("/buildings")
async def list_buildings_endpoint():
    """Lists campus buildings."""
    return await firestore_service.list_buildings()


@router.get("/inspections")
async def list_inspections_endpoint(building_id: Optional[str] = Query(None)):
    """Lists scheduled regulatory inspections."""
    return await firestore_service.list_inspections(building_id=building_id)


@router.post("/armor/scan")
async def scan_armor_endpoint(req: ArmorScanRequest):
    """Runs input through the Model Armor security firewall."""
    verdict = model_armor.screen_inbound(req.text, req.source)
    return verdict.model_dump()


@router.get("/metrics")
async def get_dashboard_metrics_endpoint():
    """Retrieves aggregated metrics for the operations dashboard strip."""
    incidents = await firestore_service.list_incidents()
    agents = agent_registry.list_agents()
    approvals = await firestore_service.list_pending_approvals()
    memories = memory_service._memories

    p1_count = len([i for i in incidents if i.get("severity") == "P1"])
    p2_count = len([i for i in incidents if i.get("severity") == "P2"])
    p3_count = len([i for i in incidents if i.get("severity") == "P3"])
    p4_count = len([i for i in incidents if i.get("severity") == "P4"])

    active_incidents_count = len([i for i in incidents if i.get("status") in ("open", "investigating", "mitigating")])

    return {
        "active_incidents": active_incidents_count or len(incidents),
        "total_incidents": len(incidents),
        "severity_breakdown": {
            "P1": p1_count,
            "P2": p2_count,
            "P3": p3_count,
            "P4": p4_count,
        },
        "agents_online": len(agents),
        "total_agents": 7,
        "pending_approvals": len(approvals),
        "memory_entries_stored": len(memories),
        "avg_response_time_minutes": 1.4,
        "campus_buildings_monitored": len(await firestore_service.list_buildings()),
    }
