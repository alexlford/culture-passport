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
- **Historic venue photo cues:** For interviews, show genuine, venue- and era-specific photos in ChatGPT to help recognition, identifying buildings and chefs precisely. Research records can carry `photographicEvidence` (source URL, caption, subject, photo date, rights). When image reuse rights are unverified, the private interview page links to the original publisher's photo rather than copying or hotlinking it. Never label a successor venue's interior as an earlier restaurant, or assume a photo proves attendance. Start with Michael Smith Restaurant's original 1900 Main facade and chef's 2016 portrait.
- **Interview answer buttons:** Always offer four options for a venue: **Yes, I visited**, **Maybe — looks familiar**, **No, haven\'t been**, **No, but want to go**. The fourth is simultaneously explicit nonattendance and a private future-visit wish, not a confirmed experience. For permanently closed historic sites preserve the wish as historical/aspirational and unbookable. The same four choices apply to in-chat interviews and the interview page.
- **Interviews are research, not attendance assertions.** Possible, negative, and unreviewed responses remain separate from confirmed experiences. Never add Le Fou Frog to the published collection: the user explicitly excluded it unless qualifying recognition is verified.
- **Link primary award evidence.** Wherever a curated venue's award or guide distinction is used as evidence, make the visible recognition on its experience page link to the exact award announcement, MICHELIN listing or other official organizer record where available. Display the issuer, year, category, result and actual recipient; retain source links and explicitly label secondary or historical citations when an official original is unavailable. Never attribute a person's or other branch's award to the restaurant itself. Do not use review roundups as proof of formal awards.
- **Select official photography, sparingly and lawfully.** Prefer one or two strong, venue-specific images from the restaurant/bar's *official website or official press kit* where permitted, chosen to support identification, atmosphere, or a personal memory—not stock galleries or generic image mosaics. Save the exact image source URL, image credit/photographer, rights or license/permission basis, and relevant venue/date/branch; respect copyright and hotlinking restrictions. Being displayed on an official website does **not** itself grant republication permission. If rights are not established, use a link to the official venue gallery or a licensed/user-owned photo instead. Preserve accessible descriptive alt text; do not imply a pictured meal or person is part of Alex's visit without confirmation.
- **Privacy by default.** Include only memories explicitly shared for this website. Avoid conflating bookers, diners, artists, and people in photos.

## Files

- `index.html`, `explore.html`, `timeline.html`, `map.html`, `record.html` — main experience pages.
- `interview.html`, `performance-interview.html` — restaurant and performing-arts reconstruction.
- `data/records.json` — canonical experience and venue records (including archived research-only entries).
- `data/interview.json`, `data/performance-interview.json`, `data/performance-leads.json` — research queues.
- `data/dining-awards-audit.json`, `data/reservation-evidence.json` — source ledgers, not competing databases.
- `data/places-to-go.json` — private list of places Alex explicitly wants to visit. Future intent stays separate from confirmed experiences and the award watchlist; Somni's current West Hollywood location is the first entry.
- `data/restaurant-award-watchlist.json` — **private, permanent, quarterly re-audit ledger** for confirmed restaurants not currently award-qualified. It includes archive-only barbecue and St. Louis memories, and keeps award promotion history. No additional public page is created from this file.
- `data/expanded-recognition-audit-2026-10-27.json` — source-linked, **full-scope recognition review** of every confirmed restaurant/location or brand-level dining memory, classifying awards, program connections, featured exceptions, and watchlisted archives without counting uncertain visits.
- `assets/` — independent stylesheet and JavaScript, with no runtime dependency on the Life Map application.

## Kansas City multi-venue cultural landmark — J. Rieger & Co. (October 31, 2026)

The user confirmed five distinct experiences at the historic East Bottoms J. Rieger & Co. complex: Sippin' Santa, Electric Park Garden Bar, Monogram Lounge, the Tasting Room and the Hey! Hey! Club. The existing confirmed J. Rieger visit acts as a **single editorial introduction** with five scoped experience chapters. It links back to **Manifesto** and **The Rieger Hotel Grill & Exchange** as separate earlier Kansas City experiences at *1924 Main Street*, not as rooms in the current 2700 Guinotte Avenue distillery. No dates, drinks or companions were invented.

