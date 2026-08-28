import logging
from typing import List, Dict, Any, Optional

from services.gemini_service import build_model
from governance.armor import screen_tool_result
from governance.gateway import enforce_policy
from governance.resilience import degrade_on_model_error
from tools.vendor_management import search_vendors, dispatch_vendor, check_vendor_history
from tools.memory_tools import update_vendor_scorecard

logger = logging.getLogger("archon.vendor_agent")


def save_to_memory(callback_context=None, **kwargs):
    return None


INSTRUCTION = """You are the Vendor Coordinator for ARCHON, an enterprise operations intelligence platform.

Your operational domain is Contractor Logistics, Emergency Trade Dispatch, SLA Verification, and Vendor Performance Accountability.

When delegated an incident response action:
1. Determine the required mechanical specialty (plumbing, electrical, hvac, elevator, fire_suppression, hazmat, or security).
2. Query vendor performance history via check_vendor_history to review historical reliability ratings, probationary status, and past institutional memory warnings (such as recurring contractor no-shows).
3. Search active campus master service agreements via search_vendors to identify the top-ranked available contractors sorted by emergency response time and contract status.
4. Issue an official contractor dispatch order via dispatch_vendor specifying the exact building, mechanical room, scope of emergency work, and estimated arrival SLA.
5. Be conscious that estimated expenditures exceeding $10,000 will be held in the Human Approval Queue by the Agent Gateway. If an emergency dispatch requires a high financial commitment, clearly state the cost basis so operators can sign off instantly.
6. If a contractor defaults or no-shows, update their reliability scorecard via update_vendor_scorecard and immediately dispatch a qualified secondary replacement.

You possess domain authority over logistics and procurement. You do not assess regulatory compliance or send stakeholder mass alerts.
"""

try:
    from google.adk.agents.llm_agent import Agent
    vendor_coordinator = Agent(
        model=build_model(),
        name="vendor_coordinator",
        description="Searches vetted contractors, checks historical reliability scores, and executes emergency dispatches.",
        instruction=INSTRUCTION,
        tools=[search_vendors, dispatch_vendor, check_vendor_history, update_vendor_scorecard],
        after_agent_callback=save_to_memory,
        on_model_error_callback=degrade_on_model_error,
        after_tool_callback=screen_tool_result,
        before_tool_callback=enforce_policy,
    )
except Exception as e:
    logger.warning(f"ADK Agent fallback for vendor_coordinator: {e}")
    class MockVendorAgent:
        name = "vendor_coordinator"
        description = "Searches vetted contractors, checks historical reliability scores, and executes emergency dispatches."
        instruction = INSTRUCTION
        tools = [search_vendors, dispatch_vendor, check_vendor_history, update_vendor_scorecard]
    vendor_coordinator = MockVendorAgent()
