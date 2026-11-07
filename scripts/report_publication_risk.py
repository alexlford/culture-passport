#!/usr/bin/env python3
"""Report public-source and visitor-release counts without printing personal data.

The owner permits public wishlists and research. Raw booking logistics remain
excluded, and website publication still requires its independent story gate.
"""
import json
from pathlib import Path
from audit_public_source import audit as audit_public_source

ROOT=Path(__file__).resolve().parents[1]


def load(filename):
    return json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))


def main():
    checked_files = audit_public_source(ROOT)
    records=load("records.json")["records"]
    interview=load("interview.json")
    performance=load("performance-interview.json")
    reservations=load("reservation-evidence.json")
    review=interview["candidates"]
    reviewed=[c for c in review if c["visitStatus"]!="unreviewed"]
    personal=[r for r in records if r.get("memory")]
    booking=[r for r in records if r.get("reservations")]
    notes=[c for c in review if c.get("interviewNote") or c.get("reviewSource") or c.get("userMemoryLead")]
    print("PUBLIC SOURCE AND VISITOR RELEASE INVENTORY (aggregate counts only)")
    print(f"  Public source datasets checked: {checked_files}")
    print(f"  Cultural record entries: {len(records)}; personal-story fields: {len(personal)}")
    print(f"  Records with reservation metadata: {len(booking)}")
    print(f"  Restaurant research candidates: {len(review)}; reviewed answers: {len(reviewed)}")
    print(f"  Candidates with review notes / personal leads: {len(notes)}")
    print(f"  Performance identification candidates: {len(performance['candidates'])}")
    print(f"  Reservation-source entries: {len(reservations['entries'])}; source rows: {len(reservations['rows'])}")
    print("  Public wishlists/research are allowed; raw booking logistics and detected credentials/contact email are rejected.")
    print("  The visitor export and content-locked story approvals independently control website publication.")
    print("  Current-tree checks do not purge earlier Git history or Actions artifacts.")


if __name__=="__main__":
    main()
