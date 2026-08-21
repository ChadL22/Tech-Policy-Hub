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

ROOT = os.path.join(os.path.dirname(__file__), "..", "docs")

# Absolute site URL -- used for the .ics feed's UIDs/event links (which need
# to be absolute regardless of what page linked to the feed) and for the
# webcal:// subscribe link on events.html (same URL, scheme swapped).
SITE_URL = "https://chadl22.github.io/Tech-Policy-Hub/"

# Bumped by hand whenever styles.css / main.js change, and appended as a
# query string to their <link>/<script> tags below. Without this, browsers
# (and GitHub Pages' CDN) can keep serving a stale cached copy of the CSS/JS
# against a freshly-deployed HTML file -- which is what produced the
# broken/unstyled ticker a user saw right after a previous deploy.
ASSET_VERSION = "2026082036"

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
# is orphaned). Publications and Teaching stay folded into Research as
# dropdown children (unchanged from the original redesign brief). Each
# entry is (label, href, children); children is None for a plain link,
# or a list of (label, href) for a dropdown. The parent href is a real
# page (not "#"), so clicking "Research" or "Events" itself navigates to
# that section's index -- the dropdown is an additional hover/tap
# affordance, not the only way in.
NAV = [
    ("Home", "index.html", None),
    ("Research", "research.html", [
        # No "All Research" entry -- clicking the "Research" label itself
        # (the <a href="research.html"> the dropdown is attached to) already
        # goes there, so a duplicate first child was pure redundancy. That
        # page is now filterable in-place (see filter_pills_html()) instead
        # of needing a nav entry to reach the unfiltered view.
        ("Cybersecurity", "topic-cybersecurity.html"),
        ("Consumer Privacy", "topic-privacy.html"),
        ("Information Integrity", "topic-integrity.html"),
        ("Trustworthy ML", "topic-ml.html"),
        ("Publications", "research.html#publications"),
        ("Teaching", "courses.html"),
    ]),
    ("Events", "events.html", [
        # Same reasoning as Research above -- "Events" itself already links
        # to events.html; that page is now filterable in-place.
        ("Speaker Series", "speaker-series.html"),
        ("Annual Event", "annual-event.html"),
    ]),
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
    return f"""
<header class="site-header">
  <div class="container header-inner">
    <div class="brand-lockup">
      <a href="https://gotech.umd.edu/" target="_blank" rel="noopener" class="umd-logo-link" aria-label="University of Maryland">
        <img src="assets/img/umd-seal.png?v={ASSET_VERSION}" alt="University of Maryland" class="umd-logo">
      </a>
      <span class="brand-divider" aria-hidden="true"></span>
      <a href="index.html" class="brand">
        <img src="assets/img/tph-mark.png?v={ASSET_VERSION}" alt="Tech Policy Hub" class="tph-mark">
      </a>
    </div>
    <nav class="primary-nav" aria-label="Primary">
      <ul>{nav_html(active)}</ul>
    </nav>
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
    """NYSE-tape-style signal rail, homepage only, one line tall: the
    "Policy Updates" label and the scrolling lane sit in the same flex
    row (see .signal-ticker in styles.css). Scope is deliberately narrow
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
          <a href="#" aria-label="LinkedIn">LinkedIn</a>
          <a href="#" aria-label="Bluesky">Bluesky</a>
          <a href="#" aria-label="YouTube">YouTube</a>
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
          <li><a href="topic-cybersecurity.html">Cybersecurity</a></li>
          <li><a href="topic-privacy.html">Consumer Privacy</a></li>
          <li><a href="topic-integrity.html">Information Integrity</a></li>
          <li><a href="topic-ml.html">Trustworthy ML</a></li>
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
          <li><a href="news.html">News</a></li>
          <li><a href="events.html">Events</a></li>
          <li><a href="people.html">People</a></li>
          <li><a href="about.html">About &amp; Contact</a></li>
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


def page(active, title, description, body, ticker=False):
    out = head(title, description) + header(active)
    if ticker:
        out += ticker_section()
    out += body + footer()
    return out


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

TOPICS = [
    dict(key="cybersecurity", file="topic-cybersecurity.html", index="01",
         name="Cybersecurity",
         blurb="Measuring attack surface, risk, and resilience across governments, critical infrastructure, and the private sector."),
    dict(key="privacy", file="topic-privacy.html", index="02",
         name="Consumer Privacy",
         blurb="Studying how privacy law is designed, enforced, and experienced -- from cookie-less tracking to watchdog accountability."),
    dict(key="integrity", file="topic-integrity.html", index="03",
         name="Information Integrity",
         blurb="Tracking misinformation, platform transparency, and the policies that shape what people see and trust online."),
    dict(key="ml", file="topic-ml.html", index="04",
         name="Trustworthy ML",
         blurb="Examining algorithmic accountability, AI governance, and the standards needed for machine learning the public can trust."),
]

# Homepage "Research Spotlight" slideshow -- 3-5 real Hub outputs across
# formats (papers, media appearances, presentations), not just papers, so
# "primary_label" varies per item ("Read the Paper" / "Read the Coverage" /
# "Event Details") instead of a single "Read the Research" for everything.
# Content is pulled from the same real, verified NEWS_ITEMS entries used
# elsewhere on the site -- see follow-up 26.
SPOTLIGHT_ITEMS = [
    dict(tag="Publication", topic="Consumer Privacy", topic_file="topic-privacy.html",
         date="Jul 2025",
         title="Cookie-less Identification: For and Against Privacy",
         summary="Work from the privacy team on the privacy implications of cookie-less identification on the Web was published in the Internet Policy Review.",
         primary_label="Read the Research",
         link="https://policyreview.info/articles/analysis/cookie-less-identification-foragainst-privacy"),
    dict(tag="Publication", topic="Information Integrity", topic_file="topic-integrity.html",
         date="Jul 2025",
         title="Classifying Trustworthy Content via Third-Party Web Structure",
         summary="New work classifying trustworthy content on the Web based on the third-party structure of websites was published through the FOCI workshop at PETs.",
         primary_label="Read the Paper",
         link="https://www.petsymposium.org/foci/2025/foci-2025-0017.pdf"),
    dict(tag="Media", topic="Cybersecurity", topic_file="topic-cybersecurity.html",
         date="Mar 2, 2025",
         title="Hub Cybersecurity Work Highlighted by Newsweek",
         summary="Research from the Hub's Cybersecurity group on county-level cyber risk was highlighted by Newsweek.",
         primary_label="Read the Coverage",
         link="https://www.newsweek.com/cybersecurity-risk-map-usa-counties-2026762"),
    dict(tag="Speaker Series", topic="Consumer Privacy", topic_file="topic-privacy.html",
         date="Mar 12, 2025",
         title="Spring 2025 Speaker Series: Privacy Research and Regulation",
         summary="An online Spring 2025 Speaker Series event on how privacy research can inform privacy regulation.",
         primary_label="Event Details",
         link="https://umd.zoom.us/meeting/register/HbxWvfXnSBWxFfr1a7vnQA"),
    dict(tag="Publication", topic="Cybersecurity", topic_file="topic-cybersecurity.html",
         date="Jan 17, 2025",
         title="Attack Surface Across U.S. County Governments Published in Journal of Cybersecurity",
         summary="Research on the size, diversity, and severity of exposed attack surface across U.S. county governments is officially published by the Journal of Cybersecurity.",
         primary_label="Read the Paper",
         link="https://academic.oup.com/cybersecurity/article/11/1/tyae032/7959399"),
]

NEWS_ITEMS = [
    dict(tag="Publication", date="Jul 2025",
         title="Cookie-less Identification: For and Against Privacy",
         summary="Work from the privacy team on the privacy implications of cookie-less identification on the Web was published in the Internet Policy Review.",
         link="https://policyreview.info/articles/analysis/cookie-less-identification-foragainst-privacy"),
    dict(tag="Publication", date="Jul 2025",
         title="Classifying Trustworthy Content via Third-Party Web Structure",
         summary="New work classifying trustworthy content on the Web based on the third-party structure of websites was published through the FOCI workshop at PETs.",
         link="https://www.petsymposium.org/foci/2025/foci-2025-0017.pdf"),
    dict(tag="Award", date="Jun 24, 2025",
         title="Lee Tiedrich Joins the Hub as AI Fellow",
         summary="Lee Tiedrich is joining the Tech Policy Hub as a co-leader and AI Fellow, under an award to Hub affiliates Charlie Harry and Katie Shilton.",
         link="https://gotech.spp.umd.edu/news/aim-seed-grants-support-22-ai-research-projects"),
    dict(tag="Event Recap", date="Jun 10, 2025",
         title="A Remarkable Annual Event",
         summary="The Hub's annual event brought together the community for a full day of tech policy programming -- a summary and photos are now available.",
         link="https://techpolicy.ischool.umd.edu/annual-event/"),
    dict(tag="Event", date="Jun 6, 2025",
         title="Join Us for the Tech Policy Hub Annual Event",
         summary="Details and registration for the in-person Tech Policy Hub Annual Event -- subscribe to our mailing list to stay informed.",
         link="https://drive.google.com/file/d/1j9EOplAzhqQ79f1RMfmoBkCWT-U1ytp2/view?usp=sharing"),
    dict(tag="Speaker Series", date="Mar 12, 2025",
         title="Spring 2025 Speaker Series: Privacy Research and Regulation",
         summary="An online Spring 2025 Speaker Series event on how privacy research can inform privacy regulation.",
         link="https://umd.zoom.us/meeting/register/HbxWvfXnSBWxFfr1a7vnQA"),
    dict(tag="Publication", date="Mar 2, 2025",
         title="Applying Contextual Integrity to Measure Web Privacy",
         summary="New work from Hub researchers applying Contextual Integrity to measure Web privacy is now available on arXiv.",
         link="https://arxiv.org/abs/2412.16246"),
    dict(tag="Media", date="Mar 2, 2025",
         title="Hub Cybersecurity Work Highlighted by Newsweek",
         summary="Research from the Hub's Cybersecurity group on county-level cyber risk was highlighted by Newsweek.",
         link="https://www.newsweek.com/cybersecurity-risk-map-usa-counties-2026762"),
    dict(tag="Speaker Series", date="Feb 26, 2025",
         title="Speaker Series: DeepSeek and AI Governance",
         summary="The first event in the Spring 2025 Speaker Series brought together an academic and a practitioner to discuss DeepSeek and what it means for AI governance.",
         link="https://umd.zoom.us/meeting/register/xRjQo5cHQPmW71fDVjoApw"),
    dict(tag="Recognition", date="Feb 24, 2025",
         title="Privacy Watchdog Accountability Work Accepted at PLSC",
         summary="Work by the Hub's researchers on the accountability powers of formal and informal U.S. privacy watchdogs has been accepted for the Privacy Law Scholars Conference (PLSC).",
         link="news.html"),
    dict(tag="Media", date="Feb 4, 2025",
         title="County Cyberattack Risk Work Highlighted by Maryland Today",
         summary="The Hub's work assessing attack surface across U.S. counties was highlighted by Maryland Today.",
         link="https://today.umd.edu/umd-researchers-calculate-cyberattack-risk-for-all-50-states"),
    dict(tag="Publication", date="Jan 17, 2025",
         title="Attack Surface Across U.S. County Governments Published in Journal of Cybersecurity",
         summary="Research on the size, diversity, and severity of exposed attack surface across U.S. county governments is officially published by the Journal of Cybersecurity.",
         link="https://academic.oup.com/cybersecurity/article/11/1/tyae032/7959399"),
    dict(tag="Recognition", date="Dec 6, 2024",
         title="Attack Surface Research Highlighted by the iSchool",
         summary="Research on measuring the integrated attack surface exposed across U.S. county governments was highlighted by the department; the project has since been accepted for publication in the Journal of Cybersecurity.",
         link="https://ischool.umd.edu/news/breaking-new-ground-a-strategic-approach-to-cyber-defense/"),
    dict(tag="Event Recap", date="Nov 21, 2024",
         title="Tech Policy Hub & VCAI AI Policy Round-Table",
         summary="The Hub and VCAI held a round-table on AI policy at the CS Department, with more AI-related round-tables from the Hub to follow.",
         link="https://ischool.umd.edu/centers-and-labs/vcai/"),
]

# Category -> color for the homepage calendar's legend/dots (see
# calendar_widget_html() / calendar_legend_html()). Kept in Hub brand
# colors (red/gold/ink) plus one added teal accent for a 4th category,
# since the site otherwise only defines red/gold/ink.
EVENT_CATEGORIES = {
    "Speaker Series": "var(--umd-red)",
    "Workshop": "var(--umd-gold)",
    "Roundtable": "var(--accent-teal)",
    "Annual Event": "var(--ink)",
}

EVENTS_ITEMS = [
    dict(y=2026, m="SEP", d="09", cat="Speaker Series", title="Speaker Series: Platform Design & the Law",
         meta="4:00 PM · College Park, MD & Zoom", link="speaker-series.html"),
    dict(y=2026, m="OCT", d="14", cat="Workshop", title="Workshop: Measuring Algorithmic Harm",
         meta="1:00 PM · Iribe Center, Room 3137", link="events.html"),
    dict(y=2026, m="NOV", d="18", cat="Roundtable", title="Roundtable: AI Policy in the States",
         meta="10:00 AM · Virtual", link="events.html"),
    dict(y=2027, m="APR", d="09", cat="Annual Event", title="Tech Policy Hub Annual Event 2027",
         meta="All day · University of Maryland", link="annual-event.html"),
]

# Past events -- same fields as EVENTS_ITEMS so both can share
# events_rows_html()/filter_pills_html(). The three Speaker Series/Roundtable
# entries and the Annual Event recap already existed as illustrative cards
# on speaker-series.html and annual-event.html (see build_all.py); pulled
# out here as one shared source of truth so events.html's new "Past Events"
# section, the Speaker Series page's "Past sessions," and the Annual
# Event page's "2026 Recap" all read from the same data instead of drifting.
# Same caveat as those existing entries: illustrative placeholder content,
# not verified real dates -- see "Known placeholders" in the README.
PAST_EVENTS_ITEMS = [
    dict(y=2026, m="APR", cat="Annual Event", title="A Record Turnout",
         summary="Our most recent event drew practitioners, scholars, and students for a full day of programming -- summary and photos in the news archive.",
         link="annual-event.html"),
    dict(y=2026, m="FEB", cat="Speaker Series", title="DeepSeek and AI Governance",
         summary="An academic and a practitioner unpack what DeepSeek means for global AI policy.",
         link="speaker-series.html"),
    dict(y=2025, m="MAR", cat="Speaker Series", title="Privacy Research to Regulation",
         summary="How academic privacy research can inform real-world privacy regulation.",
         link="speaker-series.html"),
    dict(y=2024, m="NOV", cat="Roundtable", title="AI Policy Roundtable",
         summary="A joint session with VCAI on the state of AI policy debates.",
         link="speaker-series.html"),
]

PEOPLE_ITEMS = [
    dict(initials="IS", name="Dr. Ido Sivan-Sevilla", role="Founder & Director",
         focus="Privacy law, regulatory enforcement, comparative tech policy"),
    dict(initials="CH", name="Dr. Charlie Harry", role="Affiliate, Cybersecurity Lead",
         focus="Cyber risk measurement, critical infrastructure"),
    dict(initials="KS", name="Dr. Katie Shilton", role="Affiliate, Trustworthy ML Lead",
         focus="Data ethics, responsible AI research practice"),
    dict(initials="LT", name="Lee Tiedrich", role="AI Fellow",
         focus="AI governance, emerging technology law"),
    dict(initials="JD", name="Jordan Diaz", role="Graduate Research Fellow",
         focus="Platform transparency, information integrity"),
    dict(initials="AM", name="Amara Mensah", role="Graduate Research Fellow",
         focus="Consumer privacy, algorithmic accountability"),
]

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
QUESTIONS = [
    dict(text="How do we deal with the social problems of computing through top-down and bottom-up policymaking & implementation?",
         tag="Trustworthy ML", link="topic-ml.html"),
    dict(text="What can we learn from the history of policymaking across technology issues?",
         tag="Information Integrity", link="topic-integrity.html"),
    dict(text="What can we learn about tech policy from a comparative perspective? Across sectors? Across jurisdictions?",
         tag="Consumer Privacy", link="topic-privacy.html"),
    dict(text="How and by whom tech policy issues enter the political agenda?",
         tag="Information Integrity", link="topic-integrity.html"),
    dict(text="How does the efficacy of tech policies can be assessed and evaluated?",
         tag="Cybersecurity", link="topic-cybersecurity.html"),
    dict(text="What are the politics of tech policy design?",
         tag="Policy Design", link="research.html"),
    dict(text="How can we use crowdsourcing to improve tech policies?",
         tag="Practice", link="about.html"),
    dict(text="How can we teach tech policy through an experiential learning perspective?",
         tag="Teaching", link="courses.html"),
]

# Ideas We're Reading -- placeholder examples for the Phronesis + Tech
# Policy Press carousel ("Field Pulse" on the homepage). NOT real
# published articles; swap for the Hub's actual picks before launch (see
# README "Known placeholders"). No longer feeds the signal ticker, which
# is now DMV/federal policy tracking only (see TICKER_ITEMS above).
READING_ITEMS = [
    dict(source="Tech Policy Press", topic="Information Integrity",
         title="Why Platform Transparency Reports Still Fall Short",
         summary="A look at what current disclosure requirements do and don't reveal about content moderation at scale.",
         meta="6 min read", link="#"),
    dict(source="The Phronesis Institute", topic="Trustworthy ML",
         title="The State of AI Governance, Three Years In",
         summary="A field scan of regulatory approaches emerging across the U.S., EU, and Asia.",
         meta="8 min read", link="#"),
    dict(source="Tech Policy Press", topic="Consumer Privacy",
         title="Cookies Are Dying. What Comes Next for Ad Tracking?",
         summary="An explainer on the identification methods rushing to fill the gap.",
         meta="5 min read", link="#"),
    dict(source="The Phronesis Institute", topic="Cybersecurity",
         title="County Governments Are the New Cybersecurity Frontline",
         summary="Why local governments face outsized cyber risk with the fewest resources to manage it.",
         meta="7 min read", link="#"),
    dict(source="Tech Policy Press", topic="Trustworthy ML",
         title="How the EU's AI Act Is Reshaping Global Compliance",
         summary="What multinational platforms are actually changing in response to Brussels' risk-tiered rules.",
         meta="9 min read", link="#"),
    dict(source="The Phronesis Institute", topic="Information Integrity",
         title="Congress Weighs a Federal Preemption Standard for AI",
         summary="A rundown of the competing proposals to override the current patchwork of state AI laws.",
         meta="6 min read", link="#"),
]

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
    """Compact numbered list for the homepage lead grid's left column --
    denser than question_list_html() (About's full-width list), since this
    one lives in a narrow ~240px rail column alongside the lead story.
    Not clickable (see follow-up 34) -- each item's per-topic link was
    dropped on request; it's just a hover-responsive text row now (still
    highlights on mouseover via the .guide-q:hover CSS rule, just doesn't
    navigate anywhere)."""
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
    at a time, NOT a free-scroll carousel like Field Pulse) of 3-5 Hub
    outputs: papers, media appearances, presentations, etc. "Research
    Spotlight" is a single persistent header (.rail-head, matching the
    "Guiding Questions"/"Hub News" headers on the other two lead-grid
    columns) -- it does NOT repeat per slide and never changes. Each
    slide's own .meta line (tag + date) sits next to the summary instead,
    since THAT changes per item. Reuses the .lead-media/h1/.lede/
    .hero-actions markup and CSS already defined for the single-item
    version this replaces. main.js finds every [data-spotlight],
    auto-advances through an .is-active class, pauses on hover, and wires
    the .spotlight-dot buttons for manual navigation -- see follow-ups
    26-27. Also wires the prev/next .spotlight-arrow buttons and the
    .spotlight-pause manual pause/play toggle (see follow-up 42) -- a
    manual pause sticks even through hover-unhover and dot/arrow clicks.

    Split into TWO separately-stacked tracks (follow-up 43) rather than one:
    .spotlight-media-track (just the image) and .spotlight-track (title/
    meta/summary/actions), with .spotlight-controls (dots + pause) sitting
    between them in normal flow -- per the user's request, so the dots/
    pause sit right under the image, above the title, where they're visible
    without scrolling past the text. Each still uses the same CSS Grid
    stacking trick (every slide sharing one grid-area, fixed to the
    tallest), just as two independent stacks instead of one combined one --
    main.js's show() toggles the matching pair (same data-slide index) in
    both tracks together."""
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
          <div class="meta">{it['tag']} &middot; {it['date']}</div>
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
      <div class="spotlight" data-spotlight>
        <button type="button" class="spotlight-arrow spotlight-prev" data-spotlight-prev aria-label="Previous spotlight item"></button>
        <button type="button" class="spotlight-arrow spotlight-next" data-spotlight-next aria-label="Next spotlight item"></button>
        <div class="spotlight-media-track">{''.join(media_slides)}
        </div>
        <div class="spotlight-controls">
          <div class="spotlight-dots">{dots}</div>
          <button type="button" class="spotlight-pause" data-spotlight-pause aria-pressed="false" aria-label="Pause slideshow">
            <i class="bar bar-1"></i><i class="bar bar-2"></i><i class="tri"></i>
          </button>
        </div>
        <div class="spotlight-track">{''.join(text_slides)}
        </div>
      </div>"""


