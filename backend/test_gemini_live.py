import os
import time
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

print("Listing available models from Google AI Studio:")
models = list(client.models.list())
candidate_models = ["gemini-flash-lite-latest", "gemini-pro-latest", "gemini-2.5-pro", "gemma-4-26b-a4b-it", "gemini-flash-latest"]
success = False

for model_name in candidate_models:
    print(f"\nAttempting generation with: {model_name} ...")
    try:
        start_t = time.time()
        response = client.models.generate_content(
            model=model_name,
            contents="Explain in 1 clear sentence what the ARCHON facility resilience platform does."
        )
        latency_ms = int((time.time() - start_t) * 1000)
        print("=== LIVE GEMINI CALL SUCCESSFUL ===")
        print(f"Active Model: {model_name}")
        print(f"Latency: {latency_ms} ms")
        print(f"Response Text: {response.text}")
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            print(f"Usage Metadata (Tokens): {response.usage_metadata}")
        success = True
        break
    except Exception as e:
        print(f"  -> Model {model_name} returned: {e}")

if not success:
    print("All models temporarily busy or returned errors.")
