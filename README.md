# Culture Passport

A standalone cultural experience archive for restaurants, cocktail bars, concerts, opera, theater, and film festivals.

**Canonical repository:** `alexlford/culture-passport`

**Planned public site:** `https://culture.alexlford.com` (DNS and GitHub Pages still require configuration). This code is **not** a chapter of the Life Map. Work, education, career, and personal geography remain in `alexlford/life-map`.

## Experience-first editorial rules

- **Start with the memory.** Atmosphere, companions, venue history, chefs/artists, and what made an evening memorable matter most.
- **Approximate years are sufficient.** Store an exact date only when it is meaningful to the memory and actually known; never promote a reservation date to an unquestioned meal date.
- **Distinguish evidence.** `status=confirmed` means an actual experience was recalled, while `reservation_only` denotes a research lead and must not appear in confirmed totals.
- **Michelin and James Beard are inclusion guides, not the entire story.** Maintain distinction, year, category, recipient, precise venue and an official source; never borrow honors across branches. In addition to recognized venues and explicit personal exceptions, a separate **Official Foundation / Guide Connection** tier permits directly documented Michelin/JBF editorial coverage, awards-watch profiles, TasteTwenty selections and actual JBF event/program participation, with its relationship clearly labeled. These connections are never called award wins or nominations.
- **Keep an award watchlist.** Every confirmed restaurant that lacks verified venue-specific qualifying recognition remains in the private restaurant award watchlist, even if it is featured as a favorite. Re-audit quarterly, preserve each screening, and retain promoted restaurants with their old memories. Do not treat absence of verified recognition as proof that a venue has never won any award.
- **Interviews are research, not attendance assertions.** Possible, negative, and unreviewed responses remain separate from confirmed experiences. Never add Le Fou Frog to the published collection: the user explicitly excluded it unless qualifying recognition is verified.
- **Privacy by default.** Include only memories explicitly shared for this website. Avoid conflating bookers, diners, artists, and people in photos.

## Files

- `index.html`, `explore.html`, `timeline.html`, `map.html`, `record.html` — main experience pages.
- `interview.html`, `performance-interview.html` — restaurant and performing-arts reconstruction.
- `data/records.json` — canonical experience and venue records (including archived research-only entries).
- `data/interview.json`, `data/performance-interview.json`, `data/performance-leads.json` — research queues.
- `data/dining-awards-audit.json`, `data/reservation-evidence.json` — source ledgers, not competing databases.
- `data/restaurant-award-watchlist.json` — **private, permanent, quarterly re-audit ledger** for confirmed restaurants not currently award-qualified. It includes archive-only barbecue and St. Louis memories, and keeps award promotion history. No additional public page is created from this file.
- `assets/` — independent stylesheet and JavaScript, with no runtime dependency on the Life Map application.

## Broader Michelin / James Beard curation (October 2026)

**Always lead with a direct, confirmed visit.** A restaurant can appear in one of four distinctly named tiers. The stored claims must link to official Michelin Guide or James Beard Foundation resources, not only third-party lists:

1. **Award winners / Michelin distinctions:** Stars, Bib Gourmand, Michelin Green Star and applicable special awards, or James Beard winners. Display the exact category and recipient; a chef award only applies to the restaurant where the chef earned it.
2. **Official recognition, including historical:** Michelin Selected/Recommended or the historical Plate, and James Beard semifinalists and finalists for the named restaurant or chef at that restaurant. Do not imply a Selected listing is a Star.
3. **Official Foundation / Guide Connection:** Direct venue/chef ties to Michelin editorial guides, profiles and 'ones to watch' coverage, James Beard TasteTwenty cohorts, Foundation features, and Foundation-associated events (e.g., a hosted benefit or a team featured at the Beard House). Always say *program/event/editorial connection* and give year, named chef, event location and source. **An event, a feature, or participation is not an award, endorsement, nomination or Michelin distinction**. The public UI must display this category separately from award badges and recognized-visit statistics.
4. **Personal highlights:** Explicit favorites and exceptional memories, e.g., the Allred's anniversary dinner, eligible to display without external honors and clearly marked as personal exceptions.

**Strict attribution:** If the user has visited one franchise location but an official feature concerns another, retain it as *restaurant-group context* in the private watchlist only; never imply the visited branch was featured. A guest chef from the same named location at an offsite Beard House dinner is a legitimate documented **chef-team connection**, not an event *held at* the restaurant, and never a Beard Award. Repeated visits may be stored as a single experience with unknown dates rather than fabricated individual calendar dates.

