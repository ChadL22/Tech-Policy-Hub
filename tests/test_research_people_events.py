"""Filters, search, collapsible sections, carousels, the project pop-up,
people cards and photos, and the events list."""
import re

import pytest

from conftest import open_filter_dropdown, visible_rows


def _area_keys(page):
    return page.locator(".area-filter-pill").evaluate_all("els => els.map(e => e.dataset.area)")


# ---------------------------------------------------------------- shared filter checks

@pytest.mark.parametrize("path", ["research/", "people/"])
def test_research_area_filter(site, vp, path):
    page = site.open(path, vp)
    everyone = len(visible_rows(page))
    keys = _area_keys(page)
    assert len(keys) >= 4, "Research Area filter has no options"
    for key in keys:
        dd = open_filter_dropdown(page, "Research Area")
        pill = dd.locator(f'.area-filter-pill[data-area="{key}"]')
        pill.click()
        rows = visible_rows(page)
        assert rows, f"filtering by {key} left nothing visible"
        wrong = [r["text"][:60] for r in rows if key not in r["areas"]]
        assert not wrong, f"filtering by {key} still shows rows from other areas: {wrong[:5]}"
        assert dd.locator(".filter-dropdown-count").inner_text().strip() == "1", "selected-count badge didn't update"
        open_filter_dropdown(page, "Research Area")
        pill.click()  # unselect
        assert len(visible_rows(page)) == everyone, f"clearing the {key} filter didn't bring everything back"
        page.keyboard.press("Escape")


@pytest.mark.parametrize("path,query,expect", [
    ("research/", "Temporal Aspects", "Temporal Aspects"),
    ("people/", "Patrick", "Patrick Parham"),
])
def test_search_box(site, vp, path, query, expect):
    page = site.open(path, vp)
    everyone = len(visible_rows(page))
    search = page.locator(".filter-search-input")
    search.fill(query)
    rows = visible_rows(page)
    assert rows and all(query.lower() in r["text"].lower() for r in rows), f"searching '{query}' showed non-matching rows"
    assert any(expect in r["text"] for r in rows), f"searching '{query}' didn't show {expect}"
    search.fill("zzzz-no-such-thing")
    assert not visible_rows(page)
    assert page.locator(".list-empty:not([hidden])").count() >= 1, "no 'nothing matches' message for an empty search"
    search.fill("")
    assert len(visible_rows(page)) == everyone


# ---------------------------------------------------------------- research page

def test_publication_year_filter(site):
    page = site.open("research/")
    years = page.locator(".year-filter-pill").evaluate_all("els => els.map(e => e.dataset.year)")
    assert years, "no publication years to filter by"
    dd = open_filter_dropdown(page, "Year")
    dd.locator(f'.year-filter-pill[data-year="{years[0]}"]').click()
    pubs = visible_rows(page, ".pub-row")
    assert pubs and all(p["year"] == years[0] for p in pubs), f"Year {years[0]} filter showed other years"


def test_collapsible_sections(site, vp):
    page = site.open("research/", vp)
    for section in ("people", "projects"):
        toggle = page.locator(f'.subsection-toggle[aria-controls="{section}-panel"]')
        panel = page.locator(f"#{section}-panel")
        toggle.click()
        assert toggle.get_attribute("aria-expanded") == "false" and not panel.is_visible(), f"{section} didn't collapse"
        toggle.click()
        assert toggle.get_attribute("aria-expanded") == "true" and panel.is_visible(), f"{section} didn't expand"


@pytest.mark.parametrize("carousel", ["people-panel", "projects-panel"])
def test_carousel_arrows(site, vp, carousel):
    page = site.open("research/", vp)
    root = page.locator(f"#{carousel}")
    nxt, prev = root.locator(".rp-carousel-next"), root.locator(".rp-carousel-prev")
    if nxt.is_disabled():
        pytest.skip("everything fits on one page")

    def first_visible_tile():
        return root.evaluate("""r => { const v = r.querySelector('.rp-carousel-viewport').getBoundingClientRect();
            const t = Array.from(r.querySelectorAll('.rp-tile')).find(t => !t.hidden && t.getBoundingClientRect().left >= v.left - 2);
            return t ? t.textContent.trim().slice(0, 40) : null; }""")

    start = first_visible_tile()
    nxt.click()
    page.wait_for_timeout(600)
    assert first_visible_tile() != start, "Next arrow didn't move the carousel"
    prev.click()
    page.wait_for_timeout(600)
    assert first_visible_tile() == start, "Previous arrow didn't move back"


