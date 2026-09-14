#!/usr/bin/env python3
import re
import generate as g

g.clean_stale_pages()


def _slugify(text):
    """Same convention as generate.py's event-title slugs -- used to give
    each person a stable anchor id (person-<slug>) on people.html so the
    Research page's People tiles can link straight to that person's full
    listing instead of repeating their bio in a tile."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

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
      <div class="lead-secondary-body">
        <p>The University of Maryland&rsquo;s Tech Policy Hub studies tech policy from a socio&#8209;technical&nbsp;perspective, building the bridge between computer science &amp; public policy to understand how policy is designed and implemented for, by, and with tech. Our hub spans the forefront of tech policy across four research areas, bringing together DMV&#8209;based practitioners, scholars, and civil activists to shape the future of technology in society.</p>
        <p class="lead-join"><strong>Interested in becoming affiliated with us?</strong> Please email our founder, <a href="https://idonibrasco.github.io/" target="_blank" rel="noopener">Dr.&nbsp;Sivan&#8209;Sevilla</a>, to discuss further.</p>
        <div class="rail-head rail-head--stacked">Research Areas</div>
        <div class="research-matrix research-matrix--rail">{g.research_matrix_html()}</div>
      </div>
    </div>
    <div class="lead-story">
      {g.spotlight_html(g.SPOTLIGHT_ITEMS)}
    </div>
    <div class="lead-rail">
      <div class="rail-head">Hub News</div>
      <div class="lead-rail-body">
        <div class="rail-scroll-wrap">
          <div class="rail-scroll">{g.rail_html(HUB_NEWS_RAIL)}</div>
        </div>
      </div>
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
g.write("index.html", g.page("index.html", "Home", "The University of Maryland Tech Policy Hub studies the bridge between computer science and public policy.", home_body))

# ===========================================================================
# RESEARCH HUB + TOPIC DETAIL DATA
# ===========================================================================
# Follow-up: each publication is now a dict (venue/year/title/authors)
# instead of a bare (venue-with-year, title) tuple -- direct user request
# for a publications search that covers "author, year, title, conference
# etc.", which needs the author byline as its own real field rather than
# folded into a description string.
# Content lives in build/data/topic_detail.yml -- see README "Editing
# content". `projects` entries are 2-element [name, description] lists
# now rather than Python tuples (YAML has no tuple type); every place
# that reads them just does `for n, d in ...["projects"]`, which
# unpacks a 2-item list exactly the same as a 2-item tuple.
TOPIC_DETAIL = g.load_data("topic_detail")

# Follow-up 7 (direct user request, replacing the click-to-select single-
# card explorer, guided by a hand-drawn sketch the user shared): the page
# is now a faceted layout -- multi-select area filter pills (any
# combination at once; none selected means "show everything") plus one
# shared search box (.area-controls) control three always-visible
# sections stacked below in this order: People tiles, Project tiles
# (both collapsible via their <h2> header button -- see
# .subsection-toggle in main.js), and a Publications list styled after a
# reference screenshot the user shared of Princeton's CoCoSci lab site
# (a small colored area code to the left of each citation-style row,
# grouped under a year heading). Selecting e.g. Consumer Privacy AND
# Trustworthy ML shows the union of both areas' people, projects, and
# papers across all three sections at once. AREA_META gives each area
# its own accent color, reused for: the filter pill's active-state fill,
# and the small .area-tag on every tile/row -- since every person,
# project, and publication belongs to exactly one area in this data
# model, that one tag is enough to tell entries apart once multiple
# areas are shown together. main.js's researchExplorer closure does the
# actual show/hide (every tile/row carries data-area + data-search-row);
# a pill's own id (area-panel-<key>, the site's existing deep-link
# target from the nav, footer, homepage matrix and spotlight) lets it
# select just that one area and scroll here on load, same as before.
# AREA_META now lives in generate.py (g.AREA_META) -- shared with
# people.html's research-area badges/filter pills, not just this page's.

# PEOPLE_ITEMS (generate.py) already carries a real role + one-line focus
# for everyone on the People page -- reused here as each person tile's
# description rather than inventing separate copy for the same person.
_PEOPLE_BY_NAME = {p["name"]: p for p in g.PEOPLE_ITEMS}


def _area_tag_html(key):
    m = g.AREA_META[key]
    return f'<span class="area-tag" style="--area-color:{m["color"]}">{m["code"]}</span>'


def _area_tags_html(keys):
    return f'<div class="rp-tags">{"".join(_area_tag_html(k) for k in keys)}</div>'


def _person_tile_html(name, keys):
    # Direct user request, modeled on Bloomberg.com's "Bloomberg
    # Originals" card: a photo on top, then name + research-area badges
    # in a plain white section below -- no bio, no role text, per the
    # user's own mockup ("[Picture] _________ Name [badges]"). No real
    # headshots yet, so the "photo" is a solid --ink placeholder --
    # previously the person's initials centered, now (direct user
    # request) a generic person silhouette instead, "like you might see
    # in a video game for locked characters" -- every placeholder tile
    # deliberately looks identical, the same way a game's locked-
    # character slots all show the same silhouette until unlocked. The
    # tile is itself a link to their full listing on people.html
    # (id="person-<slug>" on that page's .person-row, see
    # _person_row_html), rather than repeating their bio a second time
    # in a smaller space.
    slug = _slugify(name)
    return f"""
      <a class="rp-tile rp-tile--link rp-tile--person" href="people.html#person-{slug}" data-areas="{' '.join(keys)}" data-search-row>
        <div class="rp-tile-photo rp-tile-photo--person">
          <svg class="rp-tile-photo-silhouette" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
            <circle cx="50" cy="36" r="18"/>
            <path d="M50 60c-23 0-39 15-39 38h78c0-23-16-38-39-38z"/>
          </svg>
        </div>
        <div class="rp-tile-caption">
          <h3>{name}</h3>
          {_area_tags_html(keys)}
        </div>
      </a>"""


def _project_tile_html(name, desc, key):
    # Direct user request, modeled on Bloomberg.com's "Today's Videos"
    # card: a photo area on top (no real project photos yet, so this is
    # the same colored/textured placeholder treatment as the homepage
    # Research Spotlight's .lead-media, recolored per the project's
    # research area -- see AREA_META/g.AREA_META) with that area's badge
    # in the corner, then the title + description in a shaded caption
    # strip below (.rp-tile-caption) rather than floating directly on
    # white -- "the title... is in the grey section of the tile."
    m = g.AREA_META[key]
    return f"""
      <div class="rp-tile rp-tile--project" data-areas="{key}" data-search-row>
        <div class="rp-tile-photo" style="--area-color:{m['color']}">
          <span class="area-tag rp-tile-photo-badge">{m['code']}</span>
        </div>
        <div class="rp-tile-caption">
          <h3>{name}</h3>
          <p class="rp-desc">{desc}</p>
        </div>
      </div>"""


def _format_authors(authors):
    if len(authors) == 1:
        return authors[0]
    return ", ".join(authors[:-1]) + " &amp; " + authors[-1]


def _pub_row_html(p):
    # data-year (alongside the existing data-areas) lets researchExplorer's
    # render() in main.js filter Publications by year the same way it
    # already filters by area -- see the year-filter-pill row built below.
    return f"""
      <div class="pub-row" data-areas="{p['area']}" data-year="{p['year']}" data-search-row>
        {_area_tags_html([p['area']])}
        <p class="pub-cite"><span class="pub-cite-authors">{_format_authors(p['authors'])}</span> ({p['year']}). {p['title']} <span class="pub-cite-venue">{p['venue']}.</span></p>
      </div>"""


def _pubs_list_html():
    rows = []
    for t in g.TOPICS:
        for p in TOPIC_DETAIL[t["key"]]["pubs"]:
            rows.append(dict(p, area=t["key"]))
    rows.sort(key=lambda p: (-p["year"], p["title"]))
    out = []
    current_year = None
    for p in rows:
        if p["year"] != current_year:
            current_year = p["year"]
            out.append(f'<h3 class="pub-year">{current_year}</h3>')
        out.append(_pub_row_html(p))
    return "".join(out)


def _pub_years():
    """Distinct publication years, newest first -- drives the year-filter
    pill row above the Publications list (multi-select, same pattern as
    the area filter pills: none selected shows every year)."""
    years = {p["year"] for t in g.TOPICS for p in TOPIC_DETAIL[t["key"]]["pubs"]}
    return sorted(years, reverse=True)


def _year_filter_pills_html():
    return "".join(
        f'<button type="button" class="filter-pill year-filter-pill" data-year="{y}" aria-pressed="false">{y}</button>'
        for y in _pub_years()
    )


area_filter_pills = "".join(
    f'<button type="button" class="filter-pill area-filter-pill" id="area-panel-{t["key"]}" data-area="{t["key"]}" style="--area-color:{g.AREA_META[t["key"]]["color"]}" aria-pressed="false">{t["name"]}</button>'
    for t in g.TOPICS
)

# Follow-up 8 (direct user request): a person listed under more than one
# research area -- Jordan Diaz (Cybersecurity + Information Integrity),
# Dr. Ido Sivan-Sevilla (Consumer Privacy + Information Integrity) --
# used to render as a separate tile per area (a straight loop over each
# area's people list). Now every unique name gets exactly one tile, with
# one .area-tag per area they belong to (in TOPICS order), and
# data-areas carries all of them space-separated so selecting ANY one of
# those areas still matches the tile. _person_areas below collects that
# per-name area list once, in first-seen order, before building tiles.
_person_areas = {}
for t in g.TOPICS:
    for n in TOPIC_DETAIL[t["key"]]["people"]:
        _person_areas.setdefault(n, []).append(t["key"])

people_tiles = "".join(_person_tile_html(name, keys) for name, keys in _person_areas.items())
project_tiles = "".join(_project_tile_html(n, d, t["key"]) for t in g.TOPICS for n, d in TOPIC_DETAIL[t["key"]]["projects"])
pubs_list = _pubs_list_html()
year_filter_pills = _year_filter_pills_html()

research_body = f"""
<!-- Follow-up (direct user request): dropped the People/Teaching/Speaker
     Series/Annual Event-style .page-hero (breadcrumb/eyebrow/big
     title/lede) on Research, People, and Events -- the user felt these
     added bulk without earning it (nav + browser tab already say what
     page you're on). Left with just a plain breadcrumb line for
     orientation; content starts right at the filter bar below. -->
<section class="breadcrumb-bar">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Research</div>
  </div>
</section>
<section>
  <div class="container container-narrow">
    <!-- Follow-up (direct user request): the "Filters" toggle label and
         its underline are gone, matching Events/People -- just the
         Research Area dropdown + search box remain, always visible. -->
    <div class="area-controls">
      <div class="filter-dropdowns-row">
        <div class="filter-dropdown">
          <button type="button" class="filter-dropdown-toggle" aria-haspopup="true" aria-expanded="false">
            <span>Research Area</span><span class="filter-dropdown-count" hidden></span>
            <span class="filter-dropdown-caret" aria-hidden="true"></span>
          </button>
          <div class="filter-dropdown-menu" hidden role="group" aria-label="Filter by research area">{area_filter_pills}</div>
        </div>
      </div>
      {g.search_box_html("Search people, projects, publications&hellip;", "Search research")}
    </div>

    <section class="research-subsection" id="people">
      <!-- Follow-up (direct user request): People now starts expanded,
           matching Projects below -- it no longer starts collapsed. -->
      <button type="button" class="subsection-toggle" aria-expanded="true" aria-controls="people-panel">
        <h2>People</h2>
        <span class="subsection-caret" aria-hidden="true"></span>
      </button>
      <!-- Follow-up (direct user request, modeled on Bloomberg's homepage
           "Bloomberg Originals"/"Watch" rows): this used to be a free
           `overflow-x:auto` scroll strip, which could leave a tile
           half-cut-off at the right edge. Now a fixed-width `.rp-carousel-
           viewport` clips `.rp-grid` to a JS-computed width, paged with
           the prev/next arrows below (see initTileCarousel() in main.js)
           rather than free-scrolled/dragged -- so only whole tiles are
           ever visible. That same JS also stretches every tile to
           exactly fill the row whenever there are enough of them (no
           leftover gap at the row's edge); when a filter/search leaves
           fewer tiles than fit one page, they keep their natural width
           and the row is allowed to fall short -- direct user request
           ("if there are less tiles... the open space is fine"). No
           page dots -- direct user request to drop them and rely on the
           arrows alone (greyed out via :disabled at either end).
           `data-max-per-page="4"` caps how many tiles initTileCarousel()
           will ever show on one page here regardless of how wide the
           row is -- direct user request, matching Bloomberg's own
           "Bloomberg Originals" row (4 across); `.rp-carousel--projects`
           below has no cap, since its wider tiles already land near
           that count naturally. `.rp-carousel--people` tiles are a
           photo + name + area badges, no bio/role -- see
           _person_tile_html. -->
      <div class="rp-carousel rp-carousel--people" id="people-panel" data-carousel data-max-per-page="4">
        <div class="rp-carousel-panel">
          <div class="rp-carousel-viewport">
            <div class="rp-grid">{people_tiles}</div>
          </div>
        </div>
        <div class="rp-carousel-footer">
          <div class="rp-carousel-arrows">
            <button type="button" class="rp-carousel-arrow rp-carousel-prev" aria-label="Previous people"></button>
            <button type="button" class="rp-carousel-arrow rp-carousel-next" aria-label="Next people"></button>
          </div>
        </div>
      </div>
      <p class="list-empty" data-empty-for="people-panel" hidden>No people match your filters.</p>
    </section>

    <section class="research-subsection" id="projects">
      <button type="button" class="subsection-toggle" aria-expanded="true" aria-controls="projects-panel">
        <h2>Projects</h2>
        <span class="subsection-caret" aria-hidden="true"></span>
      </button>
      <div class="rp-carousel rp-carousel--projects" id="projects-panel" data-carousel>
        <div class="rp-carousel-panel">
          <div class="rp-carousel-viewport">
            <div class="rp-grid">{project_tiles}</div>
          </div>
        </div>
        <div class="rp-carousel-footer">
          <div class="rp-carousel-arrows">
            <button type="button" class="rp-carousel-arrow rp-carousel-prev" aria-label="Previous projects"></button>
            <button type="button" class="rp-carousel-arrow rp-carousel-next" aria-label="Next projects"></button>
          </div>
        </div>
      </div>
      <p class="list-empty" data-empty-for="projects-panel" hidden>No projects match your filters.</p>
    </section>

    <section class="research-subsection" id="publications">
      <div class="pub-section-head">
        <h2>Publications</h2>
        <div class="year-filter-bar" role="group" aria-label="Filter publications by year">{year_filter_pills}</div>
      </div>
      <div class="pub-panel">
        <div class="pub-list" id="publications-panel">{pubs_list}</div>
        <p class="list-empty" data-empty-for="publications-panel" hidden>No publications match your filters.</p>
      </div>
    </section>
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
# Follow-up (direct user request): dropped the "Upcoming"/"Past" eyebrow
# above each section's own "Upcoming Events"/"Past Events" <h2> -- the
# eyebrow was restating the heading right below it, not labeling
# something the heading didn't already say (contrast the homepage's
# eyebrows, which label a *different* word than the h2 beside them,
# e.g. "Calendar" above "Events"). See event-row styling in styles.css
# for the alternating-background/gold-top-bar treatment on every other
# row, also a direct user request (modeled on .reading-panel's gold top
# border on the homepage's "What we're reading" panel).
# Follow-up (direct user request): the calendar (.events-sidebar-sticky
# -- legend + widget + subscribe buttons) is sticky on desktop -- see
# the `min-width: 901px` rule in styles.css -- so it travels with the
# viewport as the visitor scrolls the (possibly much longer) events
# list beside it, instead of scrolling out of view after the first
# screenful. Sticky sits on an INNER div, not the grid item itself
# (.events-sidebar, the plain outer column): a grid item that's also
# the sticky element has zero room to move once it's stretched to the
# row's full height (its containing block and its own box become the
# same size, so there's no scroll range left to be sticky *within* --
# confirmed by direct testing, not just a spec reading). Nesting the
# sticky content inside a plain block gives it a real (taller, grid-
# stretched) containing block to float inside, which is what lets it
# stay pinned for the list's whole scroll instead of not sticking at
# all, or detaching after only its own short height's worth of scroll.
events_body = f"""
<!-- Follow-up (direct user request): dropped the .page-hero block --
     see the matching note on research_body above. -->
<section class="breadcrumb-bar">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Events</div>
  </div>
</section>
<section>
  <div class="container with-sidebar events-layout">
    <div>
      <!-- Follow-up (direct user request): the "Filters" toggle label
           and its collapsing behavior are gone -- Category + Search now
           sit directly at the top of the main column, always visible,
           so their top edge lines up with the sidebar's "Calendar"
           heading instead of sitting below an extra label first. The
           .area-controls div itself (and its search/pills wiring in
           main.js) is unchanged; it's just no longer wrapped in a
           hidden panel behind a button. -->
      <div class="area-controls">
        <div class="filter-dropdowns-row">
          <div class="filter-dropdown">
            <button type="button" class="filter-dropdown-toggle" aria-haspopup="true" aria-expanded="false">
              <span>Category</span><span class="filter-dropdown-count" hidden></span>
              <span class="filter-dropdown-caret" aria-hidden="true"></span>
            </button>
            <div class="filter-dropdown-menu" hidden role="group" aria-label="Filter by category">{g.filter_pills_html(list(g.EVENT_CATEGORIES.keys()), 'events')}</div>
          </div>
        </div>
        {g.search_box_html("Search events&hellip;", "Search events")}
      </div>
      <div class="section-head" style="margin-top:28px;"><div><h2>Upcoming Events</h2></div></div>
      <div class="rail-scroll-wrap events-list-wrap">
        <div class="rail-scroll events-scroll" id="upcoming-events-list">
          {g.events_rows_html(g.EVENTS_ITEMS)}
        </div>
      </div>
      <p class="list-empty" data-empty-for="upcoming-events-list" hidden>No upcoming events match your search or filter.</p>
      <div class="section-head" style="margin-top:48px;"><div><h2>Past Events</h2></div></div>
      <div class="rail-scroll-wrap events-list-wrap">
        <div class="rail-scroll events-scroll" id="past-events-list">
          {g.past_events_html(g.PAST_EVENTS_ITEMS)}
        </div>
      </div>
      <p class="list-empty" data-empty-for="past-events-list" hidden>No past events match your search or filter.</p>
    </div>
    <div class="events-sidebar">
      <div class="events-sidebar-sticky">
        <h4 style="font-family:var(--font-body); font-size:.95rem; font-weight:700; margin-bottom:14px;">Calendar</h4>
        <div class="cal-legend">{g.calendar_legend_html(g.EVENT_CATEGORIES)}</div>
        {g.calendar_widget_html(g.EVENTS_ITEMS, g.EVENT_CATEGORIES)}
        <a href="{_ics_webcal_url}" class="btn btn-primary" style="width:100%; justify-content:center; margin-top:18px;">Subscribe to Calendar</a>
        <a href="{_ics_url}" class="btn btn-ghost" style="width:100%; justify-content:center; margin-top:10px; font-size:.82rem;">Download .ics file</a>
      </div>
    </div>
  </div>
</section>
"""
g.write("events.html", g.page("events.html", "Events", "Search and browse upcoming and past Tech Policy Hub events.", events_body))
g.write_raw("events.ics", g.events_ics(g.EVENTS_ITEMS))

# ===========================================================================
# PEOPLE
# ===========================================================================
# Follow-up (direct user request): replaced the plain 3-up initials/role/
# one-liner grid with a vertical list carrying real per-person content --
# a headshot slot with links/contact underneath it, the person's title
# doing double duty as a section-header-style divider for that entry, and
# a bio to the right of the headshot alongside their research-area
# badges. Two independent, ANDed multi-select filters sit above the list
# -- Role (ROLE_TYPES in generate.py: Leadership/Area Lead/Affiliate/
# Fellow/Graduate Fellow, a person can carry more than one) and Research
# Area (the same 4 areas/colors as research.html, reusing _area_tag_html/
# _area_tags_html and g.AREA_META) -- plus a search box, all wired
# through the same researchExplorer closure in main.js that already
# drove research.html's People/Projects/Publications filtering (extended
# there with a third `data-roles` facet alongside its existing area+year
# facets). Deliberately NOT reusing research.html's `.area-filter-pill`
# ids (those are research.html's own nav/footer/homepage deep-link
# targets -- giving people.html pills the same ids would just be unused
# duplicate ids in a different document, so these carry no id at all).
#
# Photos are still the initials placeholder (no headshot files yet), and
# `bio`/`website`/`linkedin` on most PEOPLE_ITEMS entries are placeholder/
# blank pending real copy and links from each person -- see README
# "Known placeholders". A person with no website/linkedin set gets no
# links block at all rather than an empty one.
def _person_contact_html(p):
    # Direct user request: email and social-media accounts (LinkedIn,
    # etc.) sit under the photo itself, while personal/lab websites stay
    # with the bio in the content column (see _person_websites_html).
    links = []
    if p.get("email"):
        links.append(f'<a href="mailto:{p["email"]}">Email</a>')
    if p.get("linkedin"):
        links.append(f'<a href="{p["linkedin"]}" target="_blank" rel="noopener">LinkedIn</a>')
    if not links:
        return ""
    return f'<div class="person-contact">{"".join(links)}</div>'


def _person_websites_html(p):
    # `websites` is a list of {label, url} so a person with more than one
    # site (e.g. a personal site + a research/org site) can list both,
    # each under its own label. These stay below the bio, where the
    # combined links block used to live.
    links = [
        f'<a href="{w["url"]}" target="_blank" rel="noopener">{w["label"]}</a>'
        for w in (p.get("websites") or [])
    ]
    if not links:
        return ""
    return f'<div class="person-links">{"".join(links)}</div>'


def _person_row_html(p):
    # Follow-up (direct user request, modeled on research.html's own
    # People-tile cards -- see _person_tile_html/.rp-tile-photo--person):
    # the photo is no longer a small initials square floating over a
    # thin links column. It's now a full card -- photo on top (same
    # silhouette placeholder/markup as the research.html tile, reused
    # verbatim so both pages render the identical component), a divider,
    # then Email/Website/research-area badges stacked below -- sized to
    # match the height of the name/role/bio column beside it (.person-
    # body below goes align-items:stretch specifically so this card's
    # height always equals its row's tallest content, per "the card
    # should be as tall as the information... next to it"). The content
    # column itself now carries ONLY name/role/bio, per the same request
    # -- badges and links moved into the card.
    areas = _person_areas.get(p["name"], [])
    # id="person-<slug>" is a direct-linkable anchor -- research.html's
    # People tiles (see _person_tile_html) link straight here instead of
    # duplicating a person's bio in the tile itself.
    return f"""
      <div class="person-row" id="person-{_slugify(p['name'])}" data-areas="{' '.join(areas)}" data-roles="{' '.join(p['role_types'])}" data-search-row>
        <div class="person-body">
          <div class="person-media">
            <div class="rp-tile-photo rp-tile-photo--person">
              <svg class="rp-tile-photo-silhouette" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
                <circle cx="50" cy="36" r="18"/>
                <path d="M50 60c-23 0-39 15-39 38h78c0-23-16-38-39-38z"/>
              </svg>
            </div>
            <div class="person-media-caption">
              {_person_contact_html(p)}
              {_person_websites_html(p)}
              {_area_tags_html(areas) if areas else ""}
            </div>
          </div>
          <div class="person-content">
            <h3>{p['name']}</h3>
            <div class="person-role">{p['role']}</div>
            <div class="person-bio"><p>{p['bio']}</p></div>
          </div>
        </div>
      </div>"""


role_filter_pills_people = "".join(
    f'<button type="button" class="filter-pill role-filter-pill" data-role="{key}" aria-pressed="false">{label}</button>'
    for key, label in g.ROLE_TYPES.items()
)
# Follow-up (direct user request): "type" (role_types.yml) is now
# strictly Core Member vs Affiliate -- everything that used to double as
# a role *type* (Founder & Director, Co-Lead, etc.) is really a
# per-person *position*, which already lives in `role` and shows under
# their name (_person_row_html) regardless of this grouping. Core
# members and affiliates are split into their own section-headed groups
# below instead of one flat list, in People.yml's existing order within
# each group.
_core_people = [p for p in g.PEOPLE_ITEMS if "core-member" in p["role_types"]]
_affiliate_people = [p for p in g.PEOPLE_ITEMS if "core-member" not in p["role_types"]]
core_people_rows = "".join(_person_row_html(p) for p in _core_people)
affiliate_people_rows = "".join(_person_row_html(p) for p in _affiliate_people)

people_body = f"""
<!-- Follow-up (direct user request): dropped the .page-hero block --
     see the matching note on research_body above. -->
<section class="breadcrumb-bar">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / People</div>
  </div>
</section>
<!-- Follow-up (direct user request): "reduce some of the white space
     above the filter and search section and below the breadcrumb" --
     a bare <section> here inherited the generic section (padding 56px) top/bottom
     site-wide rule, same 56px-top-padding bug pattern as the earlier
     Research page People/Projects gap fix. id="people-main" gets a
     people.html-scoped override (see styles.css) that shrinks just the
     top padding; the bottom 56px (spacing before the footer) is left
     alone. -->
<section id="people-main">
  <div class="container container-narrow">
    <!-- Follow-up (direct user request): the "Filters" toggle label and
         its underline are gone (it read as an orphaned heading with no
         content header to pair with -- see the .subsection-toggle--
         filters follow-up above), and so is the Research Area dropdown
         -- just the Role dropdown + search box remain, always visible,
         no collapsing panel. The .area-controls div itself (and its
         search/role-pill wiring in main.js) is unchanged. -->
    <div class="area-controls">
      <div class="filter-dropdowns-row">
        <div class="filter-dropdown">
          <button type="button" class="filter-dropdown-toggle" aria-haspopup="true" aria-expanded="false">
            <span>Role</span><span class="filter-dropdown-count" hidden></span>
            <span class="filter-dropdown-caret" aria-hidden="true"></span>
          </button>
          <div class="filter-dropdown-menu" hidden role="group" aria-label="Filter by role">{role_filter_pills_people}</div>
        </div>
      </div>
      {g.search_box_html("Search people&hellip;", "Search people")}
    </div>
    <!-- Follow-up (direct user request, "look at the research section
         for inspiration"): Core Members and Affiliates now use the exact
         same collapsible-heading component as research.html's People/
         Projects -- a plain .subsection-toggle button (no underline,
         sits OUTSIDE the grey box) with a .subsection-caret that flips
         open/closed, wired by the same generic .subsection-toggle click
         handler in main.js (keyed off aria-controls, already page-
         agnostic). id="people-list" stays on the outer wrapper so the
         existing data-empty-for="people-list" "No people match your
         filters" message still checks every row across BOTH groups.
         Each group's [data-people-group-panel] is still hidden by
         main.js when a filter/search leaves nothing visible inside it
         (same idea as research.html's .pub-year headings) -- that check
         now hides the whole .research-subsection (panel.closest(...)),
         not a sibling-adjacency-dependent heading, so the extra
         .rail-scroll-wrap nesting around Affiliates' rows (see below)
         no longer needs to stay in any particular position for it to
         keep working. -->
    <div id="people-list">
      <section class="research-subsection" id="core-members">
        <button type="button" class="subsection-toggle" aria-expanded="true" aria-controls="core-members-panel">
          <h2>Core Members</h2>
          <span class="subsection-caret" aria-hidden="true"></span>
        </button>
        <div class="people-group" id="core-members-panel">
          <div class="people-list" data-people-group-panel>
            {core_people_rows}
          </div>
        </div>
      </section>
      <!-- Follow-up (direct user request): "The list of them should be
           scrollable like the Hub News section on the homepage" -- reusing
           the same .rail-scroll-wrap/.rail-scroll fade-bottom component as
           the homepage rail and events.html's Upcoming/Past lists (see
           HUB_NEWS_RAIL above and events_body). Core Members is
           deliberately left as a plain flat list -- only Affiliates was
           asked for here, and it's short enough not to need capping. -->
      <section class="research-subsection" id="affiliates">
        <!-- Follow-up (direct user request): Affiliates now starts
             collapsed -- Core Members above stays expanded by default,
             only this one starts closed. main.js's subsection-toggle
             wiring (see near the top of this file) is keyed off
             whatever aria-expanded/hidden state ships in the markup, so
             aria-expanded="false" + the panel's own `hidden` attribute
             here is the entire change; no JS edits needed. -->
        <button type="button" class="subsection-toggle" aria-expanded="false" aria-controls="affiliates-panel">
          <h2>Affiliates</h2>
          <span class="subsection-caret" aria-hidden="true"></span>
        </button>
        <div class="people-group" id="affiliates-panel" hidden>
          <div class="people-list rail-scroll-wrap" data-people-group-panel>
            <div class="rail-scroll affiliates-scroll">
              {affiliate_people_rows}
            </div>
          </div>
        </div>
      </section>
    </div>
    <p class="list-empty" data-empty-for="people-list" hidden>No people match your filters.</p>
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
