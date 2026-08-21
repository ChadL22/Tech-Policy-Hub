#!/usr/bin/env python3
import generate as g

g.clean_stale_pages()

# ===========================================================================
# HOME
# ===========================================================================
# The homepage's "what we do" lead grid uses NEWS_ITEMS[0] as the lead
# story, with 1-3 shown (3 items, default) in the "Hub News" rail
# (RECENT_NEWS_RAIL, below) with a "More News" link to news.html; the
# "Recent News" section further down uses NEWS_ITEMS[4:8] -- every item
# appears at most once on the homepage, no story shows up twice the way
# the old hero-rail + Recent News grid did. The remaining items (8-13)
# are real news/press but only appear on news.html, which lists the full
# NEWS_ITEMS set. The lead grid's left column is the Guiding Questions
# list rather than a news rail (see follow-up 9). As of follow-up 10,
# RECENT_NEWS_RAIL is pure Hub news again -- events are no longer folded
# in here now that it's real, dated press coverage; the "Upcoming
# Events" rail in the "Recent News" section below still covers events.
RECENT_NEWS_RAIL = g.NEWS_ITEMS[1:4]
EVENTS_RAIL = [dict(tag=f"{e['m']} {e['d']}", title=e['title'], link=e['link']) for e in g.EVENTS_ITEMS[:4]]

home_body = f"""
<section class="lead-section">
  <div class="container lead-grid">
    <div class="lead-secondary">
      <div class="rail-head">Guiding Questions</div>
      {g.guiding_questions_html(g.QUESTIONS)}
    </div>
    <div class="lead-story">
      {g.spotlight_html(g.SPOTLIGHT_ITEMS)}
    </div>
    <div class="lead-rail">
      <div class="rail-head">Hub News</div>
      {g.rail_html(RECENT_NEWS_RAIL)}
      <a href="news.html" class="text-link rail-more">More News</a>
      <div class="rail-head rail-head--stacked">Research Areas</div>
      <div class="research-matrix research-matrix--rail">{g.research_matrix_html()}</div>
    </div>
  </div>
</section>

<section>
  <div class="container carousel-wrap">
    <div class="carousel-head">
      <div>
        <span class="eyebrow">Field Pulse</span>
        <h2>What we're reading</h2>
      </div>
    </div>
    <p class="label-note carousel-note">An array of papers, essays, analyses, and articles that we have recently come across in the last 30 days or so and care to share. For previous readings visit our sister site <a href="https://phronesisresearch.org">phronesisresearch.org</a>.</p>
    <div class="reading-panel">
      <div class="grid grid-3 reading-grid">
        {g.reading_cards_html(g.READING_ITEMS)}
      </div>
    </div>
  </div>
</section>

<section class="calendar-section">
  <div class="container">
    <div class="section-head">
      <div>
        <span class="eyebrow">Calendar</span>
        <h2>Events</h2>
      </div>
      <a href="events.html" class="btn btn-ghost btn-arrow">Full Calendar</a>
    </div>
    <div class="cal-legend">{g.calendar_legend_html(g.EVENT_CATEGORIES)}</div>
    <div class="with-sidebar rail-wrap cal-wrap">
      {g.calendar_widget_html(g.EVENTS_ITEMS, g.EVENT_CATEGORIES)}
      <div class="rail-panel">
        <div class="rail-head">Upcoming Events</div>
        {g.rail_html(EVENTS_RAIL)}
        <a href="events.html" class="text-link rail-more">See All Events</a>
      </div>
    </div>
  </div>
</section>

<section class="about-hub">
  <div class="container grid grid-2">
    <div>
      <span class="eyebrow">About</span>
      <h2>What is the Tech Policy Hub?</h2>
      <p>The University of Maryland&rsquo;s Tech Policy Hub studies tech policy from a socio-technical perspective, building the bridge between computer science &amp; public policy to understand how policy is designed and implemented for, by, and with tech. Our hub spans across the forefront of tech policy domains, including cybersecurity, consumer privacy, misinformation, and trustworthy machine learning (ML). We bring together DMV-based issue networks of practitioners, scholars, industry leaders, and civil activists to inform, impact, and shape the future of technology in society, applying a mix of comparative, qualitative, and computational research methods to advance our understanding and craft socially desired future paths for tech policy development.</p>
      <a class="text-link about-hub-link" href="about.html">More About the Hub</a>
      <p class="explore-links">Explore: <a href="research.html">Research</a> &middot; <a href="people.html">People</a> &middot; <a href="events.html">Events</a></p>
    </div>
    <div class="pillars">
      <div class="pillar">
        <h4>Computing</h4>
        <p>Attack-surface measurement, algorithmic accountability, and privacy-enhancing technology.</p>
      </div>
      <div class="pillar">
        <h4>Policy</h4>
        <p>Comparative, qualitative, and computational research into how tech policy is designed, adopted, and enforced.</p>
      </div>
      <div class="pillar">
        <h4>Practice</h4>
        <p>A DMV-based issue network of scholars, practitioners, industry leaders, and civil society.</p>
      </div>
    </div>
  </div>
</section>

<section id="subscribe" class="newsletter-band">
  <div class="container inner">
    <span class="eyebrow">Stay in the Loop</span>
    <h2>Subscribe to our newsletter</h2>
    <p>A monthly briefing on developments at the intersection of technology, law, and policy.</p>
    <form class="newsletter-form">
      <input type="email" placeholder="Email Address" required>
      <button type="submit" class="btn btn-primary">Subscribe</button>
    </form>
    <p class="newsletter-partner">Produced in partnership with <a href="https://phronesisresearch.org" target="_blank" rel="noopener">The Phronesis Institute</a></p>
  </div>
</section>
"""
g.write("index.html", g.page("index.html", "Home", "The University of Maryland Tech Policy Hub studies the bridge between computer science and public policy.", home_body, ticker=True))