A separate `editorial.culturalSpotlight` curation tier allows an award-supported historic/cultural destination page without inflating the Michelin/James Beard recognized count. The original J. Rieger record retains `editorial.awardQualified=false`. The overall historic site earned a 2020 Missouri Preservation **Preserve Missouri Award**, and the project architect documents a 2019 Historic Kansas City adaptive reuse honor (secondary source). **Electric Park Garden Bar** earned the 2022 AIA Kansas City Professionals' Choice design award and 2022 Kansas City Business Journal Capstone Retail development award. **The Hey! Hey! Club** is a 2020 Tales of the Cocktail Spirited Awards **Central regional Top 10 honoree** for Best New American Cocktail Bar, not a national award winner. Monogram Lounge and the separately identified Tasting Room have no verified room-specific awards; the Monogram Whiskey product's honors do *not* transfer to either. The Tasting Room features a white marble bar, overlooks production and adjoins a glass-enclosed Atrium, documented on the [official J. Rieger private events page](https://www.jriegerco.com/host). A confirmed room visit must not be elevated to a confirmed guided distillery tour or specific tasting order. Sippin' Santa is a nationally affiliated holiday pop-up, not itself an awarded KC bar.

The original private four-venue history remains in `data/interview-updates/kansas-city-2026-10-31-j-rieger-four-experiences.json`; the fifth-visit follow-up is in `data/interview-updates/kansas-city-2026-10-31-j-rieger-tasting-room.json`. The visitor-preview export includes only curated venue context and public evidence; the project remains private and this new page is `pending` in `data/publication-review.json`. Nothing in this classification authorizes public release, image reuse or override of the publication gate.

## Broader Michelin / James Beard curation (October 2026)

**Always lead with a direct, confirmed visit.** A restaurant can appear in one of four distinctly named tiers. The stored claims must link to official Michelin Guide or James Beard Foundation resources, not only third-party lists:

1. **Award winners / Michelin distinctions:** Stars, Bib Gourmand, Michelin Green Star and applicable special awards, or James Beard winners. Display the exact category and recipient; a chef award only applies to the restaurant where the chef earned it.
2. **Official recognition, including historical:** Michelin Selected/Recommended or the historical Plate, and James Beard semifinalists and finalists for the named restaurant or chef at that restaurant. Do not imply a Selected listing is a Star.
3. **Official Foundation / Guide Connection:** Direct venue/chef ties to Michelin editorial guides, profiles and 'ones to watch' coverage, James Beard TasteTwenty cohorts, Foundation features, and Foundation-associated events (e.g., a hosted benefit or a team featured at the Beard House). Always say *program/event/editorial connection* and give year, named chef, event location and source. **An event, a feature, or participation is not an award, endorsement, nomination or Michelin distinction**. The public UI must display this category separately from award badges and recognized-visit statistics.
4. **Personal highlights:** Explicit favorites and exceptional memories, e.g., the Allred's anniversary dinner, eligible to display without external honors and clearly marked as personal exceptions.

**Strict attribution:** If the user has visited one franchise location but an official feature concerns another, retain it as *restaurant-group context* in the private watchlist only; never imply the visited branch was featured. A guest chef from the same named location at an offsite Beard House dinner is a legitimate documented **chef-team connection**, not an event *held at* the restaurant, and never a Beard Award. Repeated visits may be stored as a single experience with unknown dates rather than fabricated individual calendar dates.

**Award watchlist remains permanent:** Every confirmed restaurant without directly verified qualifying award/Guide recognition stays in the quarterly private watchlist even when included via a Foundation program or personal exception. Record newly discovered official links in its historical review ledger. Michelin editorial recognition and JBF program participation are tracked in `officialFeatures` on canonical records, independently of `recognitions` and `guide`. Only elevate `editorial.awardQualified` after confirming an actual Guide inclusion or qualifying Beard award stage.

**Public release remains unapproved.** The visitor-preview exporter may select directly confirmed `officialFeature` restaurants, but publication-review entries must stay `pending` until explicitly approved. Do not expose private interview notes or complete watchlists on the public website.

## Full confirmed-restaurant recognition sweep — October 27, 2026

The private full-scope audit reviews **43 confirmed dining entries**: 38 specific canonical restaurant venues plus five separately recorded dining/brand memories (Joe's Kansas City, Q39, Arthur Bryant's, Jack Stack at as-yet-unidentified branches, and Dominic's on the Hill). This is not 43 independently verified restaurant addresses: the Jack Stack group entry is retained in addition to the separately confirmed Overland Park branch. The confirmed bar visit to J-Bar is separately excluded.

- **19** entries already held venue-linked Michelin/James Beard distinctions; historical organization-sourced documentation was retained, with official Michelin media confirmation additionally checked for Beckon (2023) and Minetta Tavern (2017).
- **2** confirmed restaurants now have direct, explicitly nonaward official Foundation program connections: **Uchi Denver** (hosted a 2019 Foundation benefit) and **Jack Stack Overland Park** (its named chefs participated in a 2012 Beard House dinner in New York). Their source URLs and venue/chef roles are preserved; neither was promoted to an award winner.
- **5** personal-feature exceptions remain included because of the user's memories, irrespective of awards (including Allred's anniversary dinner).
- **17** confirmed entries remain in the private nonaward archive without an independently verified direct program connection. The quarterly watchlist includes these, all personal exceptions and the two program-linked restaurants.
- Further official Foundation historical Smart Catch evidence was identified for **Barolo Grill** and **Mercantile**, already formally recognized; it is now supplemental program context. **Soupçon (Crested Butte)** appears on the Foundation's historical Smart Catch Committed list, but the user's visit is still only **maybe**, so it is excluded from confirmed totals.

**October 27 additional follow-up:** The user confirmed dining at **The Breadery (Crested Butte)**; added as the 40th confirmed dining entry and 21st permanent award-watchlist record, pending qualifying Michelin/JBF evidence. Its spring 2021 restaurant and older 2018–2019 bakery incarnations remain distinct. A user-shared [5280 historical Colorado James Beard article](https://5280.com/complete-list-of-colorado-james-beard-award-winners/) (published January 22, 2026) was indexed for discovery only. It does not include June 2026 winners; corroborate with the official Foundation records. This cross-check surfaced **Ryan Fletter of Barolo Grill as a 2026 JBF Outstanding Professional in Beverage Service nominee**, verified in the Foundation's official [2026 nominee announcement](https://www.jamesbeard.org/stories/james-beard-awards-restaurant-and-chef-nominees-2026), not an award win. The recognition is new historical context at an already qualifying venue; Alex's visit date remains unknown.

**Public House follow-up:** The user directly confirmed dining at **Public House (202 Elk Avenue, Crested Butte)**, now the 41st dining entry and 22nd permanent award-watchlist record. No venue-specific Michelin/JBF recognition or official editorial/chef-program connection was verified in a targeted source check. Irwin Brewing's beer-competition prizes are not Michelin/JBF restaurant honors. The dining date is unknown, and no live-music attendance was inferred. Next Crested Butte interview: Pitas in Paradise.

**Teocalli follow-up and Sunflower deep research:** The user confirmed **Teocalli Tamale**, completing the first 10 Crested Butte interview venues at **5 confirmed / 5 possible** and adding the 42nd distinct confirmed restaurant entry and 23rd quarterly watchlist entry. A second batch begins with **Bonez**, at 130 Elk Avenue. A deeper Sunflower investigation documented former executive chefs **Christoph Peherstorfer** (listed as 2026 Crested Butte Wine + Food Festival talent) and **John Leonardi** (later Soupçon owner; Soupçon is separately on the James Beard Foundation's historic Smart Catch committed list), and former sous chef **Ian Scott** (now Slogar). Sunflower has independent recognition from Colorado tourism and Axios. However, the 2025 Michelin Outstanding Service Award belongs to **Heather Morrison at Restaurant Olivia**, and the 2026 James Beard Outstanding Hospitality semifinalist was **Restaurant Olivia**, not Sunflower. Its 2026 Wine + Food Festival bio is adjacent to a Sunflower-alumnus profile, which likely caused the user-provided generated screenshot to conflate separate people and restaurants. A shared festival or later employer association is documented as *chef alumni / industry-network context* only, **not** a Michelin star, JBF nomination, or Sunflower Foundation program participation. USA Today 2026 Restaurant of the Year claim was not verified. Source records are in the canonical Sunflower `chefAlumniConnections`, watchlist review history and the expanded recognition audit.

**Limitations:** This sweep consulted official Michelin Colorado 2026 lists, 2026 JBF award announcements, historical Michelin media releases and named James Beard event/program archives. It is *not* a claim to have exhaustively indexed every historical Guide edition or Foundation event. Absence of a match means **not verified in this review**, not never awarded. Future quarterly research should check additional official editorial features, Awards Watch, Taste America/TasteTwenty, program rosters and location-specific chef history.

Source detail, all 43 rows, the exact naming/branch distinctions and future-review guidance are in `data/expanded-recognition-audit-2026-10-27.json`. This file is private research, not included in visitor export. The new validator checks exact coverage against canonical confirmed dining and the separate archive, and ensures official program ties are never presented as awards.

**Two Twelve follow-up:** The user explicitly confirmed dining at Two Twelve, the live-fire restaurant at 212 Elk Avenue in Crested Butte, opened in July 2024. This is now the 43rd confirmed dining entry and 24th active award watchlist entry. Chef Anthony Nelson and partner Kyleena Falzone have substantial independent coverage in Axios, 5280 and Mountain Town Magazine, describing culinary ambitions and a potential future James Beard nomination. Those stories are **not official Michelin or James Beard recognition**; no award, nomination, editorial or Foundation program feature is claimed. Partner Falzone is associated with Bonez and The Secret Stash; both remain only *possibly visited*. Next pending interview: Izakaya Cabin at 321 Elk Avenue.

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

The visitor export contains only Home, Explore, Timeline, Map, experience pages, app assets, and **confirmed curated experiences** (award-qualified restaurants/bars, separately labeled official Michelin/JBF program-linked dining, explicit personal favorites, and arts). It omits interview pages, candidate lists, reservation ledgers, booking-only records, exclusion records, old source notes, provenance fields and the entire research directory. This allows the future public site to focus on stories and venues instead of private reconstruction notes.

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

The packet is intended to support story and privacy review, not the separate Michelin/James Beard eligibility audit. An initial comprehensive confirmed-restaurant recognition sweep was completed October 27, 2026; its findings remain private and quarterly re-audit will continue.

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

## City editions and interview pivot — October 27, 2026

The homepage now includes a six-city editorial browse section built at runtime from **confirmed, curated experiences**. Cities are ranked by distinct confirmed venues and feature a named experience; uncertain interview answers and friend-recalled unconfirmed evenings never enter city counts. Each card opens a city-filtered Explore view. Changing the Explore city filter synchronizes the `?city=` URL parameter so the view can be shared and cleared. City links remain deliberately distinct from map coordinates, which are only city-level.

The new city edition is responsive at tablet/phone widths and keyboard navigable. Static route tests and private Playwright browser smoke coverage now check city links, user-facing filters, shareable URLs and mobile overflow. No external service, new private research fields, or public release was added; staging `noindex`, the explicit story-approval manifest, and the manual deployment gate remain in force.

The Crested Butte dining interview has been **paused by user request**. Preserve six confirmed dining venues, ten possible venues, and unanswered Paradise Cafe; the latter is not a negative answer. The next historical visual-recall batch is Kansas City Metro (six unreviewed restaurants). Focus future work on cross-city memories, source attribution, design quality and publication review before extending any single-town checklist.

## Los Angeles correction — The Butcher's Daughter (October 27, 2026)

The user corrected the LA inventory: **The Butcher's Daughter is a confirmed restaurant visit**, alongside **République**. A separately archived Resy booking dated **July 29, 2023**, for **three people** is explicitly for the **8755 Melrose Avenue West Hollywood** branch, which opened in September 2022. The restaurant attendance is now confirmed by the user, but the exact dinner date, guests, and definitive match to that branch remain unconfirmed; do not turn the Resy booking into a meal-date assertion. This corrects the earlier research-only handling of that booking while retaining it as source evidence.

The canonical source adds a non-award-claimed dining record and a 25th permanent private restaurant watchlist entry. The expanded confirmed-restaurant recognition audit now contains **44 entries** (39 canonical distinct dining venue records and five separate archive-only brand memories), with **18** in the archived-pending-recognition tier. This supersedes the earlier October 27 counts of 43 and 24 watchlist entries; historical audit notes are retained as time-stamped prior states.

No specific Michelin Guide or James Beard Foundation award, Guide listing, or official feature for the West Hollywood branch was verified in the targeted 2026 review. Independent 2022 Eater opening coverage and the brand's own venue site are background, not a qualifying honor. Do not apply accolades from a different branch. The visitor-facing record is **not** selected into the public preview without a separately authorized featured exception or directly verified formal/official organizational recognition. The private interview also preserves the user's memory of unnamed meals with Jay, including one Taiwanese restaurant; Jay is *not* inferred to have attended the Butcher's Daughter meal.

Sources: [West Hollywood location](https://thebutchersdaughter.com/location-all/west-hollywood), [Eater LA opening coverage](https://la.eater.com/2022/9/20/23363171/butchers-daughter-melrose-west-hollywood-opening-plant-forward-vegetarian-restaurant), and the private reservation evidence ledger.

## LA interview: West Hollywood confirmed and Taiwanese discovery (October 27, 2026)

The user has **directly confirmed The Butcher's Daughter at the West Hollywood branch (8755 Melrose Avenue)**, not just the brand. The original 2023-07-29 Resy booking for three remains in the private evidence ledger, but the date and diners at the actual meal are still unknown. This supersedes the earlier *provisional location* wording in the historical October 27 correction without altering the award-watchlist classification.

The unidentified Taiwanese restaurant visited with Jay remains **a confirmed general dining recollection with an unconfirmed venue identity**. The LA visual-recall shortlist distinguishes Pine & Crane **Silver Lake** (2026 Michelin Bib Gourmand) from **DTLA** (do not transfer the Silver Lake distinction), Liu's Cafe in Koreatown (opened late August 2023, 2026 Bib Gourmand), Din Tai Fung Century City, Little Fatty Mar Vista, Joy Highland Park, Kato ROW DTLA (two Michelin Stars in June 2026), and The Formosa Cafe in West Hollywood (primarily Chinese-American; neighborhood clue). None is marked as personally visited. It is not established that the Taiwanese meal was on the 2023 Resy date or that Jay attended The Butcher's Daughter.

Sources: [Michelin California 2026](https://www.michelin.com/en/publications/products-and-services/the-michelin-guide-california-2026), [Liu's 2023 opening](https://la.eater.com/2023/9/26/23889744/lius-cafe-koreatown-hong-kong-taiwanese-opening), [Pine & Crane DTLA official site](https://www.pineandcrane.com/dtla), [Joy restaurant](https://www.joyonyork.com/), [West Hollywood Butcher's Daughter venue](https://thebutchersdaughter.com/location-all/west-hollywood). Award status and exact venue identity must not be inferred from proximity or press coverage.

## Two-track Los Angeles research: West Hollywood + Space Park (October 27, 2026)

The user explicitly requested **both research tracks to remain active simultaneously**. West Hollywood includes the confirmed République and The Butcher's Daughter (West Hollywood) venue visits; the latter's July 29, 2023 Resy reservation remains a separately sourced *booking*, not a verified meal date. The unidentified Taiwanese restaurant visited with Jay is still an open memory-identification lead, never a confirmed named dining venue. The West Hollywood vicinity includes four additional Michelin Guide-selected, location-specific *unvisited/unreviewed* candidates: Petit Trois (L'Original), Chi Spacca, Angelini Osteria, and Ardor at the West Hollywood EDITION, in addition to previously queued Osteria Mozza, Pizzeria Mozza, Jon & Vinny's (Fairfax), and Somni. The first Taiwanese image-recall shortlist remains available unchanged.

A separate South Bay / Space Park interview includes eight independently Guide-listed candidates in Manhattan Beach, Hermosa Beach, Torrance, Gardena, and Rancho Palos Verdes; **none has yet been user-confirmed as a named meal**. Both tracks appear in `data/interview.json → interviewProgress.parallelActiveChapters`, and static validation tests enforce that neither disappears. All new discoveries remain private interview research, not the public experience dataset. Do not transfer branch-level awards, equate Michelin Selected with a star, or infer 2026 status on earlier unverified meals.

## Liu's Cafe leading LA Taiwanese identification — October 27, 2026

After a photo-led West Hollywood/LA research sweep, Alex stated **"I have a strong feeling it is Liu's Cafe."** This is a **strong probable identity, still not a confirmed named venue visit**. The private interview candidate `candidate-la-lius-cafe-ktown` is `visitStatus=maybe` and `researchStatus=user_strongly_suspects_identity_not_yet_confirmed`; the separate memory lead has `probableCandidateId`, an explicit tentative confidence label and `venueIdentityConfirmed=false`. The two definitely named LA meals remain République and The Butcher's Daughter (West Hollywood), and the separate South Bay/Space Park interview remains active.

Liu's original **Koreatown** restaurant at 3915½ W 6th Street soft-opened **August 31, 2023**. Its identifiable interior features long walnut-toned communal tables, dark bentwood chairs, framed vintage artwork, pale walls and green tile/paint, with a Chinese/Taiwanese-Hong Kong-style menu. The Michelin Guide independently lists that restaurant as **Bib Gourmand (2026)**, which would meet the formal Passport criteria **if Alex confirms this precise visit and branch**. The July 29, 2023 West Hollywood Resy booking for The Butcher's Daughter predates Liu's opening and is entirely separate: never treat it as evidence of a Liu's visit or of Jay attending The Butcher's Daughter. The possibility of a later Westwood branch also must not be conflated with Koreatown.

Key sources: [Michelin California 2026](https://www.michelin.com/en/publications/products-and-services/the-michelin-guide-california-2026), [August 2023 soft opening](https://visitkoreatown.org/lius-cafe/), [September 2023 opening report](https://la.eater.com/2023/9/26/23889744/lius-cafe-koreatown-hong-kong-taiwanese-opening), [operator site/interior images](https://liuscafe.com/) and [interior photos](https://www.theinfatuation.com/los-angeles/reviews/lius-cafe-koreatown). Next interview should verify visual recall and a post-August-2023 timeframe, without soliciting a fabricated date.

## Union Station memories — October 27, 2026

Alex explicitly confirmed several visits to **Pierpont's at Union Station** and identified **Harvey's at Union Station** as the venue for the after-wedding goodbye brunch. Both are now confirmed collection entries. Individual Pierpont's meal dates and the Harvey's wedding/brunch year remain unspecified; the earlier 2012–2017 search window does not establish an exact wedding date.

Pierpont's has a direct **James Beard Foundation editorial connection**: the Foundation's May 4, 2011 Stephen Fried [Tour de Fred Harvey](https://archive.jamesbeard.org/blog/bookshelf-stephen-frieds-delicious-southwest-tour-de-fred-harvey) explicitly names and links this Kansas City restaurant. It is curated as an official editorial connection, without a Beard Award or nomination claim. Harvey's is included as an explicitly requested, permanent personal wedding-memory exception. Both remain in the quarterly award watchlist, and their prospective visitor stories are added to the publication manifest as pending. The confirmed-restaurant audit now covers **46 entries**, including **41 canonical distinct dining venues** and five separate archive-only memories. No public deployment was performed.


## Independent Passport navigation

The footer names the current Passport and preserves the existing Sports,
Adventures, and Personal Atlas destinations. The unpublished sibling Passport
is labeled **In development**, without a speculative public URL. Activating it
requires a separately verified launch change and an updated navigation contract.
The component is static HTML and has no cross-repository JavaScript or data
dependency. Each Passport retains its own content, styling, and release process.


## Loading and recovery

Visitor pages load only the archive dataset; the private restaurant interview loads only its own interview dataset. Requests time out after 15 seconds and display an accessible Try again control. Recovery does not reload the page or clear locally saved interview responses. Controls remain disabled until the data is ready, and a keyboard retry returns focus to the restored content.

The browser workflow exercises HTTP failures, malformed data, a stalled request, independent interview recovery, saved responses, and keyboard focus. Interview checks run only against a temporary localhost source server; they do not add private data or screenshots to the visitor artifact.
