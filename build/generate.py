#!/usr/bin/env python3
"""
Static site generator for the Tech Policy Hub redesign.
Assembles flat HTML pages (shared header/footer) into ../docs/
(named "docs" so GitHub Pages can serve it directly from main /docs).
No build step needed to VIEW the site -- just open the .html files.
Re-run this script any time page content or the header/footer changes.
"""
import calendar
import datetime
import json
import os
import re

import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..", "docs")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_data(name):
    """Load build/data/<name>.yml -- the site's real content (people,
    events, research areas, news, ...), externalized out of this file's
    Python literals so it can be edited without touching code: by hand
    in any text editor or GitHub's own web editor, and eventually
    through a CMS admin UI that commits straight to these same files
    (see README "Editing content"). Every constant below that used to be
    an inline list/dict literal is now just `load_data("<name>")` --
    same variable name, same shape, so nothing downstream needed to
    change. `TOPIC_DETAIL` in build_all.py follows the same pattern via
    this same function (it isn't generate.py's own data, so it isn't
    loaded here)."""
    path = os.path.join(DATA_DIR, f"{name}.yml")
    with open(path) as f:
        return yaml.safe_load(f)

# Absolute site URL -- used for the .ics feed's UIDs/event links (which need
# to be absolute regardless of what page linked to the feed) and for the
# webcal:// subscribe link on events.html (same URL, scheme swapped).
SITE_URL = "https://chadl22.github.io/Tech-Policy-Hub/"

# Bumped by hand whenever styles.css / main.js change, and appended as a
# query string to their <link>/<script> tags below. Without this, browsers
# (and GitHub Pages' CDN) can keep serving a stale cached copy of the CSS/JS
# against a freshly-deployed HTML file -- which is what produced the
# broken/unstyled ticker a user saw right after a previous deploy.
ASSET_VERSION = "2026091402"

# Every generated page (other than the homepage) is written into its own
# folder as an index.html, e.g. news.html -> news/index.html, so it serves
# at a clean, extension-less URL (.../Tech-Policy-Hub/news/) instead of
# .../Tech-Policy-Hub/news.html. LINK_ATTR_RE finds href/src attributes in
# the assembled HTML so write() can rewrite them to match, without having
# to touch every place a link is built.
LINK_ATTR_RE = re.compile(r'(href|src)="([^"]+)"')


def _rewrite_links(html, prefix):
    """Rewrite internal href/src values to clean URLs. `prefix` is '' when
    writing the homepage (root-level, links into sibling folders need no
    prefix) or '../' when writing any other page (one level deep, needs to
    climb back up to root first). External links, mailto:, and in-page
    anchors (#...) are left untouched. Also handles an in-page anchor on
    the homepage itself, e.g. href="index.html#subscribe" (used by the
    header's persistent Subscribe button so it works from any page)."""
    def repl(m):
        attr, val = m.group(1), m.group(2)
        if val.startswith(("http://", "https://", "mailto:", "#", "//")):
            return m.group(0)
        if val == "index.html" or val.startswith("index.html#"):
            frag = val[len("index.html"):]  # '' or '#subscribe'
            if prefix:
                return f'{attr}="{prefix}{frag}"'
            return f'{attr}="{frag}"' if frag else m.group(0)
        if val.startswith("assets/"):
            return f'{attr}="{prefix}{val}"'
        m2 = re.match(r"^([\w.-]+)\.html(#.*)?$", val)
        if m2:
            frag = m2.group(2) or ""
            return f'{attr}="{prefix}{m2.group(1)}/{frag}"'
        return m.group(0)
    return LINK_ATTR_RE.sub(repl, html)


def clean_stale_pages():
    """Remove leftover flat top-level *.html files from the previous
    (pre-clean-URL) build -- everything but index.html now lives in its
    own folder. Safe to call even if ROOT doesn't exist yet."""
    if not os.path.isdir(ROOT):
        return
    for fname in os.listdir(ROOT):
        if fname.endswith(".html") and fname != "index.html":
            os.remove(os.path.join(ROOT, fname))
            print("removed stale", fname)

# NAV -- top-level tabs per follow-up 33: Home / Research / Events /
# People (News and About dropped from the primary nav -- both are still
# reachable via the footer's link list, see footer() below, so nothing
# is orphaned). Follow-up (direct user request): Research and Events no
# longer have dropdown submenus -- each is now a plain link straight to
# its section page. The section pages themselves already offer the finer
# navigation the dropdowns used to (research.html's filter pills reach the
# individual focus areas and Publications; events.html links out to
# Speaker Series / Annual Event), so nothing the dropdowns offered is
# actually lost. Each entry is (label, href, children); children stays
# None for every item now, but the tuple shape (and nav_html()'s dropdown
# branch) is left in place in case a future item needs one again.
NAV = [
    ("Home", "index.html", None),
    ("Research", "research.html", None),
    ("Events", "events.html", None),
    ("People", "people.html", None),
]


def nav_html(active):
    items = []
    for label, href, children in NAV:
        is_current = href == active
        if children:
            child_current = any(c[1].split("#")[0] == active for c in children)
            li_class = "has-dropdown" + (" current" if (is_current or child_current) else "")
            sub = "".join(f'<li><a href="{h}">{l}</a></li>' for l, h in children)
            items.append(
                f'<li class="{li_class}"><a href="{href}" class="nav-link" aria-haspopup="true" aria-expanded="false">{label} <span class="caret" aria-hidden="true">&#9662;</span></a>'
                f'<ul class="dropdown">{sub}</ul></li>'
            )
        else:
            li_class = "current" if is_current else ""
            items.append(f'<li class="{li_class}"><a href="{href}" class="nav-link">{label}</a></li>')
    return "".join(items)


