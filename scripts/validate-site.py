#!/usr/bin/env python3
"""
validate-site.py — site-wide invariant gate.

Runs over every hand-authored HTML page and asserts the conventions that this
site has no template engine to enforce. Born from the July 2026 audit, where
every bug was "a thing done right once but not everywhere."

HARD failures (exit 1) — mechanical, unambiguous, must never ship:
  - no unfilled {{PLACEHOLDER}} tokens
  - no retired canon tokens (see RETIRED_TOKENS)
  - no broken internal links (link/src to a path that isn't a real page/asset)
  - no trailing-slash internal links (they force a 301)
  - consent script present on every page except the untracked /audits/ deliverable
  - JSON-LD parses; Article blocks carry the required fields with ISO-8601+tz dates
  - canonical, when present, is absolute and matches the page's own URL

WARNINGS (exit 0, printed) — structural / judgment, tracked but not blocking:
  - Cloudflare /cdn-cgi/ artifacts (counsel-scoped on /join, /legal)
  - missing <main> landmark; h1 count != 1
  - page in sitemap with no inbound internal link (orphan)

Usage:
  python3 scripts/validate-site.py            # whole site
  python3 scripts/validate-site.py a.html b/  # specific files/dirs (hard checks only)
"""
import os, re, sys, json, html as htmllib
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Retired phrasings — each must be zero across the site. Extend on every canon ruling.
RETIRED_TOKENS = [
    "{{",                 # unfilled placeholder
    "~42",                # pre-canon benchmark ("42%+" is the canon)
    "+32%",               # retired stat
    "random sample",      # replaced by "19 documented short-term-rental engagements"
    "30 documented",      # old sample count
    "met or exceeded",    # retired relation framing
    "50–75", "50-75",     # retired engagement-target range
    "3 active markets",   # retired operational-depth framing (three-tier canon is internal-only)
    "active depth markets",
    "22 active markets",  # public copy never states an active-market count
    "2024–2026", "2024-2026", "2024/2026",  # narrowed window; Board ruling v2.9 is 2019–2026
    # v3.1 sweep (2026-08-25): claims named in the canon registry but never
    # machine-gated. All were already absent from the repo — these entries stop
    # them coming back, they did not fix anything. Each is deliberately narrow:
    # the bare words ("consecutive", "guarantee", "28") appear in legitimate copy
    # (case-study timelines, "we make no guarantee", CSS pixel values), so the
    # token must carry enough context to only match the retired claim.
    "42%+",               # retired floor framing; canon is "45% median, net of market"
    "28 documented", "28+ documented",   # wrong sample count; canon is 19
    "documented client outcomes",        # retired phrasing around that count
    "consecutive quarters",              # retired Superhost framing; canon is "35× Superhost"
    "90-Day Guarantee", "90 Day Guarantee",  # retired refund framing; canon is the $500 deposit
    "20 years",           # retired tenure claim in STR context; canon is "the past decade"
    # Entity-encoded dash forms of the retired range. A page authored with an
    # encoded en-dash renders identically but would slip the literal tokens above.
    "50&ndash;75", "50&#8211;75", "50&mdash;75", "50&#8212;75",
    # v3.4 (2026-08-27): the fee is 10% of NET PAYOUT, the basis the signed
    # Co-Host Agreement uses. These phrasings describe a different basis than
    # the contract, which on a booking is a real money difference (the
    # platform's host service fee plus taxes), so they are gated rather than
    # merely corrected once. "one rate on the whole number" is the retired
    # gloss that made the gross reading explicit.
    "10% of revenue", "10% of the revenue", "10% of your revenue",
    "10% of bookings", "10% of net bookings", "10% of booking revenue",
    "one rate on the whole number",
]

# Counsel-lane exemptions: (file, token) pairs that Code is not permitted to fix.
# These do NOT pass silently — each is reported as a warning on every run so it
# stays visible until counsel resolves it. Never add to this to get CI green on
# something Code *could* fix; it exists only for documents Code must not edit.
#
# legal/index.html (2026-08-27, registry v3.4): /legal contradicts itself on the
# fee basis. §601 says "10% of the net payout per booking" (matching the signed
# Co-Host Agreement); §390, §588 and §602 say booking revenue / gross booking
# revenue "before platform service fees, taxes, or other deductions". Those are
# mutually exclusive, and every marketing surface now says net payout. Reported,
# not edited, per the standing counsel-lane rule.
COUNSEL_LANE_EXEMPT = {
    "legal/index.html": ("10% of revenue", "10% of the revenue", "10% of booking revenue",
                         "10% of bookings", "10% of net bookings", "one rate on the whole number"),
}

