#!/usr/bin/env python3
"""Create a *review-only* visitor preview with no private research ledgers.

This removes research-only records, bookings and interview answer data from the
*generated artifact*. It does not sanitize the source repository, its Git
history, or the human-authored memory stories. A human privacy review remains
mandatory before any public release.
"""
import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from html.parser import HTMLParser
from audit_passport_navigation import audit as audit_passport_navigation

ROOT = Path(__file__).resolve().parents[1]
VISITOR_PAGES = (
    "index.html", "explore.html", "timeline.html", "map.html", "record.html",
)
DIST_FILES = {"favicon.svg", ".nojekyll"}
JS_FILE = "assets/app.js"
CSS_FILE = "assets/site.css"
REDACTED = ("reservations", "recognitionLeads", "curation", "source", "evidenceType",
            "attendanceCertainty", "partySize", "screenshot")
HTML_INTERVIEW_LINK = re.compile(
    r'<a\b(?=[^>]*href="\./(?:interview|performance-interview)\.html")[^>]*>.*?</a>',
    re.IGNORECASE | re.DOTALL
)
INTERVIEW_SECTION = re.compile(
    r'<section class="arts-interview-invite"[^>]*>.*?</section>',
    re.IGNORECASE | re.DOTALL
)


def public_story(record):
    # Curated experiences only: a personal favorite may be included even
    # without a Michelin or James Beard distinction.
    editorial = record.get("editorial") or {}
    if record["status"] == "recollected":
        return editorial.get("userRequestedMemory") is True
    if record["status"] != "confirmed":
        return False
    if record["type"] in {"dining", "bar"}:
        return bool(editorial.get("awardQualified") or editorial.get("pubRecognized") or editorial.get("barRecognized") or editorial.get("breweryRecognized") or editorial.get("heritageFeatured") or editorial.get("featuredException") or editorial.get("officialFeature"))
    return True


def safe_fields(original, names):
    return {k: original[k] for k in names if k in original}


def sanitize_record(record):
    selected = safe_fields(
        record,
        ("id", "type", "title", "venueId", "status", "summary", "sourceUrl",
         "favorite", "story"),
    )
    if record.get("production"):
        # Preserve public theater-program context, not internal date evidence.
        selected["production"] = safe_fields(
            record["production"],
            ("name", "titleConfirmed", "engagementWindow",
             "identificationConfidence", "sourceUrl")
        )
    v = record["visit"]
    selected["visit"] = safe_fields(
        v, ("date", "year", "possibleYears", "label", "precision", "timeWindow")
    )
    if record.get("memory"):
        selected["memory"] = safe_fields(
            record["memory"], ("headline", "teaser", "story", "period")
        )
    if record.get("guide"):
        selected["guide"] = safe_fields(
            record["guide"], ("distinction", "stars", "edition", "sourceUrl", "note")
        )
    if record.get("recognitions"):
        selected["recognitions"] = [
            safe_fields(a, ("organization", "year", "result", "category",
                            "recipient", "relationship", "sourceUrl",
                            "timingRelativeToVisit", "recognitionAtDifferentVenue"))
            for a in record["recognitions"]
            if not a.get("recognitionAtDifferentVenue")
        ]
    selected["editorial"] = safe_fields(
        record.get("editorial", {}), ("awardQualified", "pubRecognized", "barRecognized", "breweryRecognized", "heritageFeatured", "featuredException", "officialFeature", "officialFeatureType", "userRequestedMemory")
    )
    if record.get("officialFeatures"):
        selected["officialFeatures"] = [
            safe_fields(feature, ("organization", "year", "category", "relationship",
                                  "venueScope", "recognitionType", "sourceUrl"))
            for feature in record["officialFeatures"]
            if feature.get("sourceUrl", "").startswith("https://")
        ]
    return selected


def visitor_dataset():
    full = json.loads((ROOT / "data/records.json").read_text(encoding="utf-8"))
    selected = [sanitize_record(r) for r in full["records"] if public_story(r)]
    if not selected:
        raise ValueError("Refusing to build an empty visitor site")
    ids = {r["id"] for r in selected}
    venues_used = {r["venueId"] for r in selected}
    venues = [safe_fields(v, ("id", "name", "city", "region", "country",
                              "neighborhood", "location"))
              for v in full["venues"] if v["id"] in venues_used]
    assert len(ids) == len(selected) and len(venues) == len(venues_used)
    return {"version": 1, "project": "Culture Passport",
            "categories": full["categories"], "venues": venues, "records": selected}


