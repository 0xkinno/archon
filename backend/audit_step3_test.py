import asyncio
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

from services.firestore_service import firestore_service
from services.gemini_service import generate_reasoning
from api.routes import run_full_orchestration_pipeline

async def run_step3_test():
    await firestore_service.initialize()
    
    novel_description = "Basement freight elevator in Building A is making a grinding noise and stopped between floors 2 and 3 with two people inside."
    print("=== AUDIT STEP 3: NOVEL INCIDENT ORCHESTRATION ===")
    print(f"Input Signal: {novel_description}")
    print(f"Building: BLDG-A | System: structural/elevator\n")
    
    # 1. Live Gemini LLM Reasoning Generation
    print("[1/2] Invoking live Gemini model for incident assessment...")
    start_t = time.time()
    gemini_assessment = await generate_reasoning(
        prompt=f"Assess this facility incident signal: '{novel_description}' in Building A. State severity, life-safety risk, and immediate action."
    )
    latency_ms = int((time.time() - start_t) * 1000)
    print(f"Gemini LLM Latency: {latency_ms}ms")
    print(f"Gemini LLM Output:\n{gemini_assessment}\n")
    
    # 2. Full Pipeline Orchestration
    print("[2/2] Running full multi-agent orchestration pipeline...")
    result = await run_full_orchestration_pipeline(
        raw_signal=novel_description,
        source="operator_radio",
        signal_type="structural",
        building_id="BLDG-A",
        system="elevator",
    )
    
    saved_incident = await firestore_service.get_incident(result['incident_id'])
    
    print("\n=== ORCHESTRATION PIPELINE OUTPUT ===")
    print(f"Incident ID: {result['incident_id']}")
    print(f"Severity: {result['classification']['severity']}")
    print(f"Incident Type: {result['classification']['incident_type']}")
    print(f"Playbook Activated: {result['playbook']['playbook_id']}")
    print(f"Delegation Order: {result['playbook']['delegation_order']}")
    print(f"Trace ID: {result['trace_id']}")
    print(f"Agent Executions: {len(result['agent_executions'])}")
    for exec_item in result['agent_executions']:
        print(f"  - [{exec_item['agent']}]: {list(exec_item['result'].keys()) if isinstance(exec_item['result'], dict) else exec_item['result']}")
    print(f"\nClassification Summary: {result['classification']['summary']}")
    print(f"Saved Incident in Firestore: Status={saved_incident.get('status')}, Title={saved_incident.get('title')}")

if __name__ == "__main__":
    asyncio.run(run_step3_test())
