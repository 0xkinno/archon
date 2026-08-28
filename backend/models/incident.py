from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IncidentSeverity(str, Enum):
    P1 = "P1"  # Critical: Life safety / critical infrastructure failure
    P2 = "P2"  # High: Major operational disruption across multiple buildings
    P3 = "P3"  # Medium: Single-system failure with workaround
    P4 = "P4"  # Low: Routine maintenance / non-urgent


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"


class IncidentType(str, Enum):
    WATER = "water"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    FIRE = "fire"
    SECURITY = "security"
    STRUCTURAL = "structural"
    VENDOR = "vendor"
    INSPECTION = "inspection"


class SignalPayload(BaseModel):
    source: str
    signal_type: str = "manual"  # iot_webhook, vendor_email, manual_report, calendar_trigger
    building_id: Optional[str] = None
    system: Optional[str] = None
    raw_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Building(BaseModel):
    building_id: str
    name: str
    address: str
    floors: int
    systems: List[str]  # e.g., ["hvac", "plumbing", "electrical", "fire_suppression", "elevators", "security"]
    occupancy_capacity: int
    current_occupancy: Optional[int] = None
    critical_zones: List[str] = Field(default_factory=list)
    special_requirements: str
    dependencies: List[str] = Field(default_factory=list)  # e.g., dependent building IDs for utilities


class VendorProfile(BaseModel):
    vendor_id: str
    name: str
    specialties: List[str]
    avg_response_time_hours: float
    reliability_score: float  # 0.0 - 100.0
    contract_terms: Dict[str, Any]
    contact_info: Dict[str, str]
    incidents_served: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class RemediationTask(BaseModel):
    task_id: str
    incident_id: str
    title: str
    assignee: str
    status: str = "pending"  # pending, in_progress, blocked, completed
    deadline: Optional[datetime] = None
    created_by_agent: str
    notes: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DispatchRecord(BaseModel):
    dispatch_id: str
    vendor_id: str
    vendor_name: str
    incident_id: str
    building: str
    description: str
    status: str = "DISPATCHED"  # DISPATCHED, EN_ROUTE, ON_SITE, COMPLETED, CANCELLED
    estimated_arrival_hours: float
    estimated_cost: float
    dispatched_at: datetime = Field(default_factory=datetime.utcnow)


class InspectionRecord(BaseModel):
    inspection_id: str
    agency: str
    inspection_type: str
    building_id: str
    scheduled_date: str
    status: str = "upcoming"  # upcoming, in_progress, passed, conditional_pass, failed
    required_documents: List[str] = Field(default_factory=list)
    outstanding_violations: List[str] = Field(default_factory=list)


class Incident(BaseModel):
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    incident_type: IncidentType
    affected_buildings: List[str] = Field(default_factory=list)
    assigned_agents: List[str] = Field(default_factory=list)
    playbook_id: Optional[str] = None
    playbook_progress: Dict[str, Any] = Field(default_factory=dict)
    resolution_summary: Optional[str] = None
    estimated_impact_cost: Optional[float] = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
