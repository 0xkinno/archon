import base64
import json
import urllib.request
from pathlib import Path

mermaid_code = """flowchart TB
    subgraph INBOUND["Signal Ingestion"]
        IOT["IoT Sensors<br/>(BMS webhooks)"]
        EMAIL["Vendor Emails<br/>(inbound comms)"]
        MANUAL["Manual Reports<br/>(operator input)"]
        SCHEDULE["Inspection Calendar<br/>(regulatory feeds)"]
    end

    subgraph ARMOR_LAYER["Model Armor Firewall"]
        MA["Injection Detection (16 patterns)<br/>PII Redaction (5 types)<br/>Tool Poisoning Defense"]
    end

    IOT --> MA
    EMAIL --> MA
    MANUAL --> MA
    SCHEDULE --> MA

    subgraph GATEWAY["Agent Gateway -- Policy Enforcement"]
        GW["Authorization Engine<br/>Financial Thresholds ($10k)<br/>Domain Scoping<br/>Rate Limiting (20 calls)"]
    end

    MA --> GW

    subgraph REGISTRY["Agent Registry -- Discovery & Lifecycle"]
        REG["Capability Manifests<br/>Semantic Versioning (1.0.0)<br/>Health Monitoring<br/>Playbook Catalog"]
    end

    GW --> REG

    subgraph FLEET["Agent Fleet -- Google ADK"]
        CMD["incident_commander<br/>(Orchestrator)"]
        IMP["impact_assessor"]
        VND["vendor_coordinator"]
        CMP["compliance_inspector"]
        COM["communications_officer"]
        REM["remediation_tracker"]
        MEM["memory_curator"]
    end

    REG --> CMD
    CMD -->|"transfer_to_agent"| IMP
    CMD -->|"transfer_to_agent"| VND
    CMD -->|"transfer_to_agent"| CMP
    CMD -->|"transfer_to_agent"| COM
    CMD -->|"transfer_to_agent"| REM
    CMD -->|"transfer_to_agent"| MEM

    subgraph STATE["Persistent State"]
        FS["Firestore<br/>(Incident State)"]
        MB["Memory Bank<br/>(Institutional Memory)"]
    end

    FLEET --> FS
    FLEET --> MB

    subgraph OBSERVE["Agent Observability"]
        OBS["OpenTelemetry Traces<br/>Audit Ledger<br/>Reasoning Chains<br/>Performance Metrics"]
    end

    FLEET --> OBS

    subgraph INFRA["Infrastructure & Models"]
        CR["Render Backend<br/>(API + WebSocket)"]
        VX["Vertex AI / Firestore<br/>State Engine"]
        GEM["Gemini 2.5/3.5 Flash<br/>(LLM Reasoning)"]
    end

    FLEET --> GEM
    CR --> FLEET
    VX --> FLEET

    subgraph IDENTITY["Agent Identity"]
        ID["SPIFFE IDs<br/>Scoped JWTs<br/>Least-Privilege<br/>mTLS"]
    end

    ID --> GW
    ID --> FLEET

    subgraph UI["Operations Dashboard"]
        DASH["Next.js 14 Dashboard<br/>Incident Timeline<br/>Agent Status Grid<br/>Memory Explorer<br/>Trace Viewer<br/>Approval Queue"]
    end

    OBS --> DASH
    FS --> DASH
    CR --> DASH
"""

output_path = Path(__file__).resolve().parent.parent / "docs" / "architecture_diagram.png"
output_path.parent.mkdir(parents=True, exist_ok=True)

# Encode mermaid diagram for mermaid.ink
graph_json = json.dumps({"code": mermaid_code, "mermaid": {"theme": "dark"}})
encoded_bytes = base64.urlsafe_b64encode(graph_json.encode("utf-8")).decode("ascii")
url = f"https://mermaid.ink/img/{encoded_bytes}?bgColor=1e293b"

print(f"Fetching diagram PNG from {url[:40]}...")
try:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        png_data = response.read()
        output_path.write_bytes(png_data)
        print(f"SUCCESS: Exported architecture diagram ({len(png_data)} bytes) to {output_path}")
except Exception as e:
    print(f"Error fetching from mermaid.ink: {e}")
    # Fallback to local image generator
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1200, 800), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 1150, 750], outline=(59, 130, 246), width=3)
    draw.text((100, 100), "ARCHON Architecture Diagram (Dark Mode)", fill=(248, 250, 252))
    draw.text((100, 150), "Inbound Signals -> Model Armor -> Agent Gateway -> Agent Registry -> Agent Swarm -> Observability & State", fill=(148, 163, 184))
    img.save(output_path, "PNG")
    print(f"SUCCESS: Created fallback architecture diagram at {output_path}")
