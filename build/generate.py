#!/usr/bin/env python3
"""
Static site generator for the Tech Policy Hub redesign.
Assembles flat HTML pages (shared header/footer) into ../docs/
(named "docs" so GitHub Pages can serve it directly from main /docs).
No build step needed to VIEW the site -- just open the .html files.
Re-run this script any time page content or the header/footer changes.
"""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "docs")

NAV = [
    ("Topics", None, [
        ("Cybersecurity", "topic-cybersecurity.html"),
        ("Consumer Privacy", "topic-privacy.html"),
        ("Information Integrity", "topic-integrity.html"),
        ("Trustworthy ML", "topic-ml.html"),
    ]),
    ("Programs", None, [
        ("Courses", "courses.html"),
        ("Speaker Series", "speaker-series.html"),
        ("Annual Event", "annual-event.html"),
    ]),
    ("News", "news.html", None),
    ("Events", "events.html", None),
    ("People", "people.html", None),
    ("About", "about.html", None),
]


def nav_html(active):
    items = []
    for label, href, children in NAV:
        is_current = href == active
        if children:
            child_current = any(c[1] == active for c in children)
            li_class = "has-dropdown" + (" current" if child_current else "")
            sub = "".join(f'<li><a href="{h}">{l}</a></li>' for l, h in children)
            items.append(
                f'<li class="{li_class}"><a href="#" class="nav-link">{label}</a>'
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
<link rel="stylesheet" href="assets/css/styles.css">
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
        <span class="brand-chip">Tech Policy Hub</span>
      </a>
    </div>
    <nav class="primary-nav">
      <ul>{nav_html(active)}</ul>
    </nav>
    <button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
"""


def footer():
    return """
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
        <h4>Topics</h4>
        <ul>
          <li><a href="topic-cybersecurity.html">Cybersecurity</a></li>
          <li><a href="topic-privacy.html">Consumer Privacy</a></li>
          <li><a href="topic-integrity.html">Information Integrity</a></li>
          <li><a href="topic-ml.html">Trustworthy ML</a></li>
        </ul>
      </div>
      <div>
        <h4>Programs</h4>
        <ul>
          <li><a href="courses.html">Courses</a></li>
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
      <div class="footer-bottom-copyright">&copy; 2026 Tech Policy Research and Education Hub</div>
    </div>
  </div>
</footer>
<script src="assets/js/main.js"></script>
</body>
</html>
"""


def page(active, title, description, body):
    return head(title, description) + header(active) + body + footer()


def write(name, content):
    os.makedirs(ROOT, exist_ok=True)
    with open(os.path.join(ROOT, name), "w") as f:
        f.write(content)
    print("wrote", name)


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
    """White outline pill buttons linking to each topic, used in the
    black statement band -- mirrors the Issues pill-nav on kgi.georgetown.edu."""
    out = [f'<a class="btn btn-white" href="{t["file"]}">{t["name"]}</a>' for t in TOPICS]
    out.append('<a class="btn btn-white" href="about.html">All Topics</a>')
    return "".join(out)


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
