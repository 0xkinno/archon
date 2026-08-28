import json
import os
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path(__file__).resolve().parent


def load_json_file(filename: str) -> Any:
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_seed_buildings() -> List[Dict[str, Any]]:
    return load_json_file("campus_data.json")


def get_seed_vendors() -> List[Dict[str, Any]]:
    return load_json_file("vendor_directory.json")


def get_seed_inspections() -> List[Dict[str, Any]]:
    return load_json_file("inspection_calendar.json")


def get_seed_playbooks() -> List[Dict[str, Any]]:
    return load_json_file("incident_playbooks.json")


if __name__ == "__main__":
    print(f"Loaded {len(get_seed_buildings())} campus buildings.")
    print(f"Loaded {len(get_seed_vendors())} vendors.")
    print(f"Loaded {len(get_seed_inspections())} inspections.")
    print(f"Loaded {len(get_seed_playbooks())} playbooks.")