# ===========================================================================
# RESEARCH HUB + TOPIC DETAIL DATA
# ===========================================================================
TOPIC_DETAIL = {
    "cybersecurity": dict(
        projects=[
            ("Cyber Risk Mapping for U.S. Counties", "Quantifying exposed attack surface and cyber risk across all 50 states and thousands of county governments."),
            ("Critical Infrastructure Resilience", "Working with practitioners to translate attack-surface research into actionable defense priorities."),
        ],
        pubs=[
            ("Journal of Cybersecurity, 2026", "Size, diversity, and severity of exposed attack surface across U.S. county governments."),
            ("Maryland Today, 2026", "UMD researchers calculate cyberattack risk for all 50 states."),
        ],
        people=["Dr. Charlie Harry", "Jordan Diaz"],
    ),
    "privacy": dict(
        projects=[
            ("Cookie-less Identification Tracking", "Studying how identification methods are evolving as third-party cookies are phased out, and what it means for privacy."),
            ("Watchdog Accountability", "Assessing the powers of formal and informal U.S. privacy regulators."),
        ],
        pubs=[
            ("Internet Policy Review, 2026", "Cookie-less identification: for and against privacy."),
            ("Privacy Law Scholars Conference, 2026", "Accountability powers of formal and informal U.S. privacy watchdogs."),
        ],
        people=["Dr. Ido Sivan-Sevilla", "Amara Mensah"],
    ),
    "integrity": dict(
        projects=[
            ("Trustworthy Content Classification", "Classifying trustworthy content on the web using third-party site structure."),
            ("Platform Transparency Tracker", "Monitoring platform disclosures and their real-world enforcement."),
        ],
        pubs=[
            ("FOCI Workshop @ PETs, 2026", "Classifying trustworthy content on the web based on third-party structure."),
            ("Policy Brief, 2026", "What platform transparency reports do and don't tell us."),
        ],
        people=["Jordan Diaz", "Dr. Ido Sivan-Sevilla"],
    ),
    "ml": dict(
        projects=[
            ("Algorithmic Accountability Framework", "Developing standards for evaluating machine learning systems used in public decision-making."),
            ("AI Governance Roundtables", "Convening researchers and policymakers on the governance of emerging AI systems."),
        ],
        pubs=[
            ("arXiv, 2026", "Applying Contextual Integrity to measure algorithmic decision-making."),
            ("Roundtable Summary, 2025", "Tech Policy Hub & VCAI roundtable on AI policy."),
        ],
        people=["Dr. Katie Shilton", "Lee Tiedrich"],
    ),
}

project_cards = []
for t in g.TOPICS:
    d = TOPIC_DETAIL[t["key"]]
    for name, desc in d["projects"]:
        project_cards.append(f'<div class="card" data-filter-target="{t["name"]}"><span class="kicker">{t["name"]}</span><h3>{name}</h3><p>{desc}</p></div>')

pub_feed = []
for t in g.TOPICS:
    d = TOPIC_DETAIL[t["key"]]
    for venue, desc in d["pubs"]:
        pub_feed.append(f"""
        <div class="feed-item" data-filter-target="{t['name']}">
          <span class="tag">{t['name']}</span>
          <div><div class="meta" style="margin-bottom:6px;">{venue}</div><h3><a href="{t['file']}">{desc}</a></h3></div>
        </div>""")

