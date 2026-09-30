"""The site generator itself.

Both of these would have caught the Sept. 2026 outage, where one Hub
News date ("September 2026") crashed build_all.py and every content
edit after it silently never reached the live site.
"""
import difflib
import re
import shutil
import subprocess
import sys

import pytest

from conftest import REPO_ROOT


@pytest.fixture(scope="module")
def fresh_build(tmp_path_factory):
    """Runs build/build_all.py on a scratch copy of the repo, so the
    checkout's own docs/ is left alone for the comparison below."""
    tmp = tmp_path_factory.mktemp("build")
    shutil.copytree(REPO_ROOT / "build", tmp / "build")
    shutil.copytree(REPO_ROOT / "docs", tmp / "docs")
    result = subprocess.run(
        [sys.executable, "build_all.py"], cwd=tmp / "build",
        capture_output=True, text=True, timeout=600,
    )
    return tmp, result


def test_site_builds_without_errors(fresh_build):
    _, result = fresh_build
    assert result.returncode == 0, (
        "build/build_all.py failed -- until this is fixed, no content edit "
        "(including CMS edits) will reach the live site.\n\n"
        + result.stdout[-4000:] + "\n" + result.stderr[-4000:]
    )
    # Warnings (e.g. a Hub News date the build couldn't read and is showing
    # as typed) don't fail the run, but surface as annotations on the
    # workflow run page.
    for line in result.stdout.splitlines():
        if line.startswith("WARNING"):
            print(f"::warning title=Site build warning::{line}")


# Colors sampled from photos (--photo-fill, see image_edge_color in
# generate.py) can differ by a shade between Pillow versions -- the CI
# runner's vs. whoever last built locally -- so they're ignored here.
_UNSTABLE = re.compile(r"--photo-fill:#[0-9a-f]{6};")


def test_published_site_is_up_to_date(fresh_build):
    """docs/ (what GitHub Pages serves) must match what the current
    content and code produce. A mismatch means a rebuild failed or was
    skipped, so the live site is showing out-of-date content."""
    tmp, result = fresh_build
    if result.returncode != 0:
        pytest.skip("build failed -- see test_site_builds_without_errors")
    stale = []
    for fresh in sorted((tmp / "docs").rglob("*")):
        if fresh.suffix not in (".html", ".ics"):
            continue
        rel = fresh.relative_to(tmp / "docs")
        committed = REPO_ROOT / "docs" / rel
        new_text = _UNSTABLE.sub("", fresh.read_text(encoding="utf-8"))
        old_text = _UNSTABLE.sub("", committed.read_text(encoding="utf-8")) if committed.exists() else ""
        if new_text != old_text:
            diff = difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), "published", "fresh build", n=0, lineterm="")
            stale.append(f"docs/{rel}:\n" + "\n".join(list(diff)[2:14]))
    assert not stale, (
        "These published pages don't match a fresh build of the current "
        "content -- run `cd build && python3 build_all.py` and commit docs/ "
        "(or check why the 'Rebuild site on content change' workflow "
        "failed):\n\n" + "\n\n".join(stale)
    )


def test_event_date_formats():
    """Every date format the Content Manager accepts for an event (see
    event_dates in build/generate.py). The Sept. 30, 2026 outage: a
    two-day event saved as d: 9-10 crashed the rebuild."""
    import contextlib, io
    sys.path.insert(0, str(REPO_ROOT / "build"))
    with contextlib.redirect_stdout(io.StringIO()):
        import generate as g
    ok = {
        "09": ("2027-09-09", "2027-09-09", "SEP 9"),
        "9-10": ("2027-09-09", "2027-09-10", "SEP 9–10"),
        "9 – 10": ("2027-09-09", "2027-09-10", "SEP 9–10"),
        "9 to 10": ("2027-09-09", "2027-09-10", "SEP 9–10"),
        "30-2": ("2027-09-30", "2027-10-02", "SEP 30–OCT 2"),
    }
    for d, (start, end, label) in ok.items():
        with contextlib.redirect_stdout(io.StringIO()):
            e = g.normalize_event({"y": 2027, "m": "Sep", "d": d, "title": "t"})
        assert (str(e["start"]), str(e["end"]), e["short_label"]) == (start, end, label), d
    spelled_out = g.normalize_event({"y": 2026, "m": "DEC", "d": "30", "end_m": "JAN", "end_d": "2", "title": "t"})
    assert (str(spelled_out["end"]), spelled_out["short_label"]) == ("2027-01-02", "DEC 30–JAN 2")
    for d in ("TBD", "9th", "31", "2-1"):  # unreadable -> listed as typed, never a crash
        with contextlib.redirect_stdout(io.StringIO()):
            assert g.normalize_event({"y": 2027, "m": "SEP", "d": d, "title": "t"})["start"] is None, d


def test_event_location():
    """Location line under the title (pin, or a video icon when virtual
    only) and in the .ics feed; nothing when blank."""
    import contextlib, io
    sys.path.insert(0, str(REPO_ROOT / "build"))
    with contextlib.redirect_stdout(io.StringIO()):
        import generate as g
        dc = g.normalize_event({"y": 2027, "m": "JAN", "d": "9-10", "title": "A", "cat": "External",
                                "link": "https://example.org/", "meta": "m", "location": "Washington, DC"})
        virtual = dict(dc, title="B", location="Virtual")
        blank = dict(dc, title="C", location="")
    html = g.events_rows_html([dc, virtual, blank])
    assert html.count('class="event-location"') == 2
    assert "Washington, DC" in html and html.count("event-location-icon--virtual") == 1
    ics = g.events_ics([dc, virtual, blank])
    assert "LOCATION:Washington\\, DC" in ics and "LOCATION:Virtual" in ics
    assert ics.count("LOCATION:") == 2
