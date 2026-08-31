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
    # A1 (board addendum, 2026-08-30): one turnaround phrasing — "48 hours or
    # less" — on every surface that promises the audit. Published promise is
    # 48h; the 24h internal delivery target is not a published claim.
    "2\u20133 business days", "2-3 business days",
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
# ── Paid landing pages: the no-exit rule (Rev C §1, Strategy addendum 2026-08-27) ──
# These pages are bought traffic. Every outbound link is a leak, and the page has
# exactly one sanctioned exception: the fine-print footer's privacy/terms links,
# which ad-platform destination policy effectively requires on a page collecting
# personal data. Anything else that links off-page is a regression, not a choice.
# Enforcing an existing ruling — not a canon change.
NO_EXIT_PAGES = {"lp/keep-control/index.html"}
NO_EXIT_ALLOW = ("/legal", "/legal?tab=terms")

# Contrast tokens retired by Design. Site-wide these are known debt on the older
# page designs (Home, Pricing, Method, case studies, intel) and are Design's to
# schedule; the pages built to the current tokens must not regress into them.
RETIRED_GRAYS = ("#6B6A65", "#55534E")

# ── Pen-name integrity (registry v3.11) ──
# "Jamie Melgar" is the byline Cost Seg Smart publishes editorial under. It is a
# pen name for a firm's content, not a person, and the disclosure is what keeps
# that true at face value — so the byline and the disclosure are not allowed to
# drift apart. Compared entity- and whitespace-insensitively via _flat(), since
# the apostrophe ships as &rsquo; in markup and as U+2019 in JSON-LD.
PEN_NAME = "Jamie Melgar"
DISCLOSURE = ("jamie melgar is the byline used for editorial content from cost seg smart, "
              "marketics' cost segregation partner. cost seg smart and marketics are "
              "referral partners.")
# Pages that may name the byline without carrying the disclosure: listings that
# link to the article rather than publishing it. The hub card names the article,
# not the author, so this is empty today and should stay small.
PEN_NAME_EXEMPT: set = set()


def _flat(raw: str) -> str:
    """Rendered text: tags stripped, entities resolved, whitespace collapsed.

    Tags have to go before the compare. The disclosure links the byline in the
    article and does not on the author page, so matching against markup would
    pass one and fail the other for no reason a reader could see.
    """
    txt = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    return re.sub(r"\s+", " ", htmllib.unescape(txt)).lower().replace("’", "'")

# "24 hours" cannot be a blanket retired token: /pricing uses it for PAYOUT
# SETTLEMENT ("about 24 hours after the guest checks in"), which is a different
# claim wearing the same phrase — the exact trap the Aug 30 sweep caught. So the
# rule is scoped instead: nobody but /pricing may say it. If a page legitimately
# needs the phrase for something other than audit turnaround, add it here with a
# note saying which claim it is.
TURNAROUND_EXEMPT = {
    "pricing/index.html": "payout settlement timing, not audit turnaround",
}
CURRENT_TOKEN_PAGES = {"lp/keep-control/index.html"}

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
        # Skip VCS, scratch, and local tool output. `.lighthouseci/` holds the
        # HTML reports a local `lhci autorun` drops in the repo root: gitignored,
        # so they never deploy, but this walk reads the filesystem rather than
        # git and would otherwise audit them as if they were site pages —
        # inflating the page count and the warning list for whoever ran it last.
        if any(x in dp for x in ("/.git", "/scratchpad", "/.lighthouseci", "/node_modules")):
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


def redirect_patterns(redirects):
    """Netlify placeholder rules, compiled.

    A rule like `/costseg/:placement` is stored literally by collect(), so a
    real link to /costseg/intel-article would be reported broken. `:param`
    matches one path segment, `*` (splat) matches the rest.
    """
    pats = []
    for r in redirects:
        if ":" not in r and "*" not in r:
            continue
        rx = "".join(r"[^/]+" if seg.startswith(":") else re.escape(seg)
                     for seg in re.split(r"(?<=/)", r)).replace(re.escape("*"), ".*")
        pats.append(re.compile("^" + rx.rstrip("/") + "$"))
    return pats


EXTERNAL = re.compile(r"^(https?:)?//|^mailto:|^tel:|^javascript:|^#|^data:")
ISO_TZ = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")


