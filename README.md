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
