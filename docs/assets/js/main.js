// Tech Policy Hub — shared interactions
document.addEventListener('DOMContentLoaded', function () {
  // Direct user request, modeled on Bloomberg.com's homepage "Bloomberg
  // Originals"/"Watch" rows: research.html's People/Projects tile rows
  // (.rp-carousel, see research_body in build_all.py) page through
  // whole tiles only via prev/next arrows -- never a free-scroll strip
  // that can leave a tile half-cut-off at the right edge. Each
  // `[data-carousel]` root owns a `.rp-carousel-viewport` (the clipped
  // window) wrapping a `.rp-grid` (the actual flex track of tiles) plus
  // a `.rp-carousel-footer` (just the arrows -- a follow-up direct user
  // request dropped the page dots as unnecessary; the arrows already
  // grey out via :disabled at either end, which is enough to show
  // position). initTileCarousel() below sets up ONE of these;
  // tileCarousels collects every instance on the page so the shared
  // researchExplorer filtering closure (further down this file) can
  // re-measure all of them after a filter/search change hides or shows
  // tiles -- see the `tileCarousels.forEach` call inside its render().
  var tileCarousels = [];

  function initTileCarousel(root) {
    var viewport = root.querySelector('.rp-carousel-viewport');
    var grid = root.querySelector('.rp-grid');
    var prevBtn = root.querySelector('.rp-carousel-prev');
    var nextBtn = root.querySelector('.rp-carousel-next');
    // The bordered/background box (.rp-carousel-panel) is now just the
    // viewport's own wrapper -- .rp-carousel-footer (the arrows) sits
    // outside it as a sibling, direct user request modeled on
    // Bloomberg's "Today's Videos" row (arrows below the card, not
    // inside its border). Its padding is what the tile-width math below
    // needs to measure against, not root's own (root carries none of
    // its own box styling now).
    var panel = root.querySelector('.rp-carousel-panel') || root;
    if (!viewport || !grid) return { refresh: function () {} };

    // Optional hard cap on tiles-per-page (data-max-per-page="4" on
    // research.html's People carousel -- direct user request to match
    // Bloomberg's own "Bloomberg Originals" row, 4 across, regardless of
    // how much wider the row itself is).
    var maxPerPage = parseInt(root.getAttribute('data-max-per-page'), 10) || 0;

    var page = 0;

    // Follow-up (direct user request -- "get rid of that [gap], it is
    // on the left/right of the row"): a page used to always show
    // `perPage` tiles at their fixed CSS width, which left a leftover
    // strip of empty panel whenever perPage*tileWidth didn't happen to
    // equal the available width exactly (routine for Projects' wider
    // tiles). This now stretches every tile so a full page fills the
    // row edge-to-edge -- but only when there are enough tiles to fill
    // one (tiles.length >= perPage); when a filter/search leaves fewer
    // than that, they're left at their natural width and the row is
    // allowed to fall short, since the user explicitly said that
    // shortfall is fine ("if there are less tiles... the open space is
    // fine"). Resets each tile's inline width back to '' before
    // measuring so `nominal` always reflects the real CSS value (people/
    // projects/mobile breakpoints) rather than a stale stretched one
    // from the last time this ran.
    function measure() {
      var tiles = Array.prototype.slice.call(grid.children).filter(function (t) { return !t.hidden; });
      if (!tiles.length) return { gap: 0, step: 0, perPage: 0, pages: 1, tiles: tiles };

      tiles.forEach(function (t) { t.style.flexBasis = ''; });
      var gap = parseFloat(getComputedStyle(grid).columnGap) || 0;
      var nominal = tiles[0].getBoundingClientRect().width;
      if (!nominal) return { gap: gap, step: 0, perPage: 0, pages: 1, tiles: tiles };

      var panelStyle = getComputedStyle(panel);
      var available = panel.getBoundingClientRect().width
        - (parseFloat(panelStyle.paddingLeft) || 0) - (parseFloat(panelStyle.paddingRight) || 0);
      // How many tiles WOULD fit one page at their natural width -- kept
      // separate from `perPage` below (which is capped to however many
      // tiles actually exist) so the stretch decision always compares
      // against the full page capacity, not against a count that's
      // already been shrunk to match a short, filtered list.
      var nominalPerPage = Math.max(1, Math.floor((available + gap) / (nominal + gap)));
      if (maxPerPage > 0) nominalPerPage = Math.min(nominalPerPage, maxPerPage);
      var perPage = Math.min(nominalPerPage, tiles.length);
      var pages = Math.max(1, Math.ceil(tiles.length / perPage));

      var tileWidth = nominal;
      if (tiles.length >= nominalPerPage) {
        tileWidth = (available - (nominalPerPage - 1) * gap) / nominalPerPage;
        perPage = nominalPerPage;
      }
      tiles.forEach(function (t) { t.style.flexBasis = tileWidth + 'px'; });

      return { gap: gap, step: tileWidth + gap, perPage: perPage, pages: pages, tiles: tiles };
    }

    function updateArrows(m) {
      if (prevBtn) prevBtn.disabled = page <= 0;
      if (nextBtn) nextBtn.disabled = page >= m.pages - 1;
    }

    function goTo(idx) {
      var m = measure();
      page = Math.max(0, Math.min(idx, m.pages - 1));
      if (m.step > 0) viewport.scrollTo({ left: page * m.perPage * m.step, behavior: 'smooth' });
      updateArrows(m);
    }

    function refresh() {
      var m = measure();
      viewport.style.width = m.step > 0 ? (m.perPage * m.step - m.gap) + 'px' : '';
      if (page > m.pages - 1) page = Math.max(0, m.pages - 1);
      if (m.step > 0) viewport.scrollLeft = page * m.perPage * m.step;
      updateArrows(m);
    }

    if (prevBtn) prevBtn.addEventListener('click', function () { goTo(page - 1); });
    if (nextBtn) nextBtn.addEventListener('click', function () { goTo(page + 1); });
    window.addEventListener('resize', refresh);
    refresh();

    return { refresh: refresh };
  }

  document.querySelectorAll('[data-carousel]').forEach(function (root) {
    tileCarousels.push(initTileCarousel(root));
  });

  // Mobile nav toggle -- follow-up (direct user request): the collapsed
  // nav is now a bounded-width drawer + dimmed backdrop instead of a
  // full-screen takeover (see the 1080px breakpoint in styles.css), so
  // there are three ways to close it (hamburger again, the explicit
  // .nav-close button, clicking the backdrop) plus Escape, all funneled
  // through one setNavOpen() so they can't drift out of sync with each
  // other or with the "nav-open" class that locks background scroll.
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.primary-nav');
  var navBackdrop = document.querySelector('.nav-backdrop');
  var navClose = document.querySelector('.nav-close');

  function setNavOpen(open) {
    if (!nav) return;
    nav.classList.toggle('open', open);
    if (toggle) toggle.setAttribute('aria-expanded', String(open));
    if (navBackdrop) navBackdrop.classList.toggle('open', open);
    document.body.classList.toggle('nav-open', open);
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      setNavOpen(!nav.classList.contains('open'));
    });
  }
  if (navBackdrop) navBackdrop.addEventListener('click', function () { setNavOpen(false); });
  if (navClose) navClose.addEventListener('click', function () { setNavOpen(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && nav && nav.classList.contains('open')) setNavOpen(false);
  });

  // Dropdown toggle -- on mobile (where the CSS collapses nav into a full
  // panel, see the 720px breakpoint in styles.css), tapping "Research" or
  // "Events" opens the submenu instead of navigating, since there's no
  // hover to reveal it any other way. On desktop the dropdown already
  // opens on hover/focus via CSS, so a click there follows the link
  // normally -- Research and Events are real pages, not just menu labels.
  document.querySelectorAll('.has-dropdown > .nav-link').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (window.innerWidth > 720) return;
      e.preventDefault();
      var parent = link.parentElement;
      var willOpen = !parent.classList.contains('open');
      document.querySelectorAll('.has-dropdown.open').forEach(function (li) {
        if (li !== parent) {
          li.classList.remove('open');
          var otherLink = li.querySelector('.nav-link');
          if (otherLink) otherLink.setAttribute('aria-expanded', 'false');
        }
      });
      parent.classList.toggle('open', willOpen);
      link.setAttribute('aria-expanded', String(willOpen));
    });
  });

  // Close any open dropdown when clicking outside the nav, or on Escape
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-dropdown')) {
      document.querySelectorAll('.has-dropdown.open').forEach(function (li) {
        li.classList.remove('open');
        var link = li.querySelector('.nav-link');
        if (link) link.setAttribute('aria-expanded', 'false');
      });
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.has-dropdown.open').forEach(function (li) {
        li.classList.remove('open');
        var link = li.querySelector('.nav-link');
        if (link) link.setAttribute('aria-expanded', 'false');
      });
    }
  });

  // Tabs (used on topic pages: Projects / Publications / People)
  document.querySelectorAll('.tabs').forEach(function (tabGroup) {
    var buttons = tabGroup.querySelectorAll('.tab-btn');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var target = btn.getAttribute('data-tab');
        var panelGroup = tabGroup.parentElement;
        panelGroup.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
        panelGroup.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });
        btn.classList.add('active');
        var panel = panelGroup.querySelector('.tab-panel[data-tab="' + target + '"]');
        if (panel) panel.classList.add('active');
      });
    });
  });

  // Research page: faceted explorer (direct user request, replacing the
  // earlier click-to-select single-card version, built per a hand-drawn
  // sketch the user shared) -- multi-select area filter pills (any
  // combination at once; none selected means "show everything") plus
  // one shared search box control three always-visible sections: People
  // tiles, Project tiles (both collapsible via their <h2> header
  // button), and a Publications list. Every tile/row carries
  // data-area + data-search-row; render() just toggles [hidden] on each
  // one against the active area set and the search text, then flips
  // each section's "no results" message ([data-empty-for]) when nothing
  // in it is left visible (or hides it outright while that section is
  // collapsed, so a collapsed panel never shows a stray "no results"
  // line). A pill's own id (area-panel-<key>, the site's existing
  // deep-link target from the nav, footer, homepage matrix and
  // spotlight) lets openResearchHashTarget() below select just that one
  // area and scroll here on load; a bare #people / #projects /
  // #publications hash just scrolls to that section without touching
  // the filter. Follow-up (direct user request): a second multi-select
  // pill row (.year-filter-pill) filters Publications by year the same
  // way -- only .pub-row elements carry data-year, so a row without one
  // (every People/Project tile) always passes the year check.
  var researchExplorer = (function () {
    var controls = document.querySelector('.area-controls');
    var pills = Array.prototype.slice.call(document.querySelectorAll('.area-filter-pill'));
    // Follow-up (direct user request: people.html's Research Area
    // dropdown is gone, leaving Role as its only filter dimension) --
    // this used to bail out into a no-op stub whenever there were no
    // .area-filter-pill elements on the page, which would have quietly
    // killed the Role filter AND search on people.html now that it has
    // no area pills at all (same class of bug as the .subsection-toggle
    // one fixed earlier this session: a guard scoped to one specific
    // filter facet, standing in for "is there anything to filter on
    // this page at all"). .area-controls only ever renders on pages
    // that want this whole explorer (research/events/people), so its
    // presence alone is the right guard.
    if (!controls) return { selectArea: function () {}, refresh: function () {} };

    var rows = Array.prototype.slice.call(document.querySelectorAll('[data-search-row]'));
    var emptyMsgs = Array.prototype.slice.call(document.querySelectorAll('[data-empty-for]'));
    var searchInput = controls.querySelector('.filter-search-input');
    var yearPills = Array.prototype.slice.call(document.querySelectorAll('.year-filter-pill'));
    // Role filter (people.html's second facet, ANDed with area/search --
    // direct user request to filter by role type alongside research
    // area). No page but people.html has .role-filter-pill elements or
    // data-roles rows, so this is a no-op everywhere else, same as the
    // year facet is a no-op outside research.html's Publications.
    var rolePills = Array.prototype.slice.call(document.querySelectorAll('.role-filter-pill'));
    var selected = new Set();
    var selectedYears = new Set();
    var selectedRoles = new Set();

    function render() {
      var query = ((searchInput && searchInput.value) || '').trim().toLowerCase();
      pills.forEach(function (pill) {
        var on = selected.has(pill.getAttribute('data-area'));
        pill.classList.toggle('active', on);
        pill.setAttribute('aria-pressed', String(on));
      });
      yearPills.forEach(function (pill) {
        var on = selectedYears.has(pill.getAttribute('data-year'));
        pill.classList.toggle('active', on);
        pill.setAttribute('aria-pressed', String(on));
      });
      rolePills.forEach(function (pill) {
        var on = selectedRoles.has(pill.getAttribute('data-role'));
        pill.classList.toggle('active', on);
        pill.setAttribute('aria-pressed', String(on));
      });
      rows.forEach(function (row) {
        // data-areas is space-separated -- usually one area, but a
        // person listed under more than one research area (direct user
        // request: one tile per person, not one per area) carries all
        // of them, and matches if ANY is in the active selection.
        var areas = (row.getAttribute('data-areas') || '').split(/\s+/).filter(Boolean);
        var matchesArea = selected.size === 0 || areas.some(function (a) { return selected.has(a); });
        // Only .pub-row elements carry data-year -- a People/Project
        // tile has none, so it always matches regardless of the year
        // selection (the year filter only ever narrows Publications).
        var year = row.getAttribute('data-year');
        var matchesYear = !year || selectedYears.size === 0 || selectedYears.has(year);
        // Only people.html's .person-row elements carry data-roles --
        // everything else (research.html's tiles/pub-rows) always
        // matches regardless of the role selection, same reasoning as
        // the year check above.
        var rolesAttr = row.getAttribute('data-roles');
        var matchesRole = !rolesAttr || selectedRoles.size === 0 ||
          rolesAttr.split(/\s+/).some(function (r) { return selectedRoles.has(r); });
        var matchesSearch = !query || row.textContent.toLowerCase().indexOf(query) !== -1;
        row.hidden = !(matchesArea && matchesYear && matchesRole && matchesSearch);
      });
      // Direct user request: Publications rows alternate white/grey, and
      // that alternation has to hold "no matter how the content is
      // filtered" -- a plain CSS :nth-child can't do that (it counts DOM
      // position, not visible position, so a filtered-out row would
      // throw the on-screen pattern off). Re-walk just the visible
      // .pub-row elements, in order, every time render() runs (filter,
      // search, or the initial load below) and toggle .pub-row--alt onto
      // every other one.
      var visiblePubIndex = 0;
      document.querySelectorAll('.pub-row').forEach(function (row) {
        if (row.hidden) return;
        row.classList.toggle('pub-row--alt', visiblePubIndex % 2 === 1);
        visiblePubIndex++;
      });
      // A publication year heading has no data-areas/data-search-row of
      // its own -- hide it only when every row under it (up to the next
      // heading) is hidden, so a year with some-but-not-all rows
      // filtered out keeps its heading.
      document.querySelectorAll('.pub-year').forEach(function (heading) {
        var anyVisible = false;
        var sib = heading.nextElementSibling;
        while (sib && !sib.classList.contains('pub-year')) {
          if (!sib.hidden) anyVisible = true;
          sib = sib.nextElementSibling;
        }
        heading.hidden = !anyVisible;
      });
      // Same idea as the .pub-year handling above, for people.html's
      // Core Members / Affiliates groups (direct user request): each
      // group's rows sit in their own [data-people-group-panel] --
      // hide the whole wrapping .research-subsection (its
      // .subsection-toggle heading and .people-group box together)
      // whenever a filter or search leaves nothing visible inside that
      // group, so a heading never sits over an empty section. Walks up
      // via closest() rather than assuming any particular sibling is
      // the heading, so this doesn't care how deep the panel is nested
      // (e.g. Affiliates' extra .rail-scroll-wrap around its rows).
      document.querySelectorAll('[data-people-group-panel]').forEach(function (panel) {
        var anyVisible = Array.prototype.slice.call(panel.querySelectorAll('[data-search-row]'))
          .some(function (row) { return !row.hidden; });
        panel.hidden = !anyVisible;
        var section = panel.closest('.research-subsection');
        if (section) section.hidden = !anyVisible;
      });
      emptyMsgs.forEach(function (msg) {
        var panel = document.getElementById(msg.getAttribute('data-empty-for'));
        if (!panel) return;
        // Follow-up (bug fix): `[data-empty-for]` is a page-wide lookup,
        // but not every page's "no results" message belongs to THIS
        // closure -- events.html's Upcoming/Past lists carry their own
        // [data-empty-for] messages keyed to [data-filter-target] rows,
        // owned by the generic [data-filter-group] block further down
        // this file, not by [data-search-row]/researchExplorer. Before
        // the .area-controls-only guard fix above, this whole render()
        // never ran on events.html at all (early-return stub), so this
        // loop never touched those messages and they stayed at their
        // default `hidden` markup state. Now that render() legitimately
        // runs there too (for Category/search wiring elsewhere on the
        // page), a panel with zero [data-search-row] children isn't
        // this closure's to manage -- skip it so the other mechanism's
        // (correct) hidden state is left alone instead of being
        // clobbered into permanently showing "no results".
        var searchRows = panel.querySelectorAll('[data-search-row]');
        if (!searchRows.length) return;
        if (panel.hidden) { msg.hidden = true; return; }
        var anyVisible = Array.prototype.slice.call(searchRows)
          .some(function (row) { return !row.hidden; });
        msg.hidden = anyVisible;
      });
      // Filtering/search can hide tiles inside a .rp-carousel (or the
      // People/Projects collapsible toggle can reveal one that was
      // measured at width:0 while hidden -- see initTileCarousel()
      // above) -- re-measure every carousel on the page each time this
      // runs so its page count/viewport width/dots stay correct. A
      // no-op on pages with no [data-carousel] elements.
      tileCarousels.forEach(function (c) { c.refresh(); });
    }

    pills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        var area = pill.getAttribute('data-area');
        if (selected.has(area)) selected.delete(area); else selected.add(area);
        render();
      });
    });
    yearPills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        var year = pill.getAttribute('data-year');
        if (selectedYears.has(year)) selectedYears.delete(year); else selectedYears.add(year);
        render();
      });
    });
    rolePills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        var role = pill.getAttribute('data-role');
        if (selectedRoles.has(role)) selectedRoles.delete(role); else selectedRoles.add(role);
        render();
      });
    });
    if (searchInput) searchInput.addEventListener('input', render);

    // Collapsible People/Projects sections on research.html (open by
    // default) and the Filters panel on people.html (collapsed by
    // default -- see people_body in build_all.py) -- same
    // .subsection-toggle/.subsection-caret component itself is wired
    // generically below (outside this closure) so it works on any page,
    // not just ones with area-filter-pills -- see that block for why.
    // Publications has no toggle button, so it's always shown and never
    // touched here.
    render();

    return {
      selectArea: function (area) {
        selected.clear();
        if (area) selected.add(area);
        render();
      },
      refresh: render
    };
  })();

  // Generic collapsible-section toggle (.subsection-toggle/.subsection-
  // caret, keyed off whatever aria-expanded/hidden state the page ships
  // with) -- used for research.html's People/Projects sections and every
  // page's collapsed-by-default "Filters" panel (people.html, research.html,
  // events.html). Deliberately NOT nested inside researchExplorer above:
  // that closure bails out early (a no-op stub) on any page without
  // .area-filter-pill elements -- events.html filters by category pills
  // instead, so its Filters toggle would otherwise never get wired up.
  // researchExplorer.refresh() is a safe no-op via that same stub on
  // pages where it doesn't apply.
  document.querySelectorAll('.subsection-toggle').forEach(function (btn) {
    var panel = document.getElementById(btn.getAttribute('aria-controls'));
    if (!panel) return;
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', String(open));
      panel.hidden = !open;
      researchExplorer.refresh();
    });
  });

  // Open + scroll to a category section or a specific area filter pill
  // from a URL hash, e.g. research.html#publications or
  // research.html#area-panel-cybersecurity -- direct user request: no
  // research area has its own page, so the nav dropdown, footer,
  // homepage research matrix, spotlight "Explore" buttons, and
  // publication titles all deep-link here instead. A bare category name
  // just scrolls to that section as-is; a specific area's id selects
  // only that one filter pill (clearing any others) and scrolls to the
  // controls at the top of the page.
  function openResearchHashTarget() {
    var id = window.location.hash.slice(1);
    if (!id) return;
    if (id === 'people' || id === 'projects' || id === 'publications') {
      var section = document.getElementById(id);
      if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    var pill = document.getElementById(id);
    if (!pill || !pill.classList.contains('area-filter-pill')) return;
    researchExplorer.selectArea(pill.getAttribute('data-area'));
    var controls = document.querySelector('.area-controls');
    if (controls) controls.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  openResearchHashTarget();
  window.addEventListener('hashchange', openResearchHashTarget);

  // People page: compact dropdown menus for the Role/Research Area
  // filters (direct user request -- two full pill rows read as "too
  // big" for what's now two filter dimensions, with room for more
  // later). This is purely presentational -- open/close the menu, show
  // a selected-count badge -- and deliberately doesn't touch
  // researchExplorer above: the pills inside each .filter-dropdown-menu
  // are still ordinary .role-filter-pill/.area-filter-pill buttons that
  // closure already listens to directly, so clicking one both toggles
  // its filter (via researchExplorer's own listener, which runs first
  // since it's bound to the pill itself) and refreshes this button's
  // badge (via the delegated listener below, which runs after as the
  // click bubbles up). No-op on any page without a .filter-dropdown.
  document.querySelectorAll('.filter-dropdown').forEach(function (dd) {
    var toggle = dd.querySelector('.filter-dropdown-toggle');
    var menu = dd.querySelector('.filter-dropdown-menu');
    var countEl = toggle && toggle.querySelector('.filter-dropdown-count');
    if (!toggle || !menu) return;

    function updateCount() {
      if (!countEl) return;
      // :not([data-filter="all"]) excludes single-select filter bars'
      // default "All" pill (events.html's category filter) from the
      // count -- it's always active by default, so counting it would
      // show a permanent "1" badge even when no real filter is applied.
      // Multi-select pills (role/area, no "all" pill at all) are
      // unaffected by this exclusion.
      var n = menu.querySelectorAll('.filter-pill.active:not([data-filter="all"])').length;
      countEl.textContent = String(n);
      countEl.hidden = !n;
    }

    function closeMenu() {
      menu.hidden = true;
      toggle.setAttribute('aria-expanded', 'false');
    }

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var opening = menu.hidden;
      // Only one dropdown open at a time.
      document.querySelectorAll('.filter-dropdown').forEach(function (other) {
        if (other !== dd) {
          var m = other.querySelector('.filter-dropdown-menu');
          var t = other.querySelector('.filter-dropdown-toggle');
          if (m) m.hidden = true;
          if (t) t.setAttribute('aria-expanded', 'false');
        }
      });
      menu.hidden = !opening;
      toggle.setAttribute('aria-expanded', String(opening));
    });

    // A pill click bubbles here after researchExplorer's own listener
    // (bound directly on the pill) has already toggled its .active
    // class, so the count read here is always up to date.
    menu.addEventListener('click', updateCount);
    updateCount();
  });
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.filter-dropdown').forEach(function (dd) {
      if (dd.contains(e.target)) return;
      var menu = dd.querySelector('.filter-dropdown-menu');
      var toggle = dd.querySelector('.filter-dropdown-toggle');
      if (menu) menu.hidden = true;
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.filter-dropdown-menu').forEach(function (m) { m.hidden = true; });
    document.querySelectorAll('.filter-dropdown-toggle').forEach(function (t) { t.setAttribute('aria-expanded', 'false'); });
  });

  // Filter pills (Research: by focus area / Events: by category) -- see
  // filter_pills_html() in generate.py. One filter bar per page today, so
  // this doesn't scope items to a specific bar; it just shows/hides every
  // [data-filter-target] element on the page against whichever pill in
  // [data-filter-group] is active ("all" always shows everything).
  // Follow-up: a .filter-search-input text box (see .search-box in
  // styles.css; used on events.html and research.html so far) filters
  // the same [data-filter-target] rows by their text content -- combined
  // here so a row shows only when it matches BOTH the active category
  // pill AND the search text. Looked up by class, not a page-specific
  // id, so any page can drop the same markup in without a main.js
  // change; a filter bar with no search box on the page just gets an
  // empty `query` and behaves exactly as it did before search existed.
  document.querySelectorAll('[data-filter-group]').forEach(function (bar) {
    var buttons = Array.prototype.slice.call(bar.querySelectorAll('.filter-pill'));
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-filter-target]'));
    var searchInput = document.querySelector('.filter-search-input');
    var emptyMsgs = Array.prototype.slice.call(document.querySelectorAll('[data-empty-for]'));

    function applyFilters() {
      var activeBtn = bar.querySelector('.filter-pill.active');
      var activeVal = activeBtn ? activeBtn.getAttribute('data-filter') : 'all';
      var query = searchInput ? searchInput.value.trim().toLowerCase() : '';
      items.forEach(function (item) {
        var matchesCategory = (activeVal === 'all' || item.getAttribute('data-filter-target') === activeVal);
        var matchesSearch = !query || item.textContent.toLowerCase().indexOf(query) !== -1;
        item.style.display = (matchesCategory && matchesSearch) ? '' : 'none';
      });
      // Each scrollable list (see events_body's .events-scroll boxes) has
      // its own "no results" message keyed by the list's id -- shown only
      // when every row inside that specific list is hidden, so an empty
      // Upcoming list doesn't also blank out a non-empty Past list.
      emptyMsgs.forEach(function (msg) {
        var list = document.getElementById(msg.getAttribute('data-empty-for'));
        if (!list) return;
        var anyVisible = Array.prototype.slice.call(list.querySelectorAll('[data-filter-target]'))
          .some(function (item) { return item.style.display !== 'none'; });
        msg.hidden = anyVisible;
      });
    }

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        buttons.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        applyFilters();
      });
    });
    if (searchInput) {
      searchInput.addEventListener('input', applyFilters);
    }
  });

  // Signal ticker -- NYSE-tape style: streams continuously to the left,
  // stops the instant the pointer enters the lane (hover-to-pause), and
  // is click-and-drag scrubbable in either direction while paused.
  // ticker_track_html() in generate.py renders the item list twice back
  // to back; auto-scroll and drag both wrap at the halfway point of the
  // doubled track so the loop has no visible seam.
  //
  // Driven by a CSS `transform: translateX()` on .ticker-track-inner, NOT
  // .ticker-viewport.scrollLeft. An earlier version used scrollLeft with
  // overflow-x:auto, which read as fully static on real mobile Safari --
  // iOS hands scrollLeft-driven elements to its native momentum-scroll
  // compositor, which can silently ignore programmatic scrollLeft writes
  // until the user has physically touched the element. transform sidesteps
  // that whole class of bug: .ticker-viewport is overflow:hidden (no native
  // scroll at all) and dragging/auto-advance both just move the track via
  // its own `offset` state, so there's nothing for the browser's scroll
  // compositor to intercept.
  document.querySelectorAll('.ticker-viewport').forEach(function (vp) {
    var track = vp.querySelector('.ticker-track-inner');
    if (!track) return;

    var half = 0;
    function measure() { half = track.scrollWidth / 2; }
    measure();
    window.addEventListener('resize', measure);

    var offset = 0; // px the track has moved left, wraps at `half`
    var hovered = false, isDown = false, moved = false, startX, startOffset;
    var SPEED = 0.5; // px/frame -- a slow, readable tape, not a marquee blur

    function wrap(x) {
      if (half <= 0) return x;
      return ((x % half) + half) % half;
    }
    function render() {
      track.style.transform = 'translateX(' + (-offset) + 'px)';
    }

    function frame() {
      if (!hovered && !isDown && half > 0) {
        offset = wrap(offset + SPEED);
        render();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);

    function pause() { hovered = true; }
    function resume() {
      hovered = false;
      isDown = false;
      vp.classList.remove('dragging');
    }
    // Only wire up hover-to-pause on devices with a REAL pointing device
    // (mouse/trackpad). This turned out to be the actual "ticker static on
    // mobile" bug: touching the ticker fires touchstart/touchend as
    // expected, but mobile browsers then dispatch synthetic compatibility
    // mouseover/mouseenter events afterward (for sites that only listen for
    // mouse events) -- with no matching mouseleave to follow, since there's
    // no real mouse to move away. That leaves `hovered` stuck true forever
    // after the FIRST tap, permanently freezing the tape. matchMedia
    // '(hover: hover)' is false on touch-only devices, so this skips
    // binding mouse hover-pause there entirely and leaves pause/resume to
    // the touchstart/touchend/touchcancel handlers below instead.
    if (window.matchMedia && window.matchMedia('(hover: hover)').matches) {
      vp.addEventListener('mouseenter', pause);
      vp.addEventListener('mouseleave', resume);
    }

    vp.addEventListener('mousedown', function (e) {
      isDown = true; moved = false;
      vp.classList.add('dragging');
      startX = e.pageX;
      startOffset = offset;
    });
    vp.addEventListener('mouseup', function () {
      isDown = false;
      vp.classList.remove('dragging');
    });
    vp.addEventListener('mousemove', function (e) {
      if (!isDown) return;
      e.preventDefault();
      var walk = e.pageX - startX;
      if (Math.abs(walk) > 5) moved = true;
      offset = wrap(startOffset - walk);
      render();
    });

    // Touch: pause+drag-scrub in one set of handlers (there's no native
    // touch-scroll to fall back on anymore now that .ticker-viewport is
    // overflow:hidden, so this replaces what the browser used to provide
    // for free). No separate touchcancel quirk to handle here either --
    // that was specifically a scrollLeft/momentum-scroll interaction.
    vp.addEventListener('touchstart', function (e) {
      hovered = true; isDown = true; moved = false;
      startX = e.touches[0].pageX;
      startOffset = offset;
    }, { passive: true });
    vp.addEventListener('touchmove', function (e) {
      if (!isDown) return;
      var walk = e.touches[0].pageX - startX;
      if (Math.abs(walk) > 5) moved = true;
      offset = wrap(startOffset - walk);
      render();
    }, { passive: true });
    function touchEnd() { hovered = false; isDown = false; }
    vp.addEventListener('touchend', touchEnd);
    vp.addEventListener('touchcancel', touchEnd);

    vp.addEventListener('click', function (e) {
      if (moved) { e.preventDefault(); e.stopPropagation(); }
    }, true);
  });

  // Homepage "Research Spotlight" -- one slide visible at a time, split
  // across TWO tracks that stay in sync (spotlight_html() in generate.py
  // renders both, hidden via CSS except .is-active): .spotlight-media-slide
  // (just the image) and .spotlight-slide (title/meta/summary/actions).
  // The dots and prev/next arrows now live in .spotlight-footer, a
  // persistent bottom bar in the .spotlight-card -- see the big comment
  // in styles.css/generate.py for the Bloomberg-card layout this became.
  // Auto-advances on a timer, pauses on hover so it doesn't flip out from
  // under someone reading, the .spotlight-dot buttons jump straight to a
  // slide, the .spotlight-prev/.spotlight-next arrows step one at a time,
  // and .spotlight-pause is a manual pause/play toggle -- a manual pause
  // sticks (auto-advance stays off) through hover-unhover and further
  // dot/arrow clicks, until the user un-pauses.
  document.querySelectorAll('[data-spotlight]').forEach(function (widget) {
    var mediaSlides = Array.prototype.slice.call(widget.querySelectorAll('.spotlight-media-slide'));
    var textSlides = Array.prototype.slice.call(widget.querySelectorAll('.spotlight-slide'));
    var dots = Array.prototype.slice.call(widget.querySelectorAll('.spotlight-dot'));
    if (textSlides.length < 2) return; // nothing to slide between

    var AUTO_MS = 5000;
    var FADE_MS = 600; // must match .spotlight-media-slide/.spotlight-slide's transition-duration in styles.css
    var current = 0;
    var timer = null;
    var transitioning = false;
    var userPaused = false;

    // Crossfades rather than hard-cutting: fade the current slide out,
    // THEN (once that finishes) swap which slide is .is-active and fade
    // the new one in. Sequential rather than a true overlapping crossfade,
    // so the two slides never visually double-expose mid-transition. Each
    // track holds its own slides stacked in the same CSS Grid area (see
    // styles.css), so each track's height is always its own tallest
    // slide's height regardless of which one is active/visible -- that's
    // what keeps this from resizing the whole lead grid on every swap. The
    // media and text tracks are driven by the SAME index, one call each,
    // so they always change together even though they're separate DOM
    // subtrees now.
    function swapTrack(slides, next) {
      var oldSlide = slides[current];
      var newSlide = slides[next];
      oldSlide.classList.remove('is-visible');
      setTimeout(function () {
        oldSlide.classList.remove('is-active');
        newSlide.classList.add('is-active');
        void newSlide.offsetWidth; // force layout so the opacity transition below actually runs
        newSlide.classList.add('is-visible');
      }, FADE_MS);
    }
    function show(i) {
      var next = (i % textSlides.length + textSlides.length) % textSlides.length;
      if (next === current || transitioning) return;
      transitioning = true;
      swapTrack(mediaSlides, next);
      swapTrack(textSlides, next);
      setTimeout(function () {
        current = next;
        dots.forEach(function (d, idx) { d.classList.toggle('is-active', idx === current); });
        setTimeout(function () { transitioning = false; }, FADE_MS);
      }, FADE_MS);
    }
    function stopAuto() { if (timer) clearInterval(timer); }
    // startAuto() is the single gate for "should the timer be running" --
    // it refuses to (re)start the timer while userPaused is true, so every
    // caller (dot click, arrow click, hover-unhover) can call it
    // unconditionally without needing to know about pause state itself.
    function startAuto() {
      stopAuto();
      if (userPaused) return;
      timer = setInterval(function () { show(current + 1); }, AUTO_MS);
    }

    dots.forEach(function (d, idx) {
      d.addEventListener('click', function () { show(idx); startAuto(); });
    });

    var prevBtn = widget.querySelector('[data-spotlight-prev]');
    var nextBtn = widget.querySelector('[data-spotlight-next]');
    if (prevBtn) prevBtn.addEventListener('click', function () { show(current - 1); startAuto(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { show(current + 1); startAuto(); });

    // Title/summary height reservation is a flat CSS min-height + 2-line
    // clamp (see styles.css) instead of a JS-measured "tallest real slide"
    // value -- a prior version of this measured each slide's natural
    // scrollHeight and reserved the max, which correctly held the button row
    // steady but still left a visible gap under shorter slides whenever any
    // ONE slide needed a 3rd line. A flat clamp has no such gap since it
    // never varies by content, at the cost of truncating (with an ellipsis)
    // any title/summary long enough to need a 3rd line. No JS measurement
    // needed for that, and the prev/next arrows no longer need JS
    // positioning either now that they're static flex items in
    // .spotlight-footer instead of floating beside the image.

    var pauseBtn = widget.querySelector('[data-spotlight-pause]');
    function setPaused(p) {
      userPaused = p;
      if (pauseBtn) {
        pauseBtn.classList.toggle('is-paused', p);
        pauseBtn.setAttribute('aria-pressed', p ? 'true' : 'false');
        pauseBtn.setAttribute('aria-label', p ? 'Resume slideshow' : 'Pause slideshow');
      }
      if (p) { stopAuto(); } else { startAuto(); }
    }
    if (pauseBtn) pauseBtn.addEventListener('click', function () { setPaused(!userPaused); });

    // Only pause-on-hover for a real pointing device. On touch-only devices,
    // mobile browsers fire a synthetic mouseenter (with no matching
    // mouseleave) after ANY tap in the widget -- binding this unconditionally
    // permanently freezes the slideshow after the very first touch, same bug
    // class as the signal ticker (see ticker section above / project notes).
    // mouseleave only restarts the timer if the user hasn't manually paused
    // -- otherwise hovering-then-unhovering would silently cancel a pause.
    if (window.matchMedia && window.matchMedia('(hover: hover)').matches) {
      widget.addEventListener('mouseenter', stopAuto);
      widget.addEventListener('mouseleave', function () { if (!userPaused) startAuto(); });
    }

    startAuto();
  });

  // Homepage Hub News rail -- match its scroll box's height to
  // .lead-secondary (What We Do / Join Us / Research Areas) so the two
  // hero side-columns end at the same height, same as before Research
  // Areas swapped from this rail over to .lead-secondary.
  //
  // This can't be done in CSS alone: a `.lead-grid` column can be told
  // to stretch to match its tallest sibling (`align-items:stretch`),
  // but that only works when the *shorter* column is the one being
  // grown -- here it's the reverse, the news list is the naturally
  // taller one and needs to be *capped* to its sibling's height, and
  // CSS has no "shrink this to match that" primitive (a flex:1 child
  // with no explicit bound just reports its own full content height
  // back into the grid's row-sizing pass, so the row balloons to fit
  // the whole list instead of clipping it -- see the long comment on
  // .rail-scroll-wrap in styles.css for the full autopsy of that first
  // attempt). Measuring both elements' real rendered height and setting
  // an explicit max-height in px is the only way to actually cap one to
  // the other.
  (function () {
    // Measure the actual content bottom (the Research Areas matrix),
    // not .lead-secondary's own box -- .lead-grid now stretches all
    // three columns to the tallest one (see styles.css), so
    // .lead-secondary's rendered box can be taller than its content;
    // using that box's bottom as the target would size the news list
    // to match the *stretched* column instead of where its content
    // actually ends.
    var left = document.querySelector('.research-matrix--rail');
    var wrap = document.querySelector('.lead-rail .rail-scroll-wrap');
    var scroll = document.querySelector('.lead-rail .rail-scroll');
    if (!left || !wrap || !scroll) return;

    function sync() {
      // Below the 3-column breakpoint (see styles.css) the hero columns
      // stack into separate rows instead of sharing one, so there's
      // nothing to match heights against -- clear any inline override
      // and let the CSS default (.rail-scroll's own max-height) apply.
      if (window.matchMedia('(max-width: 1150px)').matches) {
        scroll.style.maxHeight = '';
        return;
      }
      // Follow-up (direct user request): the news list used to stop
      // ~25px short of the target, reserved for a closing divider
      // below the scroll box that's since been removed (it just added
      // dead space between where the list visibly faded out and where
      // the vertical dividers/Spotlight actually end) -- the list now
      // gets the full available space, so its fade-out lands flush
      // with the vertical partition's bottom.
      var target = left.getBoundingClientRect().bottom;
      var top = wrap.getBoundingClientRect().top;
      var available = target - top;
      if (available > 40) scroll.style.maxHeight = available + 'px';
    }

    sync();
    window.addEventListener('resize', sync);
    // Re-sync after web fonts finish loading -- a font swap can change
    // .lead-secondary's wrapped line count (and so its height) after
    // the measurement above already ran.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(sync);
    }
  })();

  // Events page: cap Upcoming/Past Events to a 5-row preview, direct
  // user request "similar to what we see in the hub news section" --
  // same fixed-height/fade-out/scroll idea as syncHubNewsHeight above,
  // but sized to a row COUNT rather than matched against a sibling
  // column (there's no sibling to match on this page). Event rows
  // aren't a fixed height -- a wrapped title, or a shaded even row's
  // slightly different box, can shift things by a few px -- so this
  // measures the 5th row's actual rendered bottom edge rather than
  // multiplying an assumed per-row height, the same "measure, don't
  // guess" approach as that other function. 5 or fewer rows total
  // needs no cap at all; the CSS max-height on .events-scroll (see
  // styles.css) is left as the pre-JS/no-JS fallback either way.
  (function () {
    function capToRows(listId, n) {
      var list = document.getElementById(listId);
      if (!list) return;
      function sync() {
        var rows = Array.prototype.slice.call(list.children);
        if (rows.length <= n) { list.style.maxHeight = ''; return; }
        var top = list.getBoundingClientRect().top;
        var bottom = rows[n - 1].getBoundingClientRect().bottom;
        list.style.maxHeight = (bottom - top) + 'px';
      }
      sync();
      window.addEventListener('resize', sync);
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(sync);
      }
    }
    capToRows('upcoming-events-list', 5);
    capToRows('past-events-list', 5);
  })();

  // Homepage calendar -- pages between pre-rendered month panels (one
  // per month that actually has an event; see calendar_widget_html() in
  // generate.py) with prev/next, wrapping around at either end.
  document.querySelectorAll('.cal-widget').forEach(function (widget) {
    var panels = Array.prototype.slice.call(widget.querySelectorAll('.cal-month'));
    var title = widget.querySelector('.cal-title');
    if (!panels.length) return;
    var current = panels.findIndex(function (p) { return p.classList.contains('active'); });
    if (current < 0) current = 0;
    function show(i) {
      panels[current].classList.remove('active');
      current = (i % panels.length + panels.length) % panels.length;
      panels[current].classList.add('active');
      if (title) title.textContent = panels[current].dataset.label;
    }
    widget.querySelectorAll('.cal-nav').forEach(function (btn) {
      btn.addEventListener('click', function () {
        show(current + parseInt(btn.dataset.dir, 10));
      });
    });
  });

  // Newsletter signup -- submits to The Phronesis Institute's live subscribe
  // API (same endpoint their own site uses: POST /api/subscribe on
  // phronesisresearch.org, which is CORS-open and also syncs to their
  // Substack). This duplicates their real subscribe functionality here
  // rather than just linking out.
  var PHRONESIS_SUBSCRIBE_URL = 'https://phronesisresearch.org/api/subscribe';

  document.querySelectorAll('.newsletter-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var input = form.querySelector('input[type="email"]');
      var button = form.querySelector('button');
      var email = input.value.trim();

      var existing = form.parentElement.querySelector('.newsletter-message');
      if (existing) existing.remove();

      function showMessage(text, type) {
        var msg = document.createElement('p');
        msg.className = 'newsletter-message newsletter-message--' + type;
        msg.textContent = text;
        form.insertAdjacentElement('afterend', msg);
      }

      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showMessage('Please enter a valid email address.', 'error');
        return;
      }

      var originalText = button.textContent;
      button.disabled = true;
      button.textContent = 'Subscribing…';

      fetch(PHRONESIS_SUBSCRIBE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      })
        .then(function (res) {
          return res.json().then(function (data) { return { ok: res.ok, data: data }; });
        })
        .then(function (result) {
          if (result.ok && result.data.success) {
            showMessage(result.data.message || 'Successfully subscribed!', 'success');
            form.reset();
          } else {
            showMessage(result.data.error || 'Subscription failed. Please try again.', 'error');
          }
        })
        .catch(function () {
          showMessage('Network error. Please try again.', 'error');
        })
        .finally(function () {
          button.disabled = false;
          button.textContent = originalText;
        });
    });
  });
});
