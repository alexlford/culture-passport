#!/usr/bin/env python3
"""Prelaunch, dependency-free checks for Culture Passport's static pages.

This is a source-level smoke test, not a browser visual or public privacy approval.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE_NAMES = (
    "index.html", "explore.html", "timeline.html", "map.html",
    "record.html", "interview.html", "performance-interview.html",
)


class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.heading_count = 0
        self.description_count = 0
        self.robots = []
        self.script_refs = []
        self.stylesheets = []

    def handle_starttag(self, tag, attr_list):
        attrs = dict(attr_list)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, "Duplicate HTML id: " + attrs["id"]
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.heading_count += 1
        if tag == "meta":
            if attrs.get("name") == "description":
                self.description_count += 1
            if attrs.get("name") == "robots":
                self.robots.append(attrs.get("content", ""))
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append((tag, attr, attrs[attr]))
        if tag == "script" and attrs.get("src"):
            self.script_refs.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.append(attrs.get("href", ""))


def audited_records():
    records = json.loads((ROOT / "data/records.json").read_text(encoding="utf-8"))
    assert len({r["id"] for r in records["records"]}) == len(records["records"])
    assert all(r["venueId"] in {v["id"] for v in records["venues"]} for r in records["records"])
    return records["records"]


def audit_pages(records):
    valid_record_ids = {r["id"] for r in records if r["status"] == "confirmed"}
    checked = 0
    for name in PAGE_NAMES:
        page = ROOT / name
        assert page.is_file(), "Missing page: " + name
        parser = AuditParser()
        parser.feed(page.read_text(encoding="utf-8"))
        assert parser.heading_count == (0 if name == "record.html" else 1), (
            f"{name}: unexpected static h1 count {parser.heading_count}; record.html injects its heading from JS"
        )
        assert parser.description_count == 1, f"{name}: expected one meta description"
        assert "main" in parser.ids, f"{name}: missing main landmark id"
        assert any(url == "#main" for _, _, url in parser.links), (
            f"{name}: missing keyboard skip-to-content link"
        )
        assert parser.robots == ["noindex, nofollow"], f"{name}: expected staging noindex metadata"
        assert parser.stylesheets, f"{name}: missing site stylesheet"
        for tag, attr, url in parser.links:
            u = urlsplit(url)
            if u.scheme in ("https", "http", "mailto", "tel") or url.startswith("//"):
                continue
            assert not u.scheme and not u.netloc, f"{name}: unexpected URL scheme: {url}"
            path = unquote(u.path)
            if path:
                target = (page.parent / path).resolve()
                assert target.is_relative_to(ROOT), f"{name}: link escapes site root: {url}"
                assert target.is_file(), f"{name}: broken local {attr}: {url}"
            if u.fragment:
                # Only same-page fragments can be checked statically.
                target_page = page if not path else target
                if target_page.suffix == ".html":
                    other = AuditParser()
                    other.feed(target_page.read_text(encoding="utf-8"))
                    assert u.fragment in other.ids, f"{name}: missing local anchor {url}"
            if path == "./record.html" or path == "record.html":
                from urllib.parse import parse_qs
                ids = parse_qs(u.query).get("id", [])
                if ids:
                    assert len(ids) == 1 and ids[0] in valid_record_ids, f"{name}: invalid experience deep link {url}"
            checked += 1
        if name == "map.html":
            assert "map-category" in parser.ids and "map-summary" in parser.ids
            assert "city-list" in parser.ids
        if name == "map.html":
            js = next((i for i, x in enumerate(parser.script_refs) if "leaflet.js" in x), None)
            app = next((i for i, x in enumerate(parser.script_refs) if "assets/app.js" in x), None)
            assert js is not None and app is not None and js < app, "Leaflet must load before the map app"
        else:
            assert all("leaflet" not in x for x in parser.script_refs), f"{name}: Leaflet loaded unnecessarily"
    return checked


def audit_dynamic_data():
    # These fetches are used by the static app and are not ordinary HTML links.
    fetches = {
        "assets/app.js": ["data/records.json", "data/interview.json"],
        "assets/performance-interview.js": ["data/performance-interview.json"],
    }
    for source, paths in fetches.items():
        body = (ROOT / source).read_text(encoding="utf-8")
        for path in paths:
            assert (ROOT / path).is_file(), "Missing client-side dataset " + path
            assert "./" + path in body, source + " does not request " + path


def audit_basic_secrets():
    # This does NOT certify the repository or its Git history for publication.
    # Before changing private -> public, review personal stories, interview
    # responses, reservation source rows, and commit history explicitly.
    for f in (ROOT / "data").glob("*.json"):
        raw = f.read_text(encoding="utf-8")
        assert not re.search(r"(?i)(?:sk-[A-Za-z0-9]{18,}|gh[pousr]_[A-Za-z0-9_]{20,}|-----BEGIN PRIVATE KEY-----)", raw), (
            f.name + ": possible credential material")
        assert not re.search(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", raw), (
            f.name + ": possible personal email address")


def audit_editorial_and_city_links(records):
    script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
    assert "r.story?.paragraphs?.length" in script
    assert "r.story.chapters?.length" in script
    assert "storyPeriod(r)" in script
    assert "new URLSearchParams(location.search).get(\"city\")" in script
    assert 'const initialCity=params.get("city")' in script
    assert 'details.open=true' in script
    assert 'maxZoom:9' in script or 'maxZoom: 9' in script
    assert any(r.get("story", {}).get("paragraphs") for r in records)


def audit_release_approval_gate():
    workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
    assert "privacy_review_approved:" in workflow
    assert "default: false" in workflow
    assert "inputs.privacy_review_approved == true" in workflow
    assert "scripts/build_public_preview.py" in workflow
    assert "path: dist" in workflow


def audit_responsive_styles():
    styles = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    for selector in (".skip-link:focus", "@media(max-width:720px)", "safe-area-inset-bottom",
                     "grid-template-columns:repeat(5,minmax(0,1fr))", ".filter-row input"):
        assert selector in styles, "Mobile/accessibility rule missing: " + selector


def main():
    records = audited_records()
    links = audit_pages(records)
    audit_dynamic_data()
    audit_responsive_styles()
    audit_editorial_and_city_links(records)
    audit_release_approval_gate()
    audit_basic_secrets()
    print(f"OK: {len(PAGE_NAMES)} static pages, {links} links/assets, {len(records)} archive records;")
    print("staging metadata and local deep links checked. Privacy approval and visual QA remain open.")


if __name__ == "__main__":
    main()
