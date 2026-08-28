import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.audit import Span, AuditEntry, TraceHierarchy
from services.firestore_service import firestore_service

logger = logging.getLogger("archon.observability")


class AgentObservability:
    """Distributed tracing and reasoning chain reconstruction system."""

    def __init__(self):
        self._active_traces: Dict[str, Dict[str, Any]] = {}
        self._spans: Dict[str, Span] = {}

    def start_trace(self, incident_id: str) -> str:
        """Initializes a new distributed trace for an incident."""
        trace_id = f"TRC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        self._active_traces[trace_id] = {
            "trace_id": trace_id,
            "incident_id": incident_id,
            "start_time": datetime.utcnow(),
            "spans": [],
        }
        logger.info(f"Started trace {trace_id} for incident {incident_id}")
        return trace_id

    def start_span(
        self,
        trace_id: str,
        agent_id: str,
        action: str,
        parent_span_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Starts a child span within an incident trace."""
        span_id = f"SPN-{uuid.uuid4().hex[:8]}"
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            agent_id=agent_id,
            action=action,
            status="running",
            tool_name=tool_name,
            tool_args=tool_args,
            start_time=datetime.utcnow(),
        )
        self._spans[span_id] = span
        firestore_service._spans[span_id] = span.model_dump()
        return span_id

    def end_span(
        self,
        span_id: str,
        decision_rationale: str,
        tool_result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Span]:
        """Finalizes a span and calculates execution duration."""
        span = self._spans.get(span_id)
        if not span:
            return None

        now = datetime.utcnow()
        span.end_time = now
        span.duration_ms = round((now - span.start_time).total_seconds() * 1000, 2)
        span.status = "failed" if error_message else "completed"
        span.decision_rationale = decision_rationale
        span.tool_result = tool_result
        span.error_message = error_message
        span.metadata = metadata or {}

        # Save to firestore service
        firestore_service._spans[span_id] = span.model_dump()

        # Create audit entry
        audit_entry = AuditEntry(
            entry_id=f"AUD-{uuid.uuid4().hex[:8]}",
            trace_id=span.trace_id,
            span_id=span.span_id,
            parent_span_id=span.parent_span_id,
            agent_id=span.agent_id,
            action=span.action,
            decision_rationale=decision_rationale,
            timestamp=now,
            metadata={
                "duration_ms": span.duration_ms,
                "tool": span.tool_name,
                "status": span.status,
            }
        )
        firestore_service._audit_log.append(audit_entry.model_dump())
        return span

    def get_trace(self, trace_id: str) -> List[Span]:
        """Returns all spans associated with a trace_id."""
        spans = [s for s in self._spans.values() if s.trace_id == trace_id]
        spans.sort(key=lambda x: x.start_time)
        return spans

    def get_reasoning_chain(self, trace_id: str) -> Dict[str, Any]:
        """Reconstructs the hierarchical reasoning tree from root orchestrator to leaf tool calls."""
        spans = self.get_trace(trace_id)
        if not spans:
            return {"trace_id": trace_id, "nodes": []}

        # Build tree representation
        span_map = {s.span_id: s.model_dump() for s in spans}
        for s in span_map.values():
            s["children"] = []

        root_nodes = []
        for s in span_map.values():
            parent_id = s.get("parent_span_id")
            if parent_id and parent_id in span_map:
                span_map[parent_id]["children"].append(s)
            else:
                root_nodes.append(s)

        return {
            "trace_id": trace_id,
            "total_spans": len(spans),
            "hierarchy": root_nodes,
        }


observability = AgentObservability()
