import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

from config import settings
from models.audit import ApprovalRequest, ApprovalStatus
from services.firestore_service import firestore_service
from .armor import model_armor

logger = logging.getLogger("archon.gateway")

TupleBoolReason = Tuple[bool, Optional[str]]

# Domain -> Allowed Tools Mapping
DOMAIN_TOOL_REGISTRY = {
    "orchestration": ["classify_incident", "activate_playbook", "search_precedent", "transfer_to_agent"],
    "blast_radius": ["query_building_systems", "check_occupancy", "map_dependencies"],
    "vendor_management": ["search_vendors", "dispatch_vendor", "check_vendor_history"],
    "regulatory": ["check_inspection_schedule", "generate_compliance_doc", "flag_violations"],
    "stakeholder_comms": ["draft_notification", "route_by_severity", "check_contact_directory"],
    "corrective_actions": ["create_task", "update_task", "escalate_overdue", "shift_handoff"],
    "institutional_memory": ["store_lesson", "search_precedent", "update_vendor_scorecard"],
}


class AgentGateway:
    """Central policy enforcement engine governing all inter-agent and tool invocations."""

    def __init__(self):
        self._incident_call_counts: Dict[str, int] = {}

    def check_tainted_source(self, source: Optional[str]) -> TupleBoolReason:
        """Policy 1: Rejects execution if source is quarantined by Model Armor."""
        if source and model_armor.is_source_blocked(source):
            return False, f"Source '{source}' is quarantined by Model Armor for safety violations."
        return True, None

    def check_financial_threshold(self, estimated_cost: Optional[float], incident_id: str, agent_id: str, action: str, payload: Dict[str, Any]) -> TupleBoolReason:
        """Policy 2: Flags any action > $10,000 for mandatory human approval."""
        if estimated_cost and estimated_cost > settings.APPROVAL_THRESHOLD:
            approval_id = f"APPR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{abs(hash(action)) % 1000:03d}"
            req = ApprovalRequest(
                approval_id=approval_id,
                incident_id=incident_id or "INC-GENERAL",
                agent_id=agent_id or "unknown_agent",
                action_type=action,
                description=f"Automated action '{action}' requires approval (Estimated cost: ${estimated_cost:,.2f})",
                reason=f"Financial threshold exceeded (${estimated_cost:,.2f} > ${settings.APPROVAL_THRESHOLD:,.2f})",
                estimated_cost=estimated_cost,
                status=ApprovalStatus.PENDING,
                requested_payload=payload,
                created_at=datetime.utcnow()
            )
            # Store in firestore service synchronously in-memory
            firestore_service._approvals[approval_id] = req.model_dump()
            return False, f"Action held in Human Approval Queue (ID: {approval_id}). Estimated cost ${estimated_cost:,.2f} exceeds threshold ${settings.APPROVAL_THRESHOLD:,.2f}."
        return True, None

    def check_domain_scoping(self, agent_domain: Optional[str], tool_name: str) -> TupleBoolReason:
        """Policy 3: Enforces least-privilege tool execution per domain."""
        if not agent_domain:
            return True, None  # Orchestrator or system default
        
        allowed_tools = DOMAIN_TOOL_REGISTRY.get(agent_domain, [])
        if allowed_tools and tool_name not in allowed_tools:
            return False, f"Domain scoping violation: Agent domain '{agent_domain}' is not authorized to invoke tool '{tool_name}'."
        return True, None

    def check_rate_limiting(self, incident_id: Optional[str]) -> TupleBoolReason:
        """Policy 4: Prevents infinite reasoning loops by capping tool calls per incident."""
        inc_key = incident_id or "default_incident"
        current_count = self._incident_call_counts.get(inc_key, 0) + 1
        self._incident_call_counts[inc_key] = current_count

        if current_count > settings.RATE_LIMIT_TOOL_CALLS:
            return False, f"Rate limit exceeded: Incident '{inc_key}' reached maximum of {settings.RATE_LIMIT_TOOL_CALLS} tool calls. Terminating loop."
        return True, None

    def evaluate_request(
        self,
        tool_name: str,
        args: Dict[str, Any],
        agent_id: Optional[str] = None,
        agent_domain: Optional[str] = None,
        incident_id: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Runs all 5 policy checks in deterministic order."""
        # 1. Tainted Source Check
        passed, reason = self.check_tainted_source(source or args.get("source"))
        if not passed:
            return {"allow": False, "policy": "TAINTED_SOURCE", "reason": reason}

        # 2. Rate Limiting Check
        passed, reason = self.check_rate_limiting(incident_id or args.get("incident_id"))
        if not passed:
            return {"allow": False, "policy": "RATE_LIMIT", "reason": reason}

        # 3. Domain Scoping Check
        passed, reason = self.check_domain_scoping(agent_domain, tool_name)
        if not passed:
            return {"allow": False, "policy": "DOMAIN_SCOPING", "reason": reason}

        # 4. Financial Threshold Check
        cost = args.get("estimated_cost") or args.get("cost")
        if cost is None and "hourly_rate" in args and "hours" in args:
            cost = float(args["hourly_rate"]) * float(args["hours"])
        if cost:
            passed, reason = self.check_financial_threshold(
                float(cost),
                incident_id=incident_id or args.get("incident_id", ""),
                agent_id=agent_id or "agent_gateway",
                action=tool_name,
                payload=args
            )
            if not passed:
                return {"allow": False, "policy": "FINANCIAL_THRESHOLD", "reason": reason}

        return {"allow": True, "reason": "All policies passed"}


TupleBoolReason = tuple[bool, Optional[str]]
agent_gateway = AgentGateway()


def enforce_policy(*, tool, args, tool_context=None, callback_context=None) -> Optional[Dict[str, Any]]:
    """ADK before_tool_callback hook. Returns None if allowed, or dictionary if blocked."""
    tool_name = getattr(tool, "__name__", str(tool))
    args_dict = args if isinstance(args, dict) else {}
    
    agent_id = None
    agent_domain = None
    if callback_context and hasattr(callback_context, "agent_name"):
        agent_id = callback_context.agent_name

    verdict = agent_gateway.evaluate_request(
        tool_name=tool_name,
        args=args_dict,
        agent_id=agent_id,
        agent_domain=agent_domain,
        incident_id=args_dict.get("incident_id"),
        source=args_dict.get("source"),
    )

    if not verdict["allow"]:
        logger.warning(f"Agent Gateway DENIED tool '{tool_name}': {verdict['reason']}")
        return {
            "status": "BLOCKED_BY_AGENT_GATEWAY",
            "policy": verdict["policy"],
            "reason": verdict["reason"],
            "instruction": "Do not repeat this blocked tool invocation. Proceed to next available operational step."
        }

    return None