def head(title, description):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Tech Policy Hub</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="assets/css/styles.css?v={ASSET_VERSION}">
</head>
<body>
"""


def header(active):
    # Follow-up (direct user request, after seeing the mobile/narrow-
    # screen nav take over the entire viewport with no visible way out):
    # the collapsed nav below the 1080px breakpoint (see styles.css) is
    # now a bounded-width slide-in drawer, not a full-screen takeover --
    # `.nav-backdrop` dims the rest of the page (and closes the drawer
    # on click), and `.nav-close` is an explicit, always-visible close
    # button inside the drawer itself, in addition to the hamburger
    # (`.nav-toggle`) now morphing into an X when open and Escape also
    # closing it (see main.js). `.nav-backdrop` sits here, a sibling of
    # `.primary-nav`/`.header-actions`, purely because position:fixed
    # makes its DOM position irrelevant to where it renders.
    return f"""
<header class="site-header">
  <div class="container header-inner">
    <div class="brand-lockup">
      <a href="index.html" class="brand" aria-label="Tech Policy Hub, University of Maryland School of Public Policy">
        <img src="assets/img/sopp-tph-lockup.png?v={ASSET_VERSION}" alt="University of Maryland School of Public Policy &ndash; Tech Policy Hub" class="brand-mark">
      </a>
    </div>
    <nav class="primary-nav" aria-label="Primary">
      <div class="nav-panel-head">
        <button type="button" class="nav-close" aria-label="Close menu">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <ul>{nav_html(active)}</ul>
    </nav>
    <div class="nav-backdrop"></div>
    <div class="header-actions">
      <a href="index.html#subscribe" class="btn btn-primary">Subscribe</a>
      <button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>
"""


def affiliation_strip():
    """Thin band under the header -- was institutional affiliation text
    (University of Maryland / School of Public Policy / GoTech), then
    (follow-up 11) quick links to the Hub's 4 research areas. As of
    follow-up 16, no longer called from page() -- removed per request,
    replaced by the homepage's research_matrix_html() section. Left
    defined here in case it's wanted again."""
    links = "".join(
        f'<a href="{t["file"]}">{t["name"]}</a><span class="dot" aria-hidden="true">&middot;</span>'
        for t in TOPICS
    )
    # strip the trailing separator after the last link
    links = links.rsplit('<span class="dot" aria-hidden="true">&middot;</span>', 1)[0]
    return f"""
<div class="affiliation-strip">
  <div class="container">
    {links}
  </div>
</div>
"""


def ticker_section():
    """NYSE-tape-style signal rail, one line tall, present on every page
    (direct user request) right under the header: the "Policy Updates"
    label and the scrolling lane sit in the same flex row (see
    .signal-ticker in styles.css). Scope is deliberately narrow
    -- real, tracked tech policy activity in the DMV (DC/MD/VA) and at
    the federal level only, each item badged with its jurisdiction (see
    TICKER_ITEMS below). Streams continuously (main.js drives a
    requestAnimationFrame loop over .ticker-viewport's scrollLeft, with
    ticker_track_html() below duplicating the item list so the loop is
    seamless), pauses the moment the pointer enters the lane, and is
    click-and-drag scrubbable in either direction while paused/hovering.
    TICKER_ITEMS is machine-generated (see _load_ticker_items() and
    build/refresh_ticker.py) from the Integrity Institute's Tech Policy
    Tracker on a weekly schedule -- see .github/workflows/refresh-ticker.yml
    -- rather than hand-curated like the rest of the site's content."""
    return f"""
<div class="signal-ticker" aria-label="Latest DMV and federal policy updates -- hover to pause, drag to scrub">
  <span class="ticker-live"><span class="dot" aria-hidden="true"></span><span class="label">Policy Updates</span></span>
  <div class="ticker-viewport">
    {ticker_track_html(TICKER_ITEMS)}
  </div>
</div>
"""


def footer():
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="footer-social">
          <a href="https://sclanga.substack.com/" target="_blank" rel="noopener" aria-label="Substack">
            <img src="assets/img/social/substack.png?v={ASSET_VERSION}" alt="" loading="lazy">
          </a>
          <a href="https://x.com/phronesisres" target="_blank" rel="noopener" aria-label="X">
            <img src="assets/img/social/x.png?v={ASSET_VERSION}" alt="" loading="lazy">
          </a>
          <a href="https://www.instagram.com/phronesisres" target="_blank" rel="noopener" aria-label="Instagram">
            <img src="assets/img/social/instagram.png?v={ASSET_VERSION}" alt="" loading="lazy">
          </a>
          <a href="https://www.threads.com/@phronesisres" target="_blank" rel="noopener" aria-label="Threads">
            <img src="assets/img/social/threads.png?v={ASSET_VERSION}" alt="" loading="lazy">
          </a>
          <a href="https://www.tiktok.com/@phronesis.research" target="_blank" rel="noopener" aria-label="TikTok">
            <img src="assets/img/social/tiktok.png?v={ASSET_VERSION}" alt="" loading="lazy">
          </a>
        </div>
        <ul class="footer-legal">
          <li><a href="#">Privacy Policy</a></li>
          <li><a href="#">Web Accessibility</a></li>
          <li><a href="#">Notice of Non-discrimination</a></li>
        </ul>
      </div>
      <div>
        <h4>Research</h4>
        <ul>
          <li><a href="research.html#area-panel-cybersecurity">Cybersecurity</a></li>
          <li><a href="research.html#area-panel-privacy">Consumer Privacy</a></li>
          <li><a href="research.html#area-panel-integrity">Information Integrity</a></li>
          <li><a href="research.html#area-panel-ml">Trustworthy ML</a></li>
          <li><a href="courses.html">Teaching</a></li>
        </ul>
      </div>
      <div>
        <h4>Events</h4>
        <ul>
          <li><a href="speaker-series.html">Speaker Series</a></li>
          <li><a href="annual-event.html">Annual Event</a></li>
        </ul>
      </div>
      <div>
        <h4>Connect</h4>
        <ul>
          <li><a href="events.html">Events</a></li>
          <li><a href="people.html">People</a></li>
          <li><a href="index.html#about">About &amp; Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-bottom-brand">
        <img src="assets/img/gtech-main.svg" alt="Center for Governance of Technology and Systems (GoTech), University of Maryland">
        <span>University of Maryland School of Public Policy</span>
      </div>
      <div class="footer-bottom-partner">Newsletters, social, and events produced in partnership with <a href="https://phronesisresearch.org" target="_blank" rel="noopener">The Phronesis Institute</a></div>
      <div class="footer-bottom-copyright">&copy; 2026 Tech Policy Research and Education Hub</div>
    </div>
  </div>
