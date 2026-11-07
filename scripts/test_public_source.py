#!/usr/bin/env python3
"""Regression checks for public research data versus raw booking evidence."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from audit_public_source import audit, audit_document


class PublicSourcePolicyTests(unittest.TestCase):
    def test_wishlist_research_and_independent_visit_date_are_allowed(self):
        audit_document({
            "visit": {"date": "2026-11-01", "evidenceType": "direct_user_confirmation"},
            "candidate": {"visitStatus": "not_visited", "wantsToVisit": True,
                          "sourceUrl": "https://example.com/venue"},
            "uncertainty": "A reservation is not proof of attendance.",
            "actualPartySize": None,
        })

    def test_nested_booking_logistics_are_rejected_without_echoing_values(self):
        for key, value in (
            ("reservations", [{"date": "2099-01-01"}]),
            ("bookingEvidence", {"note": "not public"}),
            ("partySize", 4), ("reservationDate", "2099-01-01"),
            ("reservationTime", "23:47"), ("bookingTime", "23:47"),
            ("linkedReservationId", "private-source-id"),
            ("screenshotReference", "private-source-image"),
        ):
            with self.subTest(key=key):
                with self.assertRaises(AssertionError) as error:
                    audit_document({"candidates": [{key: value}]})
                self.assertNotIn(str(value), str(error.exception))

    def test_contact_and_credential_values_are_rejected(self):
        for value in ("person@example.com", "ghp_" + "a" * 30,
                      "-----BEGIN PRIVATE KEY-----"):
            with self.subTest(kind=value.split("_")[0]):
                with self.assertRaises(AssertionError) as error:
                    audit_document({"notes": value})
                self.assertNotIn(value, str(error.exception))

    def test_booking_prose_is_checked_without_banning_general_research(self):
        for value in ("A reservation for a party of four.",
                      "A Resy booking at 23:47.",
                      "July 29, 2099 was the separate reservation date."):
            with self.assertRaises(AssertionError) as error:
                audit_document({"sourceNotes": value})
            self.assertNotIn(value, str(error.exception))
        audit_document({"notes": "Reservations are required. Booking alone does not establish attendance."})

    def test_nested_update_files_are_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            updates = root / "data" / "interview-updates"
            updates.mkdir(parents=True)
            (updates / "research.json").write_text(json.dumps({"bookingEvidence": {"date": "2099-01-01"}}))
            with self.assertRaises(AssertionError):
                audit(root)

    def test_removal_notice_does_not_accept_reintroduced_rows(self):
        clean = {"publicSourceStatus": "sanitized_for_public_source", "entries": [], "rows": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            file = root / "data" / "reservation-evidence.json"
            file.write_text(json.dumps(clean))
            self.assertEqual(audit(root), 1)
            changed = copy.deepcopy(clean)
            changed["rows"].append({"name": "Raw source row"})
            file.write_text(json.dumps(changed))
            with self.assertRaises(AssertionError):
                audit(root)


if __name__ == "__main__":
    unittest.main()
