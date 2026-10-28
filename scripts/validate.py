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
assert all(c["sourceUrl"].startswith("https://") for c in candidates)
assert all(c["visitStatus"] in {"confirmed", "not_visited", "maybe", "unreviewed"} for c in candidates)
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
assert len([r for r in records if r["type"] == "bar" and r["status"] == "confirmed"]) == 3  # J-Bar added as archive-only
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
# South Bay interview: three MAYBE answers are not evidence of visits.
# Sushi Inaba is the next question and remains unreviewed. Its hidden Torrance
# omakase counter must not be conflated with regular I-naba or the older location.
space_park = [c for c in candidates if c["area"] == "South Bay / Space Park"]
assert len(space_park) == 8
assert all(c["screening"]["status"] == "award_qualified" for c in space_park)
maybe_names = {"Manhattan Beach Post", "Fishing with Dynamite", "RYLA"}
assert {c["name"] for c in space_park if c["visitStatus"] == "maybe"} == maybe_names
assert all(c["visitStatus"] == "unreviewed" for c in space_park if c["name"] not in maybe_names)
assert all(next(c for c in space_park if c["name"] == n)["lastInterviewResponse"] == "Maybe visited."
    for n in maybe_names)
assert all(not any(r["title"] == c["name"] and r["status"] == "confirmed" for r in records)
    for c in space_park)
sushi_inaba = next(c for c in space_park if c["id"] == "candidate-space-park-sushi-inaba-torrance")
assert sushi_inaba["visitStatus"] == "unreviewed"
assert "I-naba" in sushi_inaba["interviewCue"]
assert "Manhattan Beach" in sushi_inaba["interviewCue"]
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["namedConfirmedVisits"] == 0
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["maybeVisitedCandidates"] == 3
assert set(interview_data["interviewChapters"]["spaceParkSouthBay"]["maybeVisitedNames"]) == maybe_names
assert interview_data["interviewChapters"]["spaceParkSouthBay"]["nextCandidate"] == "Sushi Inaba (Torrance)"
assert interview_data["interviewProgress"]["currentBatch"]["area"] == "South Bay / Space Park"
assert interview_data["interviewProgress"]["currentBatch"]["candidateNames"][0] == "Sushi Inaba (Torrance)"
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
assert all(c["visitStatus"] == "unreviewed" for c in candidates
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
    assert match["visitStatus"] == "unreviewed"
    assert match["screening"]["basis"] == "michelin"

active_batch = interview_data["interviewProgress"]["currentBatch"]
assert active_batch["area"] in {c["area"] for c in candidates}
assert all(any(c["area"] == active_batch["area"] and c["name"] == name for c in candidates) for name in active_batch["candidateNames"])
kc_not_recalled = ["Corvino Supper Club & Tasting Room", "The Antler Room", "Bluestem", "Rye (Leawood)", "The Town Company", "Fox & Pearl", "Waldo Thai", "The American Restaurant"]
kc_reviewed = [c for c in candidates if c["area"] == "Kansas City Metro" and (c["name"] in kc_not_recalled or c["name"] == "Fox and Pearl")]
assert len(kc_reviewed) == 9
assert all(c["visitStatus"] == "not_visited" and c["reviewCertainty"] == "tentative_negative" for c in kc_reviewed)
assert active_batch["status"] in {"ready_for_visual_screening", "awaiting_user_response"}

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
                   
                   ("Fern Bar", "Kansas City Metro"), ("Wild Child", "Kansas City Metro")]:
    candidate = next(c for c in candidates if c["name"] == name and c["area"] == area)
    assert candidate["visitStatus"] == "unreviewed"
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
assert len(reservations) == 20 and len({e["id"] for e in reservations}) == 20
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
assert len(evidence["entries"]) == 20 and len(evidence["rows"]) == 52 and len({r["name"] for r in evidence["rows"]}) == 46
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
assert all(x["visitStatus"] == "unreviewed" for x in candidates if x["id"] in {
    "candidate-la-joy-highland-park", "candidate-la-pine-crane-dtla"
})
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
        assert venue["id"] == "venue-hawthorne-heights-unidentified" and not venue["city"]
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
assert len(expanded_rows) == expanded["scope"]["restaurantEntriesReviewed"]
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
assert next(x for x in candidates if x["name"] == "Soupçon" and x["area"] == "Crested Butte")["visitStatus"] == "maybe"
assert all(not (x["restaurantName"] == "Soupçon") for x in expanded_rows)
assert {r["restaurantName"] for r in expanded_rows if r["collectionTier"] == "official_program_or_editorial_connection"} == {
    "Uchi Denver", "Jack Stack Barbecue (Overland Park)"}
