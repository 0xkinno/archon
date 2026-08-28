import pytest
from governance.gateway import AgentGateway
from governance.armor import model_armor


def test_tainted_source_quarantine_block():
    gateway = AgentGateway()
    model_armor._blocked_sources.add("Malicious Inbound Vendor Feed")

    passed, reason = gateway.check_tainted_source("Malicious Inbound Vendor Feed")
    assert passed is False
    assert "quarantined by Model Armor" in reason


def test_financial_threshold_below_limit():
    gateway = AgentGateway()
    passed, reason = gateway.check_financial_threshold(
        estimated_cost=2500.0,
        incident_id="INC-001",
        agent_id="vendor_coordinator",
        action="dispatch_vendor",
        payload={"vendor": "Cascade"}
    )
    assert passed is True
    assert reason is None


def test_financial_threshold_above_limit_triggers_approval():
    gateway = AgentGateway()
    passed, reason = gateway.check_financial_threshold(
        estimated_cost=25000.0,
        incident_id="INC-001",
        agent_id="vendor_coordinator",
        action="dispatch_emergency_turbine",
        payload={"vendor": "Apex", "amount": 25000}
    )
    assert passed is False
    assert "Human Approval Queue" in reason


def test_domain_scoping_authorized_tool():
    gateway = AgentGateway()
    passed, reason = gateway.check_domain_scoping("vendor_management", "dispatch_vendor")
    assert passed is True
    assert reason is None


def test_domain_scoping_unauthorized_tool_blocked():
    gateway = AgentGateway()
    # vendor_coordinator cannot invoke compliance tools
    passed, reason = gateway.check_domain_scoping("vendor_management", "generate_compliance_doc")
    assert passed is False
    assert "Domain scoping violation" in reason


def test_rate_limiting_enforced_at_20_calls():
    gateway = AgentGateway()
    incident_key = "INC-LOOP-TEST"

    # Make 20 allowed calls
    for _ in range(20):
        passed, _ = gateway.check_rate_limiting(incident_key)
        assert passed is True

    # 21st call should trigger rate limit block
    passed, reason = gateway.check_rate_limiting(incident_key)
    assert passed is False
    assert "Rate limit exceeded" in reason


def test_evaluate_request_full_pipeline_pass():
    gateway = AgentGateway()
    verdict = gateway.evaluate_request(
        tool_name="search_vendors",
        args={"specialty": "plumbing", "urgency": "emergency"},
        agent_domain="vendor_management",
        incident_id="INC-OK-TEST"
    )
    assert verdict["allow"] is True
