import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from services.firestore_service import firestore_service
from services.memory_service import memory_service
from governance.registry import agent_registry

async def main():
    print("Seeding Firestore and Memory Bank with initial campus topologies...")
    await firestore_service.initialize()
    buildings = await firestore_service.list_buildings()
    vendors = await firestore_service.list_vendors()
    inspections = await firestore_service.list_inspections()
    agents = agent_registry.list_agents()
    memories = memory_service._memories

    print(f"Successfully seeded:")
    print(f"  - {len(buildings)} Campus Buildings")
    print(f"  - {len(vendors)} Emergency Contractors & Vendors")
    print(f"  - {len(inspections)} Scheduled Regulatory Audits")
    print(f"  - {len(agents)} Registered Specialist Agents")
    print(f"  - {len(memories)} Decades of Institutional Memories")

if __name__ == "__main__":
    asyncio.run(main())
