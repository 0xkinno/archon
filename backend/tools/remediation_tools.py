import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from services.firestore_service import firestore_service


def create_task(
    incident_id: str,
    title: str,
    assignee: str,
    deadline_hours: float = 24.0,
    created_by_agent: str = "remediation_tracker",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Creates an actionable corrective action work order.
    
    Args:
        incident_id: Active incident ID.
        title: Task objective.
        assignee: Trade group or technician responsible.
        deadline_hours: Target completion window in hours.
        created_by_agent: Authoring agent name.
        notes: Initial work instructions.
        
    Returns:
        Created work order record and tracking details.
    """
    task_id = f"TSK-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    deadline = datetime.utcnow() + timedelta(hours=deadline_hours)

    task_record = {
        "task_id": task_id,
        "incident_id": incident_id or "INC-GENERAL",
        "title": title,
        "assignee": assignee,
        "status": "pending",
        "deadline": deadline.isoformat(),
        "created_by_agent": created_by_agent,
        "notes": [notes] if notes else [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    firestore_service._tasks[task_id] = task_record

    return {
        "status": "SUCCESS",
        "task_id": task_id,
        "title": title,
        "assignee": assignee,
        "deadline": task_record["deadline"],
        "summary": f"Work order '{task_id}' assigned to {assignee} with deadline in {deadline_hours} hours.",
    }


def update_task(task_id: str, status: str, progress_note: Optional[str] = None) -> Dict[str, Any]:
    """Updates status and work logs on an open remediation task.
    
    Args:
        task_id: Identifier of the task.
        status: New state ('pending', 'in_progress', 'blocked', 'completed').
        progress_note: Field technician observations.
        
    Returns:
        Updated task record.
    """
    task = firestore_service._tasks.get(task_id)
    if not task:
        return {"status": "ERROR", "reason": f"Task '{task_id}' not found."}

    task["status"] = status
    task["updated_at"] = datetime.utcnow().isoformat()
    if progress_note:
        task["notes"].append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {progress_note}")

    return {
        "status": "SUCCESS",
        "task_id": task_id,
        "new_status": status,
        "notes_count": len(task["notes"]),
        "updated_at": task["updated_at"],
    }


def escalate_overdue(incident_id: Optional[str] = None) -> Dict[str, Any]:
    """Scans all remediation tasks and triggers immediate supervisory escalation on overdue items.
    
    Args:
        incident_id: Optional filter for specific incident.
        
    Returns:
        List of identified overdue tasks and escalated supervisor alerts.
    """
    now = datetime.utcnow()
    tasks = list(firestore_service._tasks.values())
    if incident_id:
        tasks = [t for t in tasks if t.get("incident_id") == incident_id]

    overdue = []
    for t in tasks:
        if t.get("status") not in ("completed", "cancelled"):
            deadline_str = t.get("deadline")
            if deadline_str:
                deadline = datetime.fromisoformat(deadline_str)
                if now > deadline:
                    overdue.append(t)
                    t["status"] = "blocked"
                    t["notes"].append(f"[{now.strftime('%H:%M:%S')}] AUTO-ESCALATED: Task overdue beyond SLA deadline.")

    return {
        "status": "SUCCESS",
        "total_scanned": len(tasks),
        "overdue_count": len(overdue),
        "escalated_tasks": [
            {
                "task_id": t["task_id"],
                "title": t["title"],
                "assignee": t["assignee"],
                "deadline": t["deadline"]
            }
            for t in overdue
        ],
    }


def shift_handoff(shift_name: str, incident_id: Optional[str] = None) -> Dict[str, Any]:
    """Generates structured operational briefing for incoming shift supervisor.
    
    Args:
        shift_name: Shift identifier (e.g., 'Day Shift 0700-1500', 'Graveyard Shift').
        incident_id: Optional incident filter.
        
    Returns:
        Comprehensive shift transition summary, active hazards, and open work orders.
    """
    tasks = list(firestore_service._tasks.values())
    if incident_id:
        tasks = [t for t in tasks if t.get("incident_id") == incident_id]

    pending = [t for t in tasks if t.get("status") == "pending"]
    in_progress = [t for t in tasks if t.get("status") == "in_progress"]
    completed = [t for t in tasks if t.get("status") == "completed"]

    return {
        "status": "SUCCESS",
        "handoff_id": f"HND-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        "shift_name": shift_name,
        "compiled_at": datetime.utcnow().isoformat(),
        "summary": f"Operational handoff for {shift_name}. Active tasks: {len(pending) + len(in_progress)}, Completed: {len(completed)}.",
        "pending_tasks": [p["title"] for p in pending],
        "in_progress_tasks": [ip["title"] for ip in in_progress],
        "completed_tasks": [c["title"] for c in completed],
    }
