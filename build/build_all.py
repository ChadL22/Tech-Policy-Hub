#!/usr/bin/env python3
import generate as g

g.clean_stale_pages()

# ===========================================================================
# HOME
# ===========================================================================
# Follow-up 52: the standalone news.html page is gone, so the homepage's
# "Hub News" rail (HUB_NEWS_RAIL, below) is now the site's ONE place to
# browse news -- it lists every NEWS_ITEMS entry (not a short 3-item
# excerpt with a "More News" link out to a fuller page anymore) inside a
# fixed-height scrollable box (`.rail-scroll` in styles.css), styled after
# CNBC's own "Latest News" sidebar per direct user request. The lead
# grid's left column is the Guiding Questions list rather than a second
# news rail (see follow-up 9); this is the only news listing on the page,
# so there's no risk of the same story appearing twice the way an older
# hero-rail + separate "Recent News" grid once did (see follow-up 8).
# Follow-up 53: the scroll box's last visible headline used to butt
# straight into the "Research Areas" header below it with no visual
# break, per direct user request referencing CNBC's own fade-to-white
# treatment at the bottom of their "Latest News" box. `.rail-scroll-wrap`
# is a plain, non-scrolling wrapper purely so the fade (`::after` on the
# wrapper, see styles.css) can sit OUTSIDE the scrolling element -- an
# overlay painted inside `.rail-scroll` itself would scroll away with the
# content instead of staying put over whatever's currently at the bottom
# of the visible box.
HUB_NEWS_RAIL = g.NEWS_ITEMS
EVENTS_RAIL = [dict(tag=f"{e['m']} {e['d']}", title=e['title'], link=e['link']) for e in g.EVENTS_ITEMS[:4]]

