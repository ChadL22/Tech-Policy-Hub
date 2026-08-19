#!/usr/bin/env python3
import generate as g

g.clean_stale_pages()

# ===========================================================================
# HOME
# ===========================================================================
# Curated subset of QUESTIONS for the homepage (4, per the brief); About
# shows the full set of six.
QUESTIONS_HOME = [g.QUESTIONS[0], g.QUESTIONS[2], g.QUESTIONS[3], g.QUESTIONS[4]]

# The homepage's "what we do" lead grid uses NEWS_ITEMS[0:4] (lead story +
# 2 secondary + 1 in the Hub Updates rail); Recent News further down uses
# NEWS_ITEMS[4:6] -- every item appears exactly once on the homepage, no
# story shows up twice the way the old hero-rail + Recent News grid did.
LEAD_SECONDARY = g.NEWS_ITEMS[1:3]
HUB_UPDATES_RAIL = g.NEWS_ITEMS[3:4] + [
    dict(tag=f"{e['m']} {e['d']}", title=e['title'], link=e['link']) for e in g.EVENTS_ITEMS[:2]
]
EVENTS_RAIL = [dict(tag=f"{e['m']} {e['d']}", title=e['title'], link=e['link']) for e in g.EVENTS_ITEMS[:4]]

home_body = f"""
<section class="lead-section">
  <div class="container lead-grid">
    <div class="lead-secondary">
      <div class="rail-head">More From the Hub</div>
      {g.rail_html(LEAD_SECONDARY)}
    </div>
    <div class="lead-story">
      <div class="meta">Featured Publication &middot; {g.NEWS_ITEMS[0]['date']}</div>
      <h1><a href="{g.NEWS_ITEMS[0]['link']}">{g.NEWS_ITEMS[0]['title']}</a></h1>
      <p class="lede">{g.NEWS_ITEMS[0]['summary']}</p>
      <div class="hero-actions">
        <a href="{g.NEWS_ITEMS[0]['link']}" class="btn btn-primary btn-arrow">Read the Research</a>
        <a href="topic-privacy.html" class="btn btn-ghost">Explore Consumer Privacy</a>
      </div>
    </div>
    <div class="lead-rail">
      <div class="rail-head">Hub Updates</div>
      {g.rail_html(HUB_UPDATES_RAIL)}
    </div>
  </div>
</section>

<section class="section-tight">
  <div class="container">
    <div class="pill-row">{g.topic_pills_plain_html()}</div>
  </div>
</section>

<section id="questions">
  <div class="container">
    <div class="section-head">
      <div>
        <span class="eyebrow">Questions We Answer</span>
        <h2>The questions driving our research</h2>
      </div>
      <a href="about.html#questions" class="text-link">Explore All Questions</a>
    </div>
    <div class="questions-grid questions-grid--compact">
      {g.question_cards_html(QUESTIONS_HOME)}
    </div>
  </div>
</section>

<section class="soft-bg news-grid-section">
  <div class="container">
    <div class="section-head">
      <div>
        <span class="eyebrow">Latest</span>
        <h2>Recent News</h2>
      </div>
      <a href="news.html" class="text-link">See All News</a>
    </div>
    <div class="with-sidebar rail-wrap">
      <div>{g.feed_items_html(g.NEWS_ITEMS[4:6])}</div>
      <div class="rail-panel">
        <div class="rail-head">Upcoming Events</div>
        {g.rail_html(EVENTS_RAIL)}
        <a href="events.html" class="text-link rail-more">See All Events</a>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container carousel-wrap">
    <div class="carousel-head">
      <div>
        <span class="eyebrow">Field Pulse</span>
        <h2>What we're reading</h2>
        <p class="label-note">Outside reading from Phronesis and Tech Policy Press &mdash; not Hub-authored scholarship.</p>
      </div>
      <div class="carousel-arrows">
        <button type="button" data-dir="-1" aria-label="Scroll left">&lsaquo;</button>
        <button type="button" data-dir="1" aria-label="Scroll right">&rsaquo;</button>
      </div>
    </div>
    <div class="carousel-track">
      {g.reading_cards_html(g.READING_ITEMS[:4])}
    </div>
  </div>
</section>

<section class="about-hub">
  <div class="container grid grid-2">
    <div>
      <span class="eyebrow">About</span>
      <h2>What is the Tech Policy Hub?</h2>
      <p>The University of Maryland&rsquo;s Tech Policy Hub studies tech policy from a socio-technical perspective &mdash; building the bridge between computer science and public policy. We bring together a DMV-based network of practitioners, scholars, industry leaders, and civil activists to inform, impact, and shape the future of technology in society.</p>
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
    <h2>Subscribe to our emails</h2>
    <p>Research, event invitations, and news from the Hub &mdash; a few times a month, never more.</p>
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
        project_cards.append(f'<div class="card"><span class="kicker">{t["name"]}</span><h3>{name}</h3><p>{desc}</p></div>')

pub_feed = []
for t in g.TOPICS:
    d = TOPIC_DETAIL[t["key"]]
    for venue, desc in d["pubs"]:
        pub_feed.append(f"""
        <div class="feed-item">
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
<section class="section-tight">
  <div class="container">
    <div class="pill-row">{g.topic_pills_plain_html()}</div>
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
    <div class="grid grid-2">{"".join(project_cards)}</div>
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
    <div class="grid grid-3">
      <div class="card"><span class="kicker">Feb 2026</span><h3>DeepSeek and AI Governance</h3><p>An academic and a practitioner unpack what DeepSeek means for global AI policy.</p></div>
      <div class="card"><span class="kicker">Mar 2025</span><h3>Privacy Research to Regulation</h3><p>How academic privacy research can inform real-world privacy regulation.</p></div>
      <div class="card"><span class="kicker">Nov 2024</span><h3>AI Policy Roundtable</h3><p>A joint session with VCAI on the state of AI policy debates.</p></div>
    </div>
  </div>
</section>
"""
g.write("speaker-series.html", g.page("speaker-series.html", "Speaker Series", "The Tech Policy Hub Speaker Series pairs academics and practitioners.", speaker_body))

annual_body = """
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
      <div class="card"><span class="kicker">2026 Recap</span><h3>A Record Turnout</h3><p>Our most recent event drew practitioners, scholars, and students for a full day of programming -- summary and photos in the news archive.</p></div>
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
  <div class="container">
    {g.events_rows_html(g.EVENTS_ITEMS)}
  </div>
</section>
"""
g.write("events.html", g.page("events.html", "Events", "Upcoming events from the Tech Policy Hub.", events_body))

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
    <p class="lede">The University of Maryland's Tech Policy Hub studies tech policy from a socio-technical perspective, building the bridge between computer science and public policy.</p>
  </div>
</section>
<section>
  <div class="container with-sidebar">
    <div>
      <h2>Our mission</h2>
      <p>We bring together DMV-based issue networks of practitioners, scholars, industry leaders, and civil activists to inform, impact, and shape the future of technology in society -- applying comparative, qualitative, and computational research methods to craft socially desired paths for tech policy development.</p>
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
        <p style="font-size:.9rem;">Interested in becoming affiliated with us? Email our founder, Dr. Sivan-Sevilla, to discuss further.</p>
        <a href="#" class="btn btn-primary" style="width:100%; justify-content:center;">Contact Us</a>
      </div>
      <div class="sidebar-box">
        <h4>Mailing List</h4>
        <p style="font-size:.9rem;">Subscribe to stay up to date with research outputs and events.</p>
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