# Pages that legitimately carry no consent script (confidential, untracked).
CONSENT_EXEMPT_PREFIXES = ("/audits/",)
# /cdn-cgi/ is Cloudflare's namespace, not our routing — never treat as a broken
# internal link. It IS surfaced as a warning so the counsel-scoped artifacts stay visible.
IGNORE_LINK_PREFIXES = ("/cdn-cgi/",)


def url_for(rel):
    if rel == "404.html":
        return "/404"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("/index.html")]
    if rel == "index.html":
        return "/"
    return "/" + rel[: -len(".html")]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.srcs = [], []
        self.canonical = None
        self.h1 = 0
        self.has_main = False
        self.jsonld = []
        self._ld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("img", "script", "iframe", "source", "video") and a.get("src"):
            self.srcs.append(a["src"])
        if tag == "link" and a.get("href"):
            self.srcs.append(a["href"])
            if a.get("rel") == "canonical":
                self.canonical = a["href"]
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.has_main = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = True
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "script" and self._ld:
            self.jsonld.append("".join(self._buf))
            self._ld = False

    def handle_data(self, data):
        if self._ld:
            self._buf.append(data)


def collect():
    pages, assets = {}, set()
    for dp, _, fs in os.walk(ROOT):
        if "/.git" in dp or "/scratchpad" in dp:
            continue
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), ROOT)
            if f.endswith(".html"):
                pages[url_for(rel)] = rel
            assets.add("/" + rel)
    redirects = set()
    rp = os.path.join(ROOT, "_redirects")
    if os.path.exists(rp):
        for line in open(rp):
            line = line.strip()
            if line and not line.startswith("#"):
                p = line.split()
                if p and p[0].startswith("/") and p[0] != "/*":
                    redirects.add(p[0].rstrip("/") or "/")
    return pages, assets, redirects


EXTERNAL = re.compile(r"^(https?:)?//|^mailto:|^tel:|^javascript:|^#|^data:")
ISO_TZ = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")


def check(rel, pages, assets, redirects, inbound, hard, warn):
    path = os.path.join(ROOT, rel)
    raw = open(path, encoding="utf-8", errors="replace").read()
    url = url_for(rel)
    where = f"{rel}"

    # 1. retired tokens (scan raw so schema + copy both covered)
    for tok in RETIRED_TOKENS:
        if tok in raw:
            if tok in COUNSEL_LANE_EXEMPT.get(where, ()):
                warn.append(f"{where}: counsel-lane token still present: {tok!r} "
                            f"(Code must not edit this document — see registry v3.4)")
            else:
                hard.append(f"{where}: retired token present: {tok!r}")

    # 2. consent gating
    if not url.startswith(CONSENT_EXEMPT_PREFIXES):
        if "mkx-consent.js" not in raw:
            hard.append(f"{where}: missing consent script (/mkx-consent.js)")
    else:
        if "mkx-consent.js" in raw or "googletagmanager" in raw or "clarity.ms" in raw:
            hard.append(f"{where}: /audits/ page must not load analytics/consent")

    p = Page()
    p.feed(raw)

    # 3. canonical (when present) absolute + self
    if p.canonical:
        expect = "https://marketics.io" + (url if url != "/" else "/")
        if p.canonical not in (expect, expect.rstrip("/") or "https://marketics.io/"):
            hard.append(f"{where}: canonical {p.canonical!r} != expected {expect!r}")

    # 4. links + srcs
    for l in p.links:
        if EXTERNAL.match(l):
            continue
        pth = l.split("#")[0].split("?")[0]
        if not pth:
            continue
        if pth.startswith(IGNORE_LINK_PREFIXES):
            warn.append(f"{where}: Cloudflare artifact link {l!r} (counsel-scoped)")
            continue
        if not pth.startswith("/"):
            hard.append(f"{where}: non-root-relative internal link {l!r}")
            continue
        norm = pth.rstrip("/") or "/"
        if pth != "/" and pth.endswith("/"):
            hard.append(f"{where}: trailing-slash internal link {l!r} (forces 301)")
        if norm in pages or norm in redirects or pth in assets or norm in assets:
            if norm in pages:
                inbound.setdefault(norm, set()).add(url)
            continue
        hard.append(f"{where}: broken internal link -> {l!r}")
    for s in p.srcs:
        if EXTERNAL.match(s):
            continue
        pth = s.split("#")[0].split("?")[0]
        if pth.startswith(IGNORE_LINK_PREFIXES):
            warn.append(f"{where}: Cloudflare artifact src {s!r} (counsel-scoped)")
            continue
        if pth in assets or pth.rstrip("/") in pages:
            continue
        hard.append(f"{where}: broken resource src -> {s!r}")

    # 5. JSON-LD
    for block in p.jsonld:
        try:
            data = json.loads(block)
        except Exception as e:
            hard.append(f"{where}: JSON-LD parse error: {str(e)[:80]}")
            continue
        for d in (data if isinstance(data, list) else [data]):
            if not isinstance(d, dict):
                continue
            if d.get("@type") == "Article":
                for k in ("headline", "image", "datePublished", "dateModified", "author", "publisher"):
                    if k not in d:
                        hard.append(f"{where}: Article JSON-LD missing {k!r}")
                for k in ("datePublished", "dateModified"):
                    v = d.get(k, "")
                    if v and not ISO_TZ.match(v):
                        hard.append(f"{where}: Article {k} not ISO-8601+tz: {v!r}")
                au = d.get("author", {})
                if isinstance(au, dict) and not au.get("url"):
                    hard.append(f"{where}: Article author.url missing")

    # 6. structural warnings
    if "/cdn-cgi/" in raw and "email-protection" in raw and not any(
        w.startswith(where) and "Cloudflare artifact" in w for w in warn
    ):
        warn.append(f"{where}: Cloudflare email-protection artifact present")
    if p.h1 != 1:
        warn.append(f"{where}: h1 count = {p.h1} (expected 1)")
    if not p.has_main:
        warn.append(f"{where}: no <main> landmark")


