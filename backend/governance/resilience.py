import logging
import time
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("archon.resilience")


class ResilienceManager:
    """Manages system resilience, agent loop detection, timeouts, and degradation callbacks."""

    def __init__(self):
        self._tool_history: Dict[str, List[Tuple[str, str, float]]] = {}  # incident_id -> [(tool_name, args_hash, timestamp)]

    def record_tool_call(self, incident_id: str, tool_name: str, args: Any) -> Tuple[bool, Optional[str]]:
        """Tracks tool calls and identifies repetitive execution loops (3+ identical calls)."""
        inc_key = incident_id or "default_incident"
        args_str = str(args)
        now = time.time()

        if inc_key not in self._tool_history:
            self._tool_history[inc_key] = []

        history = self._tool_history[inc_key]
        history.append((tool_name, args_str, now))

        # Check for 3 consecutive or recent identical tool invocations
        matching_recent = [
            item for item in history[-6:]
            if item[0] == tool_name and item[1] == args_str
        ]

        if len(matching_recent) >= 3:
            logger.error(f"Resilience loop detected in incident '{inc_key}': Tool '{tool_name}' invoked 3+ times identically.")
            return True, f"Agent loop detected: Tool '{tool_name}' invoked 3 times with identical parameters. Execution terminated by Resilience Manager."

        return False, None

    def check_timeout(self, start_time: float, max_seconds: float = 60.0) -> bool:
        """Returns True if an agent or tool has exceeded the allowable execution window."""
        return (time.time() - start_time) > max_seconds


resilience_manager = ResilienceManager()


def degrade_on_model_error(error: Exception, callback_context=None) -> Dict[str, Any]:
    """ADK on_model_error_callback. Degrades gracefully without fabricating false data."""
    logger.error(f"Model error captured: {error}")
    return {
        "status": "NO_ACTION_TAKEN",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "degradation_mode": "DETERMINISTIC_SAFE_FALLBACK",
        "advice": "System degraded to manual review mode. Incident dispatch queued."
    }


def detect_agent_loop(incident_id: str, tool_name: str, args: Any) -> Tuple[bool, Optional[str]]:
    return resilience_manager.record_tool_call(incident_id, tool_name, args)


def timeout_handler(start_time: float, limit_seconds: float = 60.0) -> bool:
    return resilience_manager.check_timeout(start_time, limit_seconds)
