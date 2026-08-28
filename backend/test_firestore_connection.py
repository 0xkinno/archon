import os
from pathlib import Path
from dotenv import load_dotenv

# Load env vars
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

from google.cloud import firestore

project_id = os.getenv("GCP_PROJECT_ID", "archon-ece25")
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print(f"Connecting to Firestore Project: {project_id}")
print(f"Credentials Path: {cred_path}")

db = firestore.Client(project=project_id)
doc_ref = db.collection("connection_test").document("ping")
doc_ref.set({"status": "connected", "timestamp": firestore.SERVER_TIMESTAMP})

data = doc_ref.get().to_dict()
print("Firestore connection successful! Document retrieved:")
print(data)
