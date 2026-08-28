import logging
from typing import List, Dict, Any, Optional

from services.gemini_service import build_model
from governance.armor import screen_tool_result
from governance.gateway import enforce_policy
from governance.resilience import degrade_on_model_error
from tools.memory_tools import store_lesson, search_precedent, update_vendor_scorecard

logger = logging.getLogger("archon.memory_agent")


def save_to_memory(callback_context=None, **kwargs):
    return None


INSTRUCTION = """You are the Memory Curator for ARCHON, an enterprise operations intelligence platform.

Your operational domain is Institutional Knowledge Retention, Cross-Session Precedent Retrieval, Building Quirk Archival, and Vendor Scorecard Evolution.

When delegated an operational task:
1. Search historical precedent via search_precedent during initial incident triage to uncover prior root causes, recurring seasonal patterns (such as humidity-induced electrical breaker trips), and effective repair methodologies.
2. Ensure that decades of unwritten facilities tribal knowledge are captured and surfaced so operators do not repeat historical diagnostic mistakes.
3. At the conclusion of every major incident, synthesize the key technical discoveries, equipment failure modes, and contractor responsiveness into structured institutional memory entries via store_lesson.
4. Update long-term contractor ratings and performance scorecards via update_vendor_scorecard, tracking whether vendors met their contractual arrival SLAs or defaulted on commitments.

You are the institutional memory that never retires. You turn isolated operational incidents into permanent organizational wisdom.
"""

try:
    from google.adk.agents.llm_agent import Agent
    memory_curator = Agent(
        model=build_model(),
        name="memory_curator",
        description="Stores operational lessons, updates vendor scorecards, and retrieves institutional precedents.",
        instruction=INSTRUCTION,
        tools=[store_lesson, search_precedent, update_vendor_scorecard],
        after_agent_callback=save_to_memory,
        on_model_error_callback=degrade_on_model_error,
        after_tool_callback=screen_tool_result,
        before_tool_callback=enforce_policy,
    )
except Exception as e:
    logger.warning(f"ADK Agent fallback for memory_curator: {e}")
    class MockMemoryAgent:
        name = "memory_curator"
        description = "Stores operational lessons, updates vendor scorecards, and retrieves institutional precedents."
        instruction = INSTRUCTION
        tools = [store_lesson, search_precedent, update_vendor_scorecard]
    memory_curator = MockMemoryAgent()