</footer>
<script src="assets/js/main.js?v={ASSET_VERSION}"></script>
</body>
</html>
"""


def page(active, title, description, body):
    # Follow-up (direct user request): the Policy Updates ticker used to
    # be homepage-only (an explicit ticker=True on that one g.page()
    # call) -- it's unconditional now, right under the header on every
    # page, not just the home page.
    return head(title, description) + header(active) + ticker_section() + body + footer()


def write(name, content):
    os.makedirs(ROOT, exist_ok=True)
    if name == "index.html":
        content = _rewrite_links(content, "")
        out_path = os.path.join(ROOT, "index.html")
    else:
        assert name.endswith(".html"), f"expected a '*.html' page name, got {name!r}"
        slug = name[:-5]
        page_dir = os.path.join(ROOT, slug)
        os.makedirs(page_dir, exist_ok=True)
        content = _rewrite_links(content, "../")
        out_path = os.path.join(page_dir, "index.html")
    with open(out_path, "w") as f:
        f.write(content)
    print("wrote", os.path.relpath(out_path, ROOT))


def write_raw(name, content):
    """Write a non-HTML file straight into ROOT (docs/) with no link
    rewriting -- used for events.ics, which lives at the site root
    alongside index.html regardless of clean-URL page routing."""
    os.makedirs(ROOT, exist_ok=True)
    out_path = os.path.join(ROOT, name)
    with open(out_path, "w", newline="") as f:
        f.write(content)
    print("wrote", os.path.relpath(out_path, ROOT))


# ---------------------------------------------------------------------------
# Reusable content fragments
# ---------------------------------------------------------------------------

# Content lives in build/data/topics.yml -- see README "Editing content".
TOPICS = load_data("topics")

# Each research area's accent color + short code, used for the small
# colored .area-tag badge wherever a person/project/publication is tagged
# with an area -- research.html's People/Project tiles and Publications
# rows, and people.html's per-person research-area badges (see
# PEOPLE_ITEMS below). Moved here from build_all.py (was research.html-
# only) once the People page started using the same badge/filter-pill
# language for the same four areas -- one shared source of truth for the
# color+code instead of two.
# Content lives in build/data/area_meta.yml -- see README "Editing content".
AREA_META = load_data("area_meta")

# Homepage "Research Spotlight" slideshow -- 3-5 real Hub outputs across
# formats (papers, media appearances, presentations), not just papers, so
# "primary_label" varies per item ("Read the Paper" / "Read the Coverage" /
# "Event Details") instead of a single "Read the Research" for everything.
# Content is pulled from the same real, verified NEWS_ITEMS entries used
# elsewhere on the site -- see follow-up 26.
# Content lives in build/data/spotlight_items.yml -- see README "Editing content".
SPOTLIGHT_ITEMS = load_data("spotlight_items")

# Follow-up 52: this is now the SOLE place NEWS_ITEMS is listed in full --
# the standalone news.html page was removed (the homepage's "Hub News"
# rail became a real scrollable list showing every entry, per direct user
# request comparing it to CNBC's "Latest News" sidebar box). One item
# below used to placeholder-link to "news.html" itself (a real link was
# never sourced for it); now links to "#" like other not-yet-linked
# placeholders elsewhere in the site (e.g. READING_ITEMS).
# Content lives in build/data/news_items.yml -- see README "Editing content".
NEWS_ITEMS = load_data("news_items")

# Category -> color for the homepage calendar's legend/dots (see
# calendar_widget_html() / calendar_legend_html()). Kept in Hub brand
# colors (red/gold/ink/teal) plus --slate-gray for the 5th category,
# since the site otherwise only defines those four.
# Follow-up (direct user request): "Conference" is a category for
# events the Hub did NOT organize -- field-wide technology policy
# conferences it wants visitors to know about, in support of the field
# more broadly rather than only its own programming (Speaker Series,
# Workshop, Roundtable, Annual Event). See EVENTS_ITEMS below for how
# that shows up in practice, and events_rows_html()'s docstring for why
# those rows open in a new tab.
# Content lives in build/data/event_categories.yml -- see README "Editing content".
EVENT_CATEGORIES = load_data("event_categories")

# Content lives in build/data/events.yml -- see README "Editing content".
EVENTS_ITEMS = load_data("events")

# Past events -- same fields as EVENTS_ITEMS so both can share
# events_rows_html()/filter_pills_html(). The three Speaker Series/Roundtable
# entries and the Annual Event recap already existed as illustrative cards
# on speaker-series.html and annual-event.html (see build_all.py); pulled
# out here as one shared source of truth so events.html's new "Past Events"
# section, the Speaker Series page's "Past sessions," and the Annual
# Event page's "2026 Recap" all read from the same data instead of drifting.
# Same caveat as those existing entries: illustrative placeholder content,
# not verified real dates -- see "Known placeholders" in the README.
# Content lives in build/data/past_events.yml -- see README "Editing content".
PAST_EVENTS_ITEMS = load_data("past_events")

# Role-type facet for the People page's second filter dimension (direct
# user request: "filter by role type (affiliate, grad student, leads
# etc)"), independent of and ANDed with the research-area filter below --
# a person can carry more than one (Dr. Harry is both an Affiliate and a
# research-area Lead), same multi-select-per-row idea as PEOPLE_ITEMS'
# `role_types` list and TOPIC_DETAIL's areas. Keys are what main.js's
# researchExplorer matches on (data-roles); values are the filter-pill
# labels people.html shows.
# Content lives in build/data/role_types.yml -- see README "Editing content".
ROLE_TYPES = load_data("role_types")

# `bio`, `website`, and `linkedin` added per direct user request for the
# People page redesign (headshot + bio + links + role/area badges). Real
# copy/links aren't gathered yet for most entries -- see README "Known
# placeholders" -- so `bio` extends each person's existing one-line
# `focus` into a short placeholder paragraph using only facts already on
# record here (role + focus), not invented biographical detail, and
# `website`/`linkedin` are None except where a real URL already exists
# elsewhere on the site (the founder's site, already linked from the
# homepage's "become affiliated" line). people.html's card renderer skips
# any link field that's None rather than showing a broken/empty link.
# Each person's research-area badges are NOT stored here -- they're
# derived from TOPIC_DETAIL's per-area `people` lists (build_all.py),
# the site's one existing source of truth for who works in which area,
# rather than duplicating that mapping into a second list here that could
# drift out of sync with it.
# Content lives in build/data/people.yml -- see README "Editing content".
PEOPLE_ITEMS = load_data("people")

# Homepage signal ticker -- real, tracked tech policy activity in the DMV
# (DC/MD/VA) and at the federal level only (see ticker_section()
# docstring), each item badged with its jurisdiction rather than grouped
# into channel tabs. NYSE-tape style: short "BILL NO. -- short title"
# strings, not full descriptions -- the full citation lives at the link.
# Hand-pulled from the Integrity Institute's Tech Policy Tracker
# (us-federal.techpolicytracker.com and us-state.techpolicytracker.com)
# and Congress.gov/state legislature sites as of Aug 2026 -- not a live
# feed, so this needs a periodic manual refresh to stay current as bills
# move.
def _load_ticker_items():
    """TICKER_ITEMS used to be a hand-curated literal list here. It's now
    machine-generated by build/refresh_ticker.py (real bill data pulled from
    the Integrity Institute Tech Policy Tracker's own search backend -- see
    that script's docstring for how/why) into build/data/ticker.json, kept
    on a regular refresh schedule by .github/workflows/refresh-ticker.yml.
    Loading it here (rather than inlining the JSON) keeps that file as the
    single source of truth the workflow overwrites, with generate.py just
    reading whatever it currently contains -- exactly like any other
    checked-in content file, just not hand-edited directly anymore. Run
    `python3 refresh_ticker.py` from build/ to pull a fresh copy by hand."""
    path = os.path.join(os.path.dirname(__file__), "data", "ticker.json")
    with open(path) as f:
        data = json.load(f)
    return [dict(jurisdiction=it["jurisdiction"], datum=it["datum"], link=it["link"])
            for it in data["items"]]


TICKER_ITEMS = _load_ticker_items()

# Questions We Answer -- same six questions as the Hub's mission ("Questions
# we ask"), each tagged to the research area it connects to so they double
# as intellectual navigation, not just mission-statement copy. Homepage
# shows a curated subset (see build_all.py); About shows all six.
# Content lives in build/data/questions.yml -- see README "Editing content".
QUESTIONS = load_data("questions")

# Ideas We're Reading -- placeholder examples for the Phronesis + Tech
# Policy Press list ("Field Pulse" on the homepage -- a static 3-column
# grid as of follow-up 46, not a scrolling carousel). NOT real published
# articles; swap for the Hub's actual picks before launch (see README
# "Known placeholders"). No longer feeds the signal ticker, which is now
# DMV/federal policy tracking only (see TICKER_ITEMS above).
#
# Follow-up 49: each item now carries a `type` field -- ONE of Phronesis's
# own 6 content-format categories (see READING_TYPES below), NOT a
# UMD-research-area tag (that's exactly what was removed in follow-up 47,
# since an outside reading might not fit one of the Hub's own 4 areas).
# This is orthogonal: it labels the KIND of writing (report vs. essay vs.
# legal analysis...), a classification the source site itself uses, not a
# claim about which of the Hub's topics it belongs to. Dict keys stay the
# PLURAL collection names (matching Phronesis's own section names/URLs,
# and what `type=` on each READING_ITEMS entry is set to); READING_TYPE_LABELS
# holds the SINGULAR form each kicker actually displays -- a direct user
# correction ("the category should be singular not plural"), since one
# card is tagging one piece, not a whole collection.
# Content lives in build/data/reading_types.yml -- see README "Editing content".
READING_TYPES = load_data("reading_types")
# Content lives in build/data/reading_type_labels.yml -- see README "Editing content".
READING_TYPE_LABELS = load_data("reading_type_labels")

# Content lives in build/data/reading_items.yml -- see README "Editing content".
READING_ITEMS = load_data("reading_items")

def ticker_html(items):
    """Each item is badged with its jurisdiction (DC/MD/VA/FED) instead of
    a free-text category label, since the ticker's whole scope is now
    DMV + federal tech policy tracking -- see TICKER_ITEMS."""
    return "".join(f"""
        <a class="signal-card" href="{it['link']}"{link_attrs(it['link'])}><span class="jurisdiction">{it['jurisdiction']}</span><span class="datum">{it['datum']}</span></a>""" for it in items)


def ticker_track_html(items):
    """Renders the item list twice back-to-back inside one
    .ticker-track-inner. main.js auto-scrolls .ticker-viewport's
    scrollLeft continuously and jumps back by exactly half of
    .ticker-track-inner's width once it's scrolled past the first copy
    -- with two identical copies that jump is invisible, so the tape
    loops seamlessly instead of hitting a hard edge. Drag-scrubbing
    wraps the same way in either direction."""
    return f'<div class="ticker-track"><div class="ticker-track-inner">{ticker_html(items)}{ticker_html(items)}</div></div>'


def question_cards_html(items):
    out = []
    for q in items:
        out.append(f"""
        <a class="question-card" href="{q['link']}">
          <h3>{q['text']}</h3>
          <span class="qtag">{q['tag']}</span>
        </a>""")
    return "".join(out)


def question_list_html(items):
    """Compact text-list treatment for the full 6-question set on About --
    deliberately NOT the same big card component the homepage uses for its
    curated 4, so About reads as the complete reference rather than a
    repeat of the homepage section at a larger size."""
    out = []
    for q in items:
        out.append(f"""
        <a class="question-row" href="{q['link']}">
          <span class="qtag">{q['tag']}</span>
          <span class="qtext">{q['text']}</span>
        </a>""")
    return "".join(out)


def guiding_questions_html(items):
    """Rounded-rectangle card grid for the homepage's Guiding Questions
    section (#about) -- one .guide-q card per question, laid out via
    .guide-q-list's CSS grid (4 cols desktop, responsive down to 1).
    Modeled on a Bloomberg reference the user provided: bordered white
    cards like Bloomberg's "Odd Lots" row, under a plain bold section
    title positioned like Bloomberg's "How To" label (see .guiding-head
    in styles.css) -- replacing the previous dark full-bleed band with a
    numbered text list. Not clickable (see follow-up 34) -- each item's
    per-topic link was dropped on request, and no hover highlight (follow-
    up 54) since these don't navigate anywhere."""
    out = []
    for i, q in enumerate(items, start=1):
        out.append(f"""
        <div class="guide-q">
          <span class="num">{i:02d}</span>
          <span class="qtext">{q['text']}</span>
        </div>""")
    return "".join(out)


def lead_media_html(topic_label):
    """Abstract editorial graphic (brand diagonal + topic label) for the
    homepage's Featured Publication -- deliberately not a photo, since we
    don't have real photography for these articles/events on file yet
    (see follow-up 11). Swap for a real image per-article later if the
    Hub supplies one."""
    return f"""
        <div class="lead-media"><span class="topic-mark">{topic_label}</span></div>"""


def spotlight_html(items):
    """Homepage "Research Spotlight" -- a small slideshow (one slide visible
    at a time, NOT a static list like Field Pulse) of 3-5 Hub outputs and
    Hub-adjacent research: papers, media appearances, presentations, etc.,
    NOT all necessarily Hub-authored -- the Hub is interdisciplinary and
    this is meant to also carry tech-policy-relevant work from other
    campus departments/labs (see .spotlight-credit below).

    Rebuilt (follow-up) into a single bordered .spotlight-card per a
    Bloomberg "Today's Videos" card reference the user provided:
      .rail-head          the "Research Spotlight" label, back to a plain
                          rail-head ABOVE the card -- per direct user
                          request, matching the "What We Do"/"Research
                          Areas"/"Hub News" headers on the other lead-grid
                          columns rather than living in its own boxed
                          strip inside the card (an earlier version of
                          this put the label + a "View All Research" link
                          in a gray strip at the top of the card; dropped
                          per user feedback that it made this column's
                          header uniquely different from its siblings).
      .spotlight-media-track   the image (one .spotlight-media-slide per
                          item) plus the persistent .spotlight-pause
                          toggle, inset in its bottom-right corner. Now
                          the card's first/top element, so its top
                          corners are what .spotlight-card's rounded
                          corners + overflow:hidden actually clip.
      .spotlight-track    title/meta/credit/summary/actions (one
                          .spotlight-slide per item).
      .spotlight-footer   persistent bottom bar -- .spotlight-dots (left)
                          + the prev/next .spotlight-arrow buttons
                          (right), anchored together like the reference's
                          bottom control row. Same --paper-soft gray as
                          the old header strip used, per direct user
                          request, even though that strip itself is gone.
    .spotlight-media-track/.spotlight-track still use the CSS Grid
    stacking trick (every slide sharing one grid-area, sized to the
    tallest) as two independent stacks, so each track's height stays
    constant regardless of which slide is active -- main.js's show()
    toggles the matching .spotlight-media-slide/.spotlight-slide pair
    (same data-slide index) together. main.js finds every [data-spotlight],
    auto-advances through an .is-active class, pauses on hover, and wires
    the .spotlight-dot / prev-next / pause controls -- none of that
    changed, only where those controls sit in the markup (main.js queries
    by class/attribute, not DOM position, so the move is CSS/HTML-only)."""
    media_slides = []
    text_slides = []
    for i, it in enumerate(items):
        active = " is-active is-visible" if i == 0 else ""
        media_slides.append(f"""
        <div class="spotlight-media-slide{active}" data-slide="{i}">
          {lead_media_html(it['topic'])}
        </div>""")
        text_slides.append(f"""
        <div class="spotlight-slide{active}" data-slide="{i}">
          <h1><a href="{it['link']}"{link_attrs(it['link'])}>{it['title']}</a></h1>
          <div class="meta"><span class="meta-tag">{it['tag']}</span> {it['date']}</div>
          <div class="spotlight-credit">{it['source']}</div>
          <p class="lede">{it['summary']}</p>
          <div class="hero-actions">
            <a href="{it['link']}"{link_attrs(it['link'])} class="btn btn-primary btn-arrow">{it['primary_label']}</a>
            <a href="{it['topic_file']}" class="btn btn-ghost">Explore {it['topic']}</a>
          </div>
        </div>""")
    dots = "".join(
        f'<button type="button" class="spotlight-dot{" is-active" if i == 0 else ""}" data-index="{i}" aria-label="Show spotlight item {i + 1} of {len(items)}"></button>'
        for i in range(len(items))
    )
    return f"""
      <div class="rail-head">Research Spotlight</div>
      <div class="spotlight-card" data-spotlight>
        <div class="spotlight-media-track">{''.join(media_slides)}
          <button type="button" class="spotlight-pause" data-spotlight-pause aria-pressed="false" aria-label="Pause slideshow">
            <i class="bar bar-1"></i><i class="bar bar-2"></i><i class="tri"></i>
          </button>
        </div>
        <div class="spotlight-track">{''.join(text_slides)}
        </div>
        <div class="spotlight-footer">
          <div class="spotlight-dots">{dots}</div>
          <div class="spotlight-arrows">
            <button type="button" class="spotlight-arrow spotlight-prev" data-spotlight-prev aria-label="Previous spotlight item"></button>
            <button type="button" class="spotlight-arrow spotlight-next" data-spotlight-next aria-label="Next spotlight item"></button>
          </div>
        </div>
      </div>"""


def reading_cards_html(items):
    """Field Pulse ("What we're reading") -- follow-up 46: rebuilt onto the
    site's existing .card component (the same one news_cards_html() uses)
    instead of a bespoke bordered read-card, per a direct user request
    with a SCOTUSblog "More News & Commentary" screenshot as the target:
    plain text rows (headline, one-line dek, byline-style source/read-time)
    with hairline dividers between grid columns, NOT individually-boxed
    cards -- no .media block, since outside reading doesn't get a
    thumbnail here any more than it did as a read-card.

    Follow-up 47: no research-area kicker on these cards, unlike
    news_cards_html(). These are outside pieces we're reading, not our own
    research output -- tagging them with one of the Hub's own research
    areas implies a formal categorization that may not fit, since a given
    piece can easily fall outside the Hub's defined topics.

    Follow-up 49: a kicker is back, but it now labels the piece's FORMAT
    (one of READING_TYPES, Phronesis's own 6-way content taxonomy) rather
    than a UMD research area -- a different axis of categorization the
    follow-up-47 objection doesn't apply to, and one that also helps tell
    the six titles apart at a glance now that they're tighter-packed.
    Linked out to the matching phronesisresearch.org/<type> page rather
    than a plain span, since a real destination exists for each one. The
    displayed label is the SINGULAR form (READING_TYPE_LABELS) -- one card
    tags one piece, not a whole collection -- while the link still keys
    off the plural `type` value, which is what matches Phronesis's own
    section names/URLs.

    Follow-up 50: the type label no longer uses the boxed/bordered
    `.kicker` treatment -- a direct request to lean on SCOTUSblog's own
    style more closely, which sets its category labels (COURT NEWS,
    EMPIRICAL SCOTUS, ...) as plain italic caption text, no box. Renders
    as `.reading-type` instead (italic, uppercase, no border/background).

    `summary` and `link` are written as if pulled directly from Phronesis:
    `summary` is Phronesis's own dek for the piece, and `link` points at
    the ORIGINAL document (not phronesisresearch.org) -- Phronesis is
    the source of the metadata, not the destination. Still placeholder
    text/`#` links until real Phronesis data replaces READING_ITEMS."""
    out = []
    for r in items:
        type_url = READING_TYPES[r["type"]]
        type_label = READING_TYPE_LABELS[r["type"]]
        out.append(f"""
        <div class="card">
          <a class="reading-type" href="{type_url}" target="_blank" rel="noopener">{type_label}</a>
          <h3><a href="{r['link']}"{link_attrs(r['link'])}>{r['title']}</a></h3>
          <p>{r['summary']}</p>
          <span class="meta">{r['source']} &middot; {r['meta']}</span>
        </div>""")
    return "".join(out)


def link_attrs(url):
    """Real news/press links point off-site (journals, arXiv, Zoom
    registration, Newsweek, etc.) -- open those in a new tab so a click
    doesn't navigate a visitor away from the Hub's own site. Internal
    .html links behave normally."""
    return ' target="_blank" rel="noopener"' if url.startswith("http") else ""


def rail_html(entries):
    """Compact CNBC/Bloomberg-style headline rail: a tag/date plus a linked
    title, hairline-divided, no imagery. Used for the side rails next to
    the homepage hero and the Recent News section, so those sections don't
    have to be one massive full-width block to feel substantial -- entries
    need 'tag', 'title', and 'link' keys. 'date' is optional (NEWS_ITEMS
    has one, EVENTS_RAIL doesn't -- it bakes its own date into 'tag'
    instead) -- shown next to the tag, AP-style, via ap_date()."""
    out = []
    for e in entries:
        date_bit = f'<span class="date">{ap_date(e["date"])}</span>' if e.get("date") else ""
        out.append(f"""
        <a class="rail-item" href="{e['link']}"{link_attrs(e['link'])}><span class="tag">{e['tag']}</span>{date_bit}<h4>{e['title']}</h4></a>""")
    return "".join(out)


def feed_items_html(items, limit=None):
    out = []
    for it in (items[:limit] if limit else items):
        out.append(f"""
        <div class="feed-item">
          <span class="tag">{it['tag']}</span>
          <div>
            <div class="meta" style="margin-bottom:6px;">{it['date']}</div>
            <h3><a href="{it['link']}"{link_attrs(it['link'])}>{it['title']}</a></h3>
            <p>{it['summary']}</p>
          </div>
        </div>""")
    return "".join(out)


def topic_cards_html():
    out = []
    for t in TOPICS:
        out.append(f"""
        <div class="topic-card">
          <span class="index">{t['index']}</span>
          <h3><a href="{t['file']}">{t['name']}</a></h3>
          <p>{t['blurb']}</p>
          <a class="text-link" href="{t['file']}">Explore</a>
        </div>""")
    return "".join(out)


def topic_pills_html():
    """Gold outline pill buttons linking to each topic, used in the
    black statement band -- mirrors the Issues pill-nav on kgi.georgetown.edu,
    and carries the university's third brand color (gold) into the section."""
    out = [f'<a class="btn btn-gold" href="{t["file"]}">{t["name"]}</a>' for t in TOPICS]
    out.append('<a class="btn btn-gold" href="research.html">All Topics</a>')
    return "".join(out)


def topic_pills_plain_html():
    """Plain outline pills linking to each topic, for use on light
    backgrounds. No longer used by the Research hub page itself (see
    filter_pills_html() -- research.html's old topic pill-row was pure
    navigation duplicating the Focus Areas cards right below it, so it was
    replaced with an in-page filter instead), but left defined in case a
    future page wants a plain nav-only pill row."""
    return "".join(f'<a class="btn btn-ghost" href="{t["file"]}">{t["name"]}</a>' for t in TOPICS)


def search_box_html(placeholder, aria_label):
    """Shared search-box markup: an icon + text input carrying the
    .filter-search-input class main.js looks for (see applyFilters()) to
    combine with whatever [data-filter-group] pill bar is on the same
    page. Used on events.html (search events) and research.html (search
    publications) -- same component, different placeholder/label."""
    return f"""
      <div class="search-box">
        <svg class="search-box-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="7" cy="7" r="5.25" stroke="currentColor" stroke-width="1.5"/>
          <line x1="11.1" y1="11.1" x2="15" y2="15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <input type="text" class="search-box-input filter-search-input" placeholder="{placeholder}" aria-label="{aria_label}">
      </div>"""


def filter_pills_html(values, group):
    """Pill-button filter control: "All" plus one pill per string in
    `values`. Wired up by main.js's generic [data-filter-group] handler,
    which shows/hides every [data-filter-target] element on the page
    whose value matches the active pill (or shows everything for "All").
    `group` is just a stable label for the data attribute -- there's one
    filter bar per page today, so no scoping between multiple bars on the
    same page is needed. Used on research.html (filtering by topic name)
    and events.html (filtering by event category)."""
    pills = ['<button type="button" class="filter-pill active" data-filter="all">All</button>']
    pills += [f'<button type="button" class="filter-pill" data-filter="{v}">{v}</button>' for v in values]
    return f'<div class="filter-bar" data-filter-group="{group}">{"".join(pills)}</div>'


def research_matrix_html():
    """Miniature 2x2 grid of the Hub's 4 research areas -- homepage only,
    sits directly under the lead grid's Hub News rail (follow-up 16).
    Assumes exactly 4 TOPICS (a true 2x2); if that count ever changes
    this needs a different layout, not just more/fewer cells."""
    assert len(TOPICS) == 4, "research_matrix_html() is hard-coded for a 2x2 (4 topics)"
    return "".join(f"""
        <a class="matrix-cell" href="{t['file']}">
          <span class="index">{t['index']}</span>
          <h3>{t['name']}</h3>
          <p>{t['blurb']}</p>
        </a>""" for t in TOPICS)


def news_cards_html(items, limit=None):
    """3-column card grid with a flat media placeholder block above each
    item -- mirrors the news/research grid on kgi.georgetown.edu."""
    out = []
    for it in (items[:limit] if limit else items):
        out.append(f"""
        <div class="card">
          <div class="media"><span>{it['tag']}</span></div>
          <span class="kicker">{it['tag']}</span>
          <div class="meta">{it['date']}</div>
          <h3><a href="{it['link']}"{link_attrs(it['link'])}>{it['title']}</a></h3>
          <p>{it['summary']}</p>
        </div>""")
    return "".join(out)


_MONTH_NUM = {abbr.upper(): i for i, abbr in enumerate(calendar.month_abbr) if abbr}

# AP style: Jan./Feb./Aug./Sept./Oct./Nov./Dec. abbreviate when paired
# with a day number; March/April/May/June/July are always spelled out
# (they're already short enough AP doesn't shorten them further). When
# a NEWS_ITEMS date has no day (just "Mon YYYY"), AP style also spells
# the month out in full rather than abbreviating it.
_MONTH_AP_WITH_DAY = {
    1: "Jan.", 2: "Feb.", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "Aug.", 9: "Sept.", 10: "Oct.", 11: "Nov.", 12: "Dec.",
}


def ap_date(date_str):
    """Reformat a NEWS_ITEMS "date" value ("Jun 24, 2025" or "Jul 2025")
    into AP style for display in the Hub News rail, e.g. "June 24, 2025"
    or "July 2025"."""
    parts = date_str.replace(",", "").split()
    month_num = _MONTH_NUM[parts[0].upper()]
    if len(parts) == 3:
        _, day, year = parts
        return f"{_MONTH_AP_WITH_DAY[month_num]} {day}, {year}"
    _, year = parts
    return f"{calendar.month_name[month_num]} {year}"


def calendar_legend_html(categories):
    """Colored-square legend above the homepage calendar, one entry per
    EVENT_CATEGORIES key."""
    return "".join(
        f'<span class="cal-legend-item"><span class="sw" style="background:{color}" aria-hidden="true"></span>{name}</span>'
        for name, color in categories.items()
    )


def calendar_widget_html(events, categories):
    """Real month-grid calendar (Sun-Sat, correct weekday math via the
    stdlib calendar module) -- replaces the homepage's old Recent News
    feed. One panel per (year, month) that actually has an event, in
    the order those months first appear in `events`; main.js pages
    between panels with prev/next. Event days show a small dot per
    event, color-coded by category and linked to the event."""
    month_keys = []
    by_month = {}
    for e in events:
        key = (e["y"], _MONTH_NUM[e["m"]])
        if key not in by_month:
            by_month[key] = []
            month_keys.append(key)
        by_month[key].append(e)

    cal = calendar.Calendar(firstweekday=6)  # weeks start Sunday
    panels = []
    for i, (y, mnum) in enumerate(month_keys):
        events_by_day = {}
        for e in by_month[(y, mnum)]:
            events_by_day.setdefault(int(e["d"]), []).append(e)
        label = f"{calendar.month_name[mnum]} {y}"
        day_cells = []
        for week in cal.monthdayscalendar(y, mnum):
            for day in week:
                if day == 0:
                    day_cells.append('<div class="cal-day empty"></div>')
                    continue
                evs = events_by_day.get(day)
                if evs:
                    dots = "".join(
                        f'<a class="dot" style="background:{categories[e["cat"]]}" '
                        f'href="{e["link"]}"{link_attrs(e["link"])} title="{e["title"]}" aria-label="{e["title"]}"></a>'
                        for e in evs
                    )
                    day_cells.append(f'<div class="cal-day has-event"><span class="daynum">{day}</span><span class="dots">{dots}</span></div>')
                else:
                    day_cells.append(f'<div class="cal-day"><span class="daynum">{day}</span></div>')
        active = " active" if i == 0 else ""
        panels.append(f"""
        <div class="cal-month{active}" data-label="{label}">
          <div class="cal-weekdays"><span>S</span><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span></div>
          <div class="cal-days">{''.join(day_cells)}</div>
        </div>""")

    first_label = f"{calendar.month_name[month_keys[0][1]]} {month_keys[0][0]}" if month_keys else ""
    return f"""
        <div class="cal-widget">
          <div class="cal-head">
            <button type="button" class="cal-nav" data-dir="-1" aria-label="Previous month">&lsaquo;</button>
            <span class="cal-title">{first_label}</span>
            <button type="button" class="cal-nav" data-dir="1" aria-label="Next month">&rsaquo;</button>
          </div>
          <div class="cal-panels">{''.join(panels)}</div>
        </div>"""


def events_rows_html(items, limit=None, with_btn=True):
    """Each row carries data-filter-target="{category}" so events.html's
    filter_pills_html() bar can show/hide rows by category client-side --
    harmless on the other call sites (speaker-series.html, annual-event.html)
    that render a subset of events without a filter bar present.

    Follow-up (direct user request): events.html now also carries
    "Conference" entries -- field conferences the Hub didn't organize but
    wants visitors to know about, in support of the tech policy field
    more broadly (not just the Hub's own Speaker Series/Workshop/
    Roundtable/Annual Event programming). Those rows point at a real
    external site (e.g. the conference's own registration page), so
    link_attrs() -- the same helper reading_cards_html() uses for its
    off-site links -- opens them in a new tab instead of navigating the
    visitor away from the Hub."""
    out = []
    for e in (items[:limit] if limit else items):
        attrs = link_attrs(e["link"])
        btn = f'<a class="btn btn-ghost" href="{e["link"]}"{attrs} style="padding:8px 16px; font-size:.82rem;">Details</a>' if with_btn else ""
        out.append(f"""
        <div class="event-row" data-filter-target="{e['cat']}">
          <div class="event-date"><div class="d">{e['d']}</div><div class="m">{e['m']}</div></div>
          <div><h3><a href="{e['link']}"{attrs}>{e['title']}</a></h3><div class="meta">{e['meta']}</div></div>
          {btn}
        </div>""")
    return "".join(out)


def past_events_html(items, limit=None):
    """Compact rows for PAST_EVENTS_ITEMS -- month/year instead of a day
    number (that data was never day-precise, see PAST_EVENTS_ITEMS'
    docstring) and a one-line summary instead of a logistics meta line,
    since past events don't need "4:00 PM, Room 3137"-style detail. Shares
    .event-row's layout/CSS and the same data-filter-target mechanism as
    events_rows_html() so one filter bar on events.html covers both."""
    out = []
    for e in (items[:limit] if limit else items):
        out.append(f"""
        <div class="event-row event-row--past" data-filter-target="{e['cat']}">
          <div class="event-date"><div class="d">{e['y']}</div><div class="m">{e['m']}</div></div>
          <div><h3><a href="{e['link']}">{e['title']}</a></h3><div class="meta">{e['summary']}</div></div>
        </div>""")
    return "".join(out)


def _ics_escape(text):
    """Escape TEXT-type field values per RFC 5545 4.3.11."""
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _absolute_clean_url(link):
    """Turn a page-content-style link like 'speaker-series.html' into its
    real deployed clean-URL address (SITE_URL + 'speaker-series/'),
    mirroring write()'s own _rewrite_links() folder convention. The site
    only ever writes docs/<slug>/index.html (plus docs/index.html) -- a
    flat '.../speaker-series.html' URL 404s on the live (GitHub Pages)
    site, so events_ics()'s URL field needs this same rewrite, not just a
    naive SITE_URL + link concatenation."""
    if link.startswith(("http://", "https://", "mailto:")):
        return link
    if link == "index.html":
        return SITE_URL
    m = re.match(r"^([\w.-]+)\.html(#.*)?$", link)
    if m:
        return f"{SITE_URL}{m.group(1)}/{m.group(2) or ''}"
    return SITE_URL + link


def events_ics(events):
    """Static iCalendar (.ics) feed built from EVENTS_ITEMS at build time.
    All-day VEVENTs -- the site's per-event start times live inside the
    free-text `meta` field in varying formats ("4:00 PM · ...", "All day
    · ..."), not a structured time field, so all-day is the only
    representation we can build without inventing precise start/end times
    or a timezone. Written once to docs/events.ics (site root, alongside
    index.html) by build_all.py; events.html links to it both as a plain
    download and as a webcal:// URL so calendar apps (Google/Apple/Outlook)
    can subscribe and automatically pick up whatever's current next time
    the site rebuilds and redeploys -- this file is regenerated by every
    `python3 build_all.py` run, not hand-maintained.

    DTSTAMP is deliberately NOT "now" -- it's derived from each event's
    own start date instead (see the loop below), so re-running the
    generator against unchanged EVENTS_ITEMS data produces a byte-
    identical file. A wall-clock DTSTAMP was the actual root cause of a
    recurring git conflict: this file is regenerated independently both
    by a local build and by rebuild-on-content-change.yml's CI rebuild
    of the very same commit, and "now" differs by however many minutes
    passed between the two, so every VEVENT looked "changed" to git even
    when nothing about the event data had. A deterministic DTSTAMP means
    CI's rebuild matches the locally-committed output exactly whenever
    the data didn't change, so its "commit if changed" step has nothing
    to commit -- no more surprise bot commit landing on `main` right
    after your own push, and nothing to conflict with on your next pull."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//UMD Tech Policy Hub//Events//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Tech Policy Hub Events",
    ]
    for e in events:
        mnum = _MONTH_NUM[e["m"]]
        day = int(e["d"])
        start = datetime.date(e["y"], mnum, day)
        end = start + datetime.timedelta(days=1)  # DTEND is exclusive for an all-day VEVENT
        slug = re.sub(r"[^a-z0-9]+", "-", e["title"].lower()).strip("-")
        uid = f'{start.strftime("%Y%m%d")}-{slug}@techpolicyhub.umd.edu'
        url = _absolute_clean_url(e["link"])
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{start.strftime('%Y%m%d')}T000000Z",
            f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
            f"SUMMARY:{_ics_escape(e['title'])}",
            f"DESCRIPTION:{_ics_escape(e['meta'])}",
            f"CATEGORIES:{_ics_escape(e['cat'])}",
            f"URL:{url}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


print("Generator module loaded -- run build_all.py to write pages.")
