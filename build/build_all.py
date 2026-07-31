#!/usr/bin/env python3
import generate as g

# ===========================================================================
# HOME
# ===========================================================================
home_body = f"""
<section class="featured-hero">
  <div class="container grid grid-2">
    <div class="media"><span>Tech Policy Hub</span></div>
    <div>
      <div class="meta">{g.NEWS_ITEMS[0]['date']}</div>
      <h1>{g.NEWS_ITEMS[0]['title']}</h1>
      <p class="lede">{g.NEWS_ITEMS[0]['summary']} Read more on our <a href="news.html">news &amp; publications</a> page.</p>
    </div>
  </div>
</section>

<section class="about-teaser">
  <div class="container grid grid-2">
    <div>
      <span class="eyebrow">About</span>
      <h2>What is the Tech Policy Hub?</h2>
    </div>
    <div>
      <p>The University of Maryland&rsquo;s Tech Policy Hub studies tech policy from a socio-technical perspective, building the bridge between computer science &amp; public policy to understand how policy is designed and implemented for, by, and with tech. Our hub spans across the forefront of tech policy domains, including cybersecurity, consumer privacy, misinformation, and trustworthy machine learning (ML). We bring together DMV-based issue networks of practitioners, scholars, industry leaders, and civil activists to inform, impact, and shape the future of technology in society, applying a mix of comparative, qualitative, and computational research methods to advance our understanding and craft socially desired future paths for tech policy development.</p>
      <a class="text-link" href="about.html">More About the Hub</a>
    </div>
  </div>
</section>

<section class="statement-band">
  <div class="container grid grid-2">
    <div>
      <div class="accent-bar" aria-hidden="true"></div>
      <h2>Building the bridge between computer science and public policy.</h2>
      <p>The Tech Policy Hub studies tech policy from a socio-technical perspective, bringing together practitioners, scholars, and students to work on cybersecurity, consumer privacy, information integrity, and trustworthy machine learning.</p>
    </div>
    <div class="pill-grid">
      {g.topic_pills_html()}
    </div>
  </div>
</section>

<section class="updates-hub">
  <div class="container">
    <div class="section-head">
      <div>
        <span class="eyebrow">Latest</span>
        <h2>What&rsquo;s Happening at the Hub</h2>
      </div>
    </div>
    <div class="tabs">
      <button class="tab-btn active" data-tab="research">Research Updates</button>
      <button class="tab-btn" data-tab="events">Events</button>
    </div>
    <div class="tab-panel active" data-tab="research">
      <div class="grid grid-3">
        {g.news_cards_html(g.NEWS_ITEMS, limit=3)}
      </div>
      <div class="center-cta">
        <a href="news.html" class="btn btn-ghost">See All News</a>
      </div>
    </div>
    <div class="tab-panel" data-tab="events">
      {g.events_rows_html(g.EVENTS_ITEMS, limit=3)}
      <div class="center-cta">
        <a href="events.html" class="btn btn-ghost">See All Events</a>
      </div>
    </div>
  </div>
</section>

<section class="newsletter-band">
  <div class="container inner">
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
g.write("index.html", g.page("index.html", "Home", "The University of Maryland Tech Policy Hub studies the bridge between computer science and public policy.", home_body))

# ===========================================================================
# TOPIC PAGES
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

for t in g.TOPICS:
    d = TOPIC_DETAIL[t["key"]]
    projects_html = "".join(f'<div class="card"><span class="kicker">Project</span><h3>{n}</h3><p>{desc}</p></div>' for n, desc in d["projects"])
    pubs_html = "".join(f'<div class="card"><span class="kicker">Publication</span><h3>{n}</h3><p>{desc}</p></div>' for n, desc in d["pubs"])
    people_html = "".join(f'<div class="card"><span class="kicker">Person</span><h3>{n}</h3></div>' for n in d["people"])
    body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Topics / {t['name']}</div>
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
# PROGRAMS: Courses, Speaker Series, Annual Event
# ===========================================================================
courses_body = """
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Programs / Courses</div>
    <span class="eyebrow">Programs</span>
    <h1>Courses</h1>
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
g.write("courses.html", g.page("courses.html", "Courses", "Cross-listed technology policy courses at the University of Maryland.", courses_body))

speaker_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Programs / Speaker Series</div>
    <span class="eyebrow">Programs</span>
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
    <div class="breadcrumb"><a href="index.html">Home</a> / Programs / Annual Event</div>
    <span class="eyebrow">Flagship Program</span>
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
    <span class="eyebrow">Connect</span>
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
    <span class="eyebrow">Connect</span>
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
    <span class="eyebrow">Connect</span>
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
about_body = """
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
      <h2 style="margin-top:36px;">Questions we ask</h2>
      <ul>
        <li>How do we address the social problems of computing through top-down and bottom-up policymaking?</li>
        <li>What can we learn from the history of policymaking across technology issues?</li>
        <li>What does tech policy look like from a comparative perspective -- across sectors and jurisdictions?</li>
        <li>How and by whom do tech policy issues enter the political agenda?</li>
        <li>How can the efficacy of tech policy be assessed and evaluated?</li>
        <li>How can we teach tech policy through an experiential learning perspective?</li>
      </ul>
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
        <a href="#" class="btn btn-ghost" style="width:100%; justify-content:center;">Subscribe</a>
      </div>
    </div>
  </div>
</section>
"""
g.write("about.html", g.page("about.html", "About", "About the University of Maryland Tech Policy Hub.", about_body))

print("\\nDone. Pages written to:", g.ROOT)