def main():
    pages, assets, redirects = collect()
    args = sys.argv[1:]
    if args:
        targets = {}
        for a in args:
            a = os.path.relpath(os.path.abspath(a), ROOT)
            if os.path.isdir(os.path.join(ROOT, a)):
                for dp, _, fs in os.walk(os.path.join(ROOT, a)):
                    for f in fs:
                        if f.endswith(".html"):
                            r = os.path.relpath(os.path.join(dp, f), ROOT)
                            targets[url_for(r)] = r
            elif a.endswith(".html"):
                targets[url_for(a)] = a
    else:
        targets = pages

    hard, warn, inbound = [], [], {}
    for url, rel in sorted(targets.items()):
        check(rel, pages, assets, redirects, inbound, hard, warn)

    # orphan check only meaningful on a full run
    if not args:
        sm = ""
        smp = os.path.join(ROOT, "sitemap.xml")
        if os.path.exists(smp):
            sm = open(smp).read()
        sm_raw_urls = re.findall(r"<loc>([^<]+)</loc>", sm)
        # Trailing-slash regression guard (Aug 21 2026 CTO brief, P2): the slash
        # and no-slash forms of a page were indexing independently in GSC and
        # splitting clicks/impressions between them. The sitemap must only ever
        # emit the canonical no-slash form (root "/" is the sole exception).
        for u in sm_raw_urls:
            path = u.replace("https://marketics.io", "") or "/"
            if path != "/" and path.endswith("/"):
                hard.append(f"sitemap.xml: trailing-slash entry {u!r} (emit the no-slash canonical form)")
        sm_urls = {
            (u.replace("https://marketics.io", "") or "/").rstrip("/") or "/"
            for u in sm_raw_urls
        }
        for u in sorted(sm_urls & set(pages)):
            if u != "/" and not (inbound.get(u, set()) - {u}):
                warn.append(f"{pages[u]}: in sitemap but no inbound internal link (orphan)")

    if warn:
        # Group by message type (text after the file prefix) so known, broad debt
        # collapses to one line and a NEW warning of a different kind stands out.
        groups = {}
        for w in warn:
            _, _, msg = w.partition(": ")
            key = re.sub(r"'[^']*'", "'…'", re.sub(r"= \d+", "= N", msg))
            groups.setdefault(key, []).append(w.split(":")[0])
        print(f"⚠  {len(warn)} warning(s) in {len(groups)} categor(y/ies):")
        for key, files in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            if len(files) <= 4:
                for f in files:
                    print(f"   - {f}: {key}")
            else:
                print(f"   - {key} — {len(files)} pages (tracked debt): {files[0]}, {files[1]}, … +{len(files)-2}")
        print()
    if hard:
        print(f"✗ {len(hard)} hard failure(s):")
        for h in hard:
            print(f"   - {h}")
        sys.exit(1)
    print(f"✓ site invariants pass ({len(targets)} page(s) checked, {len(warn)} warning(s))")


if __name__ == "__main__":
    main()
