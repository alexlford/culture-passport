#!/usr/bin/env python3
"""Reject raw booking logistics and credentials in the public research source.

Ordinary visits, award research, attendance states and wishlists may remain in
the repository. The website's separate export and publication gate determine
which of those records appear to visitors.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKING_FIELDS = {
    "reservations", "bookingevidence", "bookingtime", "linkedreservationid",
    "reservationdate", "reservationtime", "partysize", "actualpartysize",
    "screenshot", "screenshots", "screenshotreference", "screenshotreferences",
    "screenshotref", "screenshotrefs", "screenshotid", "sourcescreenshotid",
    "screenshotsource", "sourcescreenshot",
}
CREDENTIAL = re.compile(
    r"(?i)(?:sk-[A-Za-z0-9]{18,}|gh[pousr]_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
)
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
BOOKING_CONTEXT = re.compile(r"(?i)\b(?:reservation|booking|booked|resy)\b")
BOOKING_DETAIL = re.compile(
    r"(?i)(?:\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}:\d{2}\b|"
    r"\b\d{1,2}\s*(?:am|pm)\b|\bparty\s+(?:of\s+)?(?:\d+|two|three|four|five|six|seven|eight|nine|ten)\b|"
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b)"
)


def audit_document(value, path="document"):
    """Inspect one parsed JSON value without echoing potentially private values."""
    if isinstance(value, dict):
        for key, item in value.items():
            field = path + "." + key
            normalized = re.sub(r"[^a-z]", "", key.lower())
            if normalized in BOOKING_FIELDS:
                assert item in (None, "", [], {}), "Booking logistics must not be stored: " + field
            audit_document(item, field)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            audit_document(item, f"{path}[{index}]")
    elif isinstance(value, str):
        assert not CREDENTIAL.search(value), "Possible credential material: " + path
        assert not EMAIL.search(value), "Possible personal email address: " + path
        # Raw details can survive inside prose even after structured fields are
        # removed. Generic discussion of reservations remains permitted.
        for sentence in re.split(r"[.!?\n]", value):
            assert not (BOOKING_CONTEXT.search(sentence) and BOOKING_DETAIL.search(sentence)), (
                "Booking logistics in prose must not be stored: " + path)


def audit(root=ROOT):
    files = sorted((root / "data").rglob("*.json"))
    assert files, "No public source datasets found"
    for file in files:
        document = json.loads(file.read_text(encoding="utf-8"))
        audit_document(document, str(file.relative_to(root)))
        if file.name == "reservation-evidence.json":
            assert document["publicSourceStatus"] == "sanitized_for_public_source", "Booking ledger must be a removal notice"
            assert document["entries"] == document["rows"] == [], "Raw booking ledger must stay empty"
    return len(files)


if __name__ == "__main__":
    print(f"Public source passes: {audit()} datasets; no stored booking logistics or detected credentials/contact email.")