home_body = f"""
<section class="lead-section">
  <div class="container lead-grid">
    <div class="lead-secondary">
      <div class="rail-head">What We Do</div>
      <p>The University of Maryland&rsquo;s Tech Policy Hub studies tech policy from a socio&#8209;technical&nbsp;perspective, building the bridge between computer science &amp; public policy to understand how policy is designed and implemented for, by, and with tech. Our hub spans the forefront of tech policy across four research areas, bringing together DMV&#8209;based practitioners, scholars, and civil activists to shape the future of technology in society.</p>
      <p class="lead-join"><strong>Interested in becoming affiliated with us?</strong> Please email our founder, <a href="https://idonibrasco.github.io/" target="_blank" rel="noopener">Dr.&nbsp;Sivan&#8209;Sevilla</a>, to discuss further.</p>
      <div class="rail-head rail-head--stacked">Research Areas</div>
      <div class="research-matrix research-matrix--rail">{g.research_matrix_html()}</div>
    </div>
    <div class="lead-story">
      {g.spotlight_html(g.SPOTLIGHT_ITEMS)}
    </div>
    <div class="lead-rail">
      <div class="rail-head">Hub News</div>
      <div class="rail-scroll-wrap">
        <div class="rail-scroll">{g.rail_html(HUB_NEWS_RAIL)}</div>
      </div>
      <div class="rail-head--stacked"></div>
    </div>
  </div>
</section>

<section class="reading-section">
  <div class="container carousel-wrap">
    <div class="reading-panel">
      <div class="carousel-head">
        <h2>What we're reading</h2>
        <a href="https://phronesisresearch.org" target="_blank" rel="noopener" class="btn btn-ghost btn-arrow">More</a>
      </div>
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

<section id="about" class="guiding-section">
  <div class="container">
    <h3 class="guiding-head">Guiding Questions</h3>
    <div class="guide-q-list">
      {g.guiding_questions_html(g.QUESTIONS)}
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
# Follow-up: each publication is now a dict (venue/year/title/authors)
# instead of a bare (venue-with-year, title) tuple -- direct user request
# for a publications search that covers "author, year, title, conference
# etc.", which needs the author byline as its own real field rather than
# folded into a description string.
TOPIC_DETAIL = {
    "cybersecurity": dict(
        projects=[
            ("Cyber Risk Mapping for U.S. Counties", "Quantifying exposed attack surface and cyber risk across all 50 states and thousands of county governments."),
            ("Critical Infrastructure Resilience", "Working with practitioners to translate attack-surface research into actionable defense priorities."),
        ],
        pubs=[
            dict(venue="Journal of Cybersecurity", year=2026, title="Size, diversity, and severity of exposed attack surface across U.S. county governments.", authors=["Dr. Charlie Harry"]),
            dict(venue="Maryland Today", year=2026, title="UMD researchers calculate cyberattack risk for all 50 states.", authors=["Dr. Charlie Harry", "Jordan Diaz"]),
        ],
        people=["Dr. Charlie Harry", "Jordan Diaz"],
    ),
    "privacy": dict(
        projects=[
            ("Cookie-less Identification Tracking", "Studying how identification methods are evolving as third-party cookies are phased out, and what it means for privacy."),
            ("Watchdog Accountability", "Assessing the powers of formal and informal U.S. privacy regulators."),
        ],
        pubs=[
            dict(venue="Internet Policy Review", year=2026, title="Cookie-less identification: for and against privacy.", authors=["Dr. Ido Sivan-Sevilla"]),
            dict(venue="Privacy Law Scholars Conference", year=2026, title="Accountability powers of formal and informal U.S. privacy watchdogs.", authors=["Dr. Ido Sivan-Sevilla", "Amara Mensah"]),
        ],
        people=["Dr. Ido Sivan-Sevilla", "Amara Mensah"],
    ),
    "integrity": dict(
        projects=[
            ("Trustworthy Content Classification", "Classifying trustworthy content on the web using third-party site structure."),
            ("Platform Transparency Tracker", "Monitoring platform disclosures and their real-world enforcement."),
        ],
        pubs=[
            dict(venue="FOCI Workshop @ PETs", year=2026, title="Classifying trustworthy content on the web based on third-party structure.", authors=["Jordan Diaz"]),
            dict(venue="Policy Brief", year=2026, title="What platform transparency reports do and don't tell us.", authors=["Dr. Ido Sivan-Sevilla"]),
        ],
        people=["Jordan Diaz", "Dr. Ido Sivan-Sevilla"],
    ),
    "ml": dict(
        projects=[
            ("Algorithmic Accountability Framework", "Developing standards for evaluating machine learning systems used in public decision-making."),
            ("AI Governance Roundtables", "Convening researchers and policymakers on the governance of emerging AI systems."),
        ],
        pubs=[
            dict(venue="arXiv", year=2026, title="Applying Contextual Integrity to measure algorithmic decision-making.", authors=["Dr. Katie Shilton"]),
            dict(venue="Roundtable Summary", year=2025, title="Tech Policy Hub & VCAI roundtable on AI policy.", authors=["Lee Tiedrich"]),
        ],
        people=["Dr. Katie Shilton", "Lee Tiedrich"],
    ),
}


# Shared per-topic table renderers -- one Excel-style <table> per
# category, used inside each research.html area card below. (Each
# research area used to also get its own standalone page reusing an
# earlier card-based version of these same renderers; direct user
# request removed those pages since the area card already shows
# everything inline. A later direct user request replaced that
# card-based Projects/Publications/People tab strip with these tables,
# shown/hidden together across all four cards by the global People/
# Projects/Publications selector in main.js -- see areaCategory there.)
def _topic_people_table_html(d):
    rows = "".join(f'<tr data-search-row><td>{n}</td></tr>' for n in d["people"])
    return f'<table class="area-table"><thead><tr><th>Name</th></tr></thead><tbody>{rows}</tbody></table>'


def _topic_projects_table_html(d):
    rows = "".join(f'<tr data-search-row><td>{n}</td><td>{desc}</td></tr>' for n, desc in d["projects"])
    return f'<table class="area-table"><thead><tr><th>Project</th><th>Description</th></tr></thead><tbody>{rows}</tbody></table>'


def _topic_pubs_table_html(d):
    rows = "".join(
        f"""<tr data-search-row><td>{p['title']}</td><td>{p['venue']}</td><td>{p['year']}</td><td>{', '.join(p['authors'])}</td></tr>"""
        for p in d["pubs"]
    )
    return f'<table class="area-table"><thead><tr><th>Title</th><th>Venue</th><th>Year</th><th>Authors</th></tr></thead><tbody>{rows}</tbody></table>'


# Follow-up: the old flat "Where we work" link-grid + a separately
# filterable "Current projects" grid became one set of cards, one per
# research area, each expanding to reveal that area's own content.
# Follow-up 2: the standalone per-topic pages these used to also power
# are gone too (direct user request -- no research area needs its own
# page now that this card shows everything), so every link that used to
# point to e.g. topic-cybersecurity.html now points to
# research.html#area-panel-cybersecurity instead (see TOPICS in
# generate.py). Follow-up 3: card visuals restyled off a reference
# screenshot (MIT Media Lab's "Initiatives and Programs" grid). Follow-up
# 4 (direct user request, second reference from the same site): replaced
# the old per-card click-to-expand + internal Projects/Publications/
# People tab strip with ONE People/Projects/Publications selector above
# the whole grid (mirroring that reference's secondary nav row) plus a
# search box next to it -- picking a category opens every card's table
# for that category at once (main.js's areaCategory), and the standalone
# "Recent publications" section that used to live further down the page
# is gone too, folded into this Publications table instead of keeping
# two separate search UIs. main.js still opens + scrolls to the right
# card (or category) on load when a matching hash is present, so this
# stays a real deep-linkable, bookmarkable destination for every link
# above that points here.
area_cards = []
for t in g.TOPICS:
    d = TOPIC_DETAIL[t["key"]]
    area_cards.append(f"""
    <div class="area-card" id="area-panel-{t['key']}">
      <div class="area-card-head">
        <span class="area-card-top"><span class="area-card-index">{t['index']}</span></span>
        <span class="area-card-title"><h3>{t['name']}</h3><p>{t['blurb']}</p></span>
      </div>
      <div class="area-card-table" data-category-panel="people" hidden>{_topic_people_table_html(d)}</div>
      <div class="area-card-table" data-category-panel="projects" hidden>{_topic_projects_table_html(d)}</div>
      <div class="area-card-table" data-category-panel="publications" hidden>{_topic_pubs_table_html(d)}</div>
    </div>""")

area_tabs = "".join(
    f'<button type="button" class="filter-pill area-tab" data-category="{cat}">{label}</button>'
    for cat, label in [("people", "People"), ("projects", "Projects"), ("publications", "Publications")]
)

research_body = f"""
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Research</div>
    <span class="eyebrow">Research</span>
    <h1>Research</h1>
    <p class="lede">Cybersecurity, consumer privacy, information integrity, and trustworthy machine learning &mdash; studied through comparative, qualitative, and computational methods.</p>
  </div>
