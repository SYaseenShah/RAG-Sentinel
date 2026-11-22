"""Structured, rule-based policy-claim comparison for the controlled lab.

This module compares only supported claim types. It is not a semantic/NLI
contradiction model and must not be described as one.
"""
from __future__ import annotations
import re

TRUSTED_SOURCE = "northstar_official_policy.txt"  # legacy demo identifier


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def extract_support_hours(content: str):
    text = _normalise(content)
    if re.search(r"\b24\s*/\s*7\b|\b24\s+hours\s+a\s+day\b|\baround\s+the\s+clock\b|\bday\s+and\s+night\b", text):
        return "24/7"
    weekdays = "monday" in text and "friday" in text
    nine_am = re.search(r"\b9(?::00)?\s*a\.?m\.?", text)
    five_pm = re.search(r"\b5(?::00)?\s*p\.?m\.?", text)
    if weekdays and nine_am and five_pm:
        return "weekdays_9_to_5"
    return None


def extract_policy_claims(content: str) -> dict:
    """Extract a small set of explicit, normalized policy facts."""
    text = _normalise(content)
    claims = {}

    hours = extract_support_hours(text)
    if hours:
        claims["support_hours"] = hours

    refund = re.search(r"\brefund(?:s)?\b.{0,100}?\b(?:within|up to|no later than)\s+(\d{1,3})\s+days?\b", text)
    if refund:
        claims["refund_window_days"] = int(refund.group(1))

    password = re.search(r"\bpassword\w*\b.{0,100}?\b(?:at least|minimum of|min(?:imum)?\.?\s*)\s*(\d{1,2})\s+characters?\b", text)
    if password:
        claims["password_min_length"] = int(password.group(1))

    retention = re.search(r"\b(?:retain|retained|retention|keep|stored)\b.{0,100}?\b(\d{1,4})\s+days?\b", text)
    if retention:
        claims["data_retention_days"] = int(retention.group(1))

    return claims


def extract_organization(content: str):
    text = str(content or "")
    explicit = re.search(r"(?im)^\s*(?:organization|organisation|company|service)\s*:\s*([^\r\n.]+)", text)
    if explicit:
        return _normalise(explicit.group(1)).strip(" .:-")
    # Backward-compatible identifier for the original Northstar demonstration.
    if re.search(r"\bnorthstar\b", text, re.IGNORECASE):
        return "northstar"
    return None


def compare_policy_claims(candidate_text: str, reference_text: str, candidate_source="unknown", reference_source="trusted_reference"):
    candidate_org = extract_organization(candidate_text)
    reference_org = extract_organization(reference_text)
    if not candidate_org or not reference_org or candidate_org != reference_org:
        return []

    candidate_claims = extract_policy_claims(candidate_text)
    reference_claims = extract_policy_claims(reference_text)
    conflicts = []
    for topic, candidate_value in candidate_claims.items():
        reference_value = reference_claims.get(topic)
        if reference_value is not None and candidate_value != reference_value:
            conflicts.append({
                "type": topic,
                "organization": candidate_org,
                "candidate_claim": candidate_value,
                "trusted_claim": reference_value,
                "source": candidate_source,
                "trusted_document": reference_source,
                "reason": f"The {topic.replace('_', ' ')} claim conflicts with an administrator-approved reference for {candidate_org}.",
            })
    return conflicts


def detect_contradictions(documents):
    """Compare documents sharing an organization identifier; trusted source
    identity must be established by the caller/registry, not this function.
    The legacy Northstar source is retained for the original lab test only.
    """
    references = [d for d in documents if d.get("source") == TRUSTED_SOURCE or d.get("is_trusted_reference") is True]
    conflicts = []
    for document in documents:
        if document in references:
            continue
        for reference in references:
            conflicts.extend(compare_policy_claims(
                document.get("content", ""), reference.get("content", ""),
                document.get("source", "unknown"), reference.get("source", "trusted_reference")
            ))
    return conflicts
