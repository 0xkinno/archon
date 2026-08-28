from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class PlaybookStep(BaseModel):
    step_number: int
    agent_id: str
    action_name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required: bool = True


class Playbook(BaseModel):
    playbook_id: str
    name: str
    incident_type: str
    description: str
    required_agents: List[str]
    steps: List[PlaybookStep]
    estimated_duration_minutes: int


class AgentManifest(BaseModel):
    agent_id: str  # spiffe://archon.campus/agent/{agent_name}
    name: str
    version: str = "1.0.0"
    domain: str
    description: str
    capabilities: List[str]
    tools: List[str]
    status: AgentStatus = AgentStatus.ACTIVE
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    missed_heartbeats: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentIdentityModel(BaseModel):
    agent_id: str
    agent_name: str
    domain: str
    allowed_tools: List[str]
    spiffe_id: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
