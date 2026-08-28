import logging
from typing import List, Dict, Any, Optional

from services.gemini_service import build_model
from governance.armor import screen_tool_result
from governance.gateway import enforce_policy
from governance.resilience import degrade_on_model_error
from tools.notification_tools import draft_notification, route_by_severity, check_contact_directory

logger = logging.getLogger("archon.comms_agent")


def save_to_memory(callback_context=None, **kwargs):
    return None


INSTRUCTION = """You are the Communications Officer for ARCHON, an enterprise operations intelligence platform.

Your operational domain is Stakeholder Notifications, Life-Safety Emergency Alert Broadcasts, Executive Operational Summaries, and Multi-Channel Alert Routing.

When delegated an operational situation:
1. Review the incident severity level (P1 Critical, P2 High, P3 Medium, P4 Low) and identify all impacted campus groups.
2. Query the authorized campus contact directory via check_contact_directory to verify designated department contacts, clinical charge desks, and emergency responders.
3. Draft clear, structured, and empathetic operational notices via draft_notification that inform occupants of active hazards, utility outages, evacuation instructions, and expected restoration timelines without inciting panic.
4. Route alerts via route_by_severity across the appropriate multi-tier channels (SMS emergency broadcast, security pager override, email, digital signage, and operations dashboard).
5. For all P1 life-safety critical incidents, dispatch emergency alerts immediately without waiting for mechanical diagnosis to finish.

You possess domain authority over institutional communication. You do not perform physical repairs or edit vendor scorecards.
"""

try:
    from google.adk.agents.llm_agent import Agent
    communications_officer = Agent(
        model=build_model(),
        name="communications_officer",
        description="Drafts and dispatches multi-tiered stakeholder notifications and emergency alerts.",
        instruction=INSTRUCTION,
        tools=[draft_notification, route_by_severity, check_contact_directory],
        after_agent_callback=save_to_memory,
        on_model_error_callback=degrade_on_model_error,
        after_tool_callback=screen_tool_result,
        before_tool_callback=enforce_policy,
    )
except Exception as e:
    logger.warning(f"ADK Agent fallback for communications_officer: {e}")
    class MockCommsAgent:
        name = "communications_officer"
        description = "Drafts and dispatches multi-tiered stakeholder notifications and emergency alerts."
        instruction = INSTRUCTION
        tools = [draft_notification, route_by_severity, check_contact_directory]
    communications_officer = MockCommsAgent()
