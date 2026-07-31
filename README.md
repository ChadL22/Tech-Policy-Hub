# Tech Policy Hub

Website for the University of Maryland Tech Policy Hub, a project of the
[Center for Governance of Technology and Systems (GoTech)](https://gotech.umd.edu/)
at the UMD School of Public Policy.

The redesign keeps UMD/GoTech brand continuity (Terrapin red, SPP logo) while
adopting a more active, editorial publishing layout inspired by the
[Knight-Georgetown Institute](https://kgi.georgetown.edu/) — a homepage
research/news feed, dedicated News and Events pages, and card-based research
area and program pages.

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
(e.g. `docs/news/index.html`), so it serves at a clean, extension-less
URL — `.../Tech-Policy-Hub/news/` instead of `.../news.html`. The
generator (`build/generate.py`'s `write()`) handles this automatically,
including rewriting internal links, so page content in `build/build_all.py`
can just use plain `href="news.html"`-style references.

Pages: `index.html` (home), `topic-cybersecurity/`, `topic-privacy/`,
`topic-integrity/`, `topic-ml/`, `courses/`, `speaker-series/`,
`annual-event/`, `news/`, `events/`, `people/`, `about/`.

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
  helpers (feed items, event rows, topic cards, people grid)
- `build/build_all.py` — per-page content and the list of pages to write

The script writes directly into `docs/`.

## Branding notes

- The official GoTech (Center for Governance of Technology and Systems)
  logo is in `docs/assets/img/gtech-main.svg`, used in the header and footer.
- Colors and type live in `docs/assets/css/styles.css` (`:root` variables at
  the top of the file).

## Known placeholders

Sample/illustrative content that should be replaced with real data before
launch: people bios, publication and project descriptions, and event dates
in `build/build_all.py`.
