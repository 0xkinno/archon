import time
import pytest
from governance.resilience import (
    degrade_on_model_error,
    detect_agent_loop,
    timeout_handler,
    ResilienceManager,
)
from governance.observability import AgentObservability


def test_degrade_on_model_error():
    err = Exception("Gemini API Rate Limit Exceeded: 429 Resource Exhausted")
    degradation = degrade_on_model_error(err)
    assert degradation["status"] == "NO_ACTION_TAKEN"
    assert degradation["degradation_mode"] == "DETERMINISTIC_SAFE_FALLBACK"
    assert "Resource Exhausted" in degradation["error_message"]


def test_detect_agent_loop_terminates_at_3_calls():
    manager = ResilienceManager()
    incident_id = "INC-LOOP-DETECT"
    tool = "dispatch_vendor"
    args = {"vendor_id": "VND-001", "building": "BLDG-C"}

    is_loop, _ = manager.record_tool_call(incident_id, tool, args)
    assert is_loop is False

    is_loop, _ = manager.record_tool_call(incident_id, tool, args)
    assert is_loop is False

    # 3rd identical call triggers loop termination
    is_loop, reason = manager.record_tool_call(incident_id, tool, args)
    assert is_loop is True
    assert "Agent loop detected" in reason


def test_timeout_handler_detection():
    # Past timestamp > 60s
    start = time.time() - 65.0
    is_timeout = timeout_handler(start, limit_seconds=60.0)
    assert is_timeout is True

    # Fresh timestamp < 60s
    fresh = time.time()
    is_timeout = timeout_handler(fresh, limit_seconds=60.0)
    assert is_timeout is False


def test_trace_and_span_hierarchy_recording():
    obs = AgentObservability()
    trace_id = obs.start_trace("INC-OBS-01")
    assert "TRC-" in trace_id

    root_span = obs.start_span(trace_id, "spiffe://archon.campus/agent/incident_commander", "triage")
    child_span = obs.start_span(trace_id, "spiffe://archon.campus/agent/impact_assessor", "map_deps", parent_span_id=root_span)

    obs.end_span(child_span, "Mapped 2 buildings")
    obs.end_span(root_span, "Triage completed")

    chain = obs.get_reasoning_chain(trace_id)
    assert chain["trace_id"] == trace_id
    assert chain["total_spans"] == 2
    assert len(chain["hierarchy"]) == 1
    assert len(chain["hierarchy"][0]["children"]) == 1
