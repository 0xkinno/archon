import os
import shutil
from pathlib import Path

archon_root = Path(__file__).resolve().parent.parent
screenshots_dir = archon_root / "docs" / "screenshots"
public_dir = archon_root / "video" / "public"
public_dir.mkdir(parents=True, exist_ok=True)

for file in screenshots_dir.glob("*.png"):
    dest = public_dir / file.name
    shutil.copy2(file, dest)
    print(f"Copied {file.name} to video/public/ ({dest.stat().st_size} bytes)")

# Also copy architecture diagram
arch_diag = archon_root / "docs" / "architecture_diagram.png"
if arch_diag.exists():
    shutil.copy2(arch_diag, public_dir / "architecture_diagram.png")
    print(f"Copied architecture_diagram.png to video/public/")

print("Public assets ready!")
