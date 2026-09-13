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
generator in `build/` so those stay consistent across all 12 pages. It's
named `docs/` (not `site/`) specifically so GitHub Pages can serve it
directly — see **Publishing** below.

Every page except the homepage lives in its own folder as `index.html`
(e.g. `docs/events/index.html`), so it serves at a clean, extension-less
URL — `.../Tech-Policy-Hub/events/` instead of `.../events.html`. The
generator (`build/generate.py`'s `write()`) handles this automatically,
including rewriting internal links, so page content in `build/build_all.py`
can just use plain `href="events.html"`-style references.

Pages: `index.html` (home), `research/` (research hub — projects,
publications, teaching), `topic-cybersecurity/`, `topic-privacy/`,
`topic-integrity/`, `topic-ml/`, `courses/`, `speaker-series/`,
`annual-event/`, `events/`, `people/`, `about/`. Alongside those
12 HTML pages, the build also writes one non-HTML file to the site
root — `docs/events.ics`, a generated calendar feed (see **Site
capabilities** below). There is no standalone news page — the homepage's
"Hub News" rail is the site's one news listing (see **Site capabilities**
below).

The primary nav is **Home / Research (dropdown) / Events (dropdown) /
People**. Each dropdown's parent label is itself a real link to that
page's index (Research/Events), so there's no separate "All Research"/"All
Events" entry — the page itself is the "view everything" destination, and
both are filterable in place (see below). About isn't in the top-level
nav, but stays reachable via the footer's "Connect" column.

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
edit the source and regenerate instead, so every page stays in sync:

```bash
pip install pyyaml   # once, if not already installed
cd build
python3 build_all.py
```

**The site's actual content — people, events, research projects and
publications, homepage news/spotlight/reading items, guiding questions,
and the small taxonomies (research areas, event categories, role types,
reading types) — lives as YAML files under `build/data/`, not as Python
literals.** This is what makes the content editable without touching
code: by hand in any text editor, directly in GitHub's own web editor, or
eventually through a CMS admin UI that commits straight to these same
files (see **Content management** below for where that stands).

| File | What it holds |
| --- | --- |
| `build/data/people.yml` | `PEOPLE_ITEMS` — name, role, bio, links, role types |
| `build/data/events.yml` / `past_events.yml` | `EVENTS_ITEMS` / `PAST_EVENTS_ITEMS` |
| `build/data/news_items.yml` | Homepage "Hub News" rail |
| `build/data/spotlight_items.yml` | Homepage "Research Spotlight" slideshow |
| `build/data/reading_items.yml` | "What we're reading" cards |
| `build/data/questions.yml` | "Guiding Questions" |
| `build/data/topic_detail.yml` | Research page's per-area projects/publications/people |
| `build/data/topics.yml` | The 4 research areas (name/blurb/index) |
| `build/data/area_meta.yml` | Research-area accent colors/codes |
| `build/data/event_categories.yml` | Event category colors |
| `build/data/role_types.yml` | People-page role-type filter labels |
| `build/data/reading_types.yml` / `reading_type_labels.yml` | "What we're reading" category taxonomy |
| `build/data/ticker.json` | Policy-tracker ticker — regenerated by `refresh_ticker.py`, see below, not hand-edited |

Edit the relevant `.yml` file, then rerun `python3 build_all.py` from
`build/` to regenerate every page from it. `generate.py`'s `load_data()`
helper is what reads these files (`yaml.safe_load`) into the same
module-level constants (`PEOPLE_ITEMS`, `EVENTS_ITEMS`, etc.) that the
rest of the generator already used — nothing about how the site is
*assembled* changed, only where the content comes from.

- `build/generate.py` — shared header, footer, nav, `load_data()`, and
  reusable content helpers (feed items, event rows, topic cards, the
  people-page renderer, the signal ticker, the Research Spotlight
  slideshow, the events calendar, the filter-pill bar, the `.ics`
  calendar feed builder, etc.)
- `build/build_all.py` — per-page content assembly and the list of pages
  to write; also loads `TOPIC_DETAIL` from `build/data/topic_detail.yml`
  the same way
- `build/refresh_ticker.py` — regenerates `build/data/ticker.json` from
  the Tech Policy Tracker; run on a schedule by
  `.github/workflows/refresh-ticker.yml`, or by hand