def test_project_popup(site, vp):
    page = site.open("research/", vp)
    tile = page.locator("[data-project-trigger]").first
    title = tile.locator("h3").inner_text().strip()
    teaser = tile.locator(".rp-desc").inner_text().strip()
    modal = page.locator(".project-modal")

    closes = ["x-button", "escape"] + (["backdrop"] if vp == "desktop" else [])  # full-screen on phones
    for how in closes:
        tile.click()
        modal.wait_for(state="visible")
        assert modal.locator(".project-modal-title").inner_text().strip() == title
        assert len(modal.locator(".project-modal-desc").inner_text()) >= len(teaser), "pop-up doesn't show the full description"
        assert page.evaluate("document.body.classList.contains('project-modal-open')")
        if how == "x-button":
            modal.locator(".project-modal-close").click()
        elif how == "escape":
            page.keyboard.press("Escape")
        else:
            page.mouse.click(8, 8)
        modal.wait_for(state="hidden")
        assert not page.evaluate("document.body.classList.contains('project-modal-open')")
    for img in modal.locator(".project-modal-media img").all():
        assert img.evaluate("i => i.complete && i.naturalWidth > 0")


def test_area_deep_link_preselects_filter(site):
    page = site.open("research/#area-panel-cybersecurity")
    page.wait_for_timeout(500)
    assert page.locator("#area-panel-cybersecurity").get_attribute("aria-pressed") == "true"
    rows = visible_rows(page)
    assert rows and all("cybersecurity" in r["areas"] for r in rows)


# ---------------------------------------------------------------- people page

def test_affiliates_open_on_desktop_collapsed_on_phones(site, vp):
    page = site.open("people/", vp)
    expanded = page.locator('[aria-controls="affiliates-panel"]').get_attribute("aria-expanded")
    assert expanded == ("true" if vp == "desktop" else "false")


def test_search_opens_a_collapsed_section_with_matches(site):
    """On phones Affiliates starts collapsed; searching for an affiliate
    must still show them (and clearing the search closes it again)."""
    page = site.open("people/", "mobile")
    toggle = page.locator('[aria-controls="affiliates-panel"]')
    assert toggle.get_attribute("aria-expanded") == "false"
    page.locator(".filter-search-input").fill("Patrick")
    assert page.locator("#person-patrick-parham").is_visible(), "a matching affiliate stayed hidden in the collapsed section"
    page.locator(".filter-search-input").fill("")
    assert toggle.get_attribute("aria-expanded") == "false", "section didn't close again after clearing the search"


def test_phone_bio_card(site):
    page = site.open("people/", "mobile")
    row = page.locator(".person-row").first
    body = row.locator(".person-body")
    row.locator(".person-page-next--bio").click()
    page.wait_for_timeout(700)
    assert body.evaluate("b => b.scrollLeft") > 50, "'Bio' didn't move to the bio card"
    assert row.locator(".person-content h3").is_visible()
    row.locator(".person-page-next--back").click()
    page.wait_for_timeout(700)
    assert body.evaluate("b => b.scrollLeft") < 5, "back arrow didn't return to the photo"


def test_people_photos(site, vp):
    """Every headshot loads, and none shows the "no photo yet" diagonal
    stripes around it (see has-photo / --photo-fill in styles.css)."""
    page = site.open("people/", vp)
    toggle = page.locator('[aria-controls="affiliates-panel"]')
    if toggle.get_attribute("aria-expanded") == "false":
        toggle.click()
    page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
    page.wait_for_function("Array.from(document.querySelectorAll('.rp-tile-photo-img')).every(i => i.complete)")
    boxes = page.locator(".rp-tile-photo--person").evaluate_all("""els => els.map(b => {
        const img = b.querySelector('img.rp-tile-photo-img');
        return { name: (b.closest('.person-row') || b).querySelector('h3')?.textContent.trim(),
                 hasImg: !!img, loaded: img ? img.naturalWidth > 0 : null,
                 marked: b.classList.contains('has-photo'),
                 stripes: getComputedStyle(b, '::before').content };
      })""")
    problems = []
    for b in boxes:
        if not b["hasImg"]:
            continue
        if not b["loaded"]:
            problems.append(f"{b['name']}: photo didn't load")
        if not b["marked"] or b["stripes"] not in ("none", "normal"):
            problems.append(f"{b['name']}: placeholder stripes showing behind a real photo")
    assert not problems, "\n".join(problems)


# ---------------------------------------------------------------- events page

def test_event_category_filter(site, vp):
    page = site.open("events/", vp)
    everyone = len(visible_rows(page, "[data-filter-target]"))
    cats = page.locator("[data-filter-group] .filter-pill").evaluate_all("els => els.map(e => e.dataset.filter)")
    for cat in [c for c in cats if c != "all"]:
        open_filter_dropdown(page, "")
        page.locator(f'[data-filter-group] .filter-pill[data-filter="{cat}"]').click()
        rows = visible_rows(page, "[data-filter-target]")
        assert all(r["target"] == cat for r in rows), f"'{cat}' filter shows other categories"
        page.keyboard.press("Escape")
    open_filter_dropdown(page, "")
    page.locator('[data-filter-group] .filter-pill[data-filter="all"]').click()
    assert len(visible_rows(page, "[data-filter-target]")) == everyone


def test_event_lists_and_calendar_links(site):
    page = site.open("events/")
    assert page.locator("#upcoming-events-list, #past-events-list").count() == 2
    assert page.locator('a[href$="events.ics"]').count() >= 1, "no 'add to calendar' link"
