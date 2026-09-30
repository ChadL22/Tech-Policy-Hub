"""Turns pytest's JUnit XML into a short Markdown report for the GitHub
Actions run page (appended to $GITHUB_STEP_SUMMARY by the workflow)."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
cases = root.iter("testcase")
passed, failed, skipped = [], [], []
for c in cases:
    name = f"{c.get('classname', '').split('.')[-1]}::{c.get('name')}"
    bad = c.find("failure") if c.find("failure") is not None else c.find("error")
    if bad is not None:
        first = (bad.get("message") or bad.text or "").strip().splitlines()
        failed.append((name, first[0][:300] if first else ""))
    elif c.find("skipped") is not None:
        skipped.append((name, (c.find("skipped").get("message") or "")[:200]))
    else:
        passed.append(name)

target = sys.argv[2] if len(sys.argv) > 2 else ""
print(f"## Site check {'passed' if not failed else 'FAILED'}{' — ' + target if target else ''}\n")
print(f"**{len(passed)} passed**, **{len(failed)} failed**, {len(skipped)} skipped.\n")
if failed:
    print("### Failures\n")
    for name, msg in failed:
        print(f"- `{name}` — {msg}")
    print("\nScreenshots and Playwright traces are attached to this run as the **test-results** artifact "
          "(open a trace with `playwright show-trace <file>` or at https://trace.playwright.dev).\n")
if skipped:
    print("<details><summary>Skipped</summary>\n")
    for name, msg in skipped:
        print(f"- `{name}` — {msg}")
    print("\n</details>")
