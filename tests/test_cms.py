"""The Content Manager (docs/admin/), exercised against a FAKE GitHub.

Every call the CMS makes to api.github.com is intercepted and answered
from this checkout's own build/data files, and "publishing" is only
recorded -- nothing is ever written to the real repository, and no
GitHub token is needed.
"""
import base64
import json
import os
import re

import pytest
import yaml

from conftest import REPO_ROOT


@pytest.fixture
def cms(site):
    ctx = site.new_context("desktop")
    published = []

    def fake_github(route):
        req = route.request
        path = re.search(r"/contents/([^?]+)", req.url)
        if not path:
            return route.fulfill(status=404, body="{}")
        path = path.group(1)
        if req.method == "GET":
            f = REPO_ROOT / path
            if not f.exists():
                return route.fulfill(status=404, body="{}")
            return route.fulfill(status=200, content_type="application/json", body=json.dumps(
                {"content": base64.b64encode(f.read_bytes()).decode(), "sha": "test-sha"}))
        body = json.loads(req.post_data)
        published.append((path, base64.b64decode(body["content"]).decode("utf-8")))
        return route.fulfill(status=200, content_type="application/json",
                             body=json.dumps({"content": {"sha": "test-sha-2"}}))

    ctx.route("https://api.github.com/**", fake_github)
    # Local runs without internet access can supply js-yaml themselves.
    if os.environ.get("JSYAML_PATH"):
        ctx.route("https://cdnjs.cloudflare.com/**",
                  lambda r: r.fulfill(path=os.environ["JSYAML_PATH"], content_type="application/javascript"))
    ctx.add_init_script("localStorage.setItem('tph_cms_token', 'fake-token-for-tests')")
    page = site.open("admin/", context=ctx)
    page.wait_for_function("typeof store !== 'undefined' && store.topic_detail !== undefined", timeout=20000)
    page.published = published
    return page


def publish_label(page):
    return page.locator("#publish-btn").inner_text().strip()


def test_cms_loads_every_collection(cms):
    collections = cms.evaluate("Object.fromEntries(Object.entries(COLLECTIONS).map(([k, c]) => [k, c.file]))")
    for key, file in collections.items():
        expected = yaml.safe_load((REPO_ROOT / file).read_text()) or []
        got = cms.evaluate(f"store['{key}'] ? store['{key}'].entries.length : -1")
        assert got == len(expected), f"CMS loaded {got} {key} entries, file has {len(expected)}"
    assert publish_label(cms) == "Publish changes" and cms.locator("#publish-btn").is_disabled()


def test_cms_edit_count_and_publish(cms):
    cms.evaluate("selectCollection('people')")
    cms.evaluate("startEditEntry(0)")
    cms.locator("#field-bio").fill(cms.locator("#field-bio").input_value() + " (test edit)")
    cms.get_by_role("button", name="Save", exact=True).click()
    assert publish_label(cms) == "Publish 1 change"

    cms.evaluate("startEditEntry(1)")  # open and save WITHOUT changing anything
    cms.get_by_role("button", name="Save", exact=True).click()
    assert publish_label(cms) == "Publish 1 change", "saving an untouched entry counted as a change"

    cms.locator("#publish-btn").click()
    cms.wait_for_function("document.getElementById('publish-btn').textContent.trim() === 'Publish changes'")
    assert [p for p, _ in cms.published] == ["build/data/people.yml"]
    saved = yaml.safe_load(cms.published[0][1])
    assert saved[0]["bio"].endswith("(test edit)")


def test_cms_rejects_unreadable_news_date(cms):
    cms.evaluate("selectCollection('news')")
    cms.evaluate("startNewEntry()")
    cms.locator("#field-date").fill("Fall 2026")
    cms.locator("#field-title").fill("Test item")
    cms.get_by_role("button", name="Save", exact=True).first.click()
    assert "isn't a date the site can read" in cms.locator("#toast").inner_text()
    assert publish_label(cms) == "Publish changes", "an unreadable date was saved anyway"


def test_cms_photo_tool_desktop_and_phone(cms):
    cms.evaluate("selectCollection('people')")
    i = cms.evaluate("store.people.entries.findIndex(e => e.photo)")
    assert i >= 0
    cms.evaluate(f"startEditEntry({i})")
    box = cms.locator("#fitbox-field-photo")
    box.wait_for()
    cms.locator(".image-view-switch button", has_text="Phone").click()
    phone = cms.locator(".image-fit-box.phone img")
    phone.wait_for()
    cms.wait_for_function("(() => { const i = document.querySelector('.image-fit-box.phone img'); return i && i.complete && i.naturalWidth > 0; })()")


def test_cms_project_multiple_links(cms):
    """A project can carry several outbound links, each its own pop-up button.
    An old single `link` (if any data still has one) loads as the first row
    and publishes as `links`."""
    data = yaml.safe_load((REPO_ROOT / "build/data/topic_detail.yml").read_text())
    key, idx = next((k, i) for k, v in data.items()
                    for i, p in enumerate((v or {}).get("projects") or []) if p.get("link") or p.get("links"))
    proj0 = data[key]["projects"][idx]
    existing = ([{"label": "", "url": proj0["link"]}] if proj0.get("link") and not proj0.get("links")
                else [{"label": l.get("label") or "", "url": l.get("url") or ""} for l in proj0["links"]])
    cms.evaluate(f"selectTopicArea({json.dumps(key)})")
    assert cms.evaluate(f"store.topic_detail.data[{json.dumps(key)}].projects[{idx}].links") == existing
    assert publish_label(cms) == "Publish changes", "loading project links counted as an edit"

    new_row = len(existing)
    cms.evaluate(f"addProjectLink({idx})")
    cms.evaluate(f"addProjectLink({idx})")  # a blank row that should be dropped on publish
    target = cms.locator(".topic-card").nth(idx).locator(".project-link-row").nth(new_row)
    target.locator("input").nth(0).fill("Second site")
    target.locator("input").nth(1).fill("https://example.org/second")

    cms.locator("#publish-btn").click()
    cms.wait_for_function("document.getElementById('publish-btn').textContent.trim() === 'Publish changes'")
    saved = yaml.safe_load(dict(cms.published)["build/data/topic_detail.yml"])
    proj = saved[key]["projects"][idx]
    assert "link" not in proj
    assert proj["links"] == existing + [{"label": "Second site", "url": "https://example.org/second"}]