**Award watchlist remains permanent:** Every confirmed restaurant without directly verified qualifying award/Guide recognition stays in the quarterly private watchlist even when included via a Foundation program or personal exception. Record newly discovered official links in its historical review ledger. Michelin editorial recognition and JBF program participation are tracked in `officialFeatures` on canonical records, independently of `recognitions` and `guide`. Only elevate `editorial.awardQualified` after confirming an actual Guide inclusion or qualifying Beard award stage.

**Public release remains unapproved.** The visitor-preview exporter may select directly confirmed `officialFeature` restaurants, but publication-review entries must stay `pending` until explicitly approved. Do not expose private interview notes or complete watchlists on the public website.

## Quarterly restaurant award review

Review the **private** `data/restaurant-award-watchlist.json` against the official Michelin Guide (including locality and historical editions) and James Beard Foundation winner, finalist and semifinalist announcements. Preserve the separate evidence of each visit, the original visit period, recognition year, precise award recipient/location, a source link, the date audited, and the full review history. A restaurant may have post-visit recognition, but must not be described as award-winning *at the time of the meal* without evidence. If it newly qualifies, update its canonical `data/records.json` editorial and curation metadata, append the primary award evidence to `data/dining-awards-audit.json`, and mark its watchlist entry `promoted` without deleting it. Interview `maybe`, `not_visited`, and reservation-only venues do not enter the watchlist. Bars (including J-Bar) stay in their own bar/research evidence.

## Development

```bash
python scripts/validate.py
node --check assets/app.js
node --check assets/performance-interview.js
python -m http.server 8000
```

Open `http://localhost:8000/`. Continuous integration checks source data and JavaScript on pull requests and updates to `main`.

## Deployment

The GitHub Pages deployment workflow is deliberately **manual** until Pages hosting and the domain are configured. In the repository:

1. Publish or otherwise enable GitHub Pages eligibility for `alexlford/culture-passport` (currently a private repository).
2. Open **Settings → Pages**, select **GitHub Actions** as the build/deployment source.
3. In the repository's **Actions** tab run **Deploy Culture Passport**. Verify its generated GitHub Pages site and the Home, Explore, Timeline, Map, Record, and Interview pages.
4. Add DNS `CNAME culture → alexlford.github.io` at the domain registrar and configure `culture.alexlford.com` in repository **Settings → Pages → Custom domain**. Verify certificate issuance and HTTPS.
5. Once the standalone site is live, the legacy Life Map culture-specific content can redirect to the new address. Keep all career/map and work embeds independent.

There is intentionally no `CNAME` in the Life Map repository for this Culture domain.

## Pre-publication quality gate

Continuous integration runs `scripts/audit_static_site.py` alongside the existing record validator. The new audit checks all seven HTML routes, internal links, assets, explicit performance record deep links, map library loading order, required dynamic JSON datasets, and likely accidentally committed credentials or email addresses. It also checks that all seven pages remain marked **`noindex, nofollow` during staging**. This does **not** replace visual browser/mobile testing.

**Privacy checkpoint — before changing this repository from Private to Public:**

- [ ] Review the complete repository **including Git history**. Public visibility exposes research/interview answers, source notes, reservation dates and party sizes, approximate personal chronology, and files removed in later commits.
- [ ] Decide which private interview responses and historical reservation notes may be published. A `noindex` meta tag only affects search indexing; it does not prevent anyone from downloading published pages or public repository files.
- [ ] If any source needs to remain confidential, separate it into a genuinely private repository or storage **before changing visibility**. Deleting a file in a new commit does not erase it from public Git history.
- [ ] Run CI again and perform real phone/desktop browser QA after configuring Pages. Staging tests cannot establish the visible page is bug-free.
- [ ] Only after confirming desired public visibility should you decide whether to keep or remove `noindex`.

The deployment workflow is intentionally manual until the public launch decision. In the meantime, CI and source fixes can proceed safely in this private repository.

## Mobile and keyboard navigation (October 2026)

- All seven pages include a keyboard-accessible **Skip to content** link and main landmark.
- iPhone-sized layouts use five equal navigation cells with at least 44px tap targets, scaled headlines and safe-area padding.
- Mobile text inputs use 16px text to prevent unwanted Safari zoom; existing interview choices retain focus and scroll positions.
- Static CI asserts the skip links, dynamic record headings, locally valid links, and presence of responsive style safeguards. **Actual device and screen-reader testing is still required** once a browser test environment is available.

## Privacy release recommendation

Run `python scripts/report_publication_risk.py` for an aggregate inventory of personal stories, reservation source rows, and historical research answers. This script never prints individual records.

**Prefer keeping this canonical repository private.** If you want a public GitHub Pages website, the safest option is a clean, separate distribution repository containing only approved public pages and datasets, rather than making the existing source repository public. Git history in a newly public source repository is accessible even if data files are subsequently deleted. A staging `noindex` tag is not access control. Public release requires explicit review of which memories, names, research notes and reservation details belong in the public experience.