research_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Research</div>
    <span class="eyebrow">Research</span>
    <h1>Research</h1>
    <p class="lede">Cybersecurity, consumer privacy, information integrity, and trustworthy machine learning &mdash; studied through comparative, qualitative, and computational methods.</p>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Focus Areas</span><h2>Where we work</h2></div></div>
    <div class="grid grid-4">{g.topic_cards_html()}</div>
  </div>
</section>
<section class="soft-bg">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Featured</span><h2>Current projects</h2></div></div>
    <p style="color:var(--ink-soft); font-size:.92rem; margin-bottom:16px;">Filter projects and publications below by focus area.</p>
    {g.filter_pills_html([t['name'] for t in g.TOPICS], 'research')}
    <div class="grid grid-2" style="margin-top:28px;">{"".join(project_cards)}</div>
  </div>
</section>
<section id="publications">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Publications</span><h2>Recent publications</h2></div></div>
    {"".join(pub_feed)}
  </div>
</section>
<section class="soft-bg">
  <div class="container grid grid-2" style="align-items:center;">
    <div>
      <span class="eyebrow">Teaching</span>
      <h2>Bring tech policy into the classroom</h2>
      <p>Cross-listed courses pair computer science and public policy students to study technology governance.</p>
    </div>
    <div class="teaching-cta"><a href="courses.html" class="btn btn-primary btn-arrow">Explore Courses</a></div>
  </div>
</section>
"""
g.write("research.html", g.page("research.html", "Research", "Cybersecurity, consumer privacy, information integrity, and trustworthy ML research from the Tech Policy Hub.", research_body))

# ===========================================================================
# TOPIC PAGES
# ===========================================================================
for t in g.TOPICS:
    d = TOPIC_DETAIL[t["key"]]
    projects_html = "".join(f'<div class="card"><span class="kicker">Project</span><h3>{n}</h3><p>{desc}</p></div>' for n, desc in d["projects"])
    pubs_html = "".join(f'<div class="card"><span class="kicker">Publication</span><h3>{n}</h3><p>{desc}</p></div>' for n, desc in d["pubs"])
    people_html = "".join(f'<div class="card"><span class="kicker">Person</span><h3>{n}</h3></div>' for n in d["people"])
    body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / <a href="research.html">Research</a> / {t['name']}</div>
    <span class="eyebrow">Research Area</span>
    <h1>{t['name']}</h1>
    <p class="lede">{t['blurb']}</p>
  </div>
</section>
<section>
  <div class="container">
    <div class="tabs">
      <button class="tab-btn active" data-tab="projects">Projects</button>
      <button class="tab-btn" data-tab="pubs">Publications</button>
      <button class="tab-btn" data-tab="people">People</button>
    </div>
    <div>
      <div class="tab-panel active" data-tab="projects"><div class="grid grid-2">{projects_html}</div></div>
      <div class="tab-panel" data-tab="pubs"><div class="grid grid-2">{pubs_html}</div></div>
      <div class="tab-panel" data-tab="people"><div class="grid grid-2">{people_html}</div></div>
    </div>
  </div>
</section>
"""
    g.write(t["file"], g.page(t["file"], t["name"], t["blurb"], body))

# ===========================================================================
# TEACHING (formerly "Courses"), SPEAKER SERIES, ANNUAL EVENT
# ===========================================================================
courses_body = """
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / <a href="research.html">Research</a> / Teaching</div>
    <span class="eyebrow">Research &middot; Teaching</span>
    <h1>Teaching</h1>
    <p class="lede">Cross-listed courses that bring together computer science and public policy students to study technology governance.</p>
  </div>
</section>
<section>
  <div class="container">
    <div class="grid grid-3">
      <div class="card"><span class="kicker">INST / PLCY</span><h3>Tech Policy Design</h3><p>A studio-format course where students prototype policy responses to real technology governance problems.</p></div>
      <div class="card"><span class="kicker">CMSC / PLCY</span><h3>Cybersecurity Law &amp; Policy</h3><p>Examines the legal and regulatory frameworks that shape cybersecurity practice across sectors.</p></div>
      <div class="card"><span class="kicker">INST</span><h3>Privacy by Design</h3><p>Covers privacy-enhancing technologies and the regulatory environment that shapes their adoption.</p></div>
      <div class="card"><span class="kicker">PLCY</span><h3>AI Governance Seminar</h3><p>A graduate seminar surveying global approaches to regulating artificial intelligence.</p></div>
      <div class="card"><span class="kicker">INST</span><h3>Information Integrity &amp; the Web</h3><p>Explores misinformation, platform design, and content moderation policy.</p></div>
      <div class="card"><span class="kicker">Experiential</span><h3>Tech Policy Practicum</h3><p>Students work directly with practitioner partners on live technology policy challenges.</p></div>
    </div>
  </div>
</section>
"""
g.write("courses.html", g.page("courses.html", "Teaching", "Cross-listed technology policy courses at the University of Maryland.", courses_body))

