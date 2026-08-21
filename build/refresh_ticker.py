"""Refresh build/data/ticker.json from the Integrity Institute's Tech Policy
Tracker -- run by .github/workflows/refresh-ticker.yml on a schedule (and
runnable by hand: `python3 refresh_ticker.py` from build/).

BACKGROUND (see project memory / README for the full writeup): the tracker
sites (us-federal.techpolicytracker.com, us-state.techpolicytracker.com)
have no documented public API. But both are themselves built on a public
Typesense search backend, and each site's own shipped JS bundle embeds a
"search-only API key" (their own code comment) to talk to it -- this is
Typesense's standard, intended pattern for public-facing search widgets:
a scoped, read-only key meant to be exposed client-side. That means this
script isn't calling anything undocumented-and-hidden; it's issuing the
exact same read-only search queries the tracker's own web page issues,
just from a script instead of a browser. It IS unofficial/unsupported --
Integrity Institute could change their frontend and this would silently
stop matching without notice, hence the DATA SANITY CHECKS below rather
than trusting the response blindly.

WHAT THIS FILTERS FOR: both collections tag every bill with the tracker's
own theme taxonomy. This script keeps only bills matching at least one
CORE_THEME, a deliberately tight subset chosen (and hand-verified against
live results) to line up with the Hub's four research areas:
  - Cybersecurity            -> "Cybersecurity and Information Security",
                                 "Software and Device Security"
  - Consumer Privacy         -> "Data Privacy and Protection",
                                 "Digital Identity and Biometrics"
  - Information Integrity    -> "Misinformation and Deceptive Practices"
  - Trustworthy ML           -> "Artificial Intelligence and Machine Learning"
A broader first pass (also matching "Online Safety and Content
Regulation", "Algorithmic Fairness and Accountability", etc.) pulled in
clearly off-topic bills tagged with those as their ONLY relevant theme
(a lottery/casino age-verification bill; a political-event-contracts
insider-trading bill) -- so those looser themes were deliberately left
out of CORE_THEMES. If future runs turn up more false positives, tighten
CORE_THEMES further rather than adding a keyword blocklist.
"""
import datetime
import json
import os
import sys
import urllib.request
import urllib.error

TYPESENSE_HOST = "6b02zkvpmslnjyd8p-1.a1.typesense.net"

# These are the tracker sites' own public, read-only "search-only API
# keys" -- see the module docstring. Not secrets; not ours; sourced by
# reading the tracker's own shipped JS (us-federal./us-state.
# techpolicytracker.com/typesense-instantsearch-demo/src/app.js).
FEDERAL_COLLECTION = "bills_federal"
FEDERAL_KEY = "JrkZtt5wKSNACgUpSrJNdZ8n3hhmGdEK"
STATE_COLLECTION = "bills_US_State"
STATE_KEY = "MmG4uqUrWwR3mjdnmLKptvXfPaOLLgCC"

CORE_THEMES = [
    "Cybersecurity and Information Security",
    "Software and Device Security",
    "Data Privacy and Protection",
    "Digital Identity and Biometrics",
    "Misinformation and Deceptive Practices",
    "Artificial Intelligence and Machine Learning",
]

# jurisdiction code -> (Typesense "State" facet value or None for federal, cap)
JURISDICTIONS = [
    ("FED", None, 4),
    ("MD", "Maryland", 2),
    ("VA", "Virginia", 2),
    ("DC", "District of Columbia", 2),
]

OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "ticker.json")


def typesense_search(collection, api_key, state_filter, limit):
    theme_filter = "Themes:=[" + ",".join(CORE_THEMES) + "]"
    filter_by = f"State:=[{state_filter}] && {theme_filter}" if state_filter else theme_filter
    body = json.dumps({
        "searches": [{
            "collection": collection,
            "q": "*",
            "query_by": "Name",
            "filter_by": filter_by,
            "sort_by": "Intro date:desc",
            "per_page": limit,
        }]
    }).encode("utf-8")
    url = f"https://{TYPESENSE_HOST}/multi_search?x-typesense-api-key={api_key}"
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    result = data["results"][0]
    if result.get("error"):
        raise RuntimeError(f"Typesense error for {collection}: {result['error']}")
    return [hit["document"] for hit in result.get("hits", [])]


def to_item(jurisdiction, doc):
    name = doc.get("Name", "")
    if ": " in name:
        code, title = name.split(": ", 1)
    else:
        code, title = "", name
    link = doc.get("Entity site") or doc.get("State site") or doc.get("Legiscan") or ""
    return {"jurisdiction": jurisdiction, "datum": f"{code} — {title}", "link": link}


def main():
    items = []
    for jurisdiction, state_filter, limit in JURISDICTIONS:
        collection, key = (FEDERAL_COLLECTION, FEDERAL_KEY) if jurisdiction == "FED" else (STATE_COLLECTION, STATE_KEY)
        try:
            docs = typesense_search(collection, key, state_filter, limit)
        except (urllib.error.URLError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
            # Fail loudly rather than silently shipping a stale/empty ticker --
            # see module docstring: this is an unofficial integration that
            # could break without notice, so a fetch failure should stop the
            # workflow (and leave the last-known-good data/ticker.json alone)
            # rather than overwrite good data with an empty result.
            print(f"ERROR fetching {jurisdiction}: {exc}", file=sys.stderr)
            sys.exit(1)
        if not docs:
            print(f"ERROR: 0 results for {jurisdiction} -- tracker's data or schema may have changed", file=sys.stderr)
            sys.exit(1)
        items.extend(to_item(jurisdiction, d) for d in docs)

    out = {
        "generated_by": "build/refresh_ticker.py",
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": ("Integrity Institute Tech Policy Tracker "
                   "(us-federal.techpolicytracker.com, us-state.techpolicytracker.com)"),
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(items)} items to {OUT_PATH}")


if __name__ == "__main__":
    main()