## Clean visitor export (review-only until approved)

The script `python scripts/build_public_preview.py --check` builds a temporary static preview and runs integrity checks without publishing anything. `python scripts/build_public_preview.py` writes to `dist/` (Git-ignored). The **manual** Pages workflow will publish `dist/`, not the entire repository.

The visitor export contains only Home, Explore, Timeline, Map, experience pages, app assets, and **confirmed curated experiences** (award-qualified restaurants/bars, explicit personal favorites, and arts). It omits interview pages, candidate lists, reservation ledgers, booking-only records, exclusion records, old source notes, provenance fields and the entire research directory. This allows the future public site to focus on stories and venues instead of private reconstruction notes.

**Not yet approved for public release:** individual memory/story text, venue geography, and content in `data/records.json` still require human privacy review. Running the exporter does not cleanse or protect the current repository's Git history. Keep the existing source repository **private**; prefer deployment from private Pages (if account settings support it) or a new *clean public distribution repository* containing only the reviewed `dist/` contents. Do not make the canonical history public merely to enable Pages.

The visitor build is a conservative public-facing proposal, **not a decision to remove the private interview workflow**: you can continue using the private research pages and interview answers in this source repository.

## Visitor story and map improvements — October 2026

- Experience pages prioritize the user's own recollection and approximate period, followed by an at-a-glance context row and **optional long-form venue history**. The long-form section is shown only when the source record contains actual narrative paragraphs, sourced venue chronology, and historical references. No missing companions, chefs or dishes are invented.
- North Pond is the first richer editorial story already supported by the canonical data. Its historically grounded building/chef timeline and source links are rendered automatically. Other entries will develop similarly only as researched details become available.
- City maps now present filtered category totals and an accessible expandable city directory, with direct links to experiences. Record pages have direct city-level map and Explore links; Explore honors the city in the URL.
- Map markers remain explicitly **city-centroid** locations. Zoom levels are intentionally capped at city scope and the interface never claims those pins are the venue doorways. Replacing them with exact venue points remains a separate task requiring trustworthy coordinate sources.
- The clean public preview uses the same component logic, but excludes private research, reservation and interview files. New story material still needs privacy approval before publishing. True rendered desktop/iPhone visual QA remains outstanding until browser-based testing is available.

## Four memory-led restaurant histories (October 2026)

Four previously confirmed venue memories now include separately sourced long-form background (not new first-person claims): **Sauvage** (2020 opening and January 2021 tasting-menu memory), **Gunther & Co.** (historic brewery and Valentine's Day 2020), **The Majestic** (1911 saloon, Prohibition-era jazz room, and current steakhouse), and **Manifesto** (Ryan Maybee's 2009 speakeasy and cocktail-scene legacy). Each story clearly separates the user's firsthand recollection from researched restaurant and chef history, with source links and a compact chronology. **North Pond** already had a rich history and is now displayed by the updated experience-page renderer.

The site's approximate-visit-period rule is unchanged. No meal companions, dishes ordered or exact unknown nights were invented. Restaurant honors were not reclassified; the separate Michelin/James Beard eligibility audit remains on hold.

## Private rendered-browser QA (October 2026)

Continuous integration now runs a **real Chromium browser** against the locally hosted `dist/` visitor preview at iPhone-sized (390px) and desktop (1440px) viewports. It checks Home, Explore, Timeline, Map and a fully rendered experience page, verifies search, map filters, venue lookup links, keyboard skip navigation, known historical story content, and horizontal overflow. Ten full-page screenshots are uploaded as **private GitHub Actions artifacts**, retained for seven days.

The browser tests never publish the site, change GitHub visibility, or move research records into the public export. They provide executable layout/interaction evidence, not a substitute for manual review on a real iPhone or an approved release. Source/frontend code remains private.

Record pages offer a *venue-name lookup* in Google Maps when a venue name and city are known, rather than treating city-centroid dots as door-level coordinates. Search results can be outdated for closed or relocated venues and must not be presented as verified precise venue GPS.

## Graceful map degradation and visitor-data field safety (October 2026)

- If the Carto basemap provider is unavailable, an inline explanation appears on the map, with a keyboard-accessible link to the independent city directory. This is tested by deliberately blocking basemap tile requests during the private Chromium run; a successful tile load hides the fallback.
- The city directory remains populated and functional without basemap tiles. No map markers are represented as GPS-verified restaurant entrance locations: all stored points retain `city-centroid` precision.
- The canonical source validator checks latitude/longitude bounds and that all venue entries for the same city use consistent city-center coordinates. Any future precise venue map will need a separately verified provenance and schema.
- The visitor export now checks **nested objects as well as top-level records** for forbidden internal research fields. Internal production attendance date fields are explicitly excluded from the visitor version. This is a field-level safety gate, not editorial approval of the public stories or Git history.
- Publication remains **manual and gated**, with the repository private. The stand-alone domain, live map-provider tiles, and in-person iPhone Safari check remain external dependencies.

