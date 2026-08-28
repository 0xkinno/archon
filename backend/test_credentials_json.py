import os
import json
import asyncio
from pathlib import Path

# Load raw JSON from file to test JSON string env var
cred_path = Path(__file__).resolve().parent / "secrets" / "firebase-service-account.json"
assert cred_path.exists(), "Service account JSON must exist"
raw_json = cred_path.read_text(encoding="utf-8")

# Clear file path env var and set JSON env var
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"] = raw_json
os.environ["GCP_PROJECT_ID"] = "archon-ece25"
os.environ["USE_MEMORY_BANK"] = "false"

from services.firestore_service import FirestoreService

async def test_json_creds():
    service = FirestoreService()
    await service.initialize()
    assert service._db is not None, "Firestore client should be connected using JSON credentials!"
    print("SUCCESS: Firestore initialized with GOOGLE_APPLICATION_CREDENTIALS_JSON!")
    
    # Test ping write and read
    doc_ref = service._db.collection("connection_test").document("json_ping")
    doc_ref.set({"status": "connected_via_raw_json", "timestamp": "2026-08-28T09:17:00"})
    data = doc_ref.get().to_dict()
    print(f"Retrieved document: {data}")
    assert data["status"] == "connected_via_raw_json"
    print("STEP A PASSED: Render-compatible raw JSON credential loading is 100% verified.")

if __name__ == "__main__":
    asyncio.run(test_json_creds())
