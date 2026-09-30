"""Header navigation (desktop + phone menu) and the homepage's widgets."""
import re

import pytest

from conftest import IS_LIVE, PAGES, url


# ---------------------------------------------------------------- header

def test_desktop_nav_links_open_their_pages(site):
    page = site.open()
    links = page.locator(".primary-nav > ul > li > a")
    assert links.count() >= 4, "expected Home/Research/Events/People in the header"
    for i in range(links.count()):
        link = links.nth(i)
        label = link.inner_text().strip()
        with page.expect_navigation():
            link.click()
        assert page.url.rstrip("/") != "", label
        assert page.locator("header.site-header").is_visible(), f"'{label}' led to a page without the site header"
        page.go_back()


def test_mobile_menu_opens_and_closes_every_way(site):
    page = site.open("", "mobile")
    nav = page.locator("nav.primary-nav")
    toggle = page.locator(".nav-toggle")

    def is_open():
        return "open" in (nav.get_attribute("class") or "")

    assert toggle.is_visible(), "no menu button on phones"
    # (The open drawer covers the hamburger itself, so the X in the same
    # spot is the button-based way to close it.)
    for close in ("x-button", "backdrop", "escape"):
        toggle.click()
        page.wait_for_timeout(250)
        assert is_open(), "menu didn't open"
        assert page.evaluate("document.body.classList.contains('nav-open')"), "page behind the menu isn't scroll-locked"
        if close == "x-button":
            page.locator(".nav-close").click()
        elif close == "backdrop":
            page.mouse.click(15, 400)  # left of the right-hand drawer
        else:
            page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        assert not is_open(), f"menu didn't close via {close}"

    toggle.click()
    page.wait_for_timeout(250)
    with page.expect_navigation():
        nav.get_by_role("link", name=re.compile("People", re.I)).first.click()
    assert "/people" in page.url


def test_header_subscribe_button_reaches_signup(site, vp):
    page = site.open("research/", vp)
    with page.expect_navigation():
        page.locator(".header-actions a", has_text=re.compile("Subscribe", re.I)).first.click()
    assert page.url.endswith("#subscribe")
    assert page.locator("#subscribe .newsletter-form").first.is_visible()


# ---------------------------------------------------------------- homepage

def test_spotlight_slideshow_controls(site, vp):
    page = site.open("", vp)
    widget = page.locator("[data-spotlight]")
    pause = widget.locator("[data-spotlight-pause]")
    pause.click()  # stop autoplay so it can't move a slide mid-test
    assert pause.get_attribute("aria-pressed") == "true"

    def active():
        return widget.locator(".spotlight-slide").evaluate_all(
            "els => els.findIndex(e => e.classList.contains('is-active'))")

    # Each change fades out, swaps, fades in, then briefly ignores clicks
    # (FADE_MS = 600 in main.js, twice), so give it time to settle.
    settle = 1500
    start = active()
    widget.locator("[data-spotlight-next]").click()
    page.wait_for_timeout(settle)
    assert active() != start, "Next didn't change the slide"
    widget.locator("[data-spotlight-prev]").click()
    page.wait_for_timeout(settle)
    assert active() == start, "Previous didn't go back"
    dots = widget.locator(".spotlight-dot")
    if dots.count() > 1:
        dots.last.click()
        page.wait_for_timeout(settle)
        assert active() == dots.count() - 1, "clicking a dot didn't jump to its slide"


def test_calendar_pages_between_months(site):
    page = site.open()
    title = page.locator(".cal-widget .cal-title")
    first = title.inner_text()
    if page.locator(".cal-widget .cal-month").count() < 2:
        pytest.skip("only one month has events")
    page.locator('.cal-widget .cal-nav[data-dir="1"]').click()
    assert title.inner_text() != first, "calendar Next didn't change month"
    page.locator('.cal-widget .cal-nav[data-dir="-1"]').click()
    assert title.inner_text() == first, "calendar Previous didn't go back"


def test_policy_ticker_has_items(site):
    page = site.open()
    assert page.locator(".ticker-track-inner > *").count() > 0, "policy ticker is empty"


MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def _news_key(text):
    m = re.search(r"([A-Za-z]{3})[a-z.]*\s+(?:(\d{1,2}),\s+)?(\d{4})", text)
    return (int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2) or 0)) if m else None


def test_hub_news_is_newest_first(site):
    page = site.open()
    dates = page.locator(".lead-rail .rail-scroll .date").all_inner_texts()
    assert dates, "Hub News rail is empty"
    keys = [k for k in (_news_key(d) for d in dates) if k]
    assert keys == sorted(keys, reverse=True), "Hub News isn't sorted newest first: " + ", ".join(dates)


def test_newsletter_form_rejects_a_bad_email(site, vp):
    page = site.open("", vp)
    form = page.locator("#subscribe .newsletter-form")
    form.locator('input[type="email"]').fill("someone@nowhere")  # passes the browser's check, not ours
    form.locator("button").click()
    msg = page.locator("#subscribe .newsletter-message--error")
    msg.wait_for(timeout=3000)
    assert "valid email" in msg.inner_text().lower()


@pytest.mark.skipif(not IS_LIVE, reason="the subscribe API only accepts requests from the live domain")
def test_newsletter_endpoint_accepts_requests_from_this_site(site):
    """The Sept. 2026 "Network error" bug: the form posted to an address
    that didn't exist. This sends the form's exact kind of request from a
    techpolicyhub.org page -- with NO email, so nobody gets subscribed --
    and expects the service's normal "invalid email" answer back."""
    page = site.open()
    js = page.request.get(url("assets/js/main.js")).text()
    endpoint = re.search(r"PHRONESIS_SUBSCRIBE_URL\s*=\s*'([^']+)'", js).group(1)
    result = page.evaluate(
        """async (u) => {
             try {
               const r = await fetch(u, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
               let data = null; try { data = await r.json(); } catch (e) {}
               return { status: r.status, data };
             } catch (e) { return { error: String(e) }; }
           }""",
        endpoint,
    )
    assert "error" not in result, (
        f"The browser couldn't reach the newsletter service at {endpoint} from this site "
        f"({result.get('error')}) -- visitors trying to subscribe will see 'Network error'. "
        "Check the address, and that the service's CORS settings allow https://techpolicyhub.org.")
    assert result["status"] == 400 and result["data"] and result["data"].get("success") is False, (
        f"Unexpected answer from the newsletter service: {result}")