def check(rel, pages, assets, redirects, rpats, inbound, hard, warn):
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
        if (norm in pages or norm in redirects or pth in assets or norm in assets
                or any(rx.match(norm) for rx in rpats)):
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

    # 6. FAQ pair check (Rev C, 2026-08-27): where a page renders FAQ accordions
    # AND carries FAQPage schema, the two must be verbatim identical. The schema
    # is generated from the copy file's strings; if someone edits the rendered
    # answer and not the schema (or the reverse), Google is shown different text
    # than the visitor — which is both a structured-data violation and a claims
    # risk on a page that states the fee. Only fires when both halves exist, so
    # it costs nothing on pages that have one or neither.
    rendered_faq = re.findall(
        r"<summary><h3>(.*?)</h3></summary>\s*<p class=\"fa\">(.*?)</p>", raw, re.S)
    if rendered_faq:
        schema_faq = []
        for block in p.jsonld:
            try:
                d = json.loads(block)
            except Exception:
                continue
            for node in (d if isinstance(d, list) else [d]):
                if isinstance(node, dict) and node.get("@type") == "FAQPage":
                    for q in node.get("mainEntity", []):
                        schema_faq.append((q.get("name", ""),
                                           (q.get("acceptedAnswer") or {}).get("text", "")))
        if schema_faq:
            def norm(x):
                return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", x))).strip()
            r = [(norm(a), norm(b)) for a, b in rendered_faq]
            sm = [(norm(a), norm(b)) for a, b in schema_faq]
            if len(r) != len(sm):
                hard.append(f"{where}: FAQ pair mismatch — {len(r)} rendered vs {len(sm)} in schema")
            else:
                for idx, (ra, sa) in enumerate(zip(r, sm)):
                    if ra == sa:
                        continue
                    # Say which half diverged: printing two identical-looking
                    # questions when it was the answer that changed sends the
                    # next person looking in the wrong place.
                    part = "question" if ra[0] != sa[0] else "answer"
                    ri, si = (ra[0], sa[0]) if part == "question" else (ra[1], sa[1])
                    hard.append(f"{where}: FAQ {part} mismatch at #{idx+1} "
                                f"({ra[0][:44]!r}):\n       rendered: {ri[:90]!r}"
                                f"\n       schema  : {si[:90]!r}")
                    break

    # 7. no-exit rule on paid landing pages
    if where in NO_EXIT_PAGES:
        for href in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', raw):
            if href.startswith("#"):
                continue                       # in-page anchor: the CTA path itself
            if href in NO_EXIT_ALLOW:
                continue                       # the sanctioned fine-print footer
            hard.append(f"{where}: paid LP no-exit rule — outbound link {href!r} "
                        f"(only in-page anchors and the fine-print footer are allowed)")

    # 8. retired contrast tokens on pages built to the current palette
    if where in CURRENT_TOKEN_PAGES:
        for g in RETIRED_GRAYS:
            if g.lower() in raw.lower():
                hard.append(f"{where}: retired contrast token {g} — this page is built "
                            f"to the current accessible tokens (--dim/--faint)")

    # 9. the chat widget is loaded from mkx-consent.js and nowhere else (B4).
    # Inline per-page loaders are what put a third-party script on 33 pages for
    # a passive visitor, under no consent decision. One loader, one policy.
    if "widgets.leadconnectorhq.com/loader.js" in raw:
        hard.append(f"{where}: inline chat-widget loader — the widget is loaded from "
                    f"mkx-consent.js only, which restricts it by page and gates it on "
                    f"consent (board addendum B4)")

    # 10. turnaround promise — one phrasing, per board addendum A1
    if "24 hours" in raw and where not in TURNAROUND_EXEMPT:
        hard.append(f"{where}: retired turnaround phrasing '24 hours' — the published "
                    f"promise is '48 hours or less' everywhere (board addendum A1)")

    # 11. pen-name integrity (registry v3.11).
    # A pen name is a publishing convention; a manufactured person is a false
    # claim. The difference is a handful of fields, and every one of them is
    # the kind of thing a later "let's flesh out the author page" edit adds
    # without meaning anything by it. So it is a gate, not a note in a doc.
    if where.startswith("authors/"):
        blob = " ".join(p.jsonld)
        if '"Person"' in blob:
            hard.append(f"{where}: author page emits Person schema — a pen name asserted "
                        f"as a verified individual is the one thing that makes it a false "
                        f"claim. WebPage only (registry v3.11)")
        if "sameAs" in blob:
            hard.append(f"{where}: author page emits sameAs — there is no external identity "
                        f"to link a pen name to (registry v3.11)")
        for host in ("linkedin.com", "twitter.com", "x.com/", "facebook.com", "instagram.com"):
            if host in raw.lower():
                hard.append(f"{where}: author page links {host} — no social profile for a "
                            f"pen name (registry v3.11)")
        for word in ("founder", "co-founder", "years of experience", "CPA", "headshot"):
            if re.search(rf"\b{re.escape(word)}\b", raw, re.I):
                hard.append(f"{where}: author page carries a credential or title "
                            f"({word!r}) — name and one line only (registry v3.11)")

    # Wherever the pen name is published, the disclosure travels with it.
    if PEN_NAME in raw and where not in PEN_NAME_EXEMPT and DISCLOSURE not in _flat(raw):
        hard.append(f"{where}: uses the {PEN_NAME!r} byline without the partner disclosure "
                    f"line — it is required verbatim on the author page and at the foot of "
                    f"every article carrying the byline (registry v3.11)")

    # 12. no inline gtag.js loader on any page (registry v3.12).
    # gtag.js is loaded once, from mkx-consent.js, after this file has decided
    # consent for the visitor's region. Google's own setup page tells you to
    # paste a <script src="...gtag/js?id=..."> into every page's <head>, which
    # would register the destination before any consent decision — the same
    # failure B4 fixed for the chat widget, and the reason that one is a gate
    # too. Additional destinations are `gtag('config', ID)` in mkx-consent.js.
    if "googletagmanager.com/gtag/js" in raw:
        hard.append(f"{where}: inline gtag.js loader — the tag is loaded once from "
                    f"mkx-consent.js, after consent is decided; extra destinations "
                    f"are a gtag('config', ID) there, not a second script tag "
                    f"(registry v3.12)")

    # A page-view conversion scores every pageview as a lead. The paid
    # conversion is `generate_lead_paid` on form success (addendum A2, named v3.13).
    if "'conversion'" in raw or '"conversion"' in raw:
        if re.search(r"gtag\(\s*['\"]event['\"]\s*,\s*['\"]conversion['\"]", raw):
            hard.append(f"{where}: page-level Google Ads conversion event — the paid "
                        f"conversion is the audit lead, fired on form success, not a "
                        f"pageview (board addendum A2, registry v3.12)")

    # 12b. structural warnings
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
    rpats = redirect_patterns(redirects)
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
        check(rel, pages, assets, redirects, rpats, inbound, hard, warn)

    # Paid and organic never share a conversion counter (board ruling 4; Strategy
    # restated it 2026-08-31 when naming the paid event). If they shared a name,
    # organic leads would train the paid bidding signal — the opposite of what
    # the test is measuring, and invisible once it happens because both counters
    # would simply look healthy. Compared against the events every OTHER page
    # fires rather than a hardcoded name, so renaming the organic event cannot
    # silently collide either.
    if not args:
        lp_rel = "lp/keep-control/index.html"
        lp_path = os.path.join(ROOT, lp_rel)
        if os.path.exists(lp_path):
            lp_src = open(lp_path, encoding="utf-8").read()
            m = re.search(r"MKX_LP_EVENT\s*=\s*['\"]([^'\"]+)['\"]", lp_src)
            paid = m.group(1) if m else None
            if not paid:
                hard.append(f"{lp_rel}: paid conversion event name not found — it is "
                            f"held in MKX_LP_EVENT so it stays greppable and gateable "
                            f"(board ruling 4)")
            else:
                organic = set()
                for u, rel in sorted(pages.items()):
                    if rel == lp_rel:
                        continue
                    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
                    organic.update(re.findall(
                        r"gtag\(\s*['\"]event['\"]\s*,\s*['\"]([^'\"]+)['\"]", src))
                if paid in organic:
                    hard.append(f"{lp_rel}: paid conversion event {paid!r} is also fired "
                                f"by an organic page — paid and organic never share a "
                                f"counter (board ruling 4)")

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
