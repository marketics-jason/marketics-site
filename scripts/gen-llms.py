#!/usr/bin/env python3
"""
gen-llms.py — keep llms.txt's coverage locked to sitemap.xml.

WHY THIS IS A CHECKER AND NOT A FULL GENERATOR
----------------------------------------------
The Sep 4 GEO brief asked for build-step generation "from the same source that
emits sitemap.xml". There is no build step on this site and nothing emits
sitemap.xml — it is hand-maintained, which is why 39 of its 42 lastmod values
were frozen at 2026-07-18. So the goal ("coverage can't drift") is met a
different way: sitemap.xml IS the source, this script gates llms.txt against it,
and CI fails when a page exists in one and not the other.

Regenerating llms.txt wholesale was considered and deliberately NOT done. The 22
entries that predate this script carry curated GEO copy; replacing their
descriptions with meta descriptions would be authoring by side-effect — quietly
rewriting approved text under cover of "generation". Existing entries are never
touched. Only missing ones are added, and their descriptions come from the
page's own approved <meta name="description">, or from Strategy-supplied copy in
llms-config.json. No description is written by Code.

Usage:
  python3 scripts/gen-llms.py            # --check: fail if coverage has drifted
  python3 scripts/gen-llms.py --add      # append missing entries, then re-check
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(ROOT, "sitemap.xml")
LLMS = os.path.join(ROOT, "llms.txt")
CONFIG = os.path.join(ROOT, "scripts", "llms-config.json")
BASE = "https://marketics.io"


def load_config():
    with open(CONFIG, encoding="utf-8") as fh:
        return json.load(fh)


def sitemap_paths():
    """Every sitemap URL as a site-root path. '/' for the homepage."""
    raw = open(SITEMAP, encoding="utf-8").read()
    out = []
    for url in re.findall(r"<loc>([^<]+)</loc>", raw):
        path = url.replace(BASE, "") or "/"
        out.append(path)
    return out


def excluded(path, cfg):
    """A path is excluded if it matches an entry or sits beneath one."""
    for ex in cfg["exclude"]:
        if path == ex or path.startswith(ex.rstrip("/") + "/"):
            return True
    return False


def source_file(path):
    if path == "/":
        return os.path.join(ROOT, "index.html")
    if "." in os.path.basename(path):          # /llms.txt, /robots.txt …
        return os.path.join(ROOT, path.lstrip("/"))
    return os.path.join(ROOT, path.lstrip("/"), "index.html")


def page_meta(path):
    """(title, description) from the page's own approved copy."""
    fp = source_file(path)
    if not os.path.exists(fp):
        return None, None
    src = open(fp, encoding="utf-8", errors="replace").read()
    t = re.search(r"<title>(.*?)</title>", src, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', src)
    # Titles end with a separator + "Marketics" in three different styles across
    # the estate (|, em dash, en dash). Strip whichever one is used.
    title = re.sub(r"\s*[|\u2014\u2013-]\s*Marketics\s*$", "", t.group(1).strip()) if t else None
    return title, (d.group(1).strip() if d else None)


def section_for(path, cfg):
    best, name = -1, None
    for prefix, sec in cfg["sections"].items():
        if path == prefix or path.startswith(prefix.rstrip("/") + "/") or prefix == "/":
            if len(prefix) > best:
                best, name = len(prefix), sec
    return name


def present_paths():
    """Paths already linked from llms.txt, however they are written."""
    raw = open(LLMS, encoding="utf-8").read()
    found = set()
    for url in re.findall(r"\((https://marketics\.io[^)]*)\)", raw):
        found.add(url.replace(BASE, "") or "/")
    return found


def missing(cfg):
    have = present_paths()
    out = []
    for p in sitemap_paths():
        if excluded(p, cfg) or p in have:
            continue
        out.append(p)
    return out


def add_entries(cfg, paths):
    """Insert each missing path into its section, creating the section if needed."""
    lines = open(LLMS, encoding="utf-8").read().split("\n")
    added = []
    for path in paths:
        title, desc = page_meta(path)
        if not title or not desc:
            print(f"  ! {path}: no title/description in source — skipped", file=sys.stderr)
            continue
        desc = cfg["descriptions"].get(path, desc)
        entry = f"- [{title}]({BASE}{path if path != '/' else ''}): {desc}"
        sec = section_for(path, cfg)

        head = f"## {sec}"
        if head in lines:
            i = lines.index(head) + 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            while i > 0 and lines[i - 1].strip() == "":
                i -= 1
            lines.insert(i, entry)
        else:
            # New section, placed before the first prose section so the link
            # lists stay together at the top of the file.
            anchor = next((n for n, l in enumerate(lines)
                           if l.startswith("## What Marketics Does")), len(lines))
            lines[anchor:anchor] = [head, "", entry, ""]
        added.append(path)
    open(LLMS, "w", encoding="utf-8").write("\n".join(lines))
    return added


def main():
    cfg = load_config()
    total = len(sitemap_paths())
    keep = [p for p in sitemap_paths() if not excluded(p, cfg)]

    if "--add" in sys.argv:
        gaps = missing(cfg)
        if not gaps:
            print("llms.txt already covers every non-excluded sitemap URL.")
            return 0
        # Deepest paths first so a section's own hub entry lands above its children.
        added = add_entries(cfg, sorted(gaps))
        print(f"Added {len(added)} entr(y/ies) to llms.txt:")
        for p in added:
            print(f"  + {p}")

    gaps = missing(cfg)
    if gaps:
        print(f"\n✗ llms.txt is missing {len(gaps)} sitemap URL(s):", file=sys.stderr)
        for p in gaps:
            print(f"   {p}", file=sys.stderr)
        print("\n   Run: python3 scripts/gen-llms.py --add", file=sys.stderr)
        print("   Or add the path to scripts/llms-config.json 'exclude' with a reason.",
              file=sys.stderr)
        return 1

    print(f"✓ llms.txt covers all {len(keep)} of {total} sitemap URL(s) "
          f"({total - len(keep)} excluded by config)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
