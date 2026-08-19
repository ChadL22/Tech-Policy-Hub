#!/usr/bin/env python3
"""
Static site generator for the Tech Policy Hub redesign.
Assembles flat HTML pages (shared header/footer) into ../docs/
(named "docs" so GitHub Pages can serve it directly from main /docs).
No build step needed to VIEW the site -- just open the .html files.
Re-run this script any time page content or the header/footer changes.
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "docs")

# Bumped by hand whenever styles.css / main.js change, and appended as a
# query string to their <link>/<script> tags below. Without this, browsers
# (and GitHub Pages' CDN) can keep serving a stale cached copy of the CSS/JS
# against a freshly-deployed HTML file -- which is what produced the
# broken/unstyled ticker a user saw right after a previous deploy.
ASSET_VERSION = "2026081904"

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

# NAV -- shallow, per the redesign brief: Research / People / Events /
# News / About, with Publications and Teaching folded into Research
# rather than kept as their own top-level items. Each entry is
# (label, href, children); children is None for a plain link, or a list
# of (label, href) for a dropdown. The parent href is a real page (not
# "#"), so clicking "Research" or "Events" itself navigates to that
# section's index -- the dropdown is an additional hover/tap affordance,
# not the only way in.
NAV = [
    ("Research", "research.html", [
        ("All Research", "research.html"),
        ("Cybersecurity", "topic-cybersecurity.html"),
        ("Consumer Privacy", "topic-privacy.html"),
        ("Information Integrity", "topic-integrity.html"),
        ("Trustworthy ML", "topic-ml.html"),
        ("Publications", "research.html#publications"),
        ("Teaching", "courses.html"),
    ]),
    ("People", "people.html", None),
    ("Events", "events.html", [
        ("All Events", "events.html"),
        ("Speaker Series", "speaker-series.html"),
        ("Annual Event", "annual-event.html"),
    ]),
    ("News", "news.html", None),
    ("About", "about.html", None),
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
      <a href="https://gotech.umd.edu/" target="_blank" rel="noopener" class="umd-logo-link" aria-label="Center for Governance of Technology and Systems (GoTech), University of Maryland">
        <img src="assets/img/gtech-main.svg" alt="Center for Governance of Technology and Systems (GoTech), University of Maryland" class="umd-logo">
      </a>
      <span class="brand-divider" aria-hidden="true"></span>
      <a href="index.html" class="brand">
        <img src="assets/img/tph-icon.png" alt="" class="tph-icon">
        <span class="brand-hub-lockup">
          <span class="word-tech">Tech</span>
          <span class="word-policy">Policy</span>
          <span class="hub-word">Hub</span>
        </span>
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
    """Thin band under the header naming the Hub's institutional home --
    subordinate to the Hub logo/name, per the brief's note that
    partner-school affiliation should establish provenance without
    competing with the Hub identity."""
    return """
<div class="affiliation-strip">
  <div class="container">
    <span>University of Maryland</span><span class="dot" aria-hidden="true">&middot;</span>
    <span>School of Public Policy</span><span class="dot" aria-hidden="true">&middot;</span>
    <span>Center for Governance of Technology and Systems (GoTech)</span>
  </div>
</div>
"""


def ticker_section():
    """Bloomberg/CNBC-style signal rail, homepage only. Tabs switch between
    channels (the Hub's own signals vs. curated Phronesis / Tech Policy
    Press picks) the way CNBC's US/ASIA/EUR/BONDS row swaps which index
    strip is showing. Content is editorial (TICKER_CHANNELS below), not a
    live feed -- per the brief's own guidance to use editorial signals
    rather than faux-live metrics unless the data can be reliably kept
    current."""
    return f"""
<div class="signal-ticker" aria-label="Latest signals from the Hub">
  <div class="ticker-tabs" role="tablist">
    <span class="ticker-live"><span class="dot" aria-hidden="true"></span>Live</span>
    {ticker_tabs_html(TICKER_CHANNELS)}
  </div>
  <div class="ticker-viewport">
    {ticker_tracks_html(TICKER_CHANNELS)}
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
    out = head(title, description) + header(active) + affiliation_strip()
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

