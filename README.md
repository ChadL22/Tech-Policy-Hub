# Tech Policy Hub

Website for the University of Maryland Tech Policy Hub, a project of the
[Center for Governance of Technology and Systems (GoTech)](https://gotech.umd.edu/)
at the UMD School of Public Policy. The new site replaces
techpolicy.info.umd.edu and complements (does not replace) gotech.umd.edu.

The redesign keeps UMD/GoTech brand continuity (Terrapin red, SPP/UMD seal)
while adopting an active, editorial publishing layout inspired by the
[Knight-Georgetown Institute](https://kgi.georgetown.edu/) — a homepage
research/news feed, dedicated News and Events pages, and card-based research
area and program pages — and, in a later compactness pass, by
**SCOTUSblog**'s tight magazine-grid density: a multi-column homepage lead
grid, dense list-style feed rows instead of oversized cards, and a real
month-grid events calendar.

## Structure

```
docs/     Final static site — open docs/index.html in a browser to preview
build/    Python generator that produces the pages in docs/
```

`docs/` is a static site (no server or build step required to view it).
Each page shares the same header, footer, and nav, assembled by the
generator in `build/` so those stay consistent across all 13 pages. It's
named `docs/` (not `site/`) specifically so GitHub Pages can serve it
directly — see **Publishing** below.

Every page except the homepage lives in its own folder as `index.html`
(e.g. `docs/news/index.html`), so it serves at a clean, extension-less
URL — `.../Tech-Policy-Hub/news/` instead of `.../news.html`. The
generator (`build/generate.py`'s `write()`) handles this automatically,
including rewriting internal links, so page content in `build/build_all.py`
can just use plain `href="news.html"`-style references.

Pages: `index.html` (home), `research/` (research hub — projects,
publications, teaching), `topic-cybersecurity/`, `topic-privacy/`,
`topic-integrity/`, `topic-ml/`, `courses/`, `speaker-series/`,
`annual-event/`, `news/`, `events/`, `people/`, `about/`.

The primary nav is **Home / Research (dropdown) / Events (dropdown) /
People**. News and About aren't in the top-level nav, but both stay
reachable via the footer's "Connect" column.

## Publishing (GitHub Pages)

The site lives in `docs/`, not the repo root, so Pages needs to be pointed
at that folder:

1. GitHub → repo → **Settings → Pages**
2. Under **Build and deployment → Source**, choose **Deploy from a branch**
3. **Branch**: `main`, folder **`/docs`** → **Save**

Without this, GitHub Pages defaults to the repo root, finds no `index.html`
there, and falls back to rendering `README.md` — which is why the site was
showing the README instead of the actual pages.

## Editing content

Don't hand-edit the `<header>`/`<footer>`/nav in the HTML files directly —
edit the source in `build/` and regenerate instead, so every page stays in
sync:

```bash
cd build
python3 build_all.py
```

- `build/generate.py` — shared header, footer, nav, and reusable content
  helpers (feed items, event rows, topic cards, people grid, the signal
  ticker, the Research Spotlight slideshow, the events calendar, etc.), plus
  the real content arrays (`NEWS_ITEMS`, `EVENTS_ITEMS`, `TICKER_ITEMS`,
  `SPOTLIGHT_ITEMS`, `PEOPLE_ITEMS`, `TOPICS`, `QUESTIONS`)
- `build/build_all.py` — per-page content and the list of pages to write

The script writes directly into `docs/`. Any change to shared assets
(`build/generate.py`'s CSS/JS, header, or footer) bumps `ASSET_VERSION` in
`generate.py` so browsers pick up the new files instead of a stale cache.

## Site capabilities

Beyond a standard static brochure site, the homepage and related pages
carry a few purpose-built interactive elements, all implemented in plain
CSS/JS (no framework, no build step) in `docs/assets/css/styles.css` and
`docs/assets/js/main.js`:

- **Signal ticker** — a scrolling tape of real DC/MD/VA/federal tech policy
  bills (`TICKER_ITEMS`). Auto-scrolls continuously, pauses on hover (mouse
  only — gated behind `matchMedia('(hover: hover)')` so touch devices,
  which fire synthetic hover events after a tap, aren't left permanently
  frozen), and can be scrubbed by dragging with a mouse or a finger.
- **Research Spotlight** — a 5-slide auto-advancing slideshow of curated
  Hub outputs (`SPOTLIGHT_ITEMS`) in the homepage lead grid, crossfading
  between slides, with dot navigation and pause-on-hover.
- **Hub News rail + Research Areas matrix** — a compact side rail on the
  homepage surfacing recent news (`NEWS_ITEMS`) and the Hub's four research
  focus areas (`TOPICS`) as a 2×2 index.
- **Guiding Questions** — a list of the Hub's core research questions
  (`QUESTIONS`) that highlight on hover but are intentionally not links.
- **Field Pulse** — a secondary carousel of outside reading (papers,
  essays, articles) the Hub has recently come across, framed as
  supplementary context rather than Hub output, with a pointer to the
  Hub-affiliated sister site phronesisresearch.org for older reading.
- **Events calendar** — a real month-grid calendar (Python's `calendar`
  module) driven by `EVENTS_ITEMS`, with a category legend.
- **Newsletter signup** — a homepage section (`#subscribe`) for subscribing
  to the Hub's newsletter.
- **Join the Hub** — an outreach section on the About page inviting new
  members and pointing prospective affiliates to the Hub's founder,
  Dr. Sivan-Sevilla, by email.

## Branding notes

- The header's top-left mark is the official UMD seal
  (`docs/assets/img/umd-seal.png`); the Hub's own bordered "TECH / POLICY
  HUB" lockup (`docs/assets/img/tph-mark.png`) sits next to it.
- The official GoTech (Center for Governance of Technology and Systems)
  logo (`docs/assets/img/gtech-main.svg`, read-only on disk) appears in the
  **footer**, not the header.
- Colors and type live in `docs/assets/css/styles.css` (`:root` variables
  at the top of the file) — UMD red as the dominant accent, gold reserved
  for ticker/banner-style dark elements, squared (not pill-shaped) corners
  throughout.

## Known placeholders

Most homepage/news/events content (`NEWS_ITEMS`, `EVENTS_ITEMS`,
`TICKER_ITEMS`, `SPOTLIGHT_ITEMS`) is real, dated Hub activity with real
external links — not sample copy. What's still illustrative and should be
replaced with real material before launch:

- `PEOPLE_ITEMS` in `build/generate.py` — the founder's entry is real;
  several other bios/roles are placeholder names standing in for the
  Hub's actual affiliates and fellows.
- Fictional/forward-dated project and event content on `research.html`,
  `speaker-series.html`, and `annual-event.html`.
- `SPOTLIGHT_ITEMS`' visual — an abstract topic-accent graphic stands in
  for real per-article photography.
- `TICKER_ITEMS` needs periodic manual refresh as tracked bills move
  through committee/floor votes.
