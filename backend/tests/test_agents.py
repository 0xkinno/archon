import pytest
from governance.identity import AgentIdentityManager
from tools.building_systems import query_building_systems, map_dependencies, check_occupancy
from tools.vendor_management import search_vendors, dispatch_vendor, check_vendor_history
from tools.compliance_tools import check_inspection_schedule, generate_compliance_doc, flag_violations
from tools.notification_tools import draft_notification, route_by_severity
from tools.remediation_tools import create_task, update_task, escalate_overdue, shift_handoff
from tools.memory_tools import store_lesson, search_precedent, update_vendor_scorecard
from agents.root_agent import classify_incident, activate_playbook


def test_identity_token_issue_and_validation():
    mgr = AgentIdentityManager()
    identity = mgr.create_agent_identity(
        agent_name="vendor_coordinator",
        domain="vendor_management",
        allowed_tools=["search_vendors", "dispatch_vendor"]
    )
    token = mgr.issue_token(identity)
    assert isinstance(token, str)

    validated = mgr.validate_token(token)
    assert validated is not None
    assert validated.agent_name == "vendor_coordinator"
    assert validated.domain == "vendor_management"


def test_identity_tool_authorization_check():
    mgr = AgentIdentityManager()
    identity = mgr.create_agent_identity(
        agent_name="vendor_coordinator",
        domain="vendor_management",
        allowed_tools=["search_vendors", "dispatch_vendor"]
    )
    token = mgr.issue_token(identity)
    assert mgr.check_tool_authorization(token, "search_vendors") is True
    assert mgr.check_tool_authorization(token, "generate_compliance_doc") is False


def test_building_systems_query_and_dependency_traversal():
    bldg_c = query_building_systems("BLDG-C", "plumbing")
    assert bldg_c["status"] == "SUCCESS"
    assert "Science" in bldg_c["name"]

    deps = map_dependencies("BLDG-C", "plumbing")
    assert deps["status"] == "SUCCESS"
    # Building H and D depend on C
    downstream_ids = [b["building_id"] for b in deps["downstream_dependent_buildings"]]
    assert "BLDG-H" in downstream_ids
    assert deps["critical_ward_exposed"] is True
    assert deps["blast_radius_classification"] == "P1_LIFE_SAFETY"


def test_vendor_search_and_dispatch_logic():
    search_res = search_vendors("plumbing", urgency="emergency")
    assert search_res["status"] == "SUCCESS"
    assert len(search_res["recommended_vendors"]) > 0
    top_vendor = search_res["recommended_vendors"][0]
    assert "Cascade" in top_vendor["name"]

    dispatch_res = dispatch_vendor(
        vendor_id=top_vendor["vendor_id"],
        incident_id="INC-UNIT-01",
        description="Fix main line rupture",
        building_id="BLDG-C"
    )
    assert dispatch_res["status"] == "SUCCESS"
    assert "DSP-" in dispatch_res["dispatch_id"]


def test_compliance_schedule_and_doc_generation():
    sched = check_inspection_schedule(building_id="BLDG-D")
    assert sched["status"] == "SUCCESS"
    assert len(sched["inspections"]) > 0
    assert "Fire Marshal" in sched["inspections"][0]["agency"]

    doc = generate_compliance_doc(sched["inspections"][0]["inspection_id"])
    assert doc["status"] == "SUCCESS"
    assert "DOC-COMP-" in doc["document_id"]


def test_notification_drafting_and_routing():
    draft = draft_notification(
        incident_id="INC-99",
        severity="P1",
        title="Water Ingress in Mechanical Room",
        affected_locations=["Building C", "Building H"],
        action_instructions="Evacuate sub-basement corridors."
    )
    assert draft["status"] == "SUCCESS"
    assert "URGENT CAMPUS ALERT" in draft["email_subject"]

    route_res = route_by_severity("INC-99", "P1", draft["full_body"])
    assert route_res["status"] == "DISPATCHED"
    assert len(route_res["active_channels"]) >= 4


def test_remediation_task_creation_and_escalation():
    task = create_task(
        incident_id="INC-TEST",
        title="Isolate water pump line 4",
        assignee="Lead Plumber",
        deadline_hours=1.0
    )
    assert task["status"] == "SUCCESS"
    assert "TSK-" in task["task_id"]

    updated = update_task(task["task_id"], "in_progress", "Technician on scene")
    assert updated["status"] == "SUCCESS"
    assert updated["new_status"] == "in_progress"


def test_memory_lesson_store_and_precedent_recall():
    lesson = store_lesson(
        incident_id="INC-TEST-02",
        lesson="Building F breaker B3 required moisture barrier mastic sealing.",
        building_id="BLDG-F"
    )
    assert lesson["status"] == "SUCCESS"

    precedent = search_precedent("Building F panel B3 humidity")
    assert precedent["status"] == "SUCCESS"
    assert len(precedent["precedents"]) > 0
    assert any("Panel B3" in p["content"] or "panel B3" in p["content"] for p in precedent["precedents"])
