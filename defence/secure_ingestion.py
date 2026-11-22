"""Pre-ingestion security gate and local quarantine registry.

This is a controlled academic prototype. The local Streamlit admin action is
not an authentication boundary for a production deployment.
"""

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from rag.engine import extract_text
from defence.detector import analyze_document
from defence.contradiction import compare_policy_claims

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REVIEW_DIR = DATA_DIR / "review"
QUARANTINE_DIR = DATA_DIR / "quarantine"
APPROVED_DIR = DATA_DIR / "approved_documents"
REGISTRY_PATH = ROOT / "database" / "security_registry.json"

for folder in (REVIEW_DIR, QUARANTINE_DIR, APPROVED_DIR, REGISTRY_PATH.parent):
    folder.mkdir(parents=True, exist_ok=True)


def _load_registry():
    if not REGISTRY_PATH.exists():
        return {"documents": {}, "approved_hashes": []}
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        data.setdefault("documents", {})
        data.setdefault("approved_hashes", [])
        return data
    except (json.JSONDecodeError, OSError):
        raise RuntimeError(
            "The security registry could not be read. Back it up and repair "
            "database/security_registry.json before continuing."
        )


def _save_registry(registry):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = REGISTRY_PATH.with_suffix(".tmp")
    temp_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    temp_path.replace(REGISTRY_PATH)


def _safe_filename(filename):
    return Path(filename).name.replace("\x00", "") or "uploaded_document.txt"


def _sha256(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


def _approved_policy_conflict(candidate_text):
    """Compare supported policy claims with approved documents for same org."""
    registry = _load_registry()
    for record in registry["documents"].values():
        if record.get("status") != "APPROVED":
            continue
        stored_path = ROOT / Path(record.get("stored_path", "").replace("\\", "/"))
        if not stored_path.is_file():
            continue
        try:
            trusted_text = extract_text(record["filename"], stored_path.read_bytes())
        except Exception:
            continue
        conflicts = compare_policy_claims(
            candidate_text,
            trusted_text,
            candidate_source="new_upload",
            reference_source=record["filename"],
        )
        if conflicts:
            return conflicts[0]
    return None


def inspect_upload(filename, file_bytes):
    """Inspect an upload before it can enter the approved vector collection."""
    filename = _safe_filename(filename)
    digest = _sha256(file_bytes)
    extension = Path(filename).suffix.lower()
    if extension not in {".pdf", ".txt"}:
        raise ValueError("Only PDF and TXT files are supported.")

    text = extract_text(filename, file_bytes)
    analysis = analyze_document(text, source="unverified-upload")
    categories = analysis.get("matched_categories", [])
    # The detector adds 20 points for an unregistered filename. That is a
    # provenance warning, not a content indicator, so remove it here.
    content_risk = max(0, analysis.get("risk_score", 20) - 20)
    findings = [
        item for item in analysis.get("findings", [])
        if "Source is not present" not in item
    ]

    registry = _load_registry()
    previously_approved = digest in registry["approved_hashes"]
    conflict = _approved_policy_conflict(text)

    severe_categories = {"instruction_override"}
    if categories and severe_categories.intersection(categories):
        status = "QUARANTINED"
        findings.append("High-risk instruction-override pattern detected.")
    elif conflict:
        status = "QUARANTINED"
        findings.append(conflict["reason"])
    elif previously_approved:
        status = "APPROVED"
        findings.append("SHA-256 fingerprint matches an administrator-approved document.")
    else:
        status = "REVIEW REQUIRED"
        findings.append("Document identity has not been verified. Administrator approval is required before indexing.")

    if content_risk and not any("Suspicious indicator" in item for item in findings):
        findings.append("Content risk indicators were detected; review before approval.")

    target_dir = {
        "QUARANTINED": QUARANTINE_DIR,
        "REVIEW REQUIRED": REVIEW_DIR,
        "APPROVED": APPROVED_DIR,
    }[status]
    stored_path = target_dir / f"{digest}{extension}"
    if not stored_path.exists():
        stored_path.write_bytes(file_bytes)

    severe_detected = bool(severe_categories.intersection(categories))
    final_risk = max(content_risk, 70) if severe_detected else (max(content_risk + 30, 60) if conflict else content_risk)
    record = {
        "sha256": digest,
        "filename": filename,
        "status": status,
        "risk_score": min(final_risk, 100),
        "risk_level": "High" if final_risk >= 50 else ("Medium" if final_risk >= 20 else "Low"),
        "findings": findings,
        "matched_categories": categories,
        "conflict": conflict,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "stored_path": stored_path.relative_to(ROOT).as_posix(),
        "size_bytes": len(file_bytes),
    }
    registry["documents"][digest] = record
    _save_registry(registry)
    return record


def list_security_records(status=None):
    registry = _load_registry()
    records = list(registry["documents"].values())
    if status:
        records = [item for item in records if item.get("status") == status]
    return sorted(records, key=lambda item: item.get("uploaded_at", ""), reverse=True)


def security_counts():
    records = list_security_records()
    return {
        "approved": sum(item.get("status") == "APPROVED" for item in records),
        "review": sum(item.get("status") == "REVIEW REQUIRED" for item in records),
        "quarantined": sum(item.get("status") == "QUARANTINED" for item in records),
        "total": len(records),
    }


def approve_staged_document(digest):
    """Admin approval for a review item; returns (filename, bytes) for indexing."""
    registry = _load_registry()
    record = registry["documents"].get(digest)
    if not record or record.get("status") != "REVIEW REQUIRED":
        raise ValueError("This document is not awaiting approval.")

    source_path = ROOT / Path(record["stored_path"].replace("\\", "/"))
    if not source_path.is_file():
        raise FileNotFoundError("The staged document file is missing.")

    file_bytes = source_path.read_bytes()
    if _sha256(file_bytes) != digest:
        raise ValueError("Fingerprint mismatch. The staged file may have changed.")

    destination = APPROVED_DIR / source_path.name
    if source_path.resolve() != destination.resolve():
        shutil.move(str(source_path), str(destination))

    record["status"] = "APPROVED"
    record["stored_path"] = destination.relative_to(ROOT).as_posix()
    record["approved_at"] = datetime.now(timezone.utc).isoformat()
    record["findings"].append("Administrator approved this exact SHA-256 fingerprint.")
    if digest not in registry["approved_hashes"]:
        registry["approved_hashes"].append(digest)
    _save_registry(registry)
    return record["filename"], file_bytes


def read_stored_document(record):
    path = ROOT / Path(record["stored_path"].replace("\\", "/"))
    if not path.is_file():
        raise FileNotFoundError("Stored document is missing.")
    return path.read_bytes()


def is_fingerprint_approved(digest):
    """Return true only when this exact SHA-256 is in the local approval registry."""
    registry = _load_registry()
    record = registry["documents"].get(digest, {})
    return digest in registry["approved_hashes"] and record.get("status") == "APPROVED"
