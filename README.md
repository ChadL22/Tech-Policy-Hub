# Tech Policy Hub

Website for the University of Maryland Tech Policy Hub, a project of the
[Center for Governance of Technology and Systems (GoTech)](https://gotech.umd.edu/)
at the UMD School of Public Policy. The new site replaces
techpolicy.info.umd.edu and complements (does not replace) gotech.umd.edu.

The redesign keeps UMD/GoTech brand continuity (Terrapin red, SPP/UMD seal)
and draws its design language primarily from financial/legal news
sources — **Bloomberg** and **CNBC** (the homepage's scrolling signal
ticker: gold border, channel tabs, pulsing "live" dot) and **SCOTUSblog**
(the tight magazine-grid density: a multi-column homepage lead grid,
dense list-style feed rows instead of oversized cards, filterable
Research and Events pages, and a real month-grid events calendar with a
live subscribe feed) — all adapted for a research lab rather than a news
outlet: Hub-authored research and events take the lead spot everywhere a
news outlet would run a headline story, and outside reading/commentary is
demoted to a clearly secondary "Field Pulse" section rather than
competing with the Hub's own output. That's the current, accurate
description of the site's design language.

Earlier in the redesign the layout started from an editorial publishing
model loosely modeled on the
[Knight-Georgetown Institute](https://kgi.georgetown.edu/) — a homepage
research/news feed, dedicated News and Events pages, and card-based
research area and program pages. Repeated compactness/functionality passes
since then have moved the site well past that starting point, so KGI's
site is no longer a close visual match to what's shipped here — it's
noted here as historical context for the redesign's origin, not as a
current reference.

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
`annual-event/`, `news/`, `events/`, `people/`, `about/`. Alongside those
13 HTML pages, the build also writes one non-HTML file to the site
root — `docs/events.ics`, a generated calendar feed (see **Site
capabilities** below).

The primary nav is **Home / Research (dropdown) / Events (dropdown) /
People**. Each dropdown's parent label is itself a real link to that
page's index (Research/Events), so there's no separate "All Research"/"All
Events" entry — the page itself is the "view everything" destination, and
both are filterable in place (see below). News and About aren't in the
top-level nav, but both stay reachable via the footer's "Connect" column.

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
  ticker, the Research Spotlight slideshow, the events calendar, the
  filter-pill bar, the `.ics` calendar feed builder, etc.), plus the real
  content arrays (`NEWS_ITEMS`, `EVENTS_ITEMS`, `PAST_EVENTS_ITEMS`,
  `TICKER_ITEMS`, `SPOTLIGHT_ITEMS`, `PEOPLE_ITEMS`, `TOPICS`, `QUESTIONS`)
- `build/build_all.py` — per-page content and the list of pages to write

The script writes directly into `docs/` — HTML pages via `write()` (which
also rewrites internal links to the clean-URL folder scheme), and the
non-HTML `docs/events.ics` calendar feed via `write_raw()`. Any change to
shared assets (`build/generate.py`'s CSS/JS, header, or footer) bumps
`ASSET_VERSION` in `generate.py` so browsers pick up the new files instead
of a stale cache.

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
  Hub outputs (`SPOTLIGHT_ITEMS`) in the homepage lead grid. Slides are
  stacked in one CSS Grid area so the slideshow's footprint stays fixed
  regardless of which slide is showing — a slide change never resizes or
  reflows the rest of the page. Crossfades smoothly between slides, with
  dot navigation and pause-on-hover (same touch-safe `matchMedia` gating
  as the ticker, below).
- **Hub News rail + Research Areas matrix** — a compact side rail on the
  homepage surfacing recent news (`NEWS_ITEMS`) and the Hub's four research
  focus areas (`TOPICS`) as a 2×2 index.
- **Guiding Questions** — a list of the Hub's core research questions
  (`QUESTIONS`) that highlight on hover but are intentionally not links.
- **Field Pulse** — a secondary carousel of outside reading (papers,
  essays, articles) the Hub has recently come across, framed as
  supplementary context rather than Hub output, with a pointer to the
  Hub-affiliated sister site phronesisresearch.org for older reading.
- **Filterable Research & Events pages** — both `research.html` (by
  research focus area) and `events.html` (by event category) have a pill
  filter bar (`filter_pills_html()`) that shows/hides matching content
  client-side, via a small generic `[data-filter-group]`/
  `[data-filter-target]` mechanism in `main.js` — reusable for any future
  filterable list on the site.
- **Events page: upcoming + past lists, calendar, and a real "Subscribe to
  Calendar" feature** — `events.html` pairs a filterable Upcoming Events
  list with a Past Events list (`PAST_EVENTS_ITEMS`; the same filter bar
  narrows both together) against a sidebar carrying the month-grid
  calendar (Python's `calendar` module, `EVENTS_ITEMS`, category legend)
  and calendar subscribe options. `events_ics()` builds a genuine RFC-5545
  `.ics` feed from `EVENTS_ITEMS` on every build (written to
  `docs/events.ics`), linked as both a `webcal://` URL (subscribes live in
  Google/Apple/Outlook and picks up future rebuilds automatically) and a
  plain download link.
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
- `PAST_EVENTS_ITEMS` in `build/generate.py` — illustrative past-event
  copy (shared by the Events page's Past Events section, the Speaker
  Series page's "Past sessions," and the Annual Event page's recap card),
  not yet confirmed real dates/details.
- Fictional/forward-dated project and event content on `research.html`,
  `speaker-series.html`, and `annual-event.html`.
- `SPOTLIGHT_ITEMS`' visual — an abstract topic-accent graphic stands in
  for real per-article photography.
- `TICKER_ITEMS` and `EVENTS_ITEMS`/`PAST_EVENTS_ITEMS` need periodic
  manual refresh as tracked bills move and events are scheduled/occur —
  `events.ics` regenerates automatically from `EVENTS_ITEMS` on every
  build, so keeping that array current is what keeps the calendar
  subscription accurate.