The script writes directly into `docs/` — HTML pages via `write()` (which
also rewrites internal links to the clean-URL folder scheme), and the
non-HTML `docs/events.ics` calendar feed via `write_raw()`. Any change to
shared assets (`build/generate.py`'s CSS/JS, header, or footer) bumps
`ASSET_VERSION` in `generate.py` so browsers pick up the new files instead
of a stale cache.

## Content management

The site's content (the `build/data/*.yml` files above) is editable
without writing Python through a git-based headless CMS admin UI at
`/admin` on this site, once the one remaining manual setup step below is
done. This is [Sveltia CMS](https://github.com/sveltia/sveltia-cms) (the
current maintained successor to Decap/Netlify CMS), editing the
`build/data/*.yml` files directly and committing straight to this repo.
Three pieces, in the order they were built:

1. **The CMS config** (`docs/admin/index.html` + `docs/admin/config.yml`)
   — done. Covers the flat, frequently-edited collections: People,
   Events (upcoming + past), and homepage content (Hub News, Research
   Spotlight, What We're Reading, Guiding Questions). Deliberately NOT
   covered yet: `topic_detail.yml` (nested per-research-area data, not a
   flat list -- needs a more involved config) and the small taxonomy
   files (`area_meta.yml`, `event_categories.yml`, `role_types.yml`,
   `reading_types.yml`, `reading_type_labels.yml` -- each tied to a
   hardcoded CSS color/class elsewhere in the site, so adding a key
   through a form without a matching code change would silently render
   wrong; these stay a deliberate hand/code edit). `config.yml`'s own
   comments explain each collection's fields.
2. **Auto-rebuild on content change**
   (`.github/workflows/rebuild-on-content-change.yml`) — done. Runs
   `build/build_all.py` and commits the regenerated `docs/` whenever
   `build/data/**` changes on `main`, so a CMS commit goes live without
   anyone running the build script by hand.
3. **GitHub OAuth, so Hub members can log in with their own GitHub
   account** — the one piece that needs a person to act, not something
   that can be scripted from outside: it means registering a GitHub
   OAuth App and deploying a small token-exchange proxy, both under this
   repo's/org's own accounts. **Someone with admin access to this GitHub
   repo/org** should:
   1. Deploy [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth)
      (a small Cloudflare Worker — free tier is enough) following that
      project's own README; it needs a Cloudflare account.
   2. Register a new OAuth App at
      github.com/organizations/**ChadL22**/settings/applications (or
      github.com/settings/developers if this repo isn't under an org) —
      Homepage URL `https://chadl22.github.io/Tech-Policy-Hub/`,
      Authorization callback URL is the Worker's own URL from step 1
      (its README shows the exact path).
   3. Put that OAuth App's Client ID and Secret into the Worker's
      environment (again, per sveltia-cms-auth's README).

   Until this is done, `/admin` loads but sign-in fails — content
   changes go through editing the YAML files directly and running
   `build_all.py` by hand, as described above.

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
  `TICKER_ITEMS` is machine-generated, not hand-curated: `build/
  refresh_ticker.py` queries the Integrity Institute Tech Policy Tracker's
  own (undocumented but public, read-only) search backend directly for
  current bills tagged with themes matching the Hub's four research areas,
  writes the result to `build/data/ticker.json`, and
  `.github/workflows/refresh-ticker.yml` runs that + a full rebuild weekly
  (also runnable on demand from the Actions tab, or by hand with
  `python3 refresh_ticker.py` from `build/`). No API key needed. See that
  script's docstring for the full rationale and exactly what it filters
  for.
- **Research Spotlight** — a 5-slide auto-advancing slideshow of curated
  Hub outputs (`SPOTLIGHT_ITEMS`) in the homepage lead grid. Slides are
  stacked in one CSS Grid area so the slideshow's footprint stays fixed
  regardless of which slide is showing — a slide change never resizes or
  reflows the rest of the page. Crossfades smoothly between slides, with
  dot navigation and pause-on-hover (same touch-safe `matchMedia` gating
  as the ticker, below).
- **Hub News rail + Research Areas matrix** — a compact side rail on the
  homepage. Since there's no standalone news page, Hub News lists every
  `NEWS_ITEMS` entry inside a fixed-height scrollable box (styled after
  CNBC's own "Latest News" sidebar), not a short excerpt with a "more"
  link out to a fuller page. Below it, the Hub's four research focus
  areas (`TOPICS`) render as a 2×2 index.
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

- `PEOPLE_ITEMS` (`build/data/people.yml`) — the six people, their roles,
  and their research-area badges (derived from `TOPIC_DETAIL` in
  `build/build_all.py`) are real. Still placeholder, pending real
  material from each person: `bio` is a short paragraph auto-expanded
  from the existing role/focus fields rather than a bio they wrote;
  `website`/`linkedin` are blank except the founder's site (already
  linked from the homepage); and photos are the initials-avatar
  placeholder (no headshot files yet).
- `PAST_EVENTS_ITEMS` (`build/data/past_events.yml`) — illustrative past-event
  copy (shared by the Events page's Past Events section, the Speaker
  Series page's "Past sessions," and the Annual Event page's recap card),
  not yet confirmed real dates/details.
- Fictional/forward-dated project and event content on `research.html`,
  `speaker-series.html`, and `annual-event.html`.
- `SPOTLIGHT_ITEMS`' visual — an abstract topic-accent graphic stands in
  for real per-article photography.
- `EVENTS_ITEMS`/`PAST_EVENTS_ITEMS` need periodic manual refresh as
  events are scheduled/occur — `events.ics` regenerates automatically from
  `EVENTS_ITEMS` on every build, so keeping that array current is what
  keeps the calendar subscription accurate. `TICKER_ITEMS` no longer needs
  manual refresh — see **Site capabilities** above.
- The "Conference" category (`EVENT_CATEGORIES`, `build/data/event_categories.yml`)
  is for field-wide events the Hub didn't organize, listed in support of
  the tech policy field generally rather than only the Hub's own
  programming. Its one entry so far -- the IAPP Global Summit 2027 --
  is a real external conference with dates/venue verified via iapp.org
  as of Sep 2026, but a 3rd-party listing like this can move; reconfirm
  before relying on it, and swap/add other field conferences here the
  same way.