speaker_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / <a href="events.html">Events</a> / Speaker Series</div>
    <span class="eyebrow">Events</span>
    <h1>Speaker Series</h1>
    <p class="lede">A recurring conversation series pairing academics and practitioners to discuss the tech policy questions of the moment.</p>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head">
      <div><span class="eyebrow">Upcoming</span><h2>Next sessions</h2></div>
    </div>
    {g.events_rows_html([e for e in g.EVENTS_ITEMS if "Speaker" in e['title'] or True], limit=2)}
  </div>
</section>
<section class="soft-bg">
  <div class="container">
    <div class="section-head">
      <div><span class="eyebrow">Past sessions</span><h2>Recordings &amp; recaps</h2></div>
    </div>
    <div class="grid grid-3">{"".join(f'<div class="card"><span class="kicker">{e["m"].title()} {e["y"]}</span><h3>{e["title"]}</h3><p>{e["summary"]}</p></div>' for e in g.PAST_EVENTS_ITEMS if e["cat"] in ("Speaker Series", "Roundtable"))}</div>
  </div>
</section>
"""
g.write("speaker-series.html", g.page("speaker-series.html", "Speaker Series", "The Tech Policy Hub Speaker Series pairs academics and practitioners.", speaker_body))

_annual_recap = next(e for e in g.PAST_EVENTS_ITEMS if e["cat"] == "Annual Event")
annual_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / <a href="events.html">Events</a> / Annual Event</div>
    <span class="eyebrow">Events &middot; Flagship Program</span>
    <h1>Annual Event</h1>
    <p class="lede">Our flagship gathering brings together students, scholars, practitioners, and civil society for a full day of tech policy programming.</p>
    <div class="hero-actions"><a href="#" class="btn btn-primary">Register Interest</a></div>
  </div>
</section>
<section>
  <div class="container">
    <div class="grid grid-2">
      <div class="card"><span class="kicker">2027</span><h3>Save the Date</h3><p>Planning is underway for our next Annual Event -- details and registration will be posted here.</p></div>
      <div class="card"><span class="kicker">{_annual_recap['y']} Recap</span><h3>{_annual_recap['title']}</h3><p>{_annual_recap['summary']}</p></div>
    </div>
  </div>
</section>
"""
g.write("annual-event.html", g.page("annual-event.html", "Annual Event", "The Tech Policy Hub's flagship annual gathering.", annual_body))

# ===========================================================================
# NEWS
# ===========================================================================
news_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / News</div>
    <span class="eyebrow">Latest</span>
    <h1>News</h1>
    <p class="lede">Publications, media coverage, awards, and updates from across the Hub.</p>
  </div>
</section>
<section>
  <div class="container">
    {g.feed_items_html(g.NEWS_ITEMS)}
  </div>
</section>
"""
g.write("news.html", g.page("news.html", "News", "News, publications, and media coverage from the Tech Policy Hub.", news_body))

# ===========================================================================
# EVENTS
# ===========================================================================
# Absolute (not page-relative) so this works identically regardless of the
# fact that events.html itself lives one folder deep (docs/events/index.html)
# while events.ics lives at the site root (docs/events.ics) -- see
# events_ics()'s docstring for why the feed itself is all-day/no-timezone.
_ics_url = g.SITE_URL + "events.ics"
_ics_webcal_url = _ics_url.replace("https://", "webcal://")

events_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Events</div>
    <span class="eyebrow">Upcoming</span>
    <h1>Events</h1>
    <p class="lede">Speaker Series sessions, workshops, roundtables, and our flagship Annual Event.</p>
  </div>
</section>
<section>
  <div class="container with-sidebar">
    <div>
      {g.filter_pills_html(list(g.EVENT_CATEGORIES.keys()), 'events')}
      <div class="section-head" style="margin-top:28px;"><div><span class="eyebrow">Upcoming</span><h2>Upcoming Events</h2></div></div>
      {g.events_rows_html(g.EVENTS_ITEMS)}
      <div class="section-head" style="margin-top:48px;"><div><span class="eyebrow">Past</span><h2>Past Events</h2></div></div>
      {g.past_events_html(g.PAST_EVENTS_ITEMS)}
    </div>
    <div>
      <h4 style="font-family:var(--font-body); font-size:.95rem; font-weight:700; margin-bottom:14px;">Calendar</h4>
      <div class="cal-legend">{g.calendar_legend_html(g.EVENT_CATEGORIES)}</div>
      {g.calendar_widget_html(g.EVENTS_ITEMS, g.EVENT_CATEGORIES)}
      <a href="{_ics_webcal_url}" class="btn btn-primary" style="width:100%; justify-content:center; margin-top:18px;">Subscribe to Calendar</a>
      <a href="{_ics_url}" class="btn btn-ghost" style="width:100%; justify-content:center; margin-top:10px; font-size:.82rem;">Download .ics file</a>
    </div>
  </div>
</section>
"""
g.write("events.html", g.page("events.html", "Events", "Upcoming events from the Tech Policy Hub.", events_body))
g.write_raw("events.ics", g.events_ics(g.EVENTS_ITEMS))