NEWS_ITEMS = [
    dict(tag="Publication", date="Jul 22, 2026",
         title="Cookie-less Identification: For and Against Privacy",
         summary="New work from the privacy team examines the tradeoffs of emerging identification methods as third-party cookies phase out.",
         link="news.html"),
    dict(tag="Award", date="Jun 24, 2026",
         title="Lee Tiedrich Joins the Hub as AI Fellow",
         summary="Tiedrich joins as a co-leader and AI Fellow under the Hub's affiliates, expanding our work on AI governance.",
         link="news.html"),
    dict(tag="Event Recap", date="Jun 10, 2026",
         title="2026 Annual Event Draws Record Turnout",
         summary="Practitioners, scholars, and students gathered for a full day of tech policy programming -- recap and photos now live.",
         link="annual-event.html"),
    dict(tag="Media", date="Mar 2, 2026",
         title="Hub Cybersecurity Research Featured in Newsweek",
         summary="The county-level cyber risk mapping project was highlighted for its national policy relevance.",
         link="news.html"),
    dict(tag="Publication", date="Mar 2, 2026",
         title="Contextual Integrity for Measuring Web Privacy",
         summary="New research applies the Contextual Integrity framework to evaluate privacy on the modern web, now on arXiv.",
         link="news.html"),
    dict(tag="Speaker Series", date="Feb 26, 2026",
         title="DeepSeek and the Future of AI Governance",
         summary="An academic and a practitioner joined the Spring Speaker Series to unpack what DeepSeek means for global AI policy.",
         link="speaker-series.html"),
]

