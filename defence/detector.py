import re


# Warning signals, not proof of poisoning.
SUSPICIOUS_PATTERNS = {
    "urgent_language": [
        r"\bIMPORTANT\b",
        r"\bURGENT\b",
        r"\bCRITICAL\b",
        r"\bIMMEDIATELY\b"
    ],

    "instruction_override": [
        r"ignore previous instructions",
        r"disregard all previous instructions",
        r"override system instructions",
        r"reveal hidden instructions",
        r"ignore all rules",
        r"bypass security restrictions"
    ],

    "unusual_authority_claims": [
        r"\bofficially approved\b",
        r"\bguaranteed\b",
        r"\bwithout verification\b",
        r"\bno verification required\b"
    ],

    "unusual_access_claims": [
        r"\b24\s*/\s*7\b",
        r"\b24 hours a day\b",
        r"\bpublic holidays\b"
    ]
}


# Transparent risk weights
RISK_WEIGHTS = {
    "urgent_language": 5,
    "instruction_override": 35,
    "unusual_authority_claims": 15,
    "unusual_access_claims": 15
}


# Example source trust registry.
# In a real deployment, trust must be established
# through verified ownership and provenance.
TRUSTED_SOURCES = {
    "northstar_official_policy.txt"
}


def analyze_document(content, source="unknown"):

    score = 0
    findings = []
    matched_categories = []

    text = content.lower()

    # 1. Analyze suspicious content
    for category, patterns in SUSPICIOUS_PATTERNS.items():

        matched = False

        for pattern in patterns:

            if re.search(pattern, text, re.IGNORECASE):
                matched = True
                break

        if matched:

            score += RISK_WEIGHTS[category]

            matched_categories.append(category)

            findings.append(
                f"Suspicious indicator: "
                f"{category.replace('_', ' ')}"
            )

    # 2. Check source provenance
    source_is_trusted = source in TRUSTED_SOURCES

    if not source_is_trusted:

        findings.append(
            "Source is not present in the trusted source registry."
        )

        score += 20

    else:

        findings.append(
            "Source is present in the trusted source registry."
        )

    # 3. Limit score
    score = min(score, 100)

    # 4. Determine risk level
    if score >= 50:
        risk_level = "High"

    elif score >= 20:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    # 5. Determine security decision
    if not source_is_trusted or score >= 50:
        decision = "REJECTED"

    elif score >= 20:
        decision = "REVIEW REQUIRED"

    else:
        decision = "APPROVED"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "findings": findings,
        "matched_categories": matched_categories,
        "source_trusted": source_is_trusted,
        "decision": decision
    }