# ===========================================================================
# PEOPLE
# ===========================================================================
people_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / People</div>
    <span class="eyebrow">Our Team</span>
    <h1>People</h1>
    <p class="lede">Faculty, affiliates, and graduate fellows driving the Hub's research agenda.</p>
  </div>
</section>
<section>
  <div class="container">
    <div class="grid grid-3">
      {g.people_grid_html(g.PEOPLE_ITEMS)}
    </div>
  </div>
</section>
"""
g.write("people.html", g.page("people.html", "People", "Faculty, affiliates, and fellows of the Tech Policy Hub.", people_body))

# ===========================================================================
# ABOUT
# ===========================================================================
about_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / About</div>
    <span class="eyebrow">About</span>
    <h1>About the Hub</h1>
    <p class="lede">Who we are, what we study, and how to get involved with the Hub.</p>
  </div>
</section>
<section>
  <div class="container with-sidebar">
    <div>
      <h2>Our mission</h2>
      <p>The University of Maryland&rsquo;s Tech Policy Hub studies tech policy from a socio-technical perspective, building the bridge between computer science &amp; public policy to understand how policy is designed and implemented for, by, and with tech. Our hub spans across the forefront of tech policy domains, including cybersecurity, consumer privacy, misinformation, and trustworthy machine learning (ML). We bring together DMV-based issue networks of practitioners, scholars, industry leaders, and civil activists to inform, impact, and shape the future of technology in society, applying a mix of comparative, qualitative, and computational research methods to advance our understanding and craft socially desired future paths for tech policy development.</p>
      <h2 style="margin-top:36px;">Our approach</h2>
      <div class="pillars pillars-light">
        <div class="pillar"><h4>Computing</h4><p>Attack-surface measurement, algorithmic accountability, and privacy-enhancing technology.</p></div>
        <div class="pillar"><h4>Policy</h4><p>Comparative, qualitative, and computational research into how tech policy is designed, adopted, and enforced.</p></div>
        <div class="pillar"><h4>Practice</h4><p>A DMV-based issue network of scholars, practitioners, industry leaders, and civil society.</p></div>
      </div>
    </div>
    <div>
      <div class="sidebar-box">
        <h4>Join the Hub</h4>
        <p style="font-size:.9rem;">If all this sounds relevant and interesting for you &ndash; feel free to join our hub! We are bringing together a network of students, scholars, practitioners, civil activists, and industry leaders to discuss tech policy on a regular basis. Feel free to subscribe and join our mailing list and be up-to-date with our research outputs &amp; events. Interested in becoming affiliated with us? Please email our founder, Dr. Sivan-Sevilla, to discuss further.</p>
        <a href="mailto:sevilla@umd.edu" class="btn btn-primary" style="width:100%; justify-content:center; margin-bottom:10px;">Email Dr. Sivan-Sevilla</a>
        <a href="index.html#subscribe" class="btn btn-ghost" style="width:100%; justify-content:center;">Subscribe</a>
      </div>
    </div>
  </div>
</section>
<section id="questions" class="soft-bg">
  <div class="container">
    <div class="section-head">
      <div>
        <span class="eyebrow">Questions We Answer</span>
        <h2>The questions driving our research</h2>
      </div>
    </div>
    <div class="question-list">
      {g.question_list_html(g.QUESTIONS)}
    </div>
  </div>
</section>
"""
g.write("about.html", g.page("about.html", "About", "About the University of Maryland Tech Policy Hub.", about_body))

print("\\nDone. Pages written to:", g.ROOT)
