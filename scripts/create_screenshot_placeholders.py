import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

screenshot_dir = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
screenshot_dir.mkdir(parents=True, exist_ok=True)

placeholders = [
    ("banner.png", (1200, 380), "ARCHON Enterprise Command Platform", "Governed Multi-Agent Fleet for Campus Operations & Institutional Resilience"),
    ("dashboard_incidents.png", (800, 500), "1. Incident Command Center", "Live Telemetry Ingestion, Severity Triage & Building Blast Radius"),
    ("agent_swarm.png", (800, 500), "2. Multi-Agent Swarm Timeline", "7 Specialist ADK Agents with Real-Time Inter-Agent Delegation"),
    ("governance_approvals.png", (800, 500), "3. Model Armor & Approval Queue", "Prompt Injection Defense, PII Redaction & >$10k Human Approval Gate"),
    ("memory_explorer.png", (800, 500), "4. Institutional Memory Explorer", "Historical Incident Precedents, Equipment Quirks & Vendor Scorecards"),
]

for filename, size, title, subtitle in placeholders:
    img = Image.new("RGB", size, color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # Outer border
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline=(59, 130, 246), width=3)
    # Inner border
    draw.rectangle([20, 20, size[0]-20, size[1]-20], outline=(30, 41, 59), width=1)
    
    # Title badge
    draw.rectangle([40, 40, size[0]-40, 100], fill=(30, 58, 138), outline=(96, 165, 250), width=1)
    draw.text((60, 60), title, fill=(248, 250, 252))
    
    # Subtitle
    draw.text((60, 140), subtitle, fill=(148, 163, 184))
    draw.text((60, size[1]-60), "ARCHON Operations UI — [Replace with actual UI screenshot]", fill=(245, 158, 11))
    
    target_path = screenshot_dir / filename
    img.save(target_path, "PNG")
    print(f"Created placeholder: {target_path}")