def strip_interview_navigation(html):
    html = INTERVIEW_SECTION.sub("", html)
    html = HTML_INTERVIEW_LINK.sub("", html)
    # Keep noindex in a preview. Explicit publication approval and a launch
    # decision are needed before search indexing is appropriate.
    assert 'content="noindex, nofollow"' in html
    assert not re.search(r'href="\./(?:interview|performance-interview)\.html', html)
    return html


class LinkScanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if a.get(key):
                self.urls.append(a[key])


PRIVATE_FIELD_NAMES = {
    "reservations", "reservationEvidence", "reservationDate", "bookingEvidence",
    "reviewSource", "interviewNote", "interviewAnswers", "screening",
    "userMemoryLead", "partySize", "attendanceCertainty", "evidenceType",
    "exactAttendanceDate", "screenshot", "researchStatus",
    "confirmedVisitSource", "visitSource", "source", "curation"
}


def assert_no_private_fields(value, path="visitor"):
    if isinstance(value, dict):
        for key, child in value.items():
            assert key not in PRIVATE_FIELD_NAMES, (
                f"Private field {path}.{key} reached the public preview"
            )
            assert_no_private_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            assert_no_private_fields(child, f"{path}[{i}]")


def validate_export(output, count):
    audit_passport_navigation(output, VISITOR_PAGES, "culture")
    files = {str(p.relative_to(output)) for p in output.rglob("*") if p.is_file()}
    required = set(VISITOR_PAGES) | DIST_FILES | {
        JS_FILE, CSS_FILE, "data/records.json"
    }
    assert files == required, "Unapproved files in visitor export: " + str(sorted(files ^ required))
    assert "data/interview.json" not in files and "data/reservation-evidence.json" not in files
    data = json.loads((output / "data/records.json").read_text(encoding="utf-8"))
    assert len(data["records"]) == count
    assert_no_private_fields(data)
    assert all(
        r["status"] == "confirmed" or
        (r["status"] == "recollected" and r["editorial"].get("userRequestedMemory") is True)
        for r in data["records"]
    )
    assert all(not any(key in r for key in REDACTED) for r in data["records"])
    assert {r["venueId"] for r in data["records"]} == {v["id"] for v in data["venues"]}
    for p in VISITOR_PAGES:
        scanner = LinkScanner()
        scanner.feed((output / p).read_text(encoding="utf-8"))
        for link in scanner.urls:
            uri = urlsplit(link)
            if uri.scheme in ("http", "https", "mailto", "tel") or link.startswith("//"):
                continue
            if not uri.path:
                continue
            target = (output / uri.path.lstrip("./")).resolve()
            assert target.is_relative_to(output), f"Disallowed path traversal in {p}: {link}"
            assert target.exists(), f"Missing public export link in {p}: {link}"
    assert not (output / "interview.html").exists()
    assert not (output / "performance-interview.html").exists()
    assert all(r["title"] not in {"Le Fou Frog"}
               for r in data["records"])
    return data


def build(output):
    output = output.resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise ValueError("Do not overwrite the source repository")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    public = visitor_dataset()
    (output / "data").mkdir()
    (output / "assets").mkdir()
    for name in VISITOR_PAGES:
        src = (ROOT / name).read_text(encoding="utf-8")
        (output / name).write_text(strip_interview_navigation(src), encoding="utf-8")
    for name in DIST_FILES:
        shutil.copy2(ROOT / name, output / name)
    shutil.copy2(ROOT / CSS_FILE, output / CSS_FILE)
    # Four navigation items in the visitor site: Home, Explore, Timeline, Map.
    with (output / CSS_FILE).open("a", encoding="utf-8") as f:
        f.write("\n@media(max-width:720px){.nav{grid-template-columns:repeat(4,minmax(0,1fr))}}\n")
    js = (ROOT / JS_FILE).read_text(encoding="utf-8")
    js = js.replace('filter==="dining"?"./interview.html":null', 'null')
    (output / JS_FILE).write_text(js, encoding="utf-8")
    (output / "data/records.json").write_text(
        json.dumps(public, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    validate_export(output, len(public["records"]))
    return len(public["records"]), len(public["venues"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Test a disposable preview without writing a persistent artifact")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="culture-visitor-") as temp:
            records, venues = build(Path(temp) / "site")
    else:
        records, venues = build(args.output)
    print(f"Clean visitor export passes: {records} curated experiences, {venues} venues.")
    print("Excluded private research ledgers, raw reservations, interview pages and interview response data.")
    print("Human review of memory/story text and source Git history is still required before publication.")


if __name__ == "__main__":
    main()

