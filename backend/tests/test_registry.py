import pytest
from governance.registry import AgentRegistry
from models.agent_models import AgentManifest, AgentStatus


def test_agent_self_registration():
    registry = AgentRegistry()
    manifest = AgentManifest(
        agent_id="spiffe://archon.campus/agent/custom_test_agent",
        name="custom_test_agent",
        version="1.0.0",
        domain="corrective_actions",
        description="Test agent for verification",
        capabilities=["Testing"],
        tools=["create_task"],
    )
    reg = registry.register_agent(manifest)
    assert reg.name == "custom_test_agent"
    found = registry.get_agent("custom_test_agent")
    assert found is not None
    assert found.version == "1.0.0"


@pytest.mark.asyncio
async def test_playbook_discovery_water_incident():
    registry = AgentRegistry()
    discovered = await registry.discover_agents("water")
    assert len(discovered) > 0
    names = [a.name for a in discovered]
    assert "impact_assessor" in names
    assert "vendor_coordinator" in names


def test_heartbeat_health_monitoring():
    registry = AgentRegistry()
    agent_id = "spiffe://archon.campus/agent/incident_commander"
    ok = registry.heartbeat(agent_id)
    assert ok is True
    health = registry.check_health()
    assert health.get("incident_commander") == AgentStatus.ACTIVE


def test_agent_deregistration():
    registry = AgentRegistry()
    agent_id = "spiffe://archon.campus/agent/temp_worker"
    manifest = AgentManifest(
        agent_id=agent_id,
        name="temp_worker",
        domain="orchestration",
        description="Temp",
        capabilities=[],
        tools=[],
    )
    registry.register_agent(manifest)
    assert registry.get_agent("temp_worker") is not None

    registry.deregister_agent(agent_id)
    assert registry.get_agent("temp_worker") is None
