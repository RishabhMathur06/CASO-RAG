# Imports dependencies.
import re
from typing import Tuple, Dict, Any, List
from loguru import logger

class ResponsibleAIGuard:
    """
        Enterprise Safety and Responsible AI Guardrail:
            1. Prompt Injection and Jailbreak Shield (detects malicious override instructions).
            2. PII Sanitization (masks emails, phone numbers, credit cards, SSNs, API tokens).
    """

    # Common jailbreak and prompt-injection patterns.
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
        r"forget\s+(all\s+)?(prior|previous)\s+guidelines",
        r"you\s+are\s+now\s+(in\s+)?developer\s+mode",
        r"act\s+as\s+(an\s+)?unrestricted\s+ai",
        r"dan\s+mode",
        r"system\s+prompt\s+override",
        r"reveal\s+(your\s+)?(secret\s+)?system\s+prompt",
        r"repeat\s+the\s+words\s+above",
        r"bypass\s+(all\s+)?filters"
    ]

    # Regex pattern for PII redaction.
    PII_PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "PHONE": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "API_KEY": r"\b(sk-[a-zA-Z0-9]{20,}|Bearer\s+[a-zA-Z0-9_.-]+)\b"
    }

    def __init__(self):
        self.injection_regexes = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self.pii_regexes = {label: re.compile(p) for label, p in self.PII_PATTERNS.items()}

    def detect_prompt_injection(self, text: str) -> Tuple[bool, List[str]]:
        """
            Checks whether the input text contains known prompt-injection or jailbreak patterns.
            Returns: (is_injection_detected, matched_patterns)
        """
        matched = []
        for regex in self.injection_regexes:
            if regex.search(text):
                matched.append(regex.pattern)

        if matched:
            logger.warning(f"🚨 Security Alert: Prompt injection attempt detected: {matched}")
            return True, matched

        return False, []

    def redact_pii(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
            Masks personal identifiable information (PII) with standardized tokens like [EMAIL_REDACTED].
            Returns: (sanitized_text, redaction_counts)
        """
        sanitized = text
        counts = {}

        for label, regex in self.pii_regexes.items():
            matches = regex.findall(sanitized)
            if matches:
                counts[label] = len(matches)
                sanitized = regex.sub(f"[{label}_REDACTED]", sanitized)
                logger.info(f"🛡️ Guardrail: Redacted {len(matches)} occurrence(s) of {label} from input.")

        return sanitized, counts


    def validate_and_sanitize(self, query: str) -> Dict[str, Any]:
        """
            Unified safety gateway:
                1. Checks for malicious prompt injections.
                2. Redacts sensitive PII.
        """
        is_injection, injection_details = self.detect_prompt_injection(query)

        if is_injection:
            return {
                "is_safe": False,
                "sanitized_query": query,
                "rejection_reason": "Query rejected by Responsible AI Guardrail: detected prompt injection / jailbreak pattern."
            }

        sanitized_query, redactions = self.redact_pii(query)

        return {
            "is_safe": True,
            "sanitized_query": sanitized_query,
            "redactions": redactions,
            "rejection_reason": None
        }

# Instance creation.
guardrails = ResponsibleAIGuard()