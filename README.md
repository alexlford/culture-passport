# Culture Passport

A standalone cultural experience archive for restaurants, cocktail bars, concerts, opera, and theater.

**Canonical repository:** `alexlford/culture-passport`

**Planned public site:** `https://culture.alexlford.com` (DNS and GitHub Pages still require configuration). This code is **not** a chapter of the Life Map. Work, education, career, and personal geography remain in `alexlford/life-map`.

## Experience-first editorial rules

- **Start with the memory.** Atmosphere, companions, venue history, chefs/artists, and what made an evening memorable matter most.
- **Approximate years are sufficient.** Store an exact date only when it is meaningful to the memory and actually known; never promote a reservation date to an unquestioned meal date.
- **Distinguish evidence.** `status=confirmed` means an actual experience was recalled, while `reservation_only` denotes a research lead and must not appear in confirmed totals.
- **Michelin and James Beard are inclusion guides, not the entire story.** Maintain award year, category, and recipient, and do not borrow honors between locations. Explicit favorites such as Sauvage, Gunther & Co., The Majestic, and Death & Co Denver remain included even without award recognition.
- **Interviews are research, not attendance assertions.** Possible, negative, and unreviewed responses remain separate from confirmed experiences. Never add Le Fou Frog to the published collection: the user explicitly excluded it unless qualifying recognition is verified.
- **Privacy by default.** Include only memories explicitly shared for this website. Avoid conflating bookers, diners, artists, and people in photos.

## Files

- `index.html`, `explore.html`, `timeline.html`, `map.html`, `record.html` — main experience pages.
- `interview.html`, `performance-interview.html` — restaurant and performing-arts reconstruction.
- `data/records.json` — canonical experience and venue records (including archived research-only entries).
- `data/interview.json`, `data/performance-interview.json`, `data/performance-leads.json` — research queues.
- `data/dining-awards-audit.json`, `data/reservation-evidence.json` — source ledgers, not competing databases.
- `assets/` — independent stylesheet and JavaScript, with no runtime dependency on the Life Map application.

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