def reading_cards_html(items):
    out = []
    for r in items:
        out.append(f"""
        <div class="read-card">
          <span class="source">{r['source']}</span>
          <span class="topic-tag">{r['topic']}</span>
          <h3><a href="{r['link']}">{r['title']}</a></h3>
          <p>{r['summary']}</p>
          <span class="read-meta">{r['meta']}</span>
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
    need 'tag', 'title', and 'link' keys."""
    return "".join(f"""
        <a class="rail-item" href="{e['link']}"{link_attrs(e['link'])}><span class="tag">{e['tag']}</span><h4>{e['title']}</h4></a>""" for e in entries)


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
    out.append('<a class="btn btn-gold" href="about.html">All Topics</a>')
    return "".join(out)


def topic_pills_plain_html():
    """Plain outline pills linking to each topic, for use on light
    backgrounds. No longer used by the Research hub page itself (see
    filter_pills_html() -- research.html's old topic pill-row was pure
    navigation duplicating the Focus Areas cards right below it, so it was
    replaced with an in-page filter instead), but left defined in case a
    future page wants a plain nav-only pill row."""
    return "".join(f'<a class="btn btn-ghost" href="{t["file"]}">{t["name"]}</a>' for t in TOPICS)


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
    that render a subset of events without a filter bar present."""
    out = []
    for e in (items[:limit] if limit else items):
        btn = f'<a class="btn btn-ghost" href="{e["link"]}" style="padding:8px 16px; font-size:.82rem;">Details</a>' if with_btn else ""
        out.append(f"""
        <div class="event-row" data-filter-target="{e['cat']}">
          <div class="event-date"><div class="d">{e['d']}</div><div class="m">{e['m']}</div></div>
          <div><h3><a href="{e['link']}">{e['title']}</a></h3><div class="meta">{e['meta']}</div></div>
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
    `python3 build_all.py` run, not hand-maintained."""
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
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
            f"DTSTAMP:{stamp}",
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


def people_grid_html(items):
    out = []
    for p in items:
        out.append(f"""
        <div class="person">
          <div class="avatar">{p['initials']}</div>
          <h3>{p['name']}</h3>
          <div class="role">{p['role']}</div>
          <p style="font-size:.88rem;">{p['focus']}</p>
        </div>""")
    return "".join(out)


print("Generator module loaded -- run build_all.py to write pages.")