EVENTS_ITEMS = [
    dict(m="SEP", d="09", title="Speaker Series: Platform Design & the Law",
         meta="4:00 PM · College Park, MD & Zoom", link="speaker-series.html"),
    dict(m="OCT", d="14", title="Workshop: Measuring Algorithmic Harm",
         meta="1:00 PM · Iribe Center, Room 3137", link="events.html"),
    dict(m="NOV", d="18", title="Roundtable: AI Policy in the States",
         meta="10:00 AM · Virtual", link="events.html"),
    dict(m="APR", d="09", title="Tech Policy Hub Annual Event 2027",
         meta="All day · University of Maryland", link="annual-event.html"),
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

# Homepage signal ticker -- editorial, manually maintained (see
# ticker_section() docstring). Two entries are computed from NEWS_ITEMS /
# EVENTS_ITEMS so they can't silently drift out of sync with the actual
# latest publication/event; the rest are hand-picked highlights.
TICKER_ITEMS = [
    dict(label="Research", datum="4 active focus areas &mdash; cybersecurity, privacy, integrity, ML", link="research.html"),
    dict(label="Publications", datum=f"Latest: &ldquo;{NEWS_ITEMS[0]['title']}&rdquo; &mdash; {NEWS_ITEMS[0]['date']}", link="news.html"),
    dict(label="Events", datum=f"Next up: {EVENTS_ITEMS[0]['m']} {EVENTS_ITEMS[0]['d']} &mdash; {EVENTS_ITEMS[0]['title']}", link="events.html"),
    dict(label="People", datum="Lee Tiedrich joins the Hub as AI Fellow", link="people.html"),
    dict(label="Policy Watch", datum="Tracking AI governance in the states", link="about.html#questions"),
]

# Questions We Answer -- same six questions as the Hub's mission ("Questions
# we ask"), each tagged to the research area it connects to so they double
# as intellectual navigation, not just mission-statement copy. Homepage
# shows a curated subset (see build_all.py); About shows all six.
QUESTIONS = [
    dict(text="How do we address the social problems of computing through top-down and bottom-up policymaking?",
         tag="Trustworthy ML", link="topic-ml.html"),
    dict(text="What can we learn from the history of policymaking across technology issues?",
         tag="Information Integrity", link="topic-integrity.html"),
    dict(text="What does tech policy look like from a comparative perspective -- across sectors and jurisdictions?",
         tag="Consumer Privacy", link="topic-privacy.html"),
    dict(text="How and by whom do tech policy issues enter the political agenda?",
         tag="Information Integrity", link="topic-integrity.html"),
    dict(text="How can the efficacy of tech policy be assessed and evaluated?",
         tag="Cybersecurity", link="topic-cybersecurity.html"),
    dict(text="How can we teach tech policy through an experiential learning perspective?",
         tag="Teaching", link="courses.html"),
]

# Ideas We're Reading -- placeholder examples for the Phronesis + Tech
# Policy Press carousel (and, in condensed form, the ticker's Phronesis /
# Tech Policy Press tabs below). NOT real published articles; swap for
# the Hub's actual picks before launch (see README "Known placeholders").
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

# Ticker channels -- "Tech Policy Hub" is the Hub's own editorial signals
# (TICKER_ITEMS above); "Phronesis" and "Tech Policy Press" are condensed
# from the same READING_ITEMS that power the homepage carousel, so the two
# stay in sync automatically. Each entry is (key, tab label, items).
TICKER_CHANNELS = [
    ("hub", "Tech Policy Hub", TICKER_ITEMS),
    ("phronesis", "Phronesis", [
        dict(label=r["topic"], datum=r["title"], link=r["link"])
        for r in READING_ITEMS if r["source"] == "The Phronesis Institute"
    ]),
    ("press", "Tech Policy Press", [
        dict(label=r["topic"], datum=r["title"], link=r["link"])
        for r in READING_ITEMS if r["source"] == "Tech Policy Press"
    ]),
]


def ticker_html(items):
    return "".join(f"""
        <a class="signal-card" href="{it['link']}"><span class="label">{it['label']}</span><span class="datum">{it['datum']}</span></a>""" for it in items)


def ticker_tabs_html(channels):
    out = []
    for i, (key, label, _items) in enumerate(channels):
        active = " active" if i == 0 else ""
        out.append(f'<button type="button" class="ticker-tab{active}" data-channel="{key}" role="tab" aria-selected="{"true" if i == 0 else "false"}">{label}</button>')
    return "".join(out)


def ticker_tracks_html(channels):
    out = []
    for i, (key, _label, items) in enumerate(channels):
        active = " active" if i == 0 else ""
        cards = ticker_html(items)
        out.append(f'<div class="ticker-track{active}" data-channel="{key}"><div class="ticker-track-inner">{cards}{cards}</div></div>')
    return "".join(out)


def question_cards_html(items):
    out = []
    for q in items:
        out.append(f"""
        <a class="question-card" href="{q['link']}">
          <h3>{q['text']}</h3>
          <span class="qtag">{q['tag']}</span>
        </a>""")
    return "".join(out)


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


def rail_html(entries):
    """Compact CNBC/Bloomberg-style headline rail: a tag/date plus a linked
    title, hairline-divided, no imagery. Used for the side rails next to
    the homepage hero and the Recent News section, so those sections don't
    have to be one massive full-width block to feel substantial -- entries
    need 'tag', 'title', and 'link' keys."""
    return "".join(f"""
        <a class="rail-item" href="{e['link']}"><span class="tag">{e['tag']}</span><h4>{e['title']}</h4></a>""" for e in entries)


def feed_items_html(items, limit=None):
    out = []
    for it in (items[:limit] if limit else items):
        out.append(f"""
        <div class="feed-item">
          <span class="tag">{it['tag']}</span>
          <div>
            <div class="meta" style="margin-bottom:6px;">{it['date']}</div>
            <h3><a href="{it['link']}">{it['title']}</a></h3>
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
    backgrounds (e.g. the Research hub page) where the gold-on-black
    treatment of topic_pills_html() wouldn't have contrast."""
    return "".join(f'<a class="btn btn-ghost" href="{t["file"]}">{t["name"]}</a>' for t in TOPICS)


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
          <h3><a href="{it['link']}">{it['title']}</a></h3>
          <p>{it['summary']}</p>
        </div>""")
    return "".join(out)


def events_rows_html(items, limit=None, with_btn=True):
    out = []
    for e in (items[:limit] if limit else items):
        btn = f'<a class="btn btn-ghost" href="{e["link"]}" style="padding:8px 16px; font-size:.82rem;">Details</a>' if with_btn else ""
        out.append(f"""
        <div class="event-row">
          <div class="event-date"><div class="d">{e['d']}</div><div class="m">{e['m']}</div></div>
          <div><h3><a href="{e['link']}">{e['title']}</a></h3><div class="meta">{e['meta']}</div></div>
          {btn}
        </div>""")
    return "".join(out)


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