</section>
<section class="soft-bg">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Focus Areas</span><h2>Research areas</h2></div></div>
    <div class="area-controls">
      <div class="filter-bar">{area_tabs}</div>
      {g.search_box_html("Search by name, title, venue&hellip;", "Search research areas")}
    </div>
    <div class="area-list" id="area-list">{"".join(area_cards)}</div>
    <p class="list-empty" data-empty-for="area-list" hidden>No results match your search.</p>
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
# NEWS -- removed as a standalone page in follow-up 52. The homepage's
# "Hub News" rail (see HOME above) is now the site's one news listing,
# a scrollable box showing every NEWS_ITEMS entry -- no separate news.html
# needed. feed_items_html() (still defined in generate.py) is now unused,
# left in place in case a future fuller-archive page wants it back.
# ===========================================================================
# EVENTS
# ===========================================================================
# Absolute (not page-relative) so this works identically regardless of the
# fact that events.html itself lives one folder deep (docs/events/index.html)
# while events.ics lives at the site root (docs/events.ics) -- see
# events_ics()'s docstring for why the feed itself is all-day/no-timezone.
_ics_url = g.SITE_URL + "events.ics"
_ics_webcal_url = _ics_url.replace("https://", "webcal://")

# Follow-up: reworked at direct user request into something closer to
# SCOTUSblog's own "Supreme Court Calendar" page -- same category filter
# pills and sidebar calendar widget as before, but the on-page title now
# reads "Tech Policy Hub Calendar" (not just "Events"), a text search
# box filters both lists client-side (see main.js's applyEventFilters,
# combined with the category pills so both conditions apply together),
# and Upcoming/Past Events each sit in a capped-height scroll box
# (reusing the same .rail-scroll-wrap/.rail-scroll fade-bottom component
# as the homepage's Hub News rail) instead of growing as an unbounded
# list -- direct user request: "It wouldn't be in our best interest to
# have a laundry list of events for the page that goes on forever."
# Follow-up: the page-hero intro (breadcrumb/eyebrow/h1/lede) was
# removed entirely per direct user request -- the page now opens
# straight into the filter pills, matching SCOTUSblog's own calendar
# page (which drops straight into its filter row + search box right
# under the nav) rather than restating "Tech Policy Hub Calendar" above
# a tool the EVENTS nav item already led the visitor to.
events_body = f"""
<section>
  <div class="container with-sidebar events-layout">
    <div>
      {g.filter_pills_html(list(g.EVENT_CATEGORIES.keys()), 'events')}
      {g.search_box_html("Search events&hellip;", "Search events")}
      <div class="section-head" style="margin-top:28px;"><div><span class="eyebrow">Upcoming</span><h2>Upcoming Events</h2></div></div>
      <div class="rail-scroll-wrap">
        <div class="rail-scroll events-scroll" id="upcoming-events-list">
          {g.events_rows_html(g.EVENTS_ITEMS)}
        </div>
      </div>
      <p class="list-empty" data-empty-for="upcoming-events-list" hidden>No upcoming events match your search or filter.</p>
      <div class="section-head" style="margin-top:48px;"><div><span class="eyebrow">Past</span><h2>Past Events</h2></div></div>
      <div class="rail-scroll-wrap">
        <div class="rail-scroll events-scroll" id="past-events-list">
          {g.past_events_html(g.PAST_EVENTS_ITEMS)}
        </div>
      </div>
      <p class="list-empty" data-empty-for="past-events-list" hidden>No past events match your search or filter.</p>
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
g.write("events.html", g.page("events.html", "Events", "Search and browse upcoming and past Tech Policy Hub events.", events_body))
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
# Follow-up 59: about.html removed entirely (direct user request -- its
# mission copy, "join the Hub" invite, and founder contact link are all
# now covered by the homepage's own About the Hub band (`#about`,
# see home_body above), so a whole separate page repeating that content
# was pure redundancy). Anything that used to link to about.html now
# points at index.html#about instead (footer "Connect" column, the
# "Practice"-tagged guiding question, see generate.py), except the old
# "All Topics" pill button, which now goes to research.html since that
# was never really an About-page destination.

print("\\nDone. Pages written to:", g.ROOT)
