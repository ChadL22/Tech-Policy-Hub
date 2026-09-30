"""Shared setup for the Tech Policy Hub site tests.

The suite drives a real Chromium through Playwright's own Python API
(no pytest-playwright plugin), so the only dependencies are pytest,
playwright and PyYAML -- see tests/requirements.txt.

Which site gets tested:
  SITE_URL   Base URL to test. Defaults to the live site,
             https://techpolicyhub.org/. The weekly workflow
             (.github/workflows/site-tests.yml) can also point it at a
             local build served from docs/, e.g. http://localhost:8000/.

Checks that only make sense against the real domain -- the newsletter
endpoint's CORS probe and the external-link sweep -- skip themselves
when SITE_URL isn't the live site (set CHECK_EXTERNAL_LINKS=1 to force
the link sweep anyway).

On a failure, a full-page screenshot and a Playwright trace
(open with `playwright show-trace <file>`) are saved to test-results/.
"""
import os
import pathlib
import re
from urllib.parse import urljoin, urlparse

import pytest
from playwright.sync_api import sync_playwright

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
LIVE_ORIGIN = "https://techpolicyhub.org"
SITE_URL = os.environ.get("SITE_URL", LIVE_ORIGIN + "/").rstrip("/") + "/"
IS_LIVE = urlparse(SITE_URL).netloc == urlparse(LIVE_ORIGIN).netloc
RESULTS_DIR = pathlib.Path(os.environ.get("TEST_RESULTS_DIR", REPO_ROOT / "test-results"))

# Every generated page (see build/build_all.py), relative to SITE_URL.
PAGES = ["", "research/", "people/", "events/", "courses/", "speaker-series/", "annual-event/"]

VIEWPORTS = {
    "desktop": dict(viewport={"width": 1300, "height": 900}),
    # A typical phone. people.html's card layout switches at <=700px.
    "mobile": dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True),
}


def url(path=""):
    return urljoin(SITE_URL, path)


def same_site(u):
    return urlparse(u).netloc in (urlparse(SITE_URL).netloc, urlparse(LIVE_ORIGIN).netloc)


# ---------------------------------------------------------------- browser

@pytest.fixture(scope="session")
def playwright_session():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_session):
    b = playwright_session.chromium.launch()
    yield b
    b.close()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


class Watch:
    """Records what went wrong on a page while a test used it: uncaught
    JS exceptions, console errors, and this site's own requests that
    failed or came back 4xx/5xx. Third-party failures (fonts, embeds)
    are kept separately as notes -- they don't fail a test."""

    def __init__(self, page):
        self.problems = []
        self.notes = []
        page.on("pageerror", lambda e: self.problems.append(f"JS exception: {e}"))
        page.on("console", self._console)
        page.on("requestfailed", self._failed)
        page.on("response", self._response)

    def _console(self, msg):
        if msg.type != "error":
            return
        where = (msg.location or {}).get("url", "")
        text = f"console error: {msg.text}" + (f" ({where})" if where else "")
        (self.problems if (not where or same_site(where)) else self.notes).append(text)

    def _failed(self, req):
        text = f"request failed: {req.method} {req.url} ({req.failure})"
        # ERR_ABORTED = the browser cancelled a load itself, e.g. a lazy
        # image still downloading when the test navigated away -- not a
        # broken file (a real 404 is caught by _response).
        if same_site(req.url) and "ERR_ABORTED" not in (req.failure or ""):
            self.problems.append(text)
        else:
            self.notes.append(text)

    def _response(self, resp):
        if resp.status >= 400 and same_site(resp.url):
            self.problems.append(f"HTTP {resp.status}: {resp.url}")

    def assert_clean(self):
        assert not self.problems, "Problems on the page:\n  " + "\n  ".join(self.problems)


@pytest.fixture
def site(browser, request):
    """site.open(path, vp="desktop") -> a Page with a .watch (see Watch).
    Every page opened is also checked for errors when the test ends,
    unless the test already failed for another reason."""
    contexts = []

    class Site:
        def new_context(self, vp="desktop"):
            ctx = browser.new_context(**VIEWPORTS[vp])
            ctx.tracing.start(screenshots=True, snapshots=True)
            contexts.append(ctx)
            return ctx

        def open(self, path="", vp="desktop", context=None):
            ctx = context or self.new_context(vp)
            page = ctx.new_page()
            page.watch = Watch(page)
            resp = page.goto(url(path), wait_until="load")
            assert resp is not None and resp.status == 200, f"{url(path)} returned {resp and resp.status}"
            return page

    yield Site()

    failed = bool(getattr(request.node, "rep_call", None) and request.node.rep_call.failed)
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)[-120:]
    for i, ctx in enumerate(contexts):
        if failed:
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            for j, pg in enumerate(ctx.pages):
                try:
                    pg.screenshot(path=str(RESULTS_DIR / f"{stem}-{i}{j}.png"), full_page=True)
                except Exception:
                    pass
            ctx.tracing.stop(path=str(RESULTS_DIR / f"{stem}-{i}.trace.zip"))
        else:
            ctx.tracing.stop()
            for pg in ctx.pages:
                if hasattr(pg, "watch"):
                    pg.watch.assert_clean()
        ctx.close()


@pytest.fixture(params=list(VIEWPORTS))
def vp(request):
    """Runs a test once at desktop size and once at phone size."""
    return request.param


# ---------------------------------------------------------------- helpers

def visible_rows(page, selector="[data-search-row]"):
    """Rows the page's filters are currently showing (not [hidden], not
    display:none, and not inside a collapsed/hidden section)."""
    return page.evaluate(
        """(sel) => Array.from(document.querySelectorAll(sel)).filter(el =>
             !el.closest('[hidden]') && getComputedStyle(el).display !== 'none')
           .map(el => ({ areas: (el.dataset.areas || '').split(' ').filter(Boolean),
                         year: el.dataset.year || null,
                         target: el.dataset.filterTarget || null,
                         text: el.textContent.replace(/\\s+/g, ' ').trim() }))""",
        selector,
    )


def load_all_images(page):
    """Lazy images only load when scrolled to; force them all so a broken
    image anywhere on the page is caught."""
    page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
    page.wait_for_function("Array.from(document.images).every(i => i.complete)", timeout=20000)
    return page.evaluate(
        "Array.from(document.images).filter(i => !i.naturalWidth).map(i => i.currentSrc || i.src)"
    )


def open_filter_dropdown(page, label):
    toggle = page.locator(".filter-dropdown-toggle", has_text=label).first
    if toggle.get_attribute("aria-expanded") != "true":
        toggle.click()
    return page.locator(".filter-dropdown", has=toggle)
