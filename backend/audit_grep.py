import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SEARCH_DIRS = [ROOT / "backend", ROOT / "frontend" / "src"]

PATTERNS = {
    "mock": re.compile(r"mock", re.IGNORECASE),
    "hardcode": re.compile(r"hardcode", re.IGNORECASE),
    "TODO/FIXME/STUB/placeholder": re.compile(r"TODO|FIXME|STUB|placeholder", re.IGNORECASE),
    "static_time_strings": re.compile(r"1h ago|2h ago|just now", re.IGNORECASE),
    "fake/dummy/sample_response/canned": re.compile(r"fake|dummy|sample_response|canned", re.IGNORECASE),
}

results = {k: [] for k in PATTERNS}

for sdir in SEARCH_DIRS:
    if not sdir.exists():
        continue
    for ext in ("*.py", "*.ts", "*.tsx", "*.json"):
        for fpath in sdir.rglob(ext):
            if "node_modules" in str(fpath) or ".next" in str(fpath) or ".venv" in str(fpath) or "__pycache__" in str(fpath):
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
                for line_no, line in enumerate(content.splitlines(), start=1):
                    for name, pat in PATTERNS.items():
                        if pat.search(line):
                            rel_path = fpath.relative_to(ROOT)
                            results[name].append((str(rel_path), line_no, line.strip()))
            except Exception as e:
                pass

print("======================================================================")
print("  ARCHON CODEBASE GREP AUDIT RESULTS")
print("======================================================================")
for name, hits in results.items():
    print(f"\n--- Pattern: [{name}] ({len(hits)} hits) ---")
    if not hits:
        print("  None found.")
    for path, line_no, text in hits[:25]:
        print(f"  {path}:{line_no} -> {text}")
    if len(hits) > 25:
        print(f"  ... and {len(hits) - 25} more hits")
