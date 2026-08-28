from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ModelArmorStatus(str, Enum):
    CLEAN = "CLEAN"
    REDACTED = "REDACTED"
    BLOCKED = "BLOCKED"


class ModelArmorVerdict(BaseModel):
    status: ModelArmorStatus
    is_injected: bool = False
    injection_pattern: Optional[str] = None
    redaction_count: int = 0
    cleaned_text: str
    is_tool_poisoned: bool = False
    poison_indicator: Optional[str] = None
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)


class Span(BaseModel):
    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    agent_id: str
    action: str
    status: str = "running"  # running, completed, failed
    decision_rationale: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditEntry(BaseModel):
    entry_id: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    agent_id: str
    action: str
    decision_rationale: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TraceHierarchy(BaseModel):
    trace_id: str
    incident_id: str
    root_span: Optional[Span] = None
    spans: List[Span] = Field(default_factory=list)
    total_duration_ms: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalRequest(BaseModel):
    approval_id: str
    incident_id: str
    agent_id: str
    action_type: str
    description: str
    reason: str  # e.g., "Financial threshold exceeded ($12,500 > $10,000)" or "P1 life safety action"
    estimated_cost: Optional[float] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_payload: Dict[str, Any] = Field(default_factory=dict)
    decision_by: Optional[str] = None
    decision_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
