#!/usr/bin/env python3
"""Check story-level publication approvals; prepare a PRIVATE editorial report.

The 48-experience preview is a nonpublic QA fixture, not a release permit.
To approve a story, a reviewer must explicitly update the approval manifest
after reading the complete public record and venue details; the SHA-256
content digest locks that approval to the reviewed text and metadata.

No flag automatically approves records, and this script never deploys.
"""
import argparse
import hashlib
import json
from pathlib import Path

from build_public_preview import visitor_dataset

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "publication-review.json"
REPORT = ROOT / "test-results" / "publication-review.md"
KINDS = ("dining", "bar", "concert", "opera", "theater", "film")


def canonical_digest(record, venue):
    payload = json.dumps({"record": record, "venue": venue}, ensure_ascii=False,
                         sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def state():
    data = visitor_dataset()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1
    records = {r["id"]: r for r in data["records"]}
    venues = {v["id"]: v for v in data["venues"]}
    approvals = manifest["reviewedRecords"]
    ids = [r["id"] for r in approvals]
    assert len(ids) == len(set(ids)), "Duplicate review manifest record IDs"
    assert set(ids) == set(records), "Review manifest must match exactly the current visitor records"
    report_rows = []
    for item in approvals:
        assert set(item) == {"id", "title", "category", "status", "approvedDigest", "reviewedOn"}
        record = records[item["id"]]
        assert item["title"] == record["title"] and item["category"] == record["type"]
        assert item["category"] in KINDS
        assert item["status"] in {"pending", "approved", "withheld"}
        venue = venues[record["venueId"]]
        digest = canonical_digest(record, venue)
        if item["status"] == "approved":
            assert isinstance(item["reviewedOn"], str) and item["reviewedOn"], (
                "Approved record needs a review date: " + item["id"]
            )
            assert item["approvedDigest"] == digest, (
                "Approved record changed since review: " + item["id"]
            )
        else:
            assert item["approvedDigest"] is None and item["reviewedOn"] is None, (
                "Unapproved record should not carry an approval digest: " + item["id"]
            )
        report_rows.append((item, record, venue, digest))
    return report_rows


def report(rows, dest):
    # Reports include the text the visitor would see, so never commit or
    # publish this generated file. GitHub artifact access is repository-bound.
    lines = [
        "# Culture Passport | Private visitor-content review",
        "",
        "**Not approved for public release.** The source repository and this report "
        "are private; do not attach the report to a public issue or website.",
        "",
        "Read every story *as a prospective public visitor*. Check remembered "
        "people/occasions, exact dates, location, venue or performance identity, "
        "historical claims, and linked external sources.",
        "",
        "The excerpt below comes only from the clean visitor dataset, "
        "not from the research/booking/interview ledgers.",
        "",
    ]
    for kind in KINDS:
        members = [(a, r, v, h) for a, r, v, h in rows if r["type"] == kind]
        if not members:
            continue
        lines += [f"## {kind.title()} ({len(members)})", ""]
        for approval, rec, venue, digest in members:
            lines += [
                f"### {rec['title']}",
                "",
                f"- Record: \`{rec['id']}\`",
                f"- Current status: **{approval['status']}**",
                f"- Approximate visit: {rec.get('visit',{}).get('label','Unknown')}",
                f"- Venue: {venue.get('name','Unknown')} — "
                f"{', '.join(str(venue.get(k)) for k in ('city','region','country') if venue.get(k))}",
                f"- Visitor location precision: {venue.get('location',{}).get('precision','not mapped')}",
                "- Locally preview: \`record.html?id=" + rec["id"] + "\`",
                "",
            ]
            for label, txt in [
                ("Summary", rec.get("summary")),
                ("Memory headline", rec.get("memory", {}).get("headline")),
                ("Memory teaser", rec.get("memory", {}).get("teaser")),
                ("Memory story", rec.get("memory", {}).get("story")),
            ]:
                if isinstance(txt, str) and txt.strip():
                    lines += [f"**{label}:** {txt}", ""]
            for text in rec.get("story", {}).get("paragraphs", []):
                lines += [text, ""]
            for ch in rec.get("story", {}).get("chapters", []):
                lines += [
                    f"- Venue history: {ch.get('year','')} — {ch.get('title','')}: "
                    f"{ch.get('detail','')}"
                ]
            if rec.get("story", {}).get("chapters"):
                lines.append("")
            for award in rec.get("recognitions", []):
                lines += [
                    "- Recognition: " +
                    "; ".join(str(award.get(k, "")) for k in
                              ("year", "organization", "category", "recipient", "result")
                              if award.get(k))
                ]
            if rec.get("recognitions"):
                lines.append("")
            links = [rec.get("sourceUrl")] + [
                x.get("url") for x in rec.get("story", {}).get("sourceUrls", [])
            ]
            for url in links:
                if isinstance(url, str) and url.startswith("https://"):
                    lines += ["- Reference: " + url]
            lines += ["", "---", ""]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate review manifest, allow pending")
    parser.add_argument("--report", action="store_true", help="Write private Markdown review report")
    parser.add_argument("--require-approved", action="store_true",
                        help="Block deploy unless every reviewed record is approved and unchanged")
    args = parser.parse_args()
    rows = state()
    counts = {s: sum(a["status"] == s for a, *_ in rows)
              for s in ("pending", "approved", "withheld")}
    if args.report:
        report(rows, REPORT)
        print("Private visitor-text report generated as a protected Actions artifact.")
    print(f"Visitor publication review: {len(rows)} records; "
          f"{counts['approved']} approved, {counts['pending']} pending, "
          f"{counts['withheld']} withheld.")
    if args.require_approved:
        assert not counts["pending"] and not counts["withheld"], (
            "Publication refused: not all proposed public records are approved"
        )
        print("All visitor records have content-locked publication approval.")


if __name__ == "__main__":
    main()