## Visitor-by-visitor publication review (October 2026)

A private, explicit **48-record editorial approval manifest** now lives at `data/publication-review.json`. Every proposed visitor experience begins with `status: pending`. Nobody has approved these experiences for public release yet.

Continuous integration validates that the manifest's IDs match **exactly** the selected visitor dataset, then writes a full-text private review packet at `test-results/publication-review.md` (a private Actions artifact retained for 7 days). It includes the actual proposed visitor-facing summaries, personal memory narratives, sourced historical paragraphs, city precision, and award statements. It contains no research/booking/interview ledgers and must not be shared publicly before review.

A future approval must be a deliberate human decision. Each approved entry requires a review date and SHA-256 digest covering **both** the sanitized public record and its venue. If the text, dates, award context or public venue metadata changes afterward, the digest no longer matches and CI rejects the stale approval. The script `python scripts/audit_publication.py --check` checks integrity without authorizing release.

Even after the existing manual deployment checkbox is selected, `python scripts/audit_publication.py --require-approved` will **refuse deployment** until all proposed visitor records have current explicit approval. Withheld records require a separately reviewed visitor dataset change rather than silently publishing them. The canonical private source repository remains private; a clean distribution site/repository is still preferred when configured.

The packet is intended to support story and privacy review, not a fresh Michelin/James Beard eligibility audit. That separate Step 3 remains on hold.

## Experience-first copy edits (October 25, 2026)

The public-facing memories of Beckon, Charleston, Woodberry Kitchen, Sauvage, Manifesto, and Safta were rewritten in a personal, first-person editorial voice without asserting new companions, dishes, dates or award statuses. Booking/reconstruction references were removed **from the public memory prose only**; the private research and reservation provenance remains intact. The visitor approval manifest stays pending for every record, so all updated copy will be reviewed before any release.

## Denver dining added October 25, 2026

- **Sap Sua (Sắp Sửa)**: confirmed 2024 dining visit. Opened June 2023 by chefs Anna and Ni Nguyen; directly recognized as a **2024 James Beard Best New Restaurant semifinalist** (source: https://www.jamesbeard.org/stories/the-2024-james-beard-awards-semifinalists). Qualifies by the restaurant's own honor, not a Michelin star. Exact dining date, dishes, and company unknown.
- **FiNO**: confirmed 2026 visit to the coastal Mediterranean restaurant opened in March 2026 at All Inn Hotel, 3015 E. Colfax. User explicitly directed it into Culture Passport; **featured as a personally selected inclusion, not automatically a favorite**, without unverified Michelin or James Beard award claims. Source: https://www.finocolfax.com/.
- Both are available as private interview-confirmed experiences and are added to the 50-story prospective visitor publication manifest as **pending**, with no release approval or public visibility changes.

## Chicago friend-recalled memories, October 2026

Cindy's Rooftop and The Library at Gilt Bar now have memory-first visitor stories with `status: recollected`, intentionally distinct from confirmed user visits. The user asked to include these places for their atmosphere even though a friend, not the user, supplied the identifying texts. Both have unknown dates and explicit friend-recalled UI disclosures. Cindy's has a James Beard **restaurant design nomination** from 2016; The Library is a room within Michelin Bib Gourmand-listed **Gilt Bar**, but receives no separately attributed Michelin award. Both remain **pending** for publication privacy review. Dining award audit counts of confirmed visits remain unchanged, with provisional memories tracked separately. Lost Lake was directly ruled out by the user and remains excluded; Kumiko is next in the interview.

## Film and festival chapter — October 25, 2026

- American Fiction at the 46th Denver Film Festival opening night, Friday, November 3, 2023, is a confirmed attended screening. The official program establishes an 8 p.m. scheduled start at Ellie Caulkins Opera House, not the visitor's arrival time. Original calendar: https://www.denverfilm.org/wp-content/uploads/2023/10/DFS-DFF2023-8.25x10.75-Web-Single-Pages-compressed.pdf
- Film & Festivals is the sixth experience chapter across Home, Explore, Timeline, Map, and record pages. The prospective visitor story remains `pending` under the explicit privacy/publication gate.
- The other unidentified Denver stage outing is awaiting a friend's response; move the stage interview to the unidentified 2017 Second City revue in the meantime. No attendance is inferred from matching a candidate show's season.
