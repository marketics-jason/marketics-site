#!/usr/bin/env python3
"""
gen-lastmod.py — sitemap <lastmod> from the last git commit touching each page.

WHY GIT-PER-FILE
----------------
Before this, 39 of 42 lastmod values were frozen at 2026-07-18 and all 42
disagreed with reality. The obvious alternative — stamping build time — is
worse: it re-dates every URL on every deploy, which tells crawlers the whole
estate changed when one page did. Git per file is the only source that knows
which page actually moved.

WHAT lastmod IS, AND IS NOT
--------------------------
`lastmod` is the last modification of the FILE at that URL. It is not an
editorial revision date. Schema's `dateModified` is the editorial claim, and
intel/SCHEMA-CHECKLIST.md is explicit that it must not be bumped for a change
that did not touch the article's content ("don't fake a refresh").

They are different facts and this script deliberately does NOT write
dateModified. Driving both from git would mean a CSS sweep or a heading fix
silently re-dating every article on the estate — a freshness lie of exactly the
kind git-per-file was chosen to avoid. See the GEO PR notes; routed to Strategy.

WHY --check ONLY GATES OVERCLAIMS
---------------------------------
A strict equality check cannot work here. A squash merge creates a new commit
dated at merge time, so a sitemap generated while authoring is one day stale the
moment it lands — main would go red for a reason that has nothing to do with the
content. So the gate enforces the thing that actually harms: a lastmod NEWER
than the file's real git date, which claims freshness the page does not have.
Staleness is reported as a count, not a failure.

Usage:
  python3 scripts/gen-lastmod.py            # --check: fail on any overclaim
  python3 scripts/gen-lastmod.py --write    # rewrite lastmod from git
"""
import datetime
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(ROOT, "sitemap.xml")
BASE = "https://marketics.io"
TODAY = datetime.date.today().isoformat()


def source_file(url):
    path = url.replace(BASE, "") or "/"
    if path == "/":
        return "index.html"
    if "." in os.path.basename(path):
        return path.lstrip("/")
    return path.lstrip("/") + "/index.html"


def git_date(rel):
    """Last commit date for a file, or today if it has uncommitted changes.

    Uncommitted means the file is being modified right now, so today is the
    honest answer — and it makes the sitemap agree with git once the change
    is committed in the same batch.
    """
    full = os.path.join(ROOT, rel)
    if not os.path.exists(full):
        return None
    dirty = subprocess.run(["git", "status", "--porcelain", "--", rel],
                           cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        return TODAY
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or None


def entries():
    raw = open(SITEMAP, encoding="utf-8").read()
    for m in re.finditer(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", raw):
        yield m.group(1), m.group(2), source_file(m.group(1))


def main():
    write = "--write" in sys.argv
    raw = open(SITEMAP, encoding="utf-8").read()
    overclaims, stale, changed, missing = [], 0, 0, []

    for url, claimed, rel in entries():
        real = git_date(rel)
        if real is None:
            missing.append((url, rel))
            continue
        if claimed > real:
            overclaims.append((url, claimed, real))
        elif claimed < real:
            stale += 1
        if write and claimed != real:
            raw = raw.replace(f"<loc>{url}</loc><lastmod>{claimed}</lastmod>",
                              f"<loc>{url}</loc><lastmod>{real}</lastmod>", 1)
            changed += 1

    if write:
        open(SITEMAP, "w", encoding="utf-8").write(raw)
        print(f"Rewrote {changed} lastmod value(s) from git.")
        return main_check()

    return report(overclaims, stale, missing)


def main_check():
    overclaims, stale, missing = [], 0, []
    for url, claimed, rel in entries():
        real = git_date(rel)
        if real is None:
            missing.append((url, rel))
        elif claimed > real:
            overclaims.append((url, claimed, real))
        elif claimed < real:
            stale += 1
    return report(overclaims, stale, missing)


def report(overclaims, stale, missing):
    for url, rel in missing:
        print(f"⚠  {url}: no source file at {rel}", file=sys.stderr)
    if overclaims:
        print(f"\n✗ {len(overclaims)} sitemap lastmod value(s) claim a date the file "
              f"does not have:", file=sys.stderr)
        for url, claimed, real in overclaims:
            print(f"   {url}\n     sitemap says {claimed}, git says {real}", file=sys.stderr)
        print("\n   Run: python3 scripts/gen-lastmod.py --write", file=sys.stderr)
        return 1
    note = f", {stale} stale (not a failure — see the module docstring)" if stale else ""
    print(f"✓ no sitemap lastmod overclaims its file's git date{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
