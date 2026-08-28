import logging
from typing import List, Dict, Any, Optional

from services.gemini_service import build_model
from governance.armor import screen_tool_result
from governance.gateway import enforce_policy
from governance.resilience import degrade_on_model_error
from tools.remediation_tools import create_task, update_task, escalate_overdue, shift_handoff

logger = logging.getLogger("archon.remediation_agent")


def save_to_memory(callback_context=None, **kwargs):
    return None


INSTRUCTION = """You are the Remediation Tracker for ARCHON, an enterprise operations intelligence platform.

Your operational domain is Corrective Action Lifecycle Management, Field Work Order Tracking, Overdue SLA Escalation, and Cross-Shift Operational Handoffs.

When delegated an operational incident:
1. Break down the overarching incident remediation plan into discrete, assignable work orders via create_task (such as moisture dewatering, structural framing inspections, valve replacements, or sensor calibrations).
2. Assign each work order to specific campus trade groups (Plumbing, High-Voltage Electrical, HVAC Mechanical, or Life-Safety) with unambiguous completion deadlines.
3. Monitor active work orders and update status transitions (pending -> in_progress -> completed) via update_task as technicians log progress in the field.
4. Regularly scan for delayed or blocked work orders via escalate_overdue, automatically elevating overdue items to supervisory alerts.
5. Compile comprehensive operational transition summaries via shift_handoff to ensure incoming shift supervisors have complete situational awareness of open hazards, pending tasks, and contractor statuses.

You possess domain authority over task execution and shift continuity. You do not search precedents or author compliance documents.
"""

try:
    from google.adk.agents.llm_agent import Agent
    remediation_tracker = Agent(
        model=build_model(),
        name="remediation_tracker",
        description="Creates, monitors, and escalates corrective work orders and compiles multi-shift handoff briefings.",
        instruction=INSTRUCTION,
        tools=[create_task, update_task, escalate_overdue, shift_handoff],
        after_agent_callback=save_to_memory,
        on_model_error_callback=degrade_on_model_error,
        after_tool_callback=screen_tool_result,
        before_tool_callback=enforce_policy,
    )
except Exception as e:
    logger.warning(f"ADK Agent fallback for remediation_tracker: {e}")
    class MockRemediationAgent:
        name = "remediation_tracker"
        description = "Creates, monitors, and escalates corrective work orders and compiles multi-shift handoff briefings."
        instruction = INSTRUCTION
        tools = [create_task, update_task, escalate_overdue, shift_handoff]
    remediation_tracker = MockRemediationAgent()
