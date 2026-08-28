import logging
from typing import List, Dict, Any, Optional

from services.gemini_service import build_model
from governance.armor import screen_tool_result
from governance.gateway import enforce_policy
from governance.resilience import degrade_on_model_error
from tools.compliance_tools import check_inspection_schedule, generate_compliance_doc, flag_violations

logger = logging.getLogger("archon.compliance_agent")


def save_to_memory(callback_context=None, **kwargs):
    return None


INSTRUCTION = """You are the Compliance Inspector for ARCHON, an enterprise operations intelligence platform.

Your operational domain is Regulatory Verification, Audit Preparation, Environmental Health & Safety (EHS) Standards, and Code Compliance Documentation.

When delegated an operational task:
1. Cross-reference the impacted facility and systems against the regulatory calendar via check_inspection_schedule.
2. Determine if scheduled audits (State Fire Marshal, OSHA, EPA SPCC, Joint Commission Hospital Accreditation, or State Elevator Safety Board) are imminent for the affected facility.
3. Review outstanding prior citations and verify if current physical maintenance work addresses open compliance mandates or risks creating new code infractions.
4. Generate authoritative digital compliance documentation packages via generate_compliance_doc, including flow tests, egress verification logs, and engineering sign-offs.
5. If an unpermitted hazard or regulatory breach is uncovered (such as compromised sprinkler coverage or uncontained hazardous materials), immediately log a violation record via flag_violations with mandatory 24-72 hour remediation windows.

You represent regulatory rigor and legal safety. You do not manage work order dispatches or craft public PR messages.
"""

try:
    from google.adk.agents.llm_agent import Agent
    compliance_inspector = Agent(
        model=build_model(),
        name="compliance_inspector",
        description="Cross-references active repairs against regulatory inspection schedules and generates audit packages.",
        instruction=INSTRUCTION,
        tools=[check_inspection_schedule, generate_compliance_doc, flag_violations],
        after_agent_callback=save_to_memory,
        on_model_error_callback=degrade_on_model_error,
        after_tool_callback=screen_tool_result,
        before_tool_callback=enforce_policy,
    )
except Exception as e:
    logger.warning(f"ADK Agent fallback for compliance_inspector: {e}")
    class MockComplianceAgent:
        name = "compliance_inspector"
        description = "Cross-references active repairs against regulatory inspection schedules and generates audit packages."
        instruction = INSTRUCTION
        tools = [check_inspection_schedule, generate_compliance_doc, flag_violations]
    compliance_inspector = MockComplianceAgent()
