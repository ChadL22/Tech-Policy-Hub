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
