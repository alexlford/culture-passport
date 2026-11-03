#!/usr/bin/env python3
"""Validate Culture Passport records, historical interview states, and pages."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
records_data = json.loads((ROOT / "data/records.json").read_text(encoding="utf-8"))
interview_data = json.loads((ROOT / "data/interview.json").read_text(encoding="utf-8"))
records, venues = records_data["records"], records_data["venues"]
candidates = interview_data["candidates"]
assert records_data["project"] == "Culture Passport" and records_data["version"] == 1
assert len(records) >= 62 and len(venues) >= 60  # allow newly confirmed memories
assert len({r["id"] for r in records}) == len(records)
assert len({v["id"] for v in venues}) == len(venues)
types = {"dining", "bar", "concert", "opera", "theater", "film"}
assert {c["id"] for c in records_data["categories"]} == types
venue_ids = {v["id"] for v in venues}
assert all(r["status"] in {"confirmed", "recollected", "reservation_only"} and r["type"] in types for r in records)
assert len([r for r in records if r["status"] == "confirmed"]) >= 58
assert not any(r["status"] == "reservation_only" for r in records)  # both reservation leads now have separately confirmed venue visits
assert all(r["visit"]["date"] is None and r["reservations"] for r in records if r["status"] == "reservation_only")
assert all(r["venueId"] in venue_ids and r["visit"]["source"] for r in records)
assert all(r["visit"].get("date") is None or r["visit"]["precision"] == "day" for r in records)
assert all(v["location"] is None or v["location"]["precision"] == "city-centroid" for v in venues)
assert all(v["location"] is None or (-90 <= v["location"]["lat"] <= 90 and -180 <= v["location"]["lng"] <= 180) for v in venues)
stars = [r for r in records if r.get("guide") and r["guide"]["distinction"] == "starred"]
assert len(stars) >= 2 and all(1 <= r["guide"]["stars"] <= 3 for r in stars)
assert all(r["guide"]["stars"] == 0 for r in records if r.get("guide") and r["guide"]["distinction"] != "starred")
assert {"Minetta Tavern", "Beckon", "Charleston", "Woodberry Kitchen",
        "Momofuku CCDC", "République", "Sauvage", "Gunther & Co.",
        "Thames Street Oyster House"}.issubset({r["title"] for r in records})
assert len(candidates) >= 180
assert len({c["id"] for c in candidates}) == len(candidates)
assert len({(c["area"].casefold(), c["name"].casefold()) for c in candidates}) == len(candidates)
for candidate in candidates:
    assert isinstance(candidate.get("sourceUrl"), str) and candidate["sourceUrl"].startswith("https://"), (
        "Candidate requires an HTTPS venue source", candidate["id"])
assert all(c["visitStatus"] in {"confirmed", "not_visited", "maybe", "unreviewed"} for c in candidates)
# Explicit historical wishlist does not establish attendance, even when venue closed.
justus = next(c for c in candidates if c["id"] == "candidate-kc-justus-drugstore-smithville")
assert justus["visitStatus"] == "not_visited" and justus["wantsToVisit"] is True
assert justus["venueStatus"] == "permanently_closed_original"
wishlist = json.loads((ROOT / "data/places-to-go.json").read_text(encoding="utf-8"))
justus_wish = next(x for x in wishlist["entries"] if x["candidateId"] == justus["id"])
assert justus_wish["visitStatus"] == "not_visited" and justus_wish["status"] == "want_to_visit"
assert justus_wish["bookable"] is False
assert not any(r["title"] == "Justus Drugstore" for r in records)
# The queue must point to real, still-unanswered candidates as the interview advances.
current_names = interview_data["interviewProgress"]["currentBatch"]["candidateNames"]
assert current_names
assert all(any(c["name"] == name and (
                    c["visitStatus"] in {"unreviewed", "maybe"} or (
                        c["visitStatus"] == "not_visited"
                        and c.get("reviewCertainty") == "tentative_negative"
                        and interview_data["interviewProgress"]["currentBatch"]["status"].startswith("awaiting_reconfirmation")
                    ))
               for c in candidates) for name in current_names)
yoli = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-yoli-tortilleria")
assert yoli["visitStatus"] == "not_visited" and yoli["wantsToVisit"] is True
assert yoli["wishlistEntryId"] == "want-to-visit-yoli-tortilleria-westside-kansas-city"
yoli_wish = next(e for e in wishlist["entries"] if e["candidateId"] == yoli["id"])
assert yoli_wish["visitStatus"] == "not_visited" and yoli_wish["status"] == "want_to_visit"
assert yoli_wish["category"] == "bakery"
assert yoli_wish["location"]["address"] == "1668 Jefferson Street"
assert not any(r["title"] == "Yoli Tortilleria" for r in records)
wild = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-wild-child")
assert wild["visitStatus"] == "not_visited" and wild["wantsToVisit"] is True
assert wild["wishlistEntryId"] == "want-to-visit-wild-child-shawnee"
wild_wish = next(e for e in wishlist["entries"] if e["candidateId"] == wild["id"])
assert wild_wish["visitStatus"] == "not_visited" and wild_wish["status"] == "want_to_visit"
assert wild_wish["category"] == "bar"
assert not any(r["title"] == "Wild Child" for r in records)
fern = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-fern-bar")
assert fern["visitStatus"] == "not_visited" and fern["wantsToVisit"] is True
assert fern["wishlistEntryId"] == "want-to-visit-fern-bar-kansas-city"
fern_wish = next(e for e in wishlist["entries"] if e["candidateId"] == fern["id"])
assert fern_wish["visitStatus"] == "not_visited" and fern_wish["status"] == "want_to_visit"
assert fern_wish["category"] == "bar"
assert not any(r["title"] == "Fern Bar" for r in records)
# Preserve explicit attendance and future-interest answers from the KC list interview.
kc_wishlist_ids = {
    "candidate-kc-anjin-crossroads", "candidate-kc-the-campground",
    "candidate-kc-jjs-restaurant", "candidate-kc-green-dirt-on-oak",
}
for cid in kc_wishlist_ids:
    assert next(c for c in candidates if c["id"] == cid)["visitStatus"] == "not_visited"
    wish = next(e for e in wishlist["entries"] if e["candidateId"] == cid)
    assert wish["visitStatus"] == "not_visited" and wish["status"] == "want_to_visit"
for cid in ("candidate-kc-acre-parkville", "candidate-kc-the-belfry"):
    assert next(c for c in candidates if c["id"] == cid)["visitStatus"] == "not_visited"
    assert not any(e["candidateId"] == cid for e in wishlist["entries"])
for cid in ("candidate-kansas-city-metro-lidia-s-kansas-city", "candidate-kc-rozzelle-court"):
    assert next(c for c in candidates if c["id"] == cid)["visitStatus"] == "confirmed"
monarch = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-the-monarch-bar")
assert monarch["visitStatus"] == "not_visited" and monarch["wantsToVisit"] is True
assert monarch["wishlistEntryId"] == "want-to-visit-the-monarch-bar-kansas-city"
monarch_wish = next(e for e in wishlist["entries"] if e["candidateId"] == monarch["id"])
assert monarch_wish["visitStatus"] == "not_visited" and monarch_wish["status"] == "want_to_visit"
assert monarch_wish["category"] == "bar"
assert not any(r["title"] == "The Monarch Bar" for r in records)

# Novel has two historically different addresses; wishlisting the operating site never implies attendance.
novel_original = next(c for c in candidates if c["id"] == "candidate-kc-novel-original-westside")
novel_current = next(c for c in candidates if c["id"] == "candidate-kc-novel-east-crossroads")
assert novel_original["visitStatus"] == novel_current["visitStatus"] == "not_visited"
assert novel_original["operatingStatus"] == "closed_at_this_address"
assert novel_original["wantsToVisit"] is False
assert novel_current["wantsToVisit"] is True
assert novel_current["screening"]["status"] == "cultural_architecture_qualified"
assert novel_current["wishlistEntryId"] == "want-to-visit-novel-east-crossroads"
novel_wish = next(e for e in wishlist["entries"] if e["candidateId"] == novel_current["id"])
assert novel_wish["status"] == "want_to_visit" and novel_wish["visitStatus"] == "not_visited"
assert novel_wish["location"]["address"] == "1927 McGee Street"
assert novel_wish["recognition"]["organization"] == "AIA Kansas City"
assert not any(e["candidateId"] == novel_original["id"] for e in wishlist["entries"])
assert not any(r["title"] == "Novel Restaurant" for r in records)
assert len({e["id"] for e in wishlist["entries"]}) == len(wishlist["entries"])
# Next historical question must remain unresolved; do not ascribe another restaurant's awards.
michael_smith = next(c for c in candidates if c["id"] == "candidate-kc-michael-smith-restaurant-crossroads")
assert michael_smith["visitStatus"] == "not_visited"
assert michael_smith["wantsToVisit"] is False
assert michael_smith["wishlistDecision"] == "explicit_no"
assert not any(e["candidateId"] == michael_smith["id"] for e in wishlist["entries"])
assert michael_smith["screening"]["status"] == "award_qualified"
assert interview_data["interviewProgress"]["currentBatch"]["candidateNames"] == ["Chewology"]
rye_plaza = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-rye-plaza")
assert rye_plaza["visitStatus"] == "confirmed"
assert rye_plaza["confirmedVisitId"] == "dining-rye-plaza-kansas-city-date-unknown"
rye_visit = next(r for r in records if r["id"] == rye_plaza["confirmedVisitId"])
assert rye_visit["status"] == "confirmed" and rye_visit["type"] == "dining"
assert rye_visit["venueId"] == "venue-rye-plaza-kansas-city"
assert rye_visit["visit"]["date"] is None and rye_visit["visit"]["precision"] == "unknown"
assert rye_visit["editorial"]["awardQualified"] is True
assert rye_visit["recognitions"] and rye_visit["curation"]["verifiedForPublication"] is False
assert not any(r["title"] == "Rye (Leawood)" and r["status"] == "confirmed" for r in records)
assert "Leawood" in rye_visit["guide"]["note"] and "Bluestem" in rye_visit["guide"]["note"]
assert rye_plaza["eligibility"]["verifiedForPublication"] is False
assert rye_plaza["screening"]["status"] == "award_qualified_metro_brand_aggregation"
assert len(rye_plaza["photographicEvidence"]) == 2
assert all(e["imageRights"] == "unverified" and e["renderMode"] == "source_link_only"
           and e["sourceUrl"].startswith("https://") for e in rye_plaza["photographicEvidence"])
assert "Leawood" in rye_plaza["recognition"] and "Bluestem" in rye_plaza["recognition"]
assert michael_smith["screening"]["evidenceUrl"].startswith("https://archive.jamesbeard.org/")

# Keep the user-requested fourth answer visible on every venue interview.
button_policy = interview_data["interviewProgress"]["answerButtonPolicy"]
assert button_policy["alwaysShowFourOptions"] is True
assert [x["id"] for x in button_policy["choices"]] == [
    "visited", "maybe", "not_visited", "want_to_visit"
]
assert button_policy["choices"][3]["label"] == "No, but want to go"
assert 'want_to_visit:"No, but want to go"' in (
    ROOT / "assets/app.js").read_text(encoding="utf-8")
assert "closed/unbookable" in button_policy["closedVenueSemantics"]

# Historically accurate photo cues must be source-linked and never rehost unlicensed images.
photo_subject = next(c for c in candidates if c["id"] == "candidate-kc-michael-smith-restaurant-crossroads")
photos = photo_subject["photographicEvidence"]
assert len(photos) == 2
assert {x["id"] for x in photos} == {"historic-building-exterior", "2016-chef-portrait"}
assert all(x["sourceUrl"].startswith("https://") and x["renderMode"] == "source_link_only"
           and x["imageRights"] == "unverified" and x["caption"] for x in photos)
assert interview_data["interviewProgress"]["photoEvidencePolicy"]["showPerVenue"] is True
assert "interview-photo-evidence" in (ROOT / "assets/app.js").read_text(encoding="utf-8")

# Two distinct Hawaii regions are queued, and no attendance is inferred from queueing.
hilo = interview_data["interviewChapters"]["hiloHawaii"]
maui = interview_data["interviewChapters"]["mauiHawaii"]
assert hilo["status"] == maui["status"] == "queued_unreviewed"
assert hilo["visitClaimsEstablished"] == maui["visitClaimsEstablished"] == 0
assert hilo["visitYears"] is None and maui["visitYears"] is None
sequence = [row["area"] for row in interview_data["interviewProgress"]["nextCitySequence"]]
assert sequence[-3:] == ["Baltimore", "Hilo, Hawaiʻi Island", "Maui, Hawaiʻi"]
for chapter in (hilo, maui):
    assert chapter["responseChoices"] == [
        "Yes, I visited", "Maybe — looks familiar", "No, haven't been", "No, but want to go"]
    assert chapter["candidateIds"]
    assert all(next(c for c in candidates if c["id"] == cid)["visitStatus"] == "unreviewed"
               for cid in chapter["candidateIds"])
for cid in ["candidate-hilo-lehua-at-imiloa", "candidate-maui-tiffanys-wailuku",
            "candidate-maui-sale-pepe-lahaina"]:
    lead = next(c for c in candidates if c["id"] == cid)
    assert lead["screening"]["evidenceUrl"].startswith("https://www.jamesbeard.org/")
    assert lead["photographicEvidence"] and all(
        photo["renderMode"] == "source_link_only" and photo["imageRights"] == "unverified"
        for photo in lead["photographicEvidence"])
assert next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-bluestem")["visitStatus"] == "maybe"
assert next(x for x in wishlist["entries"] if x["candidateId"] == "candidate-kc-novel-east-crossroads")["visitStatus"] == "not_visited"

# Extra Virgin is explicitly NOT visited but is separately wanted; no awards transfer.
extra_virgin = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-extra-virgin")
assert extra_virgin["visitStatus"] == "not_visited" and extra_virgin["wantsToVisit"] is True
assert extra_virgin["wishlistEntryId"] == "want-to-visit-extra-virgin-kansas-city"
extra_wish = next(e for e in wishlist["entries"] if e["candidateId"] == extra_virgin["id"])
assert extra_wish["id"] == extra_virgin["wishlistEntryId"]
assert extra_wish["visitStatus"] == "not_visited" and extra_wish["status"] == "want_to_visit"
assert extra_wish["location"]["address"] == "1900 Main Street"
assert extra_wish["website"] == "https://www.extravirginkc.com/"
assert not any(r["title"] == "Extra Virgin" and r["status"] == "confirmed" for r in records)
# Farina is the next candidate with its OWN DiRoNA award, not Michael Smith's Beard prize.
farina = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-farina")
assert farina["visitStatus"] == "not_visited" and farina["wantsToVisit"] is True
assert farina["wishlistEntryId"] == "want-to-visit-farina-kansas-city"
farina_wish = next(e for e in wishlist["entries"] if e["candidateId"] == farina["id"])
assert farina_wish["id"] == "want-to-visit-farina-kansas-city"
assert farina_wish["visitStatus"] == "not_visited" and farina_wish["status"] == "want_to_visit"
assert farina_wish["location"]["address"] == "19 West 19th Street"
assert farina_wish["recognition"]["organization"] == "Distinguished Restaurants of North America (DiRōNA)"
assert farina_wish["recognition"]["sourceUrl"].startswith("https://dirona.com/")
assert farina["screening"]["status"] == "distinct_hospitality_award_verified"
assert farina["screening"]["basis"] == "dirona_award_of_excellence_exact_restaurant"
assert farina["awardFamily"] == "dirona"
assert farina["eligibility"]["verifiedForPublication"] is False
assert "not a James Beard or Michelin honor" in farina["recognition"]
assert len(farina["photographicEvidence"]) == 2
assert all(p["renderMode"] == "source_link_only" and p["imageRights"] == "unverified"
           for p in farina["photographicEvidence"])
assert interview_data["interviewProgress"]["currentBatch"]["candidateNames"] == ["Chewology"]
assert not any(r["title"] == "Farina" and r["status"] == "confirmed" for r in records)

# Lawrence bar: attendance is firsthand; its 2025 honor is venue-level and only a semifinalist.
jbu = next(x for x in candidates if x["id"] == "candidate-lawrence-john-browns-underground")
assert jbu["visitStatus"] == "confirmed"
assert jbu["confirmedVisitId"] == "bar-john-browns-underground-lawrence-date-unknown"
jbu_visit = next(r for r in records if r["id"] == jbu["confirmedVisitId"])
assert jbu_visit["type"] == "bar" and jbu_visit["status"] == "confirmed"
assert jbu_visit["venueId"] == "venue-john-browns-underground-lawrence"
assert jbu_visit["visit"]["date"] is None and jbu_visit["visit"]["precision"] == "unknown"
assert jbu_visit["editorial"]["awardQualified"] is True
assert len(jbu_visit["recognitions"]) == 1
assert jbu_visit["recognitions"][0]["category"] == "Outstanding Bar"
assert jbu_visit["recognitions"][0]["year"] == 2025
assert jbu_visit["recognitions"][0]["result"] == "semifinalist"
assert jbu_visit["curation"]["verifiedForPublication"] is False
story_candidate = next(x for x in candidates if x["id"] == "candidate-kc-story-prairie-village")
assert story_candidate["name"] == "Story."
assert story_candidate["visitStatus"] == "not_visited"
assert story_candidate["reviewCertainty"] == "explicit_nonattendance"
assert story_candidate["historicalInterest"] is True
assert story_candidate["wishlistStatus"] == "historical_interest_only_closed"
assert story_candidate["wantsToVisit"] is False
assert story_candidate["operatingStatus"] == "permanently_closed"
assert story_candidate["screening"]["status"] == "award_qualified"
assert "Carl Thorne-Thomsen" in story_candidate["recognition"]
assert not any(r["venueId"] == "venue-story-prairie-village" and r["status"] == "confirmed" for r in records)
assert not any(w["candidateId"] == story_candidate["id"] for w in wishlist["entries"])
barker = next(c for c in candidates if c["id"] == "candidate-lawrence-1900-barker-original")
assert barker["visitStatus"] == "confirmed"
assert barker["confirmedVisitId"] == "dining-1900-barker-original-lawrence-date-unknown"
assert barker["reviewCertainty"] == "explicit_confirmed"
assert barker["addressHint"] == "1900 Barker Avenue, Lawrence, KS 66046"
assert barker["screening"]["status"] == "award_qualified"
assert "Outstanding Baker semifinalist in 2018, 2019 and 2020" in barker["recognition"]
assert barker["openedOn"] == "2015-06"
assert len(barker["photographicEvidence"]) == 2
assert all(photo["renderMode"] == "source_link_only" for photo in barker["photographicEvidence"])
assert not any(w["candidateId"] == barker["id"] for w in wishlist["entries"])
barker_visit = next(r for r in records if r["id"] == barker["confirmedVisitId"])
assert barker_visit["status"] == "confirmed" and barker_visit["type"] == "dining"
assert barker_visit["venueId"] == "venue-1900-barker-original-lawrence"
assert barker_visit["visit"]["date"] is None and barker_visit["visit"]["precision"] == "unknown"
assert barker_visit["visit"]["orders"] is None
assert barker_visit["editorial"]["awardQualified"] is True
assert {x["year"] for x in barker_visit["recognitions"] if x["result"] == "semifinalist" and x["category"] == "Outstanding Baker"} == {2018,2019,2020}
assert barker_visit["curation"]["verifiedForPublication"] is False
assert any(a["id"] == barker_visit["id"] and a["status"] == "pending" for a in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"])
freshwater = next(c for c in candidates if c["id"] == "candidate-kc-freshwater-fine-dining-2017-2020")
assert freshwater["visitStatus"] == "not_visited"
assert freshwater["reviewCertainty"] == "explicit_nonattendance"
assert freshwater["historicalInterest"] is True
assert freshwater["wantsToVisit"] is False
assert freshwater["wishlistStatus"] == "historical_interest_only_closed"
assert freshwater["operatingStatus"] == "permanently_closed"
assert freshwater["addressHint"].startswith("3711 Southwest Trafficway")
assert freshwater["screening"]["status"] == "award_qualified"
assert freshwater["recognitionYear"] == 2019
assert len(freshwater["photographicEvidence"]) == 2
assert all(x["renderMode"] == "source_link_only" for x in freshwater["photographicEvidence"])
assert not any(x["candidateId"] == freshwater["id"] for x in wishlist["entries"])
assert not any(r["title"] == freshwater["name"] and r["status"] == "confirmed" for r in records)
american = next(x for x in candidates if x["id"] == "candidate-kansas-city-metro-the-american-restaurant")
assert american["visitStatus"] == "not_visited" and american["reviewCertainty"] == "explicit_nonattendance"
assert american["historicalInterest"] is True
assert american["wantsToVisit"] is False
assert american["wishlistStatus"] == "historical_interest_only_original_dining_closed"
assert american["reconfirmationResolvedOn"] == "2026-11-03"
assert not any(w["candidateId"] == american["id"] for w in wishlist["entries"])
assert american["reconfirmationRequestedOn"] == "2026-11-03"
assert american["regularDiningEndedOn"] == "2016-12"
assert american["screening"]["basis"] == "james_beard_2018_design_icon_exact_venue_winner"
assert "Design Icon Award WINNER" in american["recognition"]
assert american["sourceUrl"].startswith("https://www.jamesbeard.org/")
assert len(american["photographicEvidence"]) == 2
assert all(p["renderMode"] == "source_link_only" for p in american["photographicEvidence"])
assert not any(r["title"] == american["name"] and r["status"] == "confirmed" for r in records)
corvino = next(x for x in candidates if x["id"] == "candidate-kansas-city-metro-corvino-supper-club-tasting-room")
assert corvino["visitStatus"] == "not_visited" and corvino["reviewCertainty"] == "explicit_nonattendance"
assert corvino["historicalInterest"] is True
assert corvino["wantsToVisit"] is False
assert corvino["wishlistStatus"] == "historical_interest_only_closed"
assert corvino["reconfirmationResolvedOn"] == "2026-11-03"
assert not any(w["candidateId"] == corvino["id"] for w in wishlist["entries"])
assert corvino["reconfirmationRequestedOn"] == "2026-11-03"
assert corvino["closedOn"] == "2025-12-31"
assert corvino["operatingStatus"] == "permanently_closed"
assert corvino["screening"]["basis"] == "james_beard_2019_2023_best_chef_midwest_semifinalist_at_exact_venue"
assert "2019 and 2023" in corvino["recognition"]
assert len(corvino["photographicEvidence"]) == 2
assert all(p["renderMode"] == "source_link_only" and p["imageRights"] == "unverified" for p in corvino["photographicEvidence"])
assert not any(w["candidateId"] == corvino["id"] for w in wishlist["entries"])
assert not any(r["title"] == corvino["name"] and r["status"] == "confirmed" for r in records)
fox = next(x for x in candidates if x["id"] == "candidate-kansas-city-metro-fox-pearl")
assert fox["name"] == "Fox & Pearl"
assert fox["visitStatus"] == "not_visited" and fox["reviewCertainty"] == "explicit_nonvisit_with_wishlist_intent"
assert fox["wantsToVisit"] is True
assert fox["wishlistEntryId"] == "want-to-visit-fox-pearl-2143-summit-kansas-city"
fox_wish = next(w for w in wishlist["entries"] if w["candidateId"] == fox["id"])
assert fox_wish["id"] == fox["wishlistEntryId"]
assert fox_wish["location"]["address"] == "2143 Summit Street"
assert fox_wish["location"]["city"] == "Kansas City"
assert fox_wish["visitStatus"] == "not_visited" and fox_wish["status"] == "want_to_visit"
assert fox_wish["recognition"]["recipient"] == "Vaughn Good"
assert fox_wish["recognition"]["year"] == 2020
assert fox_wish["recognition"]["result"] == "semifinalist"
assert not any(r["venueId"] == "venue-fox-pearl-summit-kansas-city" and r["status"] == "confirmed" for r in records)
assert fox["reconfirmationRequestedOn"] == "2026-11-03"
assert fox["operatingStatus"] == "operating"
assert fox["addressHint"] == "2143 Summit Street, Kansas City, MO 64108"
assert fox["screening"]["status"] == "award_qualified"
assert fox["recognitionYear"] == 2020
assert fox["sourceUrl"].startswith("https://www.jamesbeard.org/")
assert len(fox["photographicEvidence"]) == 2
assert all(p["renderMode"] == "source_link_only" for p in fox["photographicEvidence"])
assert not any(r["title"] == fox["name"] and r["status"] == "confirmed" for r in records)
assert sum(w["id"] == fox["wishlistEntryId"] for w in wishlist["entries"]) == 1
fox_alias = next(x for x in candidates if x["id"] == "candidate-kansas-city-metro-fox-and-pearl")
assert fox_alias["visitStatus"] == "not_visited" and fox_alias["reviewCertainty"] == "explicit_nonvisit_with_wishlist_intent"
assert fox_alias["canonicalCandidateId"] == fox["id"]
assert fox_alias["wishlistEntryId"] == fox["wishlistEntryId"]
assert not any(w["candidateId"] == fox_alias["id"] for w in wishlist["entries"])
town = next(x for x in candidates if x["id"] == "candidate-kansas-city-metro-the-town-company")
assert town["name"] == "The Town Company"
assert town["addressHint"].startswith("1228 Baltimore Avenue")
assert town["visitStatus"] == "not_visited" and town["reviewCertainty"] == "explicit_nonvisit_with_wishlist_intent"
assert town["reviewedOn"] == town["reconfirmationResolvedOn"] == "2026-11-03"
assert town["wantsToVisit"] is True
assert town["wishlistEntryId"] == "want-to-visit-the-town-company-hotel-kansas-city"
assert town["screening"]["status"] == "award_qualified"
assert town["recognitionYear"] == 2026
assert "Helen Jo Leach" in town["recognition"] and "Johnny Leach" in town["recognition"]
assert len(town["photographicEvidence"]) == 2
assert all(p["renderMode"] == "source_link_only" for p in town["photographicEvidence"])
town_wish = next(w for w in wishlist["entries"] if w["candidateId"] == town["id"])
assert town_wish["id"] == town["wishlistEntryId"]
assert town_wish["status"] == "want_to_visit" and town_wish["visitStatus"] == "not_visited"
assert town_wish["location"]["address"] == "1228 Baltimore Avenue"
assert town_wish["location"]["postalCode"] == "64105"
assert town_wish["location"]["venue"] == "Hotel Kansas City"
assert town_wish["desiredVisitDate"] is None
assert len(town_wish["recognitions"]) == len(town["recognitions"]) == 2
assert {r["recipient"] for r in town_wish["recognitions"]} == {"Johnny Leach", "Helen Jo Leach"}
assert {(r["recipient"], r["category"]) for r in town_wish["recognitions"]} == {
    ("Johnny Leach", "Best Chef: Midwest"),
    ("Helen Jo Leach", "Outstanding Pastry Chef or Baker"),
}
assert all(r["organization"] == "James Beard Foundation" and r["year"] == 2026
           and r["result"] == "semifinalist" and "jamesbeard.org" in r["sourceUrl"]
           and "not restaurant-level award or win" in r["relationship"]
           for r in town_wish["recognitions"])
assert not any(r["title"] == town["name"] and r["status"] == "confirmed" for r in records)
# Room 39 is one metro-brand wish, not a confirmed meal or multiple branch wishes.
room_39 = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-room-39")
assert room_39["visitStatus"] == "not_visited"
assert room_39["reviewCertainty"] == "explicit_nonvisit_with_wishlist_intent"
assert room_39["wantsToVisit"] is True
assert room_39["reviewedOn"] == "2026-11-03"
assert room_39["wishlistEntryId"] == "want-to-visit-room-39-kansas-city-metro"
assert room_39["metroExperienceGroupId"] == "room-39-kansas-city-metro"
room_wishes = [e for e in wishlist["entries"] if e["candidateId"] == room_39["id"]]
assert len(room_wishes) == 1
assert room_wishes[0]["id"] == room_39["wishlistEntryId"]
assert room_wishes[0]["status"] == "want_to_visit" and room_wishes[0]["visitStatus"] == "not_visited"
assert len(room_wishes[0]["recognitions"]) == 3
assert {x["year"] for x in room_wishes[0]["recognitions"]} == {2008, 2012, 2014}
assert all(x["recipient"] == "Ted Habiger" and x["result"] == "semifinalist"
           for x in room_wishes[0]["recognitions"])
assert not any(r["title"].startswith("Room 39") and r["status"] == "confirmed" for r in records)
waldo = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-waldo-thai")
assert waldo["visitStatus"] == "not_visited" and waldo["reviewCertainty"] == "explicit_nonattendance"
assert waldo["operatingStatus"] == "permanently_closed" and waldo["closedOn"] == "2025-10-03"
assert waldo["addressHint"].startswith("8431 Wornall Road")
assert waldo["screening"]["status"] == "award_qualified"
assert waldo["recognitionYear"] == 2023 and "Pam Liberda" in waldo["recognition"]
assert len(waldo["photographicEvidence"]) == 2
assert all(x["renderMode"] == "source_link_only" and x["imageRights"] == "unverified" for x in waldo["photographicEvidence"])
assert not any(w["candidateId"] == waldo["id"] for w in wishlist["entries"])






# Stock Hill: actual AAA Four Diamond recognition, not a Michelin/JBF award or a visit.
stock_hill = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-stock-hill")
assert stock_hill["visitStatus"] == "not_visited" and stock_hill["wantsToVisit"] is True
assert stock_hill["wishlistEntryId"] == "want-to-visit-stock-hill-kansas-city"
stock_wish = next(w for w in wishlist["entries"] if w["candidateId"] == stock_hill["id"])
assert stock_wish["id"] == "want-to-visit-stock-hill-kansas-city"
assert stock_wish["status"] == "want_to_visit" and stock_wish["visitStatus"] == "not_visited"
assert stock_wish["location"]["address"] == "4800 Main Street, Suite G-001"
assert stock_wish["recognition"]["organization"] == "AAA"
assert stock_wish["recognition"]["awardFamily"] == "aaa_four_diamond"
assert stock_wish["recognition"]["sourceUrl"].startswith("https://newsroom.aaa.com/")
assert not any(r["title"] == "Stock Hill" for r in records)
assert stock_hill["screening"]["status"] == "distinct_hospitality_award_verified"
assert stock_hill["screening"]["basis"] == "aaa_four_diamond_exact_restaurant"
assert stock_hill["awardFamily"] == "aaa_four_diamond"
assert stock_hill["eligibility"]["verifiedForPublication"] is False
assert "not a Michelin or James Beard distinction" in stock_hill["recognition"]
assert len(stock_hill["photographicEvidence"]) == 2
assert all(photo["sourceUrl"].startswith("https://") and
           photo["renderMode"] == "source_link_only" and
           photo["imageRights"] == "unverified" for photo in stock_hill["photographicEvidence"])
assert not any(r["title"] == "Stock Hill" for r in records)
assert not any(r["title"] == "Farina" for r in records)

# 801 Chophouse is the original KC Missouri downtown branch, not Leawood.
chophouse = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-801-chophouse")
assert chophouse["visitStatus"] == "confirmed" and chophouse["confirmedVisitId"] == "dining-801-chophouse-kansas-city-date-unknown"
assert "71 E 14th Street" in chophouse["addressHint"]
assert "Leawood" in chophouse["addressHint"]
assert chophouse["screening"]["status"] == "distinct_hospitality_award_verified"
assert chophouse["screening"]["basis"] == "wine_spectator_best_of_award_of_excellence_exact_kc_restaurant"
assert chophouse["awardFamily"] == "wine_spectator"
assert chophouse["eligibility"]["verifiedForPublication"] is False
assert "not a James Beard/Michelin culinary award" in chophouse["recognition"]
assert len(chophouse["photographicEvidence"]) == 2
assert all(p["sourceUrl"].startswith("https://") and p["renderMode"] == "source_link_only"
           and p["imageRights"] == "unverified" for p in chophouse["photographicEvidence"])
assert any(r["id"] == chophouse["confirmedVisitId"] and r["status"] == "confirmed" for r in records)

# Recent Cambridge responses use the same locked-answer schema as older chapters.
cambridge_confirmed = {
    "candidate-cambridge-eagle", "candidate-cambridge-anchor",
    "candidate-cambridge-mill-pub", "candidate-cambridge-millworks",
    "candidate-cambridge-parkers-tavern", "candidate-cambridge-fitzbillies-trumpington",
}
assert all(next(c for c in candidates if c["id"] == cid)["visitStatus"] == "confirmed"
           for cid in cambridge_confirmed)
for cid in ("candidate-cambridge-pickerel-inn", "candidate-cambridge-granta",
            "candidate-cambridge-cambridge-blue", "candidate-cambridge-maypole"):
    candidate = next(c for c in candidates if c["id"] == cid)
    assert candidate["visitStatus"] == "not_visited"
    assert candidate.get("wantsToVisit", False) == (cid != "candidate-cambridge-maypole")
# NYC bar interview must retain explicit user responses and never count either as confirmed.
pdt = next(c for c in candidates if c["area"] == "New York City" and c["name"] == "PDT (Please Don't Tell)")
rabbit = next(c for c in candidates if c["area"] == "New York City" and c["name"] == "The Dead Rabbit")
assert pdt["visitStatus"] == "maybe" and rabbit["visitStatus"] == "not_visited"
leyenda = next(c for c in candidates if c["area"] == "New York City" and c["name"] == "Leyenda")
dante = next(c for c in candidates if c["area"] == "New York City" and c["name"] == "Dante")
assert leyenda["visitStatus"] == "not_visited" and leyenda["visitPeriod"].startswith("2018–2020")
assert dante["visitStatus"] == "not_visited" and dante["visitPeriod"].startswith("New York City, 2018–2020")
assert "did not visit" in dante["reviewSource"].lower()
assert "2018" in dante["recognition"] and dante["screening"]["status"] == "award_qualified"
bar_goto = next(c for c in candidates if c["area"] == "New York City" and c["name"] == "Bar Goto")
assert bar_goto["visitStatus"] == "not_visited"
assert bar_goto["reviewedOn"] == "2026-10-25"
assert "did not visit" in bar_goto["reviewSource"].lower()
assert bar_goto["recognitionYear"] == 2018 and bar_goto["screening"]["status"] == "award_qualified"
assert not any(r["title"] in {"Bar Goto", "The Dead Rabbit", "Dante", "Leyenda", "PDT (Please Don't Tell)"} for r in records)
existing_conditions = next(c for c in candidates if c["area"] == "New York City" and c["name"] == "Existing Conditions")
assert existing_conditions["visitStatus"] == "not_visited"
assert not any(r["title"] == "Existing Conditions" for r in records)
assert pdt["visitStatus"] == "maybe" and rabbit["visitStatus"] == "not_visited"
assert leyenda["visitStatus"] == "not_visited"
assert not any(r["title"] in {"Leyenda", "Dante"} for r in records)
assert rabbit["recognitionYear"] == 2019 and "finalist" in rabbit["recognition"]
assert not any(r["title"] in {"PDT (Please Don't Tell)", "The Dead Rabbit"} for r in records)

assert {"Baltimore", "Washington, DC", "Denver Metro", "Steamboat Springs", "Charleston, SC", "Kansas City Metro"}.issubset({c["area"] for c in candidates})
assert interview_data["periods"]["Charleston, SC"].endswith("2017–2018")
assert "2010" in interview_data["periods"]["Kansas City Metro"]
majestic = next(c for c in candidates if c["name"] == "The Majestic Restaurant" and c["area"] == "Kansas City Metro")
assert majestic["visitStatus"] == "confirmed" and majestic["userMemoryLead"]["identityConfirmed"] is True
assert majestic["confirmedVisitId"] == "dining-majestic-kansas-city"
assert "DOWNSTAIRS" in majestic["interviewCue"]
assert any(r["title"] == "The Majestic Restaurant" and r["status"] == "confirmed" for r in records)
rec_pier = next(c for c in candidates if c["name"] == "Rec Pier Chop House" and c["area"] == "Baltimore")
assert rec_pier["visitStatus"] == "confirmed" and rec_pier["confirmedVisitId"] == "dining-rec-pier-chop-house-baltimore"
assert not any(r["title"] == "Le Fou Frog" for r in records)
assert not any(c["name"] == "Le Fou Frog" for c in candidates)
north_pond = next(c for c in candidates if c["name"] == "North Pond" and c["area"] == "Chicago")
assert north_pond["visitStatus"] == "confirmed" and north_pond["confirmedVisitId"] == "dining-north-pond-chicago-2021"
assert north_pond["userMemoryLead"]["identityConfirmed"] is True
assert north_pond["screening"]["basis"] == "both"
assert any(r["title"] == "North Pond" and r["guide"]["stars"] == 1 for r in records)
assert len([r for r in records if r["type"] == "dining" and r["status"] == "confirmed"]) >= 25
assert {"bar-manifesto-kansas-city", "bar-death-and-co-denver",
        "bar-j-bar-hotel-jerome-aspen", "bar-eagle-cambridge-visit-date-unknown",
        "bar-anchor-cambridge-visit-date-unknown", "bar-mill-pub-cambridge-visit-date-unknown",
        "bar-parkers-tavern-cambridge-date-unknown"}.issubset(
    {r["id"] for r in records if r["type"] == "bar" and r["status"] == "confirmed"})
breck = [r for r in records if r["venueId"] == "venue-breckenridge-distillery"]
assert len(breck) == 3
assert sorted(r["visit"]["year"] for r in breck) == [2021, 2022, 2023]
assert all(r["visit"]["date"] is None and r["visit"]["precision"] == "approximate_year" for r in breck)
assert all(r["editorial"]["awardQualified"] is False and r["editorial"]["featuredException"] is False for r in breck)
assert {r["venueId"] for r in records} == venue_ids
qbreck = next(c for c in candidates if c["name"] == "Breckenridge Distillery Restaurant")
assert qbreck["visitStatus"] == "confirmed" and set(qbreck["linkedVisitIds"]) == {r["id"] for r in breck}
assert qbreck["screening"]["status"] == "memory_only"
assert {"New York City", "Chicago", "St. Louis", "Breckenridge"}.issubset({c["area"] for c in candidates})
assert interview_data["periods"]["New York City"].startswith("2018–2020")
assert "2010" in interview_data["periods"]["Chicago"]
assert interview_data["periods"]["St. Louis"].startswith("2011–2014")
assert interview_data["periods"]["Breckenridge"] == "2021, 2022 and 2023"
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "The Aviary")["visitStatus"] == "not_visited"
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "The Violet Hour")["visitStatus"] == "not_visited"
office_lead = next(lead for lead in interview_data["memoryLeads"] if lead["id"] == "chicago-the-office-aviary-downstairs-unresolved")
assert office_lead["visitStatus"] == "unreviewed" and office_lead["publishAsExperience"] is False
assert office_lead["relatedVenue"] == "The Aviary"
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Lost Lake")["visitStatus"] == "not_visited"
for venue_name, expected_status in (("Untitled Supper Club", "confirmed"), ("Cindy's Rooftop", "maybe")):
    lead = next(c for c in candidates if c["area"] == "Chicago" and c["name"] == venue_name)
    assert lead["visitStatus"] == expected_status
    assert lead["screening"]["status"] == "award_qualified"
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Cherry Circle Room")["visitStatus"] == "not_visited"
assert any(lead["id"] == "chicago-friend-untitled-cindys-unknown-years"
           and lead["publishAsExperience"] is False
           for lead in interview_data["memoryLeads"])
assert not any(r["title"] == "Cherry Circle Room" for r in records)
# Direct response "None of those yet" applies to exactly six previously named Chicago bar candidates.
chicago_six = {"Kumiko", "Best Intentions", "Bisous", "Hopleaf Bar", "Truce", "Cherry Circle Room"}
assert all(next(c for c in candidates if c["area"] == "Chicago" and c["name"] == name)["visitStatus"] == "not_visited" for name in chicago_six)
assert interview_data["interviewProgress"]["pausedBatches"][0]["status"] == "closed_for_now_at_user_request"
assert set(interview_data["interviewProgress"]["pausedBatches"][0]["explicitlyNotVisitedAsOfDate"]) == chicago_six
# South Bay / Space Park: preserve five MAYBE and three NOT VISITED.
# The initial eight are screened; no canonical personal dining records for these.
space_park = [c for c in candidates if c["area"] == "South Bay / Space Park"]
assert len(space_park) == 8
assert all(c["screening"]["status"] == "award_qualified" for c in space_park)
maybe_names = {"Manhattan Beach Post", "Fishing with Dynamite", "RYLA",
               "Sushi Inaba (Torrance)", "Vin Folk"}
not_visited_names = {"Sushi Sonagi", "Sweet Rice", "Mar'sel"}
assert {c["name"] for c in space_park if c["visitStatus"] == "maybe"} == maybe_names
assert {c["name"] for c in space_park if c["visitStatus"] == "not_visited"} == not_visited_names
assert {c["name"] for c in space_park if c["visitStatus"] == "unreviewed"} == set()
assert all(next(c for c in space_park if c["name"] == n)["lastInterviewResponse"] == "Maybe visited."
           for n in maybe_names)
assert all(next(c for c in space_park if c["name"] == n)["lastInterviewResponse"] == "Did not visit."
           for n in not_visited_names)
assert all(not any(r["title"] == c["name"] and r["status"] == "confirmed" for r in records)
           for c in space_park)
sushi_inaba = next(c for c in space_park if c["id"] == "candidate-space-park-sushi-inaba-torrance")
assert sushi_inaba["visitStatus"] == "maybe"
assert "I-naba" in sushi_inaba["interviewCue"]
vin_folk = next(c for c in space_park if c["id"] == "candidate-space-park-vin-folk")
assert vin_folk["visitStatus"] == "maybe"
assert vin_folk["openedYear"] == 2024
assert "Bib Gourmand" in vin_folk["recognition"]
sweet_rice = next(c for c in space_park if c["id"] == "candidate-space-park-sweet-rice")
assert sweet_rice["visitStatus"] == "not_visited"
assert sweet_rice["eligibility"]["verifiedForPublication"] is False
assert sweet_rice["openedYear"] == 2019
marsel = next(c for c in space_park if c["id"] == "candidate-space-park-marsel")
assert marsel["visitStatus"] == "not_visited"
assert "Terranea" in marsel["interviewCue"]
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["namedConfirmedVisits"] == 0
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["maybeVisitedCandidates"] == 5
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["notVisitedCandidates"] == 3
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["unreviewedCandidates"] == 0
assert set(interview_data["interviewChapters"]["spaceParkSouthBay"]["maybeVisitedNames"]) == maybe_names
assert set(interview_data["interviewChapters"]["spaceParkSouthBay"]["notVisitedNames"]) == not_visited_names
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["nextCandidate"] is None
assert interview_data["interviewProgress"]["currentBatch"]["area"] in interview_data["periods"]
assert interview_data["interviewProgress"]["currentBatch"]["candidateNames"]
assert any(x["id"] == "redondo-space-park-dining-unidentified" and
           x["publishAsExperience"] is False for x in interview_data["memoryLeads"])

# LA research is deliberately two parallel chapters. Never silently abandon
# the Taiwanese meal with Jay when the Space Park/South Bay interview resumes.
active_la = interview_data["interviewChapters"]["losAngeles"]
active_south_bay = interview_data["interviewChapters"]["spaceParkSouthBay"]
assert active_la["state"] == "active_research_parallel"
assert active_south_bay["state"] == "active_research_parallel"
assert active_la["confirmedNamedVisits"] == 2
# User's strong visual recollection of Liu's Cafe is a probable identity,
# not a license to add a confirmed restaurant visit or borrow its Bib Gourmand.
lius = next(c for c in candidates if c["id"] == "candidate-la-lius-cafe-ktown")
assert lius["visitStatus"] == "maybe"
assert lius["researchStatus"] == "previous_strong_liu_lead_now_secondary_to_joy_not_confirmed"
assert lius["eligibility"]["verifiedForPublication"] is False
taiwanese_with_jay = next(m for m in interview_data["memoryLeads"]
    if m["id"] == "la-west-hollywood-jay-taiwanese-unidentified")
assert taiwanese_with_jay["venueIdentityConfirmed"] is False
assert taiwanese_with_jay["probableCandidateId"] == "candidate-la-joy-highland-park"
assert next(c for c in candidates if c["id"] == "candidate-la-joy-highland-park")["visitStatus"] == "maybe"
assert next(c for c in candidates if c["id"] == "candidate-la-joy-highland-park")["researchStatus"] == "user_leans_toward_joy_top_unconfirmed_identity"
assert taiwanese_with_jay["alternativeProbableCandidateId"] == lius["id"]
assert active_la["maybeVisited"] == 2
assert taiwanese_with_jay["comparativeReview"]["comparisonCount"] == 8
assert len(taiwanese_with_jay["comparativeReview"]["candidates"]) == 8
assert taiwanese_with_jay["comparativeReview"]["noNewVisitConfirmations"] is True
assert {row["id"] for row in taiwanese_with_jay["comparativeReview"]["candidates"]} == {
    "candidate-la-lius-cafe-ktown", "candidate-la-pine-crane-silver-lake",
    "candidate-la-pine-crane-dtla", "candidate-la-joy-highland-park",
    "candidate-la-little-fatty-mar-vista", "candidate-la-din-tai-fung-century-city",
    "candidate-la-kato", "candidate-la-formosa-cafe"}
assert all(c["visitStatus"] in {"unreviewed", "not_visited"} for c in candidates
    if c["id"] in {row["id"] for row in taiwanese_with_jay["comparativeReview"]["candidates"]}
    - {"candidate-la-lius-cafe-ktown", "candidate-la-joy-highland-park"})
assert taiwanese_with_jay["temporalConstraint"]["earliestPossibleVisit"] == "2023-08-31"
assert not any(r["status"] == "confirmed" and "Liu's Cafe" in r["title"] for r in records)
assert "Joy (Highland Park)" in active_la["strongestUnconfirmedTaiwaneseLead"]
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["state"] == "active_research_parallel"

assert set(active_la["confirmedNames"]) == {"République", "The Butcher's Daughter"}
parallel = interview_data["interviewProgress"]["parallelActiveChapters"]
assert {x["area"] for x in parallel} == {"Los Angeles / West Hollywood", "South Bay / Space Park"}
assert any(x["id"] == "la-west-hollywood-jay-taiwanese-unidentified" and
    x["venueIdentityConfirmed"] is False for x in interview_data["memoryLeads"])
for title in ("Petit Trois (L'Original)", "Chi Spacca", "Angelini Osteria",
              "Ardor (West Hollywood EDITION)"):
    match = next(c for c in candidates if c["name"] == title and
        c["area"] == "Los Angeles / West Hollywood")
    # Attendance changes during interviews; verify the independent listing evidence.
    assert match["screening"]["sourceTier"] == "official_michelin"
    assert match["screening"]["basis"] == "michelin"

active_batch = interview_data["interviewProgress"]["currentBatch"]
assert active_batch["area"] in {c["area"] for c in candidates}
assert all(any(c["area"] == active_batch["area"] and c["name"] == name for c in candidates) for name in active_batch["candidateNames"])
kc_not_recalled = ["Corvino Supper Club & Tasting Room", "The Antler Room", "Bluestem", "Rye (Leawood)", "The Town Company", "Fox & Pearl", "Waldo Thai", "The American Restaurant"]
kc_reviewed = [c for c in candidates if c["area"] == "Kansas City Metro" and (c["name"] in kc_not_recalled or c["name"] == "Fox and Pearl")]
assert len(kc_reviewed) == 9
# The October 25 batch was only a tentative recollection. Preserve the seven
# other venues' tentative status, while honoring the user's later direct correction.
assert all(c["visitStatus"] == "not_visited" and c["reviewCertainty"] == ("explicit_nonattendance" if c["name"] in {"The Antler Room", "The American Restaurant", "Corvino Supper Club & Tasting Room"} else "explicit_nonvisit_with_wishlist_intent" if c["name"] in {"Fox and Pearl", "Fox & Pearl", "The Town Company"} else "explicit_nonattendance" if c["name"] == "Waldo Thai" else "tentative_negative")
           for c in kc_reviewed if c["name"] not in {"Bluestem", "Rye (Leawood)"})
bluestem = next(c for c in kc_reviewed if c["name"] == "Bluestem")
assert bluestem["visitStatus"] == "maybe" and bluestem["reviewCertainty"] == "explicit_uncertain"
assert bluestem["reviewedOn"] == "2026-10-28"
assert "I'm not certain I visited" in bluestem["reviewSource"]
assert not any(r["title"] == "Bluestem" and r["status"] == "confirmed" for r in records)
assert active_batch["status"] in {"ready_for_visual_screening", "awaiting_user_response", "awaiting_reconfirmation_of_prior_tentative_negative"}
if active_batch["status"] == "awaiting_reconfirmation_of_prior_tentative_negative":
    assert active_batch["candidateNames"] == ["Chewology"]
    assert waldo["reviewCertainty"] == "explicit_nonattendance"
    assert waldo["visitStatus"] == "not_visited"
    assert waldo["operatingStatus"] == "permanently_closed"
    assert "closed in October 2025" in active_batch["question"] or "closed in October 2025" in active_batch["continuation"]

assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Untitled Supper Club")["visitStatus"] == "confirmed"
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Cindy's Rooftop")["visitStatus"] == "maybe"

assert not any(r["title"] in {"The Aviary", "The Office", "The Violet Hour"} for r in records)
dominics = next(c for c in candidates if c["name"] == "Dominic's on the Hill")
assert dominics["visitStatus"] == "confirmed" and dominics["visitPeriod"] == "December 28, 2012"
assert dominics["researchOnly"] is True
assert not any(r["title"] == "Dominic's on the Hill" for r in records)
assert next(c for c in candidates if c["name"] == "The Aviary")["screening"]["status"] == "award_qualified"
assert not any(r["title"] in {"PDT (Please Don't Tell)", "The Aviary", "Dominic's on the Hill"} for r in records)
manifesto = next(r for r in records if r["title"] == "Manifesto" and r["type"] == "bar")
assert manifesto["editorial"]["awardQualified"] is True
assert any(a["year"] == 2018 and a["category"] == "Outstanding Bar Program" and a["result"] == "semifinalist" for a in manifesto["recognitions"])
death_and_co = next(r for r in records if r["title"] == "Death & Co Denver" and r["type"] == "bar")
assert death_and_co["editorial"]["awardQualified"] is False and death_and_co["editorial"]["featuredException"] is True
for name in ("Sauvage", "Gunther & Co.", "The Majestic Restaurant"):
    rec = next(r for r in records if r["title"] == name)
    assert rec["editorial"]["awardQualified"] is False and rec["editorial"]["featuredException"] is True
assert {"République", "Minetta Tavern", "Beckon", "Charleston", "Woodberry Kitchen", "Momofuku CCDC", "Manifesto", "Yuan Wonton", "Safta", "Smok", "Mister Oso", "North Pond", "Annette", "Mercantile Dining & Provision", "Barolo Grill", "Sap Sua", "Untitled Supper Club", "Sushi Den"}.issubset({r["title"] for r in records if r["status"] == "confirmed" and r.get("editorial", {}).get("awardQualified")})
assert all(not r.get("editorial", {}).get("awardQualified") or not r.get("editorial", {}).get("featuredException") for r in records)
assert any(c["name"] == "Manifesto" and c["visitStatus"] == "confirmed" for c in candidates)
assert any(c["name"] == "Death & Co Denver" and c["visitStatus"] == "confirmed" for c in candidates)
assert 'data-type="bar"' in (ROOT / "explore.html").read_text(encoding="utf-8")
assert 'id="bar-count"' in (ROOT / "index.html").read_text(encoding="utf-8")
assert 'r.editorial?.featuredException' in (ROOT / "assets/app.js").read_text(encoding="utf-8")
assert all(c.get("confirmedVisitId") in {r["id"] for r in records}
           for c in candidates if c["visitStatus"] == "confirmed" and c.get("confirmedVisitId"))
assert any(c["name"] == "Alma Cocina Latina" and c["visitStatus"] == "maybe" for c in candidates)
pdt = next(c for c in candidates if c["name"] == "PDT (Please Don't Tell)" and c["area"] == "New York City")
assert pdt["visitStatus"] == "maybe" and "2018–2020" in pdt["visitPeriod"]
assert pdt["recognitionYear"] == 2012 and pdt["screening"]["status"] == "award_qualified"
assert pdt["sourceUrl"].startswith("https://archive.jamesbeard.org")
assert not any(r["title"] == "PDT (Please Don't Tell)" for r in records)
for name, area in [("Clover Club", "New York City"), ("Columbia Room", "Washington, DC"),
                   
                   ("Anjin", "Kansas City Metro")]:
    candidate = next(c for c in candidates if c["name"] == name and c["area"] == area)
    assert candidate["visitStatus"] == ("not_visited" if name == "Anjin" else "unreviewed")
    assert candidate["screening"]["status"] == "award_qualified"
    assert candidate["sourceUrl"].startswith("https://")
traveling_mercies = next(c for c in candidates if c["name"] == "Traveling Mercies" and c["area"] == "Denver Metro")
assert traveling_mercies["visitStatus"] == "not_visited"  # Alex's explicit 2026-10-26 response
assert traveling_mercies["screening"]["status"] == "award_qualified"  # Venue research remains preserved
assert any(c["name"] == "Gunther & Co." and c["visitStatus"] == "confirmed" for c in candidates)
assert all(len(c.get("linkedVisitIds", [])) == 3 for c in candidates if c["name"] == "Breckenridge Distillery Restaurant")
assert all(c["name"] not in {r["title"] for r in records}
           for c in candidates if c["visitStatus"] == "not_visited")
for page in ("index", "explore", "timeline", "map", "record", "interview"):
    source = (ROOT / (page + ".html")).read_text(encoding="utf-8")
    assert "Culture Passport" in source and "./assets/site.css" in source
    assert "./assets/app.js" in source
map_html = (ROOT / "map.html").read_text(encoding="utf-8")
assert map_html.index("leaflet.js") < map_html.index('src="./assets/app.js'), "Load Leaflet before Culture map app"
assert 'id="interview-period"' in (ROOT / "interview.html").read_text(encoding="utf-8")
assert 'byId("interview-period")' in (ROOT / "assets/app.js").read_text(encoding="utf-8")
assert (ROOT / "assets/app.js").exists()
assert (ROOT / "assets/site.css").exists()
evidence_data = json.loads((ROOT / "data/reservation-evidence.json").read_text(encoding="utf-8"))
reservations = evidence_data["entries"]
assert len(reservations) == 22 and len({e["id"] for e in reservations}) == 22
booked_campbell = next(e for e in reservations if e["id"] == "the-campbell-new-york-2026-11-01")
assert booked_campbell["name"] == "The Campbell"
assert booked_campbell["reservationDate"] == "2026-11-01" and booked_campbell["reservationTime"] == "19:30"
assert booked_campbell["timezone"] == "America/New_York" and booked_campbell["partySize"] == 3
assert booked_campbell["platform"] == "Resy" and booked_campbell["reservationStatus"] == "visited_confirmed"
assert booked_campbell["attendanceInference"] == "user_confirmed_attendance"
assert booked_campbell["publicCuration"] == "research_only"
assert booked_campbell["recognition"]["status"] == "not_verified_as_qualifying"
assert booked_campbell["recognition"]["formalAwards"]["verified"] is False
assert booked_campbell["recognition"]["classification"]["currentPolicy"] == "editorially_recognized_personal_selection"
assert booked_campbell["recognition"]["classification"]["publicationStatus"] == "pending_story_review"
assert booked_campbell["recognition"]["classification"]["possibleExpandedTier"] == "editorially_recognized_bar"
assert len(booked_campbell["recognition"]["editorialSelections"]) == 3
assert {(item["publisher"], item["publicationDate"]) for item in booked_campbell["recognition"]["editorialSelections"]} == {("Tasting Table", "2023-02-16"), ("Time Out New York", "2025-03-10"), ("Eater New York", "2017-12-29")}
assert all(item["sourceUrl"].startswith("https://") and item["type"].endswith("not_award") for item in booked_campbell["recognition"]["editorialSelections"])
assert booked_campbell["recognition"]["historicalUnverified"][0]["confidence"] == "secondary_reproduction_only_original_list_not_located"
assert booked_campbell["childrenPolicy"]["sourceUrl"].startswith("https://www.thecampbellnyc.com/")
assert any(r["title"] == "The Campbell" and r["status"] == "confirmed" for r in records)
assert sum(1 for e in reservations if e["reservationStatus"] == "completed") >= 1
booked_tonchin = next(e for e in reservations if e["id"] == "tonchin-new-york-2026-11-01")
assert booked_tonchin["name"] == "Tonchin New York"
assert booked_tonchin["reservationDate"] == "2026-11-01" and booked_tonchin["reservationTime"] == "21:00"
assert booked_tonchin["partySize"] == 4 and booked_tonchin["seating"] == "Dining Room"
assert booked_tonchin["reservationStatus"] == "visited_confirmed"
assert booked_tonchin["attendanceInference"] == "confirmed_on_site_photo_and_user_instruction"
assert booked_tonchin["publicCuration"] == "pending_explicit_story_review"
assert booked_tonchin["recognition"]["distinction"] == "Bib Gourmand"
assert any(r["title"] == "Tonchin New York" and r["status"] == "confirmed" for r in records)
assert all(e["reservationDate"] and e["partySize"] >= 1 and e["source"] == "user_provided_reservation_screenshot" for e in reservations)
assert not any(e["name"] == "Le Fou Frog" for e in reservations)
assert sum(1 for e in reservations if e["name"] == "Ritual Social House") == 2
assert sum(1 for e in reservations if e["reservationStatus"] == "waitlist_completed") == 1
blanco = next(e for e in reservations if e["name"].startswith("Blanco Cocina"))
assert blanco["attendanceInference"] == "not_confirmed"
# Historical reservations remain verifiable even after separate user confirmation of dining.
for name, date, evidence_name in [("Wildflower", "2022-03-21", "Wildflower - Denver")]:
    restaurant = next(r for r in records if r["title"] == name)
    assert restaurant["status"] == "confirmed" and restaurant["visit"]["date"] is None
    assert restaurant["visit"]["evidenceType"] == "direct_user_recollection"
    assert restaurant["visit"]["attendanceCertainty"] == "restaurant_visit_confirmed_exact_date_unverified"
    assert restaurant["editorial"]["awardQualified"] is True
    assert any(b["date"] == date and b["attendanceInference"] == "reservation_date_not_verified_as_meal_date" for b in restaurant["reservations"])
    assert any(e.get("archivedRecordId") == restaurant["id"] and e["publicCuration"] == "research_only" for e in reservations)
    assert next(e for e in reservations if e["name"] == evidence_name)["attendanceInference"] == "venue_visit_confirmed_separately_exact_date_unverified"
    candidate = next(c for c in candidates if c["name"] == name and c["area"] == "Denver Metro")
    assert candidate["visitStatus"] == "confirmed" and candidate["confirmedVisitId"] == restaurant["id"]
q_house = next(r for r in records if r["title"] == "Q House")
assert q_house["status"] == "confirmed"
assert q_house["visit"]["date"] is None and q_house["visit"]["evidenceType"] == "direct_user_recollection"
assert q_house["visit"]["attendanceCertainty"] == "restaurant_visit_confirmed_exact_date_unverified"
assert any(b["date"] == "2021-10-21" and b["attendanceInference"] == "reservation_date_not_verified_as_meal_date" for b in q_house["reservations"])
assert any(a["organization"] == "James Beard Foundation" and a["year"] == 2019 and a["result"] == "semifinalist" and a["timingRelativeToVisit"] == "visit_date_unknown" for a in q_house["recognitions"])
q_house_candidate = next(c for c in candidates if c["area"] == "Denver Metro" and c["name"] == "Q House")
assert q_house_candidate["visitStatus"] == "confirmed" and q_house_candidate["confirmedVisitId"] == q_house["id"]
assert next(e for e in reservations if e["name"] == "Q House")["reservationDate"] == "2021-10-21"
assert next(e for e in reservations if e["name"] == "Q House")["attendanceInference"] == "venue_visit_confirmed_separately_exact_date_unverified"
wildflower = next(r for r in records if r["title"] == "Wildflower")
assert wildflower["guide"]["stars"] == 0 and all(a["timingRelativeToVisit"] == "visit_date_unknown" for a in wildflower["recognitions"])
uchi = next(c for c in candidates if c["name"] == "Uchi Denver")
assert uchi["visitStatus"] == "confirmed" and uchi.get("confirmedVisitId") == "dining-uchi-denver"
assert uchi["screening"]["status"] == "needs_verification"
mister = next(c for c in candidates if c["name"] == "Mister Oso" and c["area"] == "Denver Metro")
assert mister["visitStatus"] == "confirmed"
assert mister["confirmedVisitId"] == "dining-mister-oso-denver"
assert mister["screening"]["status"] == "award_qualified"
assert "branchWarning" not in mister
oso = next(r for r in records if r["title"] == "Mister Oso")
assert oso["guide"]["distinction"] == "bib" and oso["guide"]["stars"] == 0
assert "Señor Bear" in oso["memory"]["story"] and "Wash Park" in oso["memory"]["story"] and "RiNo" in oso["memory"]["story"]
assert any(r["title"] == "Uchi Denver" and r["status"] == "confirmed" and not r["editorial"]["awardQualified"] for r in records)
assert not any(r["title"] == "Mister Oso Wash Park" for r in records)
assert "culture.alexlford.com" in (ROOT / "README.md").read_text(encoding="utf-8")
print("Culture Passport OK: %d experiences, %d venues, %d interview prospects" %
      (len(records), len(venues), len(candidates)))

# Reservation provenance must be distinct from user-confirmed visits.
evidence = json.loads((ROOT / "data/reservation-evidence.json").read_text(encoding="utf-8"))
assert len(evidence["entries"]) == 22 and len(evidence["rows"]) == 54 and len({r["name"] for r in evidence["rows"]}) == 48
future_campbell = next(r for r in evidence["rows"] if r["name"] == "The Campbell" and r["date"] == "2026-11-01")
assert future_campbell["time"] == "19:30" and future_campbell["partySize"] == 3
assert future_campbell["platform"] == "Resy" and future_campbell["status"] == "visited_confirmed"
assert future_campbell["attendanceInference"] == "user_confirmed_attendance"
future_tonchin = next(r for r in evidence["rows"] if r["name"] == "Tonchin New York")
assert future_tonchin["date"] == "2026-11-01" and future_tonchin["time"] == "21:00"
assert future_tonchin["status"] == "visited_confirmed"
assert future_tonchin["attendanceInference"] == "confirmed_on_site_photo_and_user_instruction"
assert not any(r["name"] == "Le Fou Frog" for r in evidence["rows"])
assert not any(r["title"] == "Le Fou Frog" for r in records)
republique = next(r for r in records if r["title"] == "République")
assert republique["visit"]["date"] == "2026-10-24" and republique["visit"]["evidenceType"] == "direct_user_recollection"
for title, date in [("Woodberry Kitchen", "2018-05-16"), ("Momofuku CCDC", "2018-08-21"), ("Rec Pier Chop House", "2018-05-16")]:
    row = next(r for r in records if r["title"] == title)
    assert row["status"] == "confirmed" and row["visit"]["date"] is None
    assert row["visit"]["precision"] != "day"
    assert row["visit"]["attendanceCertainty"] == "user_confirmed_venue_exact_meal_date_unverified"
    assert any(b["date"] == date and b["attendanceInference"] == "not_independently_verified" for b in row["reservations"])
assert "2018" in next(r for r in records if r["title"] == "Woodberry Kitchen")["visit"]["label"]

# Yuan Wonton qualifies on its chef-owner's 2026 James Beard Best Chef: Mountain win.
yuan = next(r for r in records if r["title"] == "Yuan Wonton")
assert yuan["editorial"]["awardQualified"] is True and yuan["visit"]["date"] is None
assert yuan["recognitions"][0]["recipient"] == "Penelope Wong" and yuan["recognitions"][0]["year"] == 2026
assert yuan["recognitions"][0]["timingRelativeToVisit"] == "unknown_visit_date"
assert next(q for q in candidates if q["name"] == "Yuan Wonton")["confirmedVisitId"] == yuan["id"]
assert not any(r["title"] == "Bistro Barbès" for r in records)
excluded = json.loads((ROOT / "data/excluded-dining-memories.json").read_text(encoding="utf-8"))
assert any(r["name"] == "Bistro Barbès" and r["qualifies"] is False for r in excluded["entries"])

# Two user-confirmed Source Hotel visits are Michelin Selected, never stars.
for name in ("Safta", "Smok"):
    r = next(x for x in records if x["title"] == name)
    assert r["type"] == "dining" and r["status"] == "confirmed"
    assert r["visit"]["date"] is None and r["visit"]["year"] is None
    assert r["guide"]["distinction"] == "selected" and r["guide"]["stars"] == 0
    assert r["editorial"]["awardQualified"] is True and r["memory"]["headline"]
    q = next(x for x in candidates if x["name"] == name and x["area"] == "Denver Metro")
    assert q["visitStatus"] == "confirmed" and q["confirmedVisitId"] == r["id"]

# The story should lead the experience page, with precise booking details tucked away.
assert sum(bool(r.get("memory")) for r in records) >= 19
assert 'Historical notes & sources' in (ROOT / "assets/app.js").read_text(encoding="utf-8")
assert 'const storyPeriod=(r)' in (ROOT / "assets/app.js").read_text(encoding="utf-8")
assert 'function timelineChapter' not in (ROOT / "assets/app.js").read_text(encoding="utf-8") or 'Other memories' in (ROOT / "assets/app.js").read_text(encoding="utf-8")

# Historical Colorado interview expansion: candidates, not automatically confirmed visits.
for area in ("Boulder", "Aspen", "Vail / Beaver Creek", "Telluride", "Breckenridge"):
    assert sum(c["area"] == area for c in candidates) >= (11 if area == "Boulder" else 3 if area != "Telluride" else 1)
for name,area in (("Basta","Boulder"),("Bosq","Aspen"),("Radicato","Breckenridge"),("Sweet Basil","Vail / Beaver Creek"),("The National","Telluride")):
    c = next(c for c in candidates if c["name"] == name and c["area"] == area)
    assert c["visitStatus"] in {"unreviewed", "maybe", "confirmed", "not_visited"} and c["screening"]["status"] == "award_qualified"  # screening status may evolve through interviews
assert next(c for c in candidates if c["name"] == "Frasca Food and Wine")["area"] == "Boulder"

# Stable batch interview: answering must never rebuild the list and lose scroll position.
app_js = (ROOT / "assets/app.js").read_text(encoding="utf-8")
interview_html = (ROOT / "interview.html").read_text(encoding="utf-8")
assert 'const batchSize=12' in app_js
assert 'do not rebuild the card or page after answering' in app_js
assert 'localStorage.setItem(uiKey' in app_js
assert 'id="interview-next"' in interview_html and 'id="interview-previous"' in interview_html
assert 'id="interview-save-status"' in interview_html
for title in ("Sauvage", "Charleston", "Safta", "Manifesto"):
    rec = next(r for r in records if r["title"] == title)
    assert rec.get("reservations") and rec.get("memory",{}).get("story")
manifesto = next(r for r in records if r["title"] == "Manifesto")
assert manifesto["reservations"][0]["date"] == "2019-10-25"
assert len([r for r in evidence["rows"] if r["name"] == "Sauvage"]) == 2
assert len([r for r in evidence["rows"] if r["name"] == "Michelob Ultra Mountain House"]) == 3
assert not any(r["title"] in {"Michelob Ultra Mountain House", "The Butcher's Daughter - West Hollywood", "Willow Creek Restaurant", "Q39 South"} for r in records)

# The 2023 West Hollywood Resy booking was explicitly confirmed as a restaurant
# visit in the October 27, 2026 LA interview, NOT as an exact attended date.
butchers = next(r for r in records if r["id"] == "dining-butchers-daughter-los-angeles-date-unknown")
assert butchers["status"] == "confirmed" and butchers["type"] == "dining"
assert butchers["title"] == "The Butcher's Daughter"
assert butchers["visit"]["date"] is None and butchers["visit"]["precision"] == "unknown"
assert butchers["reservations"][0]["date"] == "2023-07-29"
assert butchers["reservations"][0]["partySize"] == 3
assert butchers["editorial"]["awardQualified"] is False
assert butchers["venueId"] == "venue-butchers-daughter-west-hollywood"
assert butchers["visit"]["attendanceCertainty"] == "venue_and_branch_confirmed_date_unknown"
assert butchers["visit"]["source"].find("West Hollywood") >= 0
assert "provisionally" not in butchers["visit"]["source"].lower()
assert interview_data["interviewChapters"]["losAngeles"]["confirmedNamedVisits"] == 2
assert any(x["name"] == "The Butcher's Daughter (West Hollywood)" and x["visitStatus"] == "confirmed"
    for x in candidates)
assert next(x for x in evidence["rows"] if x["name"] == "The Butcher's Daughter - West Hollywood")["date"] == "2023-07-29"
assert next(x for x in evidence["rows"] if x["name"] == "The Butcher's Daughter - West Hollywood")["attendanceInference"] == "restaurant_and_west_hollywood_branch_confirmed_independently_of_booking_date"
assert next(x for x in candidates if x["id"] == "candidate-la-joy-highland-park")["visitStatus"] == "maybe"
assert next(x for x in candidates if x["id"] == "candidate-la-pine-crane-dtla")["visitStatus"] == "unreviewed"
assert "The Butcher's Daughter" in interview_data["interviewChapters"]["losAngeles"]["confirmedNames"]



# Venue-level audit: do not inflate stats with repeat visits or unverified awards.
aud = json.loads((ROOT / "data/dining-awards-audit.json").read_text(encoding="utf-8"))
archive_only_names = {x["name"] for x in aud["confirmedArchiveOnly"]}
published_experiences = [r for r in records if r["type"] in {"dining", "bar"} and r["status"] == "confirmed" and r["title"] not in archive_only_names]
assert aud["summary"] == {
    "canonExperienceRecords": len(published_experiences),
    "distinctPublishedVenues": len({r["venueId"] for r in published_experiences}),
    "recognized": sum(r.get("editorial", {}).get("awardQualified", False) for r in published_experiences),
    "featuredPersonal": sum(r.get("editorial", {}).get("featuredException", False) for r in published_experiences),
    "officiallyFeatured": sum(r.get("editorial", {}).get("officialFeature", False) for r in published_experiences),
    "unfeaturedOther": len({r["venueId"] for r in published_experiences if not r.get("editorial", {}).get("awardQualified", False) and not r.get("editorial", {}).get("featuredException", False) and not r.get("editorial", {}).get("officialFeature", False)}),
    "additionalConfirmedArchiveOnly": len(aud["confirmedArchiveOnly"]),
    "possibleVisitLeads": len(aud["possiblyVisited"]),
    "reviewedButNotConfirmedReservations": len(aud["bookingLeads"]),
}
assert {x["venueId"] for x in aud["publishedVenues"]} == {r["venueId"] for r in published_experiences}
assert not aud["reservationOnlyVenues"]  # both former booking-only venues directly confirmed by Alex
assert not {x["name"] for x in aud["reservationOnlyVenues"]} & {x["name"] for x in aud["publishedVenues"]}
assert any(x["name"] == "Q House" and x["visitConfidence"] == "direct_user_confirmation_exact_meal_date_unknown" for x in aud["publishedVenues"])
assert {r["title"] for r in records if r["status"] == "reservation_only"} == {x["name"] for x in aud["reservationOnlyVenues"]}
assert len(published_experiences) == aud["summary"]["canonExperienceRecords"]
assert {"Joe's Kansas City Bar-B-Que", "Q39", "Arthur Bryant's Barbeque",
    "Jack Stack Barbecue", "Dominic's on the Hill",
    "The Kitchen American Bistro"}.issubset(archive_only_names)
assert {x["name"] for x in aud["possiblyVisited"]} == {
    "Alma Cocina Latina", "Lucina Eatery & Bar", "PDT (Please Don't Tell)"
}
assert next(x for x in aud["publishedVenues"] if x["name"] == "North Pond")["recognitionStatus"] == "qualifies"
for name in ("Annette", "Mercantile Dining & Provision", "Barolo Grill"):
    row = next(r for r in records if r["title"] == name)
    assert row["status"] == "confirmed" and row["editorial"]["awardQualified"] is True
    assert row["visit"]["date"] is None and row["memory"]["headline"]
for name in ("Q39", "Joe's Kansas City Bar-B-Que", "Arthur Bryant's Barbeque"):
    candidate = next(q for q in candidates if q["name"] == name)
    assert candidate["visitStatus"] == "confirmed" and candidate["screening"]["status"] == "memory_only"
    assert not any(r["title"] == name for r in records)
assert next(q for q in candidates if q["name"] == "Lucina Eatery & Bar")["visitStatus"] == "maybe"
assert len([r for r in records if r.get("guide", {}).get("distinction") == "starred"]) == 3
assert len([r for r in records if r["status"] == "confirmed" and r.get("editorial", {}).get("awardQualified")]) == aud["summary"]["recognized"]
# Broader source-linked JBF participation is not an award, nomination or win.
for name in ("Uchi Denver", "Jack Stack Barbecue (Overland Park)"):
    rec = next(r for r in records if r["title"] == name)
    assert name not in archive_only_names, f"{name}: program-linked inclusion must not remain archive-only"
    assert rec["status"] == "confirmed" and rec["editorial"]["officialFeature"]
    assert not rec["editorial"]["awardQualified"]
    assert rec["officialFeatures"] and all(f["organization"] == "James Beard Foundation" and
        f["sourceUrl"].startswith("https://") for f in rec["officialFeatures"])
jack_op = next(r for r in records if r["title"] == "Jack Stack Barbecue (Overland Park)")
assert jack_op["visit"]["date"] is None
assert next(c for c in candidates if c["name"] == "Jack Stack Barbecue (Overland Park)")["confirmedVisitId"] == jack_op["id"]
assert next(c for c in candidates if c["name"] == "Jack Stack Barbecue (Freight House)")["visitStatus"] == "unreviewed"
assert aud["summary"]["officiallyFeatured"] >= 2


# Theater memories: preserve uncertainty in titles, not in the fact an outing occurred.
stage=[r for r in records if r["id"] in {"theater-book-of-mormon-kansas-city-2016", "theater-second-city-chicago-2017", "theater-six-denver-2023", "theater-denver-holiday-theater-2024"}]
assert len(stage) == 4
assert all(r["visit"]["date"] is None and r["visit"]["year"] in {2016,2017,2023,2024} for r in stage)
assert {r["title"] for r in stage} == {"The Book of Mormon", "SIX", "The Second City — Chicago holiday outing", "A Christmas Carol — Denver"}
assert next(r for r in stage if r["title"] == "The Book of Mormon")["production"]["engagementWindow"] == "December 6–11, 2016"
assert next(r for r in stage if r["title"] == "SIX")["production"]["engagementWindow"] == "December 5–24, 2023"
assert next(r for r in stage if r["title"] == "A Christmas Carol — Denver")["production"]["titleConfirmed"] is True
assert next(r for r in stage if r["title"] == "The Second City — Chicago holiday outing")["production"]["titleConfirmed"] is False
assert next(r for r in stage if r["id"] == "theater-second-city-chicago-2017")["visit"]["month"] == 11
assert next(r for r in stage if r["id"] == "theater-second-city-chicago-2017")["production"]["identificationConfidence"] == "user_says_title_makes_sense_not_confirmed"
assert next(r for r in stage if r["title"] == "A Christmas Carol — Denver")["production"]["exactAttendanceDate"] is None
stage_research=json.loads((ROOT / "data/performance-interview.json").read_text(encoding="utf-8"))
assert len(stage_research["candidates"]) >= 3
assert any(c["id"] == "denver-unknown-play" for c in stage_research["candidates"])
assert next(c for c in stage_research["candidates"] if c["id"] == "theater-christmas-carol-denver-2024")["confirmation"] == "confirmed"
assert stage_research["interviewRoute"]["nextQuestionId"] == "denver-wicked-2024"
assert stage_research["interviewRoute"]["interviewMode"] == "rapid_batch"

# Verified family-linked cultural artifacts already exist; opera interview now resolved.
ring_record=next(r for r in records if r["id"] == "opera-wagner-s-ring-cycle-lyric-opera-of-chicago")
assert [(x["title"], x["date"]) for x in ring_record["attendedPerformances"]] == [("Das Rheingold","2016-10-09"),("Die Walküre","2017-11-26"),("Siegfried","2018-11-11")]
assert "Michelle Ford" in ring_record["summary"] and "October 9, 2016" in ring_record["memory"]["story"]
assert len(ring_record["michelleFordCredits"]["appearances"]) == 3
assert [a["printedCredit"] for a in ring_record["michelleFordCredits"]["appearances"]] == ["Actor; Lyric debut", "Actor", "Actor"]
assert all(x["programUrl"].endswith(".pdf") and "michelleFordCredit" in x for x in ring_record["attendedPerformances"])
assert "role growing" in ring_record["memory"]["story"]
assert stage_research["interviewRoute"]["currentCategory"] == "musicals_and_plays"
assert stage_research["michelleFordAdditionalLyricResearch"]["attendanceStatus"] == "not_asked_not_confirmed"
carnegie_record=next(r for r in records if r["id"] == "concert-murray-state-choruses-at-carnegie-hall")
assert carnegie_record["status"] == "confirmed" and carnegie_record["visit"]["date"] == "2010-01-18"
assert "Michelle" in carnegie_record["memory"]["story"]
assert next(x for x in stage_research["candidates"] if x["id"] == "lyric-ring-performances")["confirmation"] == "three_individual_operas_confirmed"

# Film festival attendance and interview-hold integrity.
film=next(r for r in records if r["id"] == "film-american-fiction-denver-film-festival-2023")
assert film["status"] == "confirmed" and film["type"] == "film"
assert film["visit"]["date"] == "2023-11-03" and film["visit"]["precision"] == "day"
assert "Ellie Caulkins" in film["screening"]["location"]
assert film["screening"]["scheduledTime"] == "8:00 PM" and film["screening"]["exactArrivalTimeKnown"] is False
assert film["screening"]["scheduleSourceUrl"].startswith("https://www.denverfilm.org/")
assert next(v for v in venues if v["id"] == film["venueId"])["location"]["precision"] == "city-centroid"
assert next(x for x in stage_research["candidates"] if x["id"] == "denver-unknown-play")["followUpStatus"] == "awaiting_friends_reply"
assert stage_research["interviewRoute"]["nextQuestionId"] == "denver-wicked-2024"
assert any(a["id"] == film["id"] and a["category"] == "film" and a["status"] == "pending" for a in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"])
assert '<button type="button" data-type="film"' in (ROOT / "explore.html").read_text(encoding="utf-8")
assert '<option value="film">' in (ROOT / "timeline.html").read_text(encoding="utf-8")
assert '<option value="film">' in (ROOT / "map.html").read_text(encoding="utf-8")

# Concert chronology provenance: independent event research is not personal attendance proof.
concerts = [r for r in records if r["type"] == "concert"]
concert_audit = json.loads((ROOT / "data/concert-history-audit.json").read_text(encoding="utf-8"))
assert len(concerts) == 21
assert concert_audit["summary"]["totalConfirmedMusicExperiences"] == 21
assert concert_audit["summary"]["exactCalendarDates"] == 19
assert concert_audit["summary"]["multiDayFestivalWithoutSingleDate"] == 1
assert concert_audit["summary"]["externalEventMatches"] == 20
assert {r["id"] for r in concerts} == {x["experienceId"] for x in concert_audit["entries"]}
assert all(r["historicalEventVerification"]["status"] == "independently_corresponding_event_found" and r["sourceUrl"].startswith("https://") for r in concerts if r["id"] != "concert-hawthorne-heights")
assert next(r for r in concerts if r["id"] == "concert-hawthorne-heights")["historicalEventVerification"]["status"] == "attendance_confirmed_event_details_unresolved"
assert all(r["historicalEventVerification"]["note"].startswith("The source corroborates") for r in concerts if r["id"] != "concert-hawthorne-heights")
hawthorne = next(r for r in concerts if r["id"] == "concert-hawthorne-heights")
assert hawthorne["status"] == "confirmed" and hawthorne["visit"]["attendanceCertainty"] == "confirmed"
assert hawthorne["visit"]["date"] is None and hawthorne["visit"]["year"] is None
assert next(v for v in venues if v["id"] == hawthorne["venueId"])["location"] is None
assert concert_audit["summary"]["recordsWithoutSingleCalendarDate"] == 2
assert next(a for a in concert_audit["entries"] if a["experienceId"] == hawthorne["id"])["attendanceStatus"] == "confirmed_direct_user_statement"
assert any(x["id"] == hawthorne["id"] and x["status"] == "pending" for x in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"])
assembly = next(r for r in concerts if r["id"] == "concert-red-hot-chili-peppers")
assert next(v for v in venues if v["id"] == assembly["venueId"])["historicalName"] == "Assembly Hall"
lolla = next(r for r in concerts if r["id"] == "concert-lollapalooza-all-three-days")
assert lolla["visit"]["date"] is None and lolla["visit"]["timeWindow"]["startDate"] == "2007-08-03" and lolla["visit"]["timeWindow"]["endDate"] == "2007-08-05"
# Preserve direct Lollapalooza performer confirmations while leaving the rest unresolved.
lolla_acts = json.loads((ROOT / "data/lollapalooza-2007-interview.json").read_text(encoding="utf-8"))
assert len(lolla_acts["sets"]) > 100 and len(lolla_acts["days"]) == 3
assert lolla_acts["watchedArtistCount"] == 15
assert lolla_acts["interviewState"] == "paused_at_user_request_more_memories_unidentified"
assert len(lolla["attendedPerformers"]) == 15
assert {x["artist"] for x in lolla["attendedPerformers"]} == {x["artist"] for x in lolla_acts["confirmedArtists"]}
assert all(lolla_acts["answers"][x["setId"]] == "watched" for x in lolla_acts["confirmedArtists"])
assert lolla["performerInterview"]["unidentifiedAdditionalPerformers"] is True
assert all(x["setExtent"] == "unspecified" for x in lolla["attendedPerformers"])
assert concert_audit["entries"] and next(x for x in concert_audit["entries"] if x["experienceId"] == lolla["id"])["confirmedArtistsCount"] == 15

# Stage chronology preserves distinct performances and existing theater entries.
stage = [r for r in records if r["type"] in {"concert","opera","theater"}]
assert len(stage) == 30 and len([r for r in stage if r["title"].startswith("Lollapalooza")]) == 1
assert any(r["title"] == "The Book of Mormon" and r["visit"]["year"] == 2016 and r["visit"]["date"] is None for r in stage)
assert any(r["title"] == "SIX" and r["visit"]["year"] == 2023 and r["visit"]["date"] is None for r in stage)
assert any(r["type"] == "opera" and "Ring" in r["title"] for r in stage)
assert all(r["memory"]["story"] for r in stage)
theater_leads = json.loads((ROOT / "data/performance-leads.json").read_text(encoding="utf-8"))
assert any(x["id"] == "another-denver-show" for x in theater_leads["leads"])

# Precision and provenance in date presentation.
assert next(c for c in candidates if c["name"] == "PDT (Please Don't Tell)")["visitStatus"] == "maybe"
assert next(c for c in candidates if c["name"] == "The Dead Rabbit")["visitStatus"] == "not_visited"
assert next(c for c in candidates if c["name"] == "Existing Conditions")["visitStatus"] == "not_visited"
assert any(c["id"] == "lyric-ring-performances" for c in stage_research["candidates"])
date_app=(ROOT / "assets/app.js").read_text(encoding="utf-8")
assert "const readableDate=(d)=>" in date_app
assert "Historical notes & sources" in date_app
assert "Reservation evidence:" in date_app
assert "Production's engagement dates:" in date_app
assert "const dateMonth=" in date_app

# The performing-arts interview must preserve all published memories and keep research leads separate.
performance_leads=json.loads((ROOT / "data/performance-interview.json").read_text(encoding="utf-8"))
assert len(performance_leads["candidates"]) >= 9
assert len({c["id"] for c in performance_leads["candidates"]}) == len(performance_leads["candidates"])
assert any(c["id"] == "denver-unknown-play" for c in performance_leads["candidates"])
assert any(c["id"] == "denver-hamlet-2024" and c["confirmation"] == "unreviewed_candidate" for c in performance_leads["candidates"])
assert all(c["sourceUrl"].startswith("https://") for c in performance_leads["candidates"])
performance_page=(ROOT / "performance-interview.html").read_text(encoding="utf-8")
performance_js=(ROOT / "assets/performance-interview.js").read_text(encoding="utf-8")
assert "performance-candidates" in performance_page and "performance-notes" in performance_page
assert "performance-interview.js" in performance_page and "performance-interview.html" in (ROOT / "interview.html").read_text(encoding="utf-8")
assert "performance-interview.html" in (ROOT / "index.html").read_text(encoding="utf-8")
assert 'localStorage.setItem(storageKey' in performance_js
assert "preserve the entire card" in performance_js
assert "denver-unknown-play" in performance_js
assert {"The Book of Mormon", "SIX", "The Second City — Chicago holiday outing", "A Christmas Carol — Denver"}.issubset({x["title"] for x in stage})


# Provenance and geography integrity for the new Boston / Cape Cod memory lead.
assert {"Boston", "Cape Cod", "Cambridge, UK"}.issubset(interview_data["periods"])
assert any(lead["id"] == "boston-cape-cod-seafood-unknown"
           and lead["venueIdentityConfirmed"] is False
           and lead["publishAsExperience"] is False
           and lead["visitDate"] is None
           for lead in interview_data["memoryLeads"])
assert not any(r["title"].startswith("Unidentified excellent fish restaurant") for r in records)
# Bookings must not be treated as a user-confirmed dinner date.
assert all(r["visit"]["date"] is None for r in records if r["visit"].get("evidenceType") == "completed_reservation_only")
assert not any(r["status"] == "confirmed" and r["visit"]["attendanceCertainty"] == "not_independently_verified"
               for r in records if "attendanceCertainty" in r["visit"])

# Culture Passport prioritizes memory and approximate periods over exact booking days.
assert 'const isDining=["dining","bar"].includes(r.type);' in (ROOT / "assets/app.js").read_text(encoding="utf-8")
assert 'const allAreas=[...new Set([...included.map(x=>x.area),...Object.keys(db.periods||{})])];' in (ROOT / "assets/app.js").read_text(encoding="utf-8")
assert any(x["id"] == "cambridge-uk-restaurants-unknown" and x["publishAsExperience"] is False
           for x in interview_data["memoryLeads"])

# Story-first editorial expansion: source-linked venue history, not invented meal details.
featured_history = {r["title"]: r for r in records if r["status"] == "confirmed" and r.get("story", {}).get("paragraphs")}
assert {"North Pond", "Sauvage", "Gunther & Co.", "The Majestic Restaurant", "Manifesto"} <= set(featured_history)
for title in ("Sauvage", "Gunther & Co.", "The Majestic Restaurant", "Manifesto"):
    record = featured_history[title]
    story = record["story"]
    assert len(story["paragraphs"]) >= 2 and len(story["chapters"]) >= 2
    assert all(phase.get("year") and phase.get("title") and phase.get("detail") for phase in story["chapters"])
    assert all(src["url"].startswith("https://") and src["label"] for src in story["sourceUrls"])
    assert record["status"] == "confirmed"
assert featured_history["Sauvage"]["visit"].get("year") == 2021
assert featured_history["Gunther & Co."]["visit"].get("year") == 2020
assert featured_history["The Majestic Restaurant"]["visit"]["date"] is None
assert featured_history["Manifesto"]["visit"]["date"] is None

# Every stored point in the current city map has coherent, truthful precision.
cities = {}
for venue in venues:
    pos = venue["location"]
    if pos is None:
        # A known branch may still await trustworthy map coordinates.
        unmapped_cities = {
            "venue-hawthorne-heights-unidentified": "",
            "venue-butchers-daughter-west-hollywood": "West Hollywood",
            "venue-eagle-cambridge": "Cambridge",
            "venue-toms-town-kansas-city": "Kansas City",
            "venue-j-rieger-kansas-city": "Kansas City",
            "venue-kingston-arms-cambridge": "Cambridge",
            "venue-lidias-kansas-city": "Kansas City",
            "venue-rozzelle-court-kansas-city": "Kansas City",
            "venue-anchor-cambridge": "Cambridge",
            "venue-mill-pub-cambridge": "Cambridge",
            "venue-millworks-cambridge": "Cambridge",
            "venue-parkers-tavern-cambridge": "Cambridge",
            "venue-fitzbillies-original-trumpington-cambridge": "Cambridge",
            "venue-port-fonda-westport-kansas-city": "Kansas City",
            "venue-drastic-measures-shawnee-kansas": "Shawnee",
            "venue-la-marchande-new-york": "New York",
            "venue-the-campbell-grand-central-new-york": "New York",
            "venue-tonchin-midtown-new-york": "New York",
            "venue-801-chophouse-kansas-city-power-light": "Kansas City",
            "venue-westport-cafe-bar-kansas-city": "Kansas City",
            "venue-rye-plaza-kansas-city": "Kansas City",
            "venue-john-browns-underground-lawrence": "Lawrence",
            "venue-1900-barker-original-lawrence": "Lawrence",
        }
        assert venue["id"] in unmapped_cities, "Document venues awaiting trustworthy map coordinates"
        assert venue["city"] == unmapped_cities[venue["id"]]
        continue
    assert pos["precision"] == "city-centroid"
    assert isinstance(pos["lat"], (int, float)) and -90 <= pos["lat"] <= 90
    assert isinstance(pos["lng"], (int, float)) and -180 <= pos["lng"] <= 180
    city_key = (venue["city"], venue.get("region"), venue.get("country"))
    coord = (pos["lat"], pos["lng"])
    assert city_key not in cities or cities[city_key] == coord, (
        "Inconsistent city-level map coordinate: " + venue["name"]
    )
    cities[city_key] = coord

# Two user-confirmed Denver meals, approximate years, no invented exact dates.
sap = next(r for r in records if r["id"] == "dining-sap-sua-denver-2024")
fino = next(r for r in records if r["id"] == "dining-fino-denver-2026")
assert sap["visit"]["year"] == 2024 and sap["visit"]["date"] is None
assert fino["visit"]["year"] == 2026 and fino["visit"]["date"] is None
assert sap["status"] == fino["status"] == "confirmed"
assert sap["editorial"]["awardQualified"] is True and sap["editorial"]["featuredException"] is False
assert fino["editorial"]["awardQualified"] is False and fino["editorial"]["featuredException"] is True
assert fino.get("favorite") is False  # user requested inclusion, not a favorite designation
assert any(x["year"] == 2024 and x["category"] == "Best New Restaurant" and x["result"] == "semifinalist" for x in sap["recognitions"])
for name, record in (("Sap Sua", sap), ("FiNO", fino)):
    candidate = next(c for c in candidates if c["name"] == name and c["area"] == "Denver Metro")
    assert candidate["visitStatus"] == "confirmed" and candidate["confirmedVisitId"] == record["id"]
    assert any(x["id"] == record["id"] and x["status"] == "pending" for x in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"])
assert all(next(v for v in venues if v["id"] == r["venueId"])["location"]["precision"] == "city-centroid" for r in (sap,fino))

# User-confirmed Untitled, still unknown exact year; separate Cindy's remains unanswered.
untitled = next(r for r in records if r["id"] == "dining-untitled-supper-club-chicago-year-unknown")
assert untitled["status"] == "confirmed" and untitled["visit"]["year"] is None and untitled["visit"]["date"] is None
assert untitled["visit"]["possibleYears"] == [] and untitled["guide"]["verifiedEditions"] == [2019, 2020]
assert untitled["guide"]["distinction"] == "bib" and untitled["guide"]["stars"] == 0
assert untitled["guide"]["historicalVisitDistinction"] == "unknown_visit_year"
assert untitled["editorial"]["awardQualified"] is True
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Untitled Supper Club")["confirmedVisitId"] == untitled["id"]
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Untitled Supper Club")["visitStatus"] == "confirmed"
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Cindy's Rooftop")["visitStatus"] == "maybe"
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Cherry Circle Room")["visitStatus"] == "not_visited"
assert any(x["id"] == untitled["id"] and x["status"] == "pending"
           for x in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"])

# Cindy's Rooftop deliberately remains provisional after direct user reply.
cindy = next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Cindy's Rooftop")
assert cindy["visitStatus"] == "maybe"
assert "possibly visited" in cindy["reviewSource"]
assert "do not mark confirmed" in cindy["reviewSource"]
assert not any(r["title"] == "Cindy's Rooftop" and r["status"] == "confirmed" for r in records)
friend_chicago = next(l for l in interview_data["memoryLeads"] if l["id"] == "chicago-friend-untitled-cindys-unknown-years")
assert friend_chicago["unresolvedVenueNames"] == ["Cindy's Rooftop"]
assert "Cindy\'s Rooftop remains possibly visited" in friend_chicago["note"]
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Lost Lake")["visitStatus"] == "not_visited"

# Friend-recalled memories: intentionally curated, not independently attended.
recalled = [r for r in records if r["status"] == "recollected"]
assert {r["title"] for r in recalled} == {"Cindy's Rooftop", "The Library at Gilt Bar"}
assert all(r["editorial"]["userRequestedMemory"] is True and r["visit"]["date"] is None
           and r["visit"]["year"] is None and r["visit"]["attendanceCertainty"] == "not_independently_verified"
           for r in recalled)
assert all(r["editorial"]["collection"] == "friend_recalled_memory" for r in recalled)
assert cindy["visitStatus"] == "maybe"
assert cindy["memoryRecordId"] == next(r["id"] for r in recalled if r["title"] == "Cindy's Rooftop")
gilt = next(c for c in candidates if c["name"] == "The Library at Gilt Bar" and c["area"] == "Chicago")
assert gilt["visitStatus"] == "maybe"
assert gilt["memoryRecordId"] == next(r["id"] for r in recalled if r["title"] == "The Library at Gilt Bar")
assert next(r for r in recalled if r["title"] == "The Library at Gilt Bar")["editorial"]["awardQualified"] is False
assert all(any(x["id"] == r["id"] and x["status"] == "pending" for x in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"]) for r in recalled)
assert next(c for c in candidates if c["name"] == "Lost Lake" and c["area"] == "Chicago")["visitStatus"] == "not_visited"
# Empty Chicago checklist is an interview pause, not a series of non-attendance answers.
chapter = interview_data["interviewChapters"]["chicagoCocktailBars"]
assert chapter["state"] == "paused_by_user_for_now" and chapter["newConfirmedVisits"] == []
assert chapter["unansweredVenues"] == []
assert chapter["unansweredVenues"] == []
assert set(chapter["explicitlyNotVisitedAsOf"]) == chicago_six
assert all(next(c for c in candidates if c["area"] == "Chicago" and c["name"] == name)["visitStatus"] == "not_visited" for name in chapter["explicitlyNotVisitedAsOf"])

assert "const inCollection=" in (ROOT / "assets/app.js").read_text(encoding="utf-8")
assert 'record["status"] == "recollected"' in (ROOT / "scripts/build_public_preview.py").read_text(encoding="utf-8")
audit_recalled = json.loads((ROOT / "data/dining-awards-audit.json").read_text(encoding="utf-8"))["recollectedMemoryVenues"]
assert {x["experienceId"] for x in audit_recalled} == {r["id"] for r in recalled}

# Concurrent direct user interview explicitly excluded Lost Lake.
lost_lake = next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Lost Lake")
assert lost_lake["visitStatus"] == "not_visited"
assert "did not visit" in lost_lake["reviewSource"]
assert next(c for c in candidates if c["area"] == "Chicago" and c["name"] == "Kumiko")["visitStatus"] == "not_visited"
assert not any(r["title"] == "Lost Lake" for r in records)

# Watchlist is a durable, private audit trail for confirmed restaurants without
# verified qualifying awards. New memory-only dining entries must be added to it.
watch = json.loads((ROOT / "data/restaurant-award-watchlist.json").read_text(encoding="utf-8"))
assert watch["version"] == 1 and watch["classification"] == "private_research"
watch_entries = watch["entries"]
assert len(watch_entries) >= 16
assert len({w["id"] for w in watch_entries}) == len(watch_entries)
assert all(w["status"] in {"monitoring", "promoted"} for w in watch_entries)
assert all(w["reviewHistory"] and w["lastReviewedOn"] for w in watch_entries)
assert all(w["recognitionEvents"] for w in watch_entries if w["status"] == "promoted")
# Never accidentally drop a confirmed, non-qualified restaurant when curating the site.
nonqualified_venue_ids = {r["venueId"] for r in records
    if r["type"] == "dining" and r["status"] == "confirmed"
    and not r.get("editorial", {}).get("awardQualified", False)
    and r.get("curation", {}).get("status") != "qualifies"}
active_watch_ids = {w["venueId"] for w in watch_entries
    if w["status"] == "monitoring" and w["venueId"]}
assert nonqualified_venue_ids == active_watch_ids, (
    "Keep restaurant award watchlist synchronized with confirmed non-qualified dining records",
    sorted(nonqualified_venue_ids ^ active_watch_ids))
# Preserve separately confirmed archive-only restaurant visits from the historical audit.
audit_confirmed = json.loads((ROOT / "data/dining-awards-audit.json").read_text(encoding="utf-8"))["confirmedArchiveOnly"]
archive_only_names = {v["name"] for v in audit_confirmed if v["name"] != "J-Bar (Hotel Jerome)"}
assert archive_only_names.issubset({w["venueName"] for w in watch_entries})

# Expanded Michelin and James Beard recognition audit must cover every confirmed restaurant.
expanded = json.loads((ROOT / "data/expanded-recognition-audit-2026-10-27.json").read_text(encoding="utf-8"))
assert expanded["schemaVersion"] == 1 and expanded["classification"] == "private_research"
expanded_rows = expanded["confirmedRestaurants"]
assert len(expanded_rows) == expanded["scope"]["restaurantEntriesTracked"]
pending_recognition_reviews = sum(r.get("recognitionReviewStatus") == "pending" for r in expanded_rows)
assert pending_recognition_reviews == expanded["scope"]["restaurantEntriesPendingRecognitionReview"]
assert len(expanded_rows) == expanded["scope"]["restaurantEntriesReviewed"] + pending_recognition_reviews
assert len({(r["venueId"] or "archive:"+r["restaurantName"]) for r in expanded_rows}) == len(expanded_rows)
confirmed_dining_venue_ids = {r["venueId"] for r in records if r["type"] == "dining" and r["status"] == "confirmed"}
assert confirmed_dining_venue_ids == {r["venueId"] for r in expanded_rows if r["venueId"]}
archived_not_in_records = {x["name"] for x in audit_confirmed
    if x["name"] != "J-Bar (Hotel Jerome)" and
    x["name"] not in {r["title"] for r in records if r["type"] == "dining" and r["status"] == "confirmed"}}
assert archived_not_in_records == {x["restaurantName"] for x in expanded_rows if x["venueId"] is None}
tier_names = {"formal_michelin_jbf_recognition", "official_program_or_editorial_connection",
    "personal_featured_exception", "archived_pending_recognition"}
assert {x["collectionTier"] for x in expanded_rows} <= tier_names
assert sum(expanded["countsByTier"].values()) == len(expanded_rows)
assert all(expanded["countsByTier"][tier] ==
    sum(r["collectionTier"] == tier for r in expanded_rows)
    for tier in expanded["countsByTier"])
for row in expanded_rows:
    if row["venueId"] is None:
        assert row["collectionTier"] == "archived_pending_recognition"
        continue
    experience = next(r for r in records if r["venueId"] == row["venueId"] and r["type"] == "dining")
    assert row["formalAwardOrGuideQualified"] == bool(experience["editorial"].get("awardQualified"))
    assert row["officialProgramConnection"] == bool(experience["editorial"].get("officialFeature"))
    assert row["personalFeaturedException"] == bool(experience["editorial"].get("featuredException"))
    assert set(row["experienceIds"]) == {r["id"] for r in records
        if r["type"] == "dining" and r["status"] == "confirmed" and r["venueId"] == row["venueId"]}
    assert all(url.startswith("https://") for url in row["officialSourceUrls"])
    if row["collectionTier"] == "official_program_or_editorial_connection":
        assert experience["editorial"]["officialFeature"] is True
        assert experience["editorial"]["awardQualified"] is False
        assert row["officialFeatures"]
    if row["collectionTier"] == "archived_pending_recognition":
        assert not experience["editorial"].get("awardQualified")
    if row.get("recognitionReviewStatus") == "pending":
        assert row["collectionTier"] == "archived_pending_recognition"
        assert row["reviewedOn"] is None
        assert not row["formalRecognitions"] and not row["officialFeatures"]
assert next(x for x in candidates if x["name"] == "Soupçon" and x["area"] == "Crested Butte")["visitStatus"] == "maybe"
assert all(not (x["restaurantName"] == "Soupçon") for x in expanded_rows)
assert {r["restaurantName"] for r in expanded_rows if r["collectionTier"] == "official_program_or_editorial_connection"} == {
    "Uchi Denver", "Jack Stack Barbecue (Overland Park)", "Pierpont's at Union Station",
    "Lidia's Kansas City", "Rozzelle Court Restaurant"}

# NYC dinner: confirm the experience from the user's statement, independently
# of an award or reservation, and attribute the professional honor precisely.
la_marchande = next(r for r in records if r["id"] == "dining-la-marchande-new-york-2026-10-30")
assert la_marchande["status"] == "confirmed" and la_marchande["type"] == "dining"
assert la_marchande["visit"]["date"] == "2026-10-30" and la_marchande["visit"]["precision"] == "day"
assert la_marchande["visit"]["evidenceType"] == "direct_user_recollection"
assert la_marchande["favorite"] is False and la_marchande["editorial"]["awardQualified"] is True
assert la_marchande["curation"]["verifiedForPublication"] is False
assert len(la_marchande["recognitions"]) == 1
la_marchande_award = la_marchande["recognitions"][0]
assert la_marchande_award["organization"] == "James Beard Foundation"
assert la_marchande_award["category"] == "Outstanding Professional in Beverage Service"
assert la_marchande_award["recipient"] == "Amy Racine" and la_marchande_award["year"] == 2026
assert la_marchande_award["result"] == "semifinalist"
assert la_marchande_award["timingRelativeToVisit"] == "before_visit"
assert la_marchande["guide"]["stars"] == 0 and la_marchande["guide"]["distinction"] == "not_verified"
la_marchande_candidate = next(c for c in candidates if c["id"] == "candidate-new-york-city-la-marchande")
assert la_marchande_candidate["visitStatus"] == "confirmed"
assert la_marchande_candidate["confirmedVisitId"] == la_marchande["id"]
assert la_marchande_candidate["screening"]["status"] == "award_qualified"
assert any(x["venueId"] == la_marchande["venueId"] and x["recognitionStatus"] == "qualifies"
           for x in aud["publishedVenues"])
assert any(x["venueId"] == la_marchande["venueId"]
           and x["collectionTier"] == "formal_michelin_jbf_recognition"
           and x["formalAwardOrGuideQualified"] for x in expanded_rows)
la_marchande_review = next(x for x in json.loads(
    (ROOT / "data/publication-review.json").read_text(encoding="utf-8")
)["reviewedRecords"] if x["id"] == la_marchande["id"])
assert la_marchande_review["status"] == "pending"
assert la_marchande_review["approvedDigest"] is None

# Website incorporation preserves confirmed visits, distinct recognition and pending review.
incorporated_ids = ["dining-lidias-kansas-city-2015-2019","dining-rozzelle-court-kansas-city-date-unknown","bar-eagle-cambridge-visit-date-unknown","bar-anchor-cambridge-visit-date-unknown","bar-mill-pub-cambridge-visit-date-unknown","dining-millworks-cambridge-visit-date-unknown","dining-parkers-tavern-cambridge-date-unknown","bar-parkers-tavern-cambridge-date-unknown","dining-fitzbillies-trumpington-cambridge-date-unknown","bar-kingston-arms-cambridge-date-unknown"]
from build_public_preview import visitor_dataset
visitor_ids = {r["id"] for r in visitor_dataset()["records"]}
assert set(incorporated_ids) <= visitor_ids
for cid in incorporated_ids:
    rec = next(r for r in records if r["id"] == cid)
    assert rec["status"] == "confirmed" and not rec["editorial"]["awardQualified"]
    assert rec["visit"]["date"] is None
    approval = next(a for a in json.loads((ROOT / "data/publication-review.json").read_text())["reviewedRecords"] if a["id"] == cid)
    assert approval["status"] == "pending" and approval["approvedDigest"] is None
for title in ("The Mill (pub)", "The Kingston Arms", "The Eagle"):
    rec = next(r for r in records if r["title"] == title)
    assert any(a["organization"] == "CAMRA" and a["sourceUrl"].startswith("https://camra.org.uk/") for a in rec["recognitions"])
assert next(r for r in records if r["id"] == "dining-lidias-kansas-city-2015-2019")["visit"]["possibleYears"] == [2015, 2016, 2017, 2018, 2019]

# A withdrawn venue identification must never remain a confirmed visitor story.
assert not any(r["id"] == "bar-drastic-measures-shawnee-kansas" for r in records)
assert "bar-drastic-measures-shawnee-kansas" not in visitor_ids
withdrawn_bar = next(c for c in candidates if c["id"] == "candidate-kansas-city-metro-drastic-measures")
assert withdrawn_bar["visitStatus"] == "unreviewed" and "confirmedVisitId" not in withdrawn_bar
assert withdrawn_bar["correctionHistory"][-1]["previousAnswer"]["withdrawn"] is True
unidentified_bar = next(x for x in interview_data["memoryLeads"] if x["id"] == "kc-unidentified-bar-formerly-misidentified-drastic-measures")
assert unidentified_bar["publishAsExperience"] is False and unidentified_bar["venueIdentityConfirmed"] is False

# Distillery confirmations and venue-specific recognition must remain separate.
toms = next(r for r in records if r["id"] == "bar-toms-town-kansas-city-multiple-visits")
jrieger = next(r for r in records if r["id"] == "bar-j-rieger-kansas-city-multiple-visits")
assert toms["status"] == jrieger["status"] == "confirmed"
assert toms["visit"]["repeatVisits"] and jrieger["visit"]["repeatVisits"]
assert not toms["editorial"]["awardQualified"] and not jrieger["editorial"]["awardQualified"]
assert toms["officialFeatures"][0]["recognitionType"] == "beverage_supplier"
assert toms["id"] in visitor_ids and jrieger["id"] in visitor_ids
assert jrieger["editorial"]["culturalSpotlight"] is True
assert jrieger["editorial"]["awardQualified"] is False
assert {x["title"] for x in jrieger["onSiteExperiences"]} == {
    "Sippin' Santa", "Electric Park Garden Bar", "Monogram Lounge",
    "The Tasting Room", "The Hey! Hey! Club"
}
assert all(x["visitStatus"] == "confirmed" and x["visitDate"] is None
           for x in jrieger["onSiteExperiences"])
rieger_experiences = {x["id"]: x for x in jrieger["onSiteExperiences"]}
assert not rieger_experiences["j-rieger-sippin-santa"]["recognitions"]
assert not rieger_experiences["j-rieger-monogram-lounge"]["recognitions"]
assert len(jrieger["onSiteExperiences"]) == 5
tasting_room = rieger_experiences["j-rieger-tasting-room"]
assert tasting_room["visitStatus"] == "confirmed" and tasting_room["visitDate"] is None
assert tasting_room["experienceType"] == "distillery_tasting_room"
assert not tasting_room["recognitions"]
assert tasting_room["sources"] and all(x["url"].startswith("https://")
                                     for x in tasting_room["sources"])
assert "tour" in tasting_room["description"] and "not been established" in tasting_room["description"]

assert {x["organization"] for x in rieger_experiences["j-rieger-electric-park"]["recognitions"]} == {
    "AIA Kansas City", "Kansas City Business Journal"
}
hey_honor = rieger_experiences["j-rieger-hey-hey-club"]["recognitions"]
assert len(hey_honor) == 1 and hey_honor[0]["year"] == 2020
assert hey_honor[0]["result"] == "Regional Top 10 honoree"
assert all(x["sourceUrl"].startswith("https://") for ex in jrieger["onSiteExperiences"]
           for x in ex["recognitions"])
assert {x["organization"] for x in jrieger["siteRecognitions"]} == {
    "Missouri Preservation", "Historic Kansas City"
}
assert set(jrieger["relatedExperienceIds"]) == {
    "bar-manifesto-kansas-city", "dining-rieger-hotel-grill-exchange-kansas-city"
}

assert next(c for c in candidates if c["id"] == "candidate-kc-lifted-spirits-distillery")["visitStatus"] == "maybe"

# The Campbell is an attended November 1 bar visit, corroborated by the dated
# Resy booking and direct user confirmation. Editorial selections do not become awards.
campbell_record = next(r for r in records if r["id"] == "bar-the-campbell-grand-central-new-york")
assert campbell_record["type"] == "bar" and campbell_record["status"] == "confirmed"
assert campbell_record["visit"]["date"] == "2026-11-01"
assert campbell_record["visit"]["evidenceType"] == "direct_user_confirmation_and_dated_reservation_screenshot"
assert campbell_record["visit"]["linkedReservationId"] == "the-campbell-new-york-2026-11-01"
assert campbell_record["editorial"]["featuredException"] is True
assert campbell_record["editorial"]["awardQualified"] is False
assert campbell_record["editorial"]["collection"] == "editorially_recognized_bar"
assert campbell_record["recognitions"] == [] and len(campbell_record["editorialRecognitions"]) == 3
assert booked_campbell["confirmedVisitId"] == campbell_record["id"]
assert booked_campbell["confirmedVisitDate"] == "2026-11-01"
assert future_campbell["confirmedVisitId"] == campbell_record["id"]
assert next(c for c in candidates if c["name"] == "The Campbell")["confirmedVisitId"] == campbell_record["id"]
assert any(v["venueId"] == campbell_record["venueId"] for v in aud["publishedVenues"])
from build_public_preview import visitor_dataset as campbell_visitor_dataset
assert any(r["id"] == campbell_record["id"] for r in campbell_visitor_dataset()["records"])
assert any(item["id"] == campbell_record["id"] and item["status"] == "pending"
           for item in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"])

# Tonchin: user-submitted same-day restaurant photo plus original booked
# reservation and instruction to add it establish the visited date.
tonchin_record = next(r for r in records if r["id"] == "dining-tonchin-new-york-2026-11-01")
assert tonchin_record["type"] == "dining" and tonchin_record["status"] == "confirmed"
assert tonchin_record["visit"]["date"] == "2026-11-01" and tonchin_record["visit"]["precision"] == "day"
assert tonchin_record["visit"]["linkedReservationId"] == "tonchin-new-york-2026-11-01"
assert tonchin_record["visit"]["evidenceType"] == "direct_user_same_day_photo_and_confirmed_reservation"
assert tonchin_record["visit"]["photoEvidence"]["sourceFilename"] == "IMG_3661.jpeg"
assert tonchin_record["visit"]["photoEvidence"]["imageBytesArchivedInGitHub"] is False
assert tonchin_record["visit"]["arrivalTime"] is None
assert tonchin_record["visit"]["actualPartySize"] is None
assert tonchin_record["editorial"]["awardQualified"] is True
assert tonchin_record["editorial"]["featuredException"] is False
assert tonchin_record["guide"]["distinction"] == "bib" and tonchin_record["guide"]["stars"] == 0
assert tonchin_record["guide"]["verifiedEditions"] == [2025]
assert tonchin_record["recognitions"][0]["organization"] == "MICHELIN Guide"
assert tonchin_record["recognitions"][0]["result"] == "Bib Gourmand"
assert booked_tonchin["confirmedVisitId"] == tonchin_record["id"]
assert booked_tonchin["confirmedVisitDate"] == "2026-11-01"
assert booked_tonchin["photoEvidence"]["sourceFilename"] == "IMG_3661.jpeg"
assert future_tonchin["confirmedVisitId"] == tonchin_record["id"]
assert next(x for x in candidates if x["id"] == "candidate-new-york-city-tonchin-midtown")["confirmedVisitId"] == tonchin_record["id"]
assert any(v["venueId"] == tonchin_record["venueId"] and v["recognitionStatus"] == "qualifies" for v in aud["publishedVenues"])
assert any(v["venueId"] == tonchin_record["venueId"] and v["formalAwardOrGuideQualified"] and v["collectionTier"] == "formal_michelin_jbf_recognition" for v in expanded_rows)
from build_public_preview import visitor_dataset as tonchin_visitor_dataset
assert any(r["id"] == tonchin_record["id"] for r in tonchin_visitor_dataset()["records"])
assert any(item["id"] == tonchin_record["id"] and item["status"] == "pending" and item["approvedDigest"] is None
           for item in json.loads((ROOT / "data/publication-review.json").read_text(encoding="utf-8"))["reviewedRecords"])
