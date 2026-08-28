from typing import Dict, Any, List, Optional
from datetime import datetime
from data.seed_campus import get_seed_buildings


CAMPUS_CONTACT_DIRECTORY = [
    {"role": "Campus Operations Director", "name": "Marcus Sterling", "phone": "555-010-1001", "email": "director.ops@campus.edu", "tier": "EXECUTIVE"},
    {"role": "Hospital Clinical Director", "name": "Dr. Miriam Vance", "phone": "555-010-2002", "email": "m.vance@hospital.campus.edu", "tier": "LIFE_SAFETY"},
    {"role": "NICU Charge Nurse Station", "name": "Station 3B", "phone": "555-010-2003", "email": "nicu.station@hospital.campus.edu", "tier": "LIFE_SAFETY"},
    {"role": "Campus Environmental Health & Safety", "name": "EHS Hotline", "phone": "555-010-3003", "email": "ehs-emergency@campus.edu", "tier": "SAFETY"},
    {"role": "Campus Police & Security Dispatch", "name": "Central Dispatch", "phone": "555-010-9111", "email": "police.dispatch@campus.edu", "tier": "EMERGENCY"},
    {"role": "Facilities Shift Supervisor", "name": "On-Duty Lead", "phone": "555-010-4004", "email": "shift.lead@campus.edu", "tier": "OPERATIONAL"},
]


def draft_notification(
    incident_id: str,
    severity: str,
    title: str,
    affected_locations: List[str],
    action_instructions: str,
    audience: str = "ALL_STAKEHOLDERS"
) -> Dict[str, Any]:
    """Drafts a structured emergency broadcast or operational update message.
    
    Args:
        incident_id: Active incident ID.
        severity: Priority level ('P1', 'P2', 'P3', 'P4').
        title: Bulletin headline.
        affected_locations: Buildings or zones impacted.
        action_instructions: Specific safety precautions or instructions.
        audience: Target recipient group.
        
    Returns:
        Formatted multi-channel notification text, SMS snippet, and broadcast metadata.
    """
    banner = "🚨 [URGENT CAMPUS ALERT]" if severity in ("P1", "P2") else "ℹ️ [CAMPUS OPERATIONAL NOTICE]"
    loc_str = ", ".join(affected_locations) if affected_locations else "Campus Wide"

    body = (
        f"{banner}\n"
        f"INCIDENT: {incident_id} | SEVERITY: {severity}\n"
        f"TITLE: {title}\n"
        f"AFFECTED LOCATIONS: {loc_str}\n\n"
        f"INSTRUCTIONS FOR OCCUPANTS & STAFF:\n{action_instructions}\n\n"
        f"Automated Notice Issued By ARCHON Communications Center at {datetime.utcnow().strftime('%H:%M:%S UTC')}."
    )

    sms_short = f"[{severity} ALERT] {title} at {loc_str}. {action_instructions[:90]}... More info: archon.campus/alerts"

    return {
        "status": "SUCCESS",
        "notification_id": f"NOTIF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "severity": severity,
        "audience": audience,
        "email_subject": f"{banner} {title} - {loc_str}",
        "full_body": body,
        "sms_summary": sms_short,
        "channels_ready": ["EMAIL", "SMS_GATEWAY", "CAMPUS_MOBILE_APP", "DIGITAL_SIGNAGE"],
    }


def route_by_severity(
    incident_id: str,
    severity: str,
    message: str,
    building_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Determines exact dispatch channels and recipient groups based on incident severity.
    
    Args:
        incident_id: Active incident.
        severity: Priority level ('P1', 'P2', 'P3', 'P4').
        message: Notification payload.
        building_ids: Impacted building identifiers.
        
    Returns:
        Routing matrix, confirmed dispatched channels, and contact recipient list.
    """
    recipients = []
    channels = []

    if severity == "P1":
        recipients = CAMPUS_CONTACT_DIRECTORY  # Full escalation
        channels = ["SMS_BROADCAST", "EMAIL_PUSH", "PAGER_OVERRIDE", "SECURITY_RADIO"]
    elif severity == "P2":
        recipients = [c for c in CAMPUS_CONTACT_DIRECTORY if c["tier"] in ("EXECUTIVE", "OPERATIONAL", "SAFETY")]
        channels = ["SMS_DIRECT", "EMAIL_PUSH", "OPERATIONS_DASHBOARD"]
    elif severity == "P3":
        recipients = [c for c in CAMPUS_CONTACT_DIRECTORY if c["tier"] in ("OPERATIONAL", "SAFETY")]
        channels = ["EMAIL_PUSH", "OPERATIONS_DASHBOARD"]
    else:
        recipients = [c for c in CAMPUS_CONTACT_DIRECTORY if c["tier"] == "OPERATIONAL"]
        channels = ["OPERATIONS_DASHBOARD"]

    return {
        "status": "DISPATCHED",
        "incident_id": incident_id,
        "severity": severity,
        "active_channels": channels,
        "recipients_notified_count": len(recipients),
        "recipient_names": [r["name"] for r in recipients],
        "delivery_timestamp": datetime.utcnow().isoformat(),
    }


def check_contact_directory(tier: Optional[str] = None) -> Dict[str, Any]:
    """Queries campus emergency contact directory.
    
    Args:
        tier: Optional filter ('LIFE_SAFETY', 'EXECUTIVE', 'SAFETY', 'EMERGENCY', 'OPERATIONAL').
        
    Returns:
        List of authorized personnel, phone lines, and email addresses.
    """
    contacts = CAMPUS_CONTACT_DIRECTORY
    if tier:
        contacts = [c for c in contacts if c["tier"].upper() == tier.upper()]

    return {
        "status": "SUCCESS",
        "contacts": contacts,
        "total_contacts": len(contacts),
    }
