"""Every page loads cleanly, and every link on the site goes somewhere."""
import os
import re
from urllib.parse import urldefrag, urljoin, urlparse

import pytest

from conftest import IS_LIVE, LIVE_ORIGIN, PAGES, SITE_URL, load_all_images, url


@pytest.mark.parametrize("path", PAGES, ids=lambda p: p or "home")
def test_page_loads_cleanly(site, vp, path):
    page = site.open(path, vp)
    assert page.title().strip(), "page has no <title>"
    assert page.locator("header.site-header").is_visible(), "site header missing"
    assert page.locator("footer").first.is_visible(), "footer missing"

    broken = load_all_images(page)
    assert not broken, "Images that failed to load:\n  " + "\n  ".join(broken)

    # Nothing wider than the screen -- sideways scrolling on a phone is
    # the most common way a layout change quietly breaks mobile.
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    assert overflow <= 1, f"page is {overflow}px wider than the {vp} viewport"
    # (Errors seen while loading are checked when the test ends -- see Watch.)


def test_admin_page_loads(site):
    page = site.open("admin/")
    assert page.locator("#connect-wrap").is_visible(), "Content Manager sign-in screen didn't render"


def test_calendar_feed_is_valid(site):
    page = site.open()
    resp = page.request.get(url("events.ics"))
    assert resp.status == 200
    body = resp.text()
    assert body.startswith("BEGIN:VCALENDAR") and "END:VCALENDAR" in body, "events.ics isn't a valid calendar file"
    assert body.count("BEGIN:VEVENT") == body.count("END:VEVENT") >= 1


# ---------------------------------------------------------------- links

def _to_site(href):
    """Links to https://techpolicyhub.org/... (and the webcal:// calendar
    link) count as this site's own; point them at SITE_URL so a local
    test run checks the local copy."""
    if href.startswith("webcal://"):
        href = "https://" + href[len("webcal://"):]
    if href.startswith(LIVE_ORIGIN):
        href = urljoin(SITE_URL, href[len(LIVE_ORIGIN):].lstrip("/"))
    return href


@pytest.fixture(scope="module")
def all_links(browser):
    """Every link on every page, as {absolute_url: [pages it appears on]}."""
    ctx = browser.new_context()
    page = ctx.new_page()
    found = {}
    for path in PAGES:
        page.goto(url(path), wait_until="load")
        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(a => a.getAttribute('href'))")
        for h in hrefs:
            if not h or h.startswith(("mailto:", "tel:", "javascript:")):
                continue
            absolute = _to_site(urljoin(url(path), h))
            found.setdefault(absolute, []).append("/" + path)
    ctx.close()
    return found


def test_internal_links_and_anchors_resolve(browser, all_links):
    """Every link to this site returns a page, and every #anchor exists on
    the page it points to (e.g. people/#person-..., research/#area-panel-...)."""
    ctx = browser.new_context()
    html_cache, problems = {}, []
    base = urlparse(SITE_URL).netloc
    for link, pages in sorted(all_links.items()):
        if urlparse(link).netloc != base:
            continue
        target, fragment = urldefrag(link)
        if target not in html_cache:
            resp = ctx.request.get(target)
            html_cache[target] = resp.text() if resp.ok else None
            if not resp.ok:
                problems.append(f"HTTP {resp.status}: {link} (linked from {', '.join(sorted(set(pages)))})")
        body = html_cache[target]
        if fragment and body is not None and not re.search(r'\bid="%s"' % re.escape(fragment), body):
            problems.append(f"missing anchor #{fragment} on {target} (linked from {', '.join(sorted(set(pages)))})")
    ctx.close()
    assert not problems, "Broken internal links:\n  " + "\n  ".join(problems)


CHROME_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


@pytest.mark.skipif(not (IS_LIVE or os.environ.get("CHECK_EXTERNAL_LINKS")),
                    reason="external links are only checked against the live site")
def test_external_links_are_not_dead(playwright_session, all_links):
    """Outbound links (papers, news coverage, partner sites). Only a
    definite "this page is gone" fails the test -- 404/410, or a domain
    that no longer exists. Sites that block automated checks (401/403/429,
    LinkedIn's 999) or time out are listed as notes, not failures."""
    base = urlparse(SITE_URL).netloc
    req = playwright_session.request.new_context(extra_http_headers={"User-Agent": CHROME_UA})
    dead, notes = [], []
    for link, pages in sorted(all_links.items()):
        if urlparse(link).scheme not in ("http", "https") or urlparse(link).netloc == base:
            continue
        where = ", ".join(sorted(set(pages)))
        status, error = None, None
        for _ in range(2):  # one retry for blips
            try:
                status = req.get(urldefrag(link)[0], timeout=25000, max_redirects=10).status
                error = None
                break
            except Exception as e:  # DNS failure, refused connection, timeout...
                error = str(e).splitlines()[0]
        if status in (404, 410):
            dead.append(f"HTTP {status}: {link} (on {where})")
        elif error and re.search(r"ERR_NAME_NOT_RESOLVED|ENOTFOUND|getaddrinfo", error):
            dead.append(f"domain doesn't exist: {link} (on {where})")
        elif error or (status and status >= 400):
            notes.append(f"{status or error}: {link}")
    req.dispose()
    for n in notes:
        print(f"::notice title=External link not checkable::{n}")
    assert not dead, "Dead external links:\n  " + "\n  ".join(dead)
