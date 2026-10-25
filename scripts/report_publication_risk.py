#!/usr/bin/env python3
"""Print a privacy-risk inventory without revealing individual private data.

This is NOT a clearance to change GitHub repository visibility. Git history
may expose content even when the working tree or Pages artifact is sanitized.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(filename):
    return json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))


def main():
    records=load("records.json")["records"]
    interview=load("interview.json")
    performance=load("performance-interview.json")
    reservations=load("reservation-evidence.json")
    review=interview["candidates"]
    reviewed=[c for c in review if c["visitStatus"]!="unreviewed"]
    personal=[r for r in records if r.get("memory")]
    booking=[r for r in records if r.get("reservations")]
    notes=[c for c in review if c.get("interviewNote") or c.get("reviewSource") or c.get("userMemoryLead")]
    print("PRE-PUBLICATION DATA INVENTORY (aggregate counts only)")
    print(f"  Cultural record entries: {len(records)}; personal-story fields: {len(personal)}")
    print(f"  Records with reservation metadata: {len(booking)}")
    print(f"  Restaurant research candidates: {len(review)}; reviewed answers: {len(reviewed)}")
    print(f"  Candidates with review notes / personal leads: {len(notes)}")
    print(f"  Performance identification candidates: {len(performance['candidates'])}")
    print(f"  Reservation-source entries: {len(reservations['entries'])}; source rows: {len(reservations['rows'])}")
    print("  Reminder: changing the GitHub repository to PUBLIC makes its files and Git history accessible.")
    print("  HTML noindex does not protect the source code or published research datasets.")
    print("  No publication is authorized by this report; review the sensitive material and full history first.")
    print("  Consider publishing from a separate, clean distribution repository, keeping source private.")


if __name__=="__main__":
    main()
