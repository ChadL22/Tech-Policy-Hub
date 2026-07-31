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
site/     Final static site — open site/index.html in a browser to preview
build/    Python generator that produces the pages in site/
```

`site/` is a flat static site (no server or build step required to view it).
Each page shares the same header, footer, and nav, assembled by the
generator in `build/` so those stay consistent across all 12 pages.

Pages: `index.html`, `topic-cybersecurity.html`, `topic-privacy.html`,
`topic-integrity.html`, `topic-ml.html`, `courses.html`,
`speaker-series.html`, `annual-event.html`, `news.html`, `events.html`,
`people.html`, `about.html`.

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

The script writes directly into `site/`.

## Branding notes

- The UMD School of Public Policy logo is in `site/assets/img/umd-spp-logo.png`.
- `site/assets/img/gotech-logo.svg` is currently a placeholder wordmark —
  swap in the official GoTech logo file under the same name once available.
- Colors and type live in `site/assets/css/styles.css` (`:root` variables at
  the top of the file).

## Known placeholders

Sample/illustrative content that should be replaced with real data before
launch: people bios, publication and project descriptions, and event dates
in `build/build_all.py`.
