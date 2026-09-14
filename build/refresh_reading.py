"""Refresh build/data/reading_items.yml ("What we're reading" on the
homepage) from Phronesis's own public content feed -- run by
.github/workflows/refresh-reading.yml on a schedule (and runnable by
hand: `python3 refresh_reading.py` from build/).

WHAT THIS PULLS: phronesisresearch.org's homepage "Recently Added"
section shows, for six of its seven content categories (everything
except "Phronesis Original" and "Canon" -- excluded per direct user
request, since those aren't outside reading pulled from elsewhere), a
small carousel per category with the most recently dated entry shown
first. Rather than scraping that rendered page (a client-side app with
no server HTML to parse), this reads the same public, static JSON files
the page itself fetches to build those carousels
(phronesisresearch.org/content/<research|policy|legal|essays|articles|
reports>.json) -- unauthenticated, same-origin data Phronesis's own
frontend already exposes, not a private API.

Each file is a flat list of entries across ALL of that category's
sub-types and origins; the site's own "Recently Added" carousel for a
given category only shows entries where:
  - `placeholder` is false (seed/draft entries aren't real content yet)
  - `origin` is "via" (curated from elsewhere) -- "original" entries are
    Phronesis's own authored pieces, shown under a separate "Phronesis
    Original" carousel this script deliberately skips
  - `type` matches that file's own primary type key -- every file is
    homogeneous except policy.json, which mixes "policy"/"proposal"/
    "memo" sub-types; only "policy" belongs in the Policy Artifact
    carousel (hand-verified against the live site: a bare
    date-descending sort without this filter picks the wrong entry)
...sorted by `date` descending, taking the single most recent match.

FIELD MAPPING (see reading_cards_html() in generate.py for how these
render): `source` <- entry's `publisher` (the original outlet, e.g.
"arXiv", "Bloomberg Law" -- Phronesis is curating this, not authoring
it); `title` <- `title`; `summary` <- `subtitle`, a short original
Phronesis-written dek (NOT `abstract`/`body`, which can be a full
paragraph or more -- see the site's own field notes in each JSON file);
`meta` <- `date` reformatted "Mon D" (no year), matching how Phronesis's
own site displays it; `link` <- `original_url`, the source document
itself (not a phronesisresearch.org page -- Phronesis is the source of
the metadata, not the destination, same as before this script existed).

DATA SANITY: fails loudly (nonzero exit, leaving the last-known-good
reading_items.yml alone) if a fetch fails, a file's JSON doesn't parse,
or any of the six categories comes up with zero matching entries --
better to skip a week's refresh than silently ship five cards or stale
placeholder-shaped data.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

import yaml

BASE_URL = "https://phronesisresearch.org/content"

# (json filename stem, entry `type` value to require, plural key matching
# build/data/reading_types.yml / reading_type_labels.yml -- in the order
# the homepage grid should display them).
CATEGORIES = [
    ("research", "research", "Research Papers"),
    ("policy", "policy", "Policy Artifacts"),
    ("legal", "legal", "Legal Analyses"),
    ("essays", "essay", "Essays"),
    ("articles", "article", "Articles"),
    ("reports", "report", "Reports"),
]

OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "reading_items.yml")


def fetch_json(name):
    url = f"{BASE_URL}/{name}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "TechPolicyHub-ReadingRefresh/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def format_date(iso_date):
    dt = datetime.datetime.strptime(iso_date, "%Y-%m-%d")
    # "%-d" (no leading zero) isn't portable across platforms (fails on
    # some Windows Pythons) -- strip a leading zero by hand instead.
    return dt.strftime("%b ") + str(dt.day)


def clean_url(url):
    """A couple of source URLs in the feed carry trailing junk (an
    unencoded/encoded trailing space) picked up from whatever the
    Phronesis editor pasted in -- strip it so the Hub doesn't ship the
    same stray character."""
    url = (url or "").strip()
    while url.endswith("%20") or url.endswith(" "):
        url = url[:-3] if url.endswith("%20") else url[:-1]
    return url


def pick_latest(entries, want_type):
    matches = [
        e for e in entries
        if not e.get("placeholder", False)
        and e.get("origin") == "via"
        and e.get("type") == want_type
    ]
    if not matches:
        return None
    matches.sort(key=lambda e: e.get("date", ""), reverse=True)
    return matches[0]


def main():
    items = []
    for filename, want_type, type_key in CATEGORIES:
        try:
            data = fetch_json(filename)
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            print(f"ERROR fetching {filename}.json: {exc}", file=sys.stderr)
            sys.exit(1)

        entries = data.get("entries", [])
        entry = pick_latest(entries, want_type)
        if entry is None:
            print(f"ERROR: no non-placeholder, curated (origin=via) '{want_type}' "
                  f"entries found in {filename}.json -- feed shape may have changed",
                  file=sys.stderr)
            sys.exit(1)

        for field in ("title", "subtitle", "date", "publisher", "original_url"):
            if not entry.get(field):
                print(f"ERROR: {filename}.json entry {entry.get('id')!r} is missing "
                      f"required field {field!r}", file=sys.stderr)
                sys.exit(1)

        items.append({
            "source": entry["publisher"],
            "type": type_key,
            "title": entry["title"],
            "summary": entry["subtitle"],
            "meta": format_date(entry["date"]),
            "link": clean_url(entry["original_url"]),
        })

    with open(OUT_PATH, "w") as f:
        f.write("# Auto-refreshed weekly by build/refresh_reading.py from "
                 "phronesisresearch.org's own public content feed --\n"
                 "# see that script's docstring. Hand edits here will be "
                 "overwritten by the next scheduled run.\n")
        yaml.dump(items, f, default_flow_style=False, sort_keys=False,
                   allow_unicode=True, width=95)

    print(f"wrote {len(items)} items to {OUT_PATH}")


if __name__ == "__main__":
    main()
