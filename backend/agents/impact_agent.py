import logging
from typing import List, Dict, Any, Optional

from services.gemini_service import build_model
from governance.armor import screen_tool_result
from governance.gateway import enforce_policy
from governance.resilience import degrade_on_model_error
from tools.building_systems import query_building_systems, check_occupancy, map_dependencies
from tools.memory_tools import store_lesson

logger = logging.getLogger("archon.impact_agent")


def save_to_memory(callback_context=None, **kwargs):
    """Universal memory callback for ADK agents."""
    return None


INSTRUCTION = """You are the Impact Assessor for ARCHON, an enterprise operational resilience platform governing a 50-building university and hospital campus.

Your operational domain is Blast Radius Mapping, System Interdependency Tracing, and Occupancy Risk Calculation.

When delegated a task:
1. Identify the source building experiencing the fault or anomaly.
2. Query building systems and live telemetry via query_building_systems to establish active equipment states and critical environmental requirements (such as cleanrooms, vivariums, or server banks).
3. Check current occupancy headcounts and capacity percentages via check_occupancy. Flag any high-density life-safety evacuation risks immediately.
4. Traverse the campus topological graph via map_dependencies to determine all downstream facilities that rely on the compromised building for chilled water, high-voltage electricity, domestic water, or medical air. Pay extraordinary attention to Building H (Hospital NICU and Surgical suites) and Building D (Biohazard containment).
5. Categorize the overall blast radius tier (P1_LIFE_SAFETY, P2_MULTI_BUILDING, or P3_ISOLATED) and summarize secondary exposure risks clearly for the Incident Commander.

You possess domain authority over spatial and mechanical topologies. You never dispatch vendors or issue public alerts directly.
"""

try:
    from google.adk.agents.llm_agent import Agent
    impact_assessor = Agent(
        model=build_model(),
        name="impact_assessor",
        description="Maps affected buildings, occupancy headcounts, utility dependencies, and blast radius.",
        instruction=INSTRUCTION,
        tools=[query_building_systems, check_occupancy, map_dependencies],
        after_agent_callback=save_to_memory,
        on_model_error_callback=degrade_on_model_error,
        after_tool_callback=screen_tool_result,
        before_tool_callback=enforce_policy,
    )
except Exception as e:
    logger.warning(f"ADK Agent fallback initialization for impact_assessor: {e}")
    class MockImpactAgent:
        name = "impact_assessor"
        description = "Maps affected buildings, occupancy headcounts, utility dependencies, and blast radius."
        instruction = INSTRUCTION
        tools = [query_building_systems, check_occupancy, map_dependencies]
    impact_assessor = MockImpactAgent()
