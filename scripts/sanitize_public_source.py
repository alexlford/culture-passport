#!/usr/bin/env python3
"""Remove raw personal booking logistics from public source JSON.

Ordinary wishes, attendance states, venue facts and recognition research remain.
This filter is also usable on historical JSON blobs, but it never rewrites Git
history or changes remote refs. History cleanup requires a separate review.
"""
import argparse
import copy
import json
import re
from pathlib import Path


REMOVED_FIELDS = {
    "reservations", "reservationEvidence", "bookingEvidence",
    "reservationDate", "reservationTime", "bookingTime", "partySize",
    "linkedReservationId", "bookingLeadRecordId", "screenshot", "screenshots",
    "screenshotArchiveNote", "sourceFile", "sourceBatch", "photoEvidenceFilename",
    "sourceAssetNote", "confirmationNumber", "confirmationCode", "bookingReference",
    "reservationConfirmation", "bookingConfirmation", "reservationId", "bookingId",
    "bookingDate", "reservation_date", "reservation_time", "booking_date",
    "booking_time", "party_size", "confirmation_code", "confirmation_number",
}
EVIDENCE_TYPES = {
    "direct_confirmation_of_venue_plus_reservation": "direct_user_confirmation",
    "user_confirmed_venue_and_booking": "direct_user_confirmation",
    "direct_user_confirmation_and_dated_reservation_screenshot": "direct_user_confirmation",
    "direct_user_same_day_photo_and_confirmed_reservation": "direct_user_photo",
}
BOOKING = re.compile(r"\b(?:reservations?|bookings?|resy|tock|opentable)\b", re.I)
LOGISTICS = re.compile(
    r"\b(?:19|20)\d{2}\b|\b\d{1,2}:\d{2}\b|\b\d{1,2}\s*(?:a\.?m\.?|p\.?m\.?)\b|"
    r"\bparty\b|\b(?:guest|diner|people|person|seating|screenshot|confirmation)\b",
    re.I,
)
RAW_REFERENCE = re.compile(
    r"(?:sandbox:/|/mnt/data/|sediment://|file://)|"
    r"\b(?:reservation|booking)[- ](?:screenshot|confirmation)\b|"
    r"\b(?:user[- ](?:supplied|provided|shared)|uploaded|original)\s+"
    r"(?:resy\s+)?screenshots?\b|\bscreenshot[- ](?:derived|sourced|archive)\b",
    re.I,
)
SENTENCES = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
REDACTED_SOURCE = (
    "Personal booking logistics and raw upload references were removed from the public source. "
    "Attendance and visit-date confidence remain recorded independently."
)


def contains_booking_details(text):
    """Identify logistics/provenance, not a generic wishlist or venue mention."""
    return bool(RAW_REFERENCE.search(text) or (BOOKING.search(text) and LOGISTICS.search(text)))


def sanitize_text(text, field):
    # Public venue/reference URLs remain valid; they are not personal bookings.
    if text.startswith(("https://", "http://")):
        return text
    if not contains_booking_details(text):
        return text
    kept = [part for part in SENTENCES.split(text) if not contains_booking_details(part)]
    result = " ".join(kept).strip()
    if result:
        return result
    if field in {"visitPeriod", "visitDateEvidence", "visitSource"}:
        return "Date and attendance confidence are recorded independently of booking evidence."
    return REDACTED_SOURCE


def sanitize_document(path, data):
    """Return a sanitized copy of one data JSON document; never mutate input."""
    path = str(path).replace("\\", "/").lstrip("./")
    if not (path.startswith("data/") or "/data/" in path):
        return copy.deepcopy(data)
    if path.endswith("/reservation-evidence.json"):
        metadata = data if isinstance(data, dict) else {}
        return {
            "version": metadata.get("version", 1),
            "updated": metadata.get("updated"),
            "publicSourceStatus": "sanitized_for_public_source",
            "source": "Raw personal reservation records were removed from the public source.",
            "policy": "A reservation or waitlist entry does not establish attendance or an exact visit date.",
            "entries": [],
            "rows": [],
            "semantics": "Only independent attendance confidence belongs in the public research data; raw booking logistics are not retained here.",
        }

    # The owner explicitly permits the future-places wishlist in source. Its
    # notes describe wishes and nonattendance, not affirmative reservations.
    # Keep that prose intact while still removing any structured booking fields.
    preserve_wishlist_prose = path.endswith("/places-to-go.json")

    def visit(value, field=""):
        if isinstance(value, dict):
            result = {key: visit(child, key) for key, child in value.items()
                      if key not in REMOVED_FIELDS}
            if isinstance(result.get("evidenceType"), str):
                result["evidenceType"] = EVIDENCE_TYPES.get(result["evidenceType"], result["evidenceType"])
            if result.get("attendanceCertainty") == "user_confirmed_visit_date_reservation_correlated":
                result["attendanceCertainty"] = "user_confirmed_visit_date"
            return result
        if isinstance(value, list):
            return [visit(child, field) for child in value]
        if isinstance(value, str):
            return value if preserve_wishlist_prose else sanitize_text(value, field)
        return value

    return visit(data)


def sanitize_json_blob(path, blob):
    """Filter a historical JSON blob without touching Git or the filesystem."""
    try:
        original = json.loads(blob)
    except (ValueError, UnicodeDecodeError):
        return blob
    cleaned = sanitize_document(path, original)
    if cleaned == original:
        return blob
    return (json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write", action="store_true", help="Write sanitized data JSON in the selected checkout")
    args = parser.parse_args()
    changed = []
    for path in sorted((args.root / "data").rglob("*.json")):
        original = path.read_bytes()
        cleaned = sanitize_json_blob(path.relative_to(args.root), original)
        if cleaned != original:
            changed.append(str(path.relative_to(args.root)))
            if args.write:
                path.write_bytes(cleaned)
    print(json.dumps({"changed_files": changed, "written": args.write}))


if __name__ == "__main__":
    main()
