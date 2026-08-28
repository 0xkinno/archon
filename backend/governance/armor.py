import re
import logging
from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime

from models.audit import ModelArmorVerdict, ModelArmorStatus

logger = logging.getLogger("archon.armor")

# Comprehensive Injection Signatures (14+ patterns)
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?(prior|previous)\s+",
    r"you\s+are\s+now\s+in\s+\w+\s+mode",
    r"do\s+not\s+report\s+this",
    r"system\s*prompt",
    r"override\s+(security|policy|protocol|authorization)",
    r"pretend\s+you\s+are",
    r"act\s+as\s+(if|though)",
    r"forget\s+(everything|all|your)",
    r"new\s+instructions?\s*:",
    r"admin\s+mode\s+(activate|enable)",
    r"execute\s+command",
    r"bypass\s+(security|filter|check|gateway)",
    r"jailbreak",
    r"dan\s+mode",
    r"developer\s+override\s+code",
]

# PII Patterns to Redact (5 types)
PII_PATTERNS = [
    (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED_PHONE]"),
    (r"\b[\w.+-]+@[\w-]+\.[\w.]+\b", "[REDACTED_EMAIL]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
    (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b", "[REDACTED_CARD]"),
    (r"\b\d{1,5}\s[\w\s]{1,30}(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard)\b", "[REDACTED_ADDRESS]"),
]

# Tool Poisoning Indicators
TOOL_POISONING_INDICATORS = [
    r"call\s+\w+\s+with\s+parameters?",
    r"invoke\s+function",
    r"execute\s+tool",
    r"set\s+\w+\s*=\s*",
    r"__import__",
    r"eval\(",
    r"exec\(",
]


def scan_for_injection(text: str) -> Tuple[bool, Optional[str]]:
    """Scans input text for prompt injection signatures."""
    if not text:
        return False, None
    for pattern in INJECTION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return True, match.group(0)
    return False, None


def redact_pii(text: str) -> Tuple[str, int]:
    """Scans and replaces PII instances with canonical redaction placeholders."""
    if not text:
        return text, 0
    total_redactions = 0
    cleaned = text
    for pattern, replacement in PII_PATTERNS:
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        if matches:
            total_redactions += len(matches)
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned, total_redactions


def detect_tool_poisoning(text: str) -> Tuple[bool, Optional[str]]:
    """Detects malicious payload fragments attempting tool invocation poisoning."""
    if not text:
        return False, None
    for pattern in TOOL_POISONING_INDICATORS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return True, match.group(0)
    return False, None


class ModelArmor:
    """Enterprise firewall screening all inbound signals and tool returns."""

    def __init__(self):
        self._blocked_sources: set = set()
        self._verdict_log: List[ModelArmorVerdict] = []

    def screen_inbound(self, text: str, source: str) -> ModelArmorVerdict:
        """Full screening pipeline for external text signals."""
        is_injected, injection_pattern = scan_for_injection(text)
        is_poisoned, poison_indicator = detect_tool_poisoning(text)
        cleaned_text, redaction_count = redact_pii(text)

        status = ModelArmorStatus.CLEAN
        if is_injected or is_poisoned:
            status = ModelArmorStatus.BLOCKED
            self._blocked_sources.add(source)
            logger.warning(f"Model Armor BLOCKED source '{source}'. Injected: {is_injected} ({injection_pattern}), Poisoned: {is_poisoned} ({poison_indicator})")
        elif redaction_count > 0:
            status = ModelArmorStatus.REDACTED
            logger.info(f"Model Armor REDACTED {redaction_count} PII items for source '{source}'")

        verdict = ModelArmorVerdict(
            status=status,
            is_injected=is_injected,
            injection_pattern=injection_pattern,
            redaction_count=redaction_count,
            cleaned_text=cleaned_text if status != ModelArmorStatus.BLOCKED else "[QUARANTINED_UNSAFE_PAYLOAD]",
            is_tool_poisoned=is_poisoned,
            poison_indicator=poison_indicator,
            source=source,
            timestamp=datetime.utcnow(),
            details={
                "original_length": len(text),
                "redaction_applied": redaction_count > 0,
            }
        )
        self._verdict_log.append(verdict)
        return verdict

    def is_source_blocked(self, source: str) -> bool:
        return source in self._blocked_sources

    def get_verdicts(self, limit: int = 50) -> List[ModelArmorVerdict]:
        return self._verdict_log[-limit:]


model_armor = ModelArmor()


def screen_inbound(text: str, source: str) -> ModelArmorVerdict:
    return model_armor.screen_inbound(text, source)


def screen_tool_result(*, tool, args, tool_context=None, tool_response=None, callback_context=None):
    """ADK after_tool_callback compatible hook."""
    response_str = str(tool_response) if tool_response else ""
    verdict = model_armor.screen_inbound(response_str, source=getattr(tool, "__name__", "unknown_tool"))
    if verdict.status == ModelArmorStatus.BLOCKED:
        return {
            "status": "QUARANTINED_BY_MODEL_ARMOR",
            "reason": f"Tool output contained adversarial pattern: {verdict.injection_pattern or verdict.poison_indicator}",
            "safe_response": "Action halted due to Model Armor security rule."
        }
    return tool_response
