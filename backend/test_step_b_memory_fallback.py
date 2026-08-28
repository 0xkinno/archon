import os
import asyncio

os.environ["USE_MEMORY_BANK"] = "false"

from services.memory_service import memory_service
from tools.memory_tools import search_precedent

async def test_memory_fallback():
    print("=== STEP B: VERIFYING PERMANENT USE_MEMORY_BANK=false FALLBACK ===")
    print(f"memory_service.use_vertex: {memory_service.use_vertex}")
    assert memory_service.use_vertex is False, "Vertex Memory Bank should be disabled when USE_MEMORY_BANK=false"
    
    query = "Building F panel B3 humidity"
    print(f"\nSearching precedent for query: '{query}'")
    
    # 1. Test via synchronous tool function
    tool_res = search_precedent(query=query, limit=3)
    print(f"Tool Search Results ({tool_res['precedents_found']} found):")
    for p in tool_res["precedents"]:
        print(f"  - [{p.get('category')} | Relevance: {p.get('relevance_score')}]: {p.get('content')}")
        print(f"    Tags: {p.get('tags')}")
        
    assert tool_res["precedents_found"] > 0, "Should find at least 1 precedent"
    top_p = tool_res["precedents"][0]
    assert top_p["building_id"] == "BLDG-F"
    assert "panel B3" in top_p["content"]
    assert top_p["relevance_score"] == 1.0, f"Expected relevance score 1.0, got {top_p['relevance_score']}"

    # 2. Test via async service function directly
    service_res = await memory_service.search_precedent(query, limit=3)
    print(f"\nService Direct Search Results ({len(service_res)} found):")
    for s in service_res:
        print(f"  - [{s.get('category')} | Relevance: {s.get('relevance_score')}]: {s.get('content')}")
    
    assert len(service_res) > 0
    assert service_res[0]["building_id"] == "BLDG-F"
    print("\nSTEP B PASSED: Clean fallback returns exact precedent with relevance score 1.0.")

if __name__ == "__main__":
    asyncio.run(test_memory_fallback())
