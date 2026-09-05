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
    # C3 item 7 (board addendum C, 2026-09-01): the last three holdouts lived in
    # /legal, which Code could not edit until C2 named a ruler for that lane.
    # Now corrected, so the gloss that stated the gross basis outright is gated
    # with the rest of them rather than left as a documented exception.
    "gross booking revenue",
    # C3 item 3: the policy described a Meta Pixel that has never existed on
    # this site. Retired as a token so a future "add our vendors back" edit
    # fails rather than reintroducing a vendor we do not run. If a Pixel is ever
    # actually installed, this entry is the thing that forces the conversation.
    "Meta Pixel",
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
# EMPTY as of 2026-09-01, and that is the point: the fee-basis entry for
# legal/index.html (v3.4) was here for five days because Code could not edit the
# document, not because the contradiction was acceptable. Board Addendum C2 named
# an interim ruler for that lane, C3 ruled the corrections, and Jason approved
# them — so §390, §588 and §602 now say net payout like §601 and every marketing
# surface, and the exemption is deleted rather than kept as a courtesy.
# The dict stays because the mechanism is still right: a document Code must not
# edit gets a visible warning, never a silent pass.
# ── Paid landing pages: the no-exit rule (Rev C §1, Strategy addendum 2026-08-27) ──
# These pages are bought traffic. Every outbound link is a leak, and the page has
# exactly one sanctioned exception: the fine-print footer's privacy/terms links,
# which ad-platform destination policy effectively requires on a page collecting
# personal data. Anything else that links off-page is a regression, not a choice.
# Enforcing an existing ruling — not a canon change.
NO_EXIT_PAGES = {"lp/keep-control/index.html"}
NO_EXIT_ALLOW = ("/legal", "/legal?tab=terms")

# ── Paid-only surfaces are never linked from organic surfaces (Strategy brief
# 2026-09-03 §5.3, registry v3.31) ──
# The inverse of the no-exit rule above, and it protects a different thing. A paid
# LP carries a paid conversion counter (generate_lead_paid) and is noindex. One
# link from an indexed page pours organic traffic into that counter, and the paid
# numbers stop meaning anything -- silently, because a lead is still a lead. Paid
# and organic never share a counter (board ruling 4), so they must not share an
# entry point either. Organic conversion paths point to /get-started.
PAID_ONLY_PREFIX = "/lp/"

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


# ── Partner capacity (registry v3.18) ──
# Matched against _flat() output, so entity- and whitespace-insensitive.
PARTNER_CAPACITY = re.compile(
    r"\b(?:our|marketics'?s?)\s+(?:national\s+)?"
    r"(?:tax|accounting|cpa|legal)\s+(?:partner|advis[eo]r|firm)\b")


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

COUNSEL_LANE_EXEMPT: dict = {}

# ── Webhook triggers (registry v3.22) ──
# Trigger ids only, never the full URL: these strings are already public in the
# page source of every visitor's browser, but there is no reason for a grep of
# this file to hand someone a ready-to-POST endpoint.
SHARED_HOOK = "1297f709-5970-411d-b58c-e3a47721392e"   # organic: 29 files + the consent beacon
PAID_HOOK = "3c750621-84a1-444d-b64a-5712e15cfb5e"     # /lp/keep-control ONLY
# 2ebb4312-… was superseded before it ever shipped — named here so a stale copy
# of it in a branch, a doc or someone's clipboard fails loudly rather than
# quietly posting paid leads into a trigger nobody is watching.
DEAD_HOOKS = ("2ebb4312-80b3-4ef6-9e78-10e3807abc40",)

# ── sendBeacon + a non-safelisted Content-Type (registry v3.30) ──
# navigator.sendBeacon() ALWAYS sends with credentials mode 'include'. That is
# specified behaviour, not a browser quirk and not an extension. A Blob typed
# anything outside the three CORS-safelisted values therefore forces a preflight,
# and a preflight can never be satisfied by the wildcard
# `Access-Control-Allow-Origin: *` that most third-party webhooks answer with —
# so the request is dropped before it leaves the browser. Console errors, zero
# data, and nothing in the calling code can tell that nothing was delivered.
#
# The consent beacon shipped in exactly this shape and never delivered a single
# event. Its errors were then misread as a broken LEAD path and "fixed" with a
# Content-Type change GHL rejects, dropping ~20 minutes of real submissions
# (registry v3.29/v3.30). Gated so the shape cannot return on any file.
def _first_touch_guard_body(src):
    """The body of `if (!sessionStorage.getItem(LAND_KEY)) { ... }`, braces matched.

    Slicing on the next `} catch` instead was the obvious shortcut and it is
    WRONG: a write moved out of the `if` but left inside the same `try` still
    falls in that slice, so the check passed on exactly the regression it exists
    to catch. Found by negative control before it shipped. The closing brace of
    the if-block is the boundary that means something, so it has to be found.
    """
    i = src.find("if (!sessionStorage.getItem(LAND_KEY))")
    if i < 0:
        return ""
    start = src.find("{", i)
    if start < 0:
        return ""
    depth = 0
    for j in range(start, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[start:j]
    return ""


# ── <br> inside a heading (registry v3.36 item 6; CTO authorised 2026-09-05) ──
# A <br> yields NO whitespace when tags are stripped, so extraction reads
# "YOUR MARKET. MASTERED." as "YOURMARKET.MASTERED." -- one token, in every AI
# summariser and snippet extractor that flattens markup. 60 were removed across
# 28 files in #143 and replaced with <span class="hln"> blocks joined by a REAL
# space: the space is what fixes extraction, display:block restores the break.
#
# Until now that fix was defended ONLY by a production smoke assertion, which
# speaks after a merge -- so a regression would ship, get crawled, and surface on
# the next daily run rather than in review. A <br> in a heading looks like
# ordinary markup to anyone who was not there, which makes it the one GEO finding
# most likely to be undone by accident. Repo side and served side now agree, the
# standard the other three already met.
#
# Comments, <script> and <style> go BEFORE any matching. The original sweep
# corrupted /calculator by matching an <h1> inside an HTML COMMENT and swallowing
# 93 lines to the next </h1>. A regex that finds tags will find them in comments
# too, and a checker has exactly the same exposure a rewriter does.
HEADING_BR = re.compile(r"<h[1-6]\b[^>]*>(?:(?!</h[1-6]>).)*?<br\b", re.S | re.I)


def heading_br_violations(raw):
    """Headings that contain a <br>. Empty list = fine."""
    src = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    src = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", src, flags=re.S | re.I)
    return [re.sub(r"\s+", " ", m.group(0))[:90] for m in HEADING_BR.finditer(src)]


SAFELISTED_TYPES = ("text/plain", "application/x-www-form-urlencoded",
                    "multipart/form-data")
SENDBEACON_CALL = re.compile(r"sendBeacon\s*\(([^;]{0,300})")

def sendbeacon_violations(raw):
    """Content-Types passed to sendBeacon that will fail preflight. Empty = fine."""
    bad = []
    for args in SENDBEACON_CALL.findall(raw):
        for t in re.findall(r"type\s*:\s*['\"]([^'\"]+)['\"]", args):
            if t.split(";")[0].strip().lower() not in SAFELISTED_TYPES:
                bad.append(t)
    return bad

# Same phrase, different claim — the trap the Aug 30 turnaround sweep caught and
# the reason "24 hours" is scoped rather than blanket-retired. A retired token
# gates a CLAIM, not a string, so a page using the same words for something else
# is exempted here with the reason written down, never by softening the token.
# Caught by the gate on its first run, which is what it is for.
SAME_PHRASE_EXEMPT = {
    "calculator/index.html": {
        "gross booking revenue":
            "what the calculator MEASURES (top-line, before platform and cleaning "
            "fees) — not the basis Marketics' 10% fee is charged on. The page says "
            "so explicitly in its assumptions list. Different claim, same words.",
    },
}

# Required tokens: the inverse gate. A retired token catches copy that came back;
# this catches copy that quietly went away. /legal must name the ad platform in
# use — that omission is the whole reason for the 2026-09-01 counsel routing, and
# it is the kind of thing a later tidy-up of a vendor list removes without
# noticing (registry v3.20, board addendum C3 item 1).
REQUIRED_TOKENS = {
    "legal/index.html": ("Google Ads", "net payout", "Do Not Sell or Share",
                         "Global Privacy Control", "click identifier"),
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
            if tok in SAME_PHRASE_EXEMPT.get(where, {}):
                continue
            if tok in COUNSEL_LANE_EXEMPT.get(where, ()):
                warn.append(f"{where}: counsel-lane token still present: {tok!r} "
                            f"(Code must not edit this document — see registry v3.4)")
            else:
                hard.append(f"{where}: retired token present: {tok!r}")

    # 1b. required tokens — copy that must not quietly disappear (registry v3.20)
    for tok in REQUIRED_TOKENS.get(where, ()):
        if tok not in raw:
            hard.append(f"{where}: required token missing: {tok!r} — the document has "
                        f"to keep describing this (board addendum C3, registry v3.20)")

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

    # 7b. and nothing organic links INTO a paid-only surface (registry v3.31).
    if not url.startswith(PAID_ONLY_PREFIX):
        for href in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', raw):
            if href.split("?")[0].split("#")[0].rstrip("/").startswith(PAID_ONLY_PREFIX.rstrip("/")):
                hard.append(f"{where}: links to the paid-only surface {href!r} — a paid LP "
                            f"is noindex and carries the paid conversion counter, so organic "
                            f"traffic reaching it corrupts that counter silently. Organic "
                            f"conversion paths point to /get-started (registry v3.31)")

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

    # 11b. partner capacity (registry v3.18).
    # Cost Seg Smart's own terms disclaim being a CPA firm, accounting firm, law
    # firm or RIA, and our referral agreement obliges us not to hold them out as
    # able to advise. "Our tax partner" implies exactly the capacity they
    # disclaim; "cost segregation partner" describes what they actually produce.
    # Scoped to the possessive form on purpose — a page telling a reader to check
    # with THEIR own tax advisor is the correct sentence and must keep passing.
    m = PARTNER_CAPACITY.search(_flat(raw))
    if m:
        hard.append(f"{where}: describes a partner as {m.group(0)!r} — an advisory "
                    f"capacity our referral partner disclaims. They run cost "
                    f"segregation studies: 'cost segregation partner' "
                    f"(Strategy ruling 2026-09-01, registry v3.18)")

    # 11c. webhook payload keys a GHL mapping row points at (v3.21, v3.35).
    # A form field's `name` and the JSON key the webhook actually SENDS are two
    # different things here: the handler reads elements by id and hand-builds the
    # payload, so `name="listing_url"` is never transmitted — `listingUrl` is.
    # That gap cost a wrong diagnosis on 2026-09-01 and is invisible from the
    # markup, so the transmitted keys are gated by name. A rename here silently
    # empties a CRM field and a conditional email branch downstream; nothing
    # errors, the lead just arrives blank.
    # /get-started is listed as of 2026-09-05: Jason wired six mapping rows against
    # its keys that day (five utm_* plus first_touch_lp <- landingPage), so those
    # key names became load-bearing for the organic path the same way the LP's are.
    # Before that they were inert and a rename cost nothing; now it silently empties
    # a field on every organic lead.
    PAYLOAD_KEYS = {
        "lp/keep-control/index.html": (
            "email", "listingUrl", "pricingOwner", "pricing_owner", "source",
            "gclid_first",
            "utm_source_first", "utm_medium_first", "utm_campaign_first",
            "utm_content_first", "utm_term_first", "first_touch_lp",
            "first_touch_ts",
        ),
        "get-started/index.html": (
            "email", "source", "landingPage", "submittedAt",
            "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
            "first_touch_ts",
        ),
    }
    if where in PAYLOAD_KEYS:
        for key in PAYLOAD_KEYS[where]:
            if not re.search(rf"^\s*{re.escape(key)}\s*:", raw, re.M):
                hard.append(f"{where}: webhook payload key {key!r} missing — a GHL "
                            f"mapping row points at this key BY NAME, so renaming or "
                            f"removing it empties that CRM field silently, with no "
                            f"error on either side (registry v3.35)")

    # 11d. the paid LP posts to its OWN webhook trigger (registry v3.22).
    # SHARED_HOOK is the organic one: 29 files use it, the consent beacon
    # included. The paid path had to be separated because a workflow sharing it
    # can only tell itself apart by filtering on `source`, and a filter that
    # quietly stops matching looks exactly like a broken deploy — two hours were
    # lost to that on 2026-09-03. Gated in both directions: the LP must carry the
    # paid hook, and must not carry the shared one. A copy-paste from any other
    # form's handler would otherwise put it back without anyone noticing.
    if where == "lp/keep-control/index.html":
        if SHARED_HOOK in raw:
            hard.append(f"{where}: posts to the SHARED organic webhook trigger — the paid "
                        f"path has its own, so the paid workflow does not have to filter "
                        f"itself out of 29 other surfaces (registry v3.22)")
        if PAID_HOOK not in raw:
            hard.append(f"{where}: paid webhook trigger {PAID_HOOK!r} missing — this is the "
                        f"only entry point for the paid conversion path (registry v3.22)")
    elif PAID_HOOK in raw:
        hard.append(f"{where}: uses the PAID LP webhook trigger — it belongs to "
                    f"/lp/keep-control alone, and a second caller would put organic "
                    f"traffic into the paid conversion workflow (registry v3.22)")

    for dead in DEAD_HOOKS:
        if dead in raw:
            hard.append(f"{where}: posts to a RETIRED webhook trigger {dead!r} — it is not "
                        f"wired to any workflow, so leads sent there are lost with no "
                        f"error and no contact (registry v3.22)")

    # 11d-2. No self-review structured data (GEO brief finding 3, registry v3.36).
    # A ClaimReview whose author and itemReviewed.author are both Marketics is us
    # rating our own claim five stars. Google treats ClaimReview as fact-checking
    # markup for accredited publishers; ours asserted "Documented" about our own
    # numbers, which is the schema equivalent of citing yourself as the source.
    # Gated as a CLASS, not as two known instances: ClaimReview is banned outright
    # (we are not a fact-checking publisher and never will be), and a Review whose
    # author is Marketics is banned too. Customer reviews are untouched -- their
    # authors are Person nodes, which is exactly the distinction that makes them
    # legitimate.
    if "ClaimReview" in raw:
        hard.append(f"{where}: ClaimReview structured data — self-review markup. "
                    f"ClaimReview is fact-checking markup for accredited publishers; "
                    f"a claim we make about ourselves does not qualify "
                    f"(GEO brief finding 3, registry v3.36)")
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        try:
            parsed = json.loads(blob)
        except Exception:
            continue                      # malformed JSON-LD is caught elsewhere
        for node in (parsed if isinstance(parsed, list) else [parsed]):
            if not isinstance(node, dict):
                continue
            if str(node.get("@type", "")).endswith("Review"):
                auth = node.get("author") or {}
                name = auth.get("name", "") if isinstance(auth, dict) else ""
                if "marketics" in str(name).lower():
                    hard.append(f"{where}: {node.get('@type')} authored by "
                                f"{name!r} — self-review. A review of our own work "
                                f"must have a third-party author "
                                f"(registry v3.36)")

    # 11e. sendBeacon with a non-safelisted Content-Type is a dead request.
    for t in sendbeacon_violations(raw):
        hard.append(f"{where}: sendBeacon sends a {t!r} body — sendBeacon always uses "
                    f"credentials mode 'include', so a non-safelisted type forces a "
                    f"preflight no wildcard ACAO can satisfy and the request never "
                    f"leaves the browser (registry v3.30)")

    # 11g. first_touch_ts must be the FIRST-TOUCH moment (CTO ruling 2026-09-05).
    # The ruling that authorised this field also refused the shortcut: mapping
    # `submittedAt` into it fills the field with a real value from the WRONG
    # moment, and a CRM full of confidently wrong timestamps cannot be told apart
    # from a correct one after the fact. Blank is recoverable; wrong is not.
    #
    # This is the gate for that refusal, because the shortcut is one line and
    # reads like a simplification: `first_touch_ts: new Date().toISOString()`
    # right next to `submittedAt` doing exactly that would pass every other check
    # in this file. So the VALUE is inspected, not just the key's presence.
    m = re.search(r"^\s*first_touch_ts\s*:\s*([^,\n]+)", raw, re.M)
    if m:
        expr = m.group(1)
        if re.search(r"new\s+Date|Date\.now|submittedAt", expr):
            hard.append(f"{where}: first_touch_ts is derived from submission time "
                        f"({expr.strip()!r}) — that is a different moment and is "
                        f"already sent as submittedAt. It must come from "
                        f"mkxGetFirstTouchTS(), which reads the value captured on "
                        f"the session's first page (CTO ruling 2026-09-05)")
        elif "mkxGetFirstTouchTS" not in raw:
            hard.append(f"{where}: sends first_touch_ts but never calls "
                        f"mkxGetFirstTouchTS() — the value cannot be a first-touch "
                        f"timestamp (CTO ruling 2026-09-05)")

    # 11f. no <br> inside a heading (registry v3.36 item 6).
    for snippet in heading_br_violations(raw):
        hard.append(f"{where}: <br> inside a heading — a <br> yields no whitespace "
                    f"when tags are stripped, so extraction glues the words on "
                    f"either side into one token. Use <span class=\"hln\"> blocks "
                    f"joined by a real space (registry v3.36): {snippet!r}")

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

    # 13. ad_personalization is denied everywhere (board addendum C1, registry v3.19).
    # C1 amends B1: the two ad MEASUREMENT signals still follow the region rules,
    # but personalization is off for every visitor, including one who clicks
    # Accept in a gated region. The inline stubs already deny it; this makes a
    # later "grant everything on Accept" edit to a stub fail rather than ship.
    if re.search(r"ad_personalization\s*:\s*['\"]granted['\"]", raw):
        hard.append(f"{where}: grants ad_personalization — it is denied for every "
                    f"visitor in every region, with no Accept path that turns it "
                    f"on (board addendum C1, registry v3.19)")

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

    # The same rule for mkx-consent.js, which is where the grant actually
    # happens — the pages only carry defaults. Checked as a literal rather than
    # a variable: `ad_personalization: ad` was the B1 shape and reads correct at
    # a glance, so the gate requires the hardcoded 'denied' and rejects anything
    # derived (board addendum C1, registry v3.19).
    if not args:
        cpath = os.path.join(ROOT, "mkx-consent.js")
        if os.path.exists(cpath):
            csrc = open(cpath, encoding="utf-8").read()
            vals = re.findall(r"ad_personalization\s*:\s*([^,\n}]+)", csrc)
            if not vals:
                hard.append("mkx-consent.js: no ad_personalization in the consent "
                            "update — it must be sent explicitly denied, not omitted "
                            "(board addendum C1)")
            for v in vals:
                if v.strip() not in ("'denied'", '"denied"'):
                    hard.append(f"mkx-consent.js: ad_personalization set to {v.strip()!r} "
                                f"— it is a hardcoded 'denied' so no code path can turn "
                                f"it on (board addendum C1, registry v3.19)")

    # Click identifiers are captured ONLY where ad_storage is granted (ruled
    # Jason, 2026-09-04; registry v3.33). The gate IS the ruling: it is what
    # moots the privacy question rather than deferring it, and the
    # consent-independent variant was considered and explicitly not shipped.
    # An unconditional capture would look like a harmless simplification and
    # would silently put an advertising identifier in the CRM for a visitor who
    # was shown a banner and declined, so it fails the build instead.
    if not args:
        upath = os.path.join(ROOT, "mkx-utm.js")
        if os.path.exists(upath):
            usrc = open(upath, encoding="utf-8").read()
            if "mkx_click" in usrc or "mkxCommitClickIds" in usrc:
                if "adStorageGranted" not in usrc:
                    hard.append("mkx-utm.js: click identifiers are captured without an "
                                "ad_storage check — capture is consent-gated by ruling "
                                "(Jason, 2026-09-04), and the gate is the ruling "
                                "(registry v3.33)")
                else:
                    body = usrc.split("mkxCommitClickIds = function")[-1].split("};")[0]
                    if "adStorageGranted()" not in body:
                        hard.append("mkx-utm.js: mkxCommitClickIds() persists without "
                                    "calling adStorageGranted() — the consent gate has "
                                    "been bypassed (registry v3.33)")

    # The first-touch timestamp is written INSIDE the landing-page guard, and has
    # to stay there (CTO ruling 2026-09-05). Moving it out — or adding a second
    # unconditional write — makes it record the CURRENT page load rather than the
    # session's first, which is the same defect as mapping submittedAt into it,
    # arrived at from the other direction and much harder to see: the field fills,
    # the value looks like a timestamp, and it is wrong on every returning visitor.
    if not args:
        upath = os.path.join(ROOT, "mkx-utm.js")
        if os.path.exists(upath) and "mkx_ts" in open(upath, encoding="utf-8").read():
            usrc = open(upath, encoding="utf-8").read()
            if "mkxGetFirstTouchTS" not in usrc:
                hard.append("mkx-utm.js: captures mkx_ts but exposes no "
                            "mkxGetFirstTouchTS() reader — nothing can send it")
            writes = len(re.findall(r"setItem\(\s*TS_KEY", usrc))
            if writes != 1:
                hard.append(f"mkx-utm.js: TS_KEY is written {writes} time(s), want "
                            f"exactly 1 — a second write cannot be first-touch "
                            f"(CTO ruling 2026-09-05)")
            elif "setItem(TS_KEY" not in _first_touch_guard_body(usrc):
                hard.append("mkx-utm.js: the first-touch timestamp is written "
                            "outside the landing-page guard — it now records the "
                            "current page load, not the session's first "
                            "(CTO ruling 2026-09-05)")

    # The consent script does not talk to the CRM (registry v3.30). A beacon
    # here posted consent_impression/accept/decline/ad_optout to a GHL inbound
    # webhook and never delivered one event: sendBeacon's credentials mode made
    # the preflight unsatisfiable against GHL's wildcard ACAO. It was removed on
    # 2026-09-03 rather than re-typed, because "make it transmit" is a guess
    # about whether GHL PARSES the new type, and that exact guess broke lead
    # capture the same evening. If consent telemetry returns it goes through a
    # same-origin proxy, which has no CORS to satisfy — so a webhook URL
    # reappearing in this file means the removal was undone, not fixed.
    #
    # Both JS files get the sendBeacon gate too; check() only sees HTML.
    if not args:
        for jsrel in ("mkx-consent.js", "mkx-utm.js"):
            jspath = os.path.join(ROOT, jsrel)
            if not os.path.exists(jspath):
                continue
            jsrc = open(jspath, encoding="utf-8").read()
            for t in sendbeacon_violations(jsrc):
                hard.append(f"{jsrel}: sendBeacon sends a {t!r} body — sendBeacon always "
                            f"uses credentials mode 'include', so a non-safelisted type "
                            f"forces a preflight no wildcard ACAO can satisfy and the "
                            f"request never leaves the browser (registry v3.30)")
        cpath = os.path.join(ROOT, "mkx-consent.js")
        if os.path.exists(cpath):
            csrc = open(cpath, encoding="utf-8").read()
            # Match the URL path segment, not a hook id: a NEW trigger id would
            # sail past an id list, and any of them is the same mistake.
            for m in re.findall(r"webhook-trigger/[0-9a-f-]+", csrc):
                hard.append(f"mkx-consent.js: posts to a CRM webhook ({m}) — the consent "
                            f"beacon was removed on 2026-09-03 because sendBeacon can "
                            f"never satisfy that endpoint's preflight; telemetry from "
                            f"this file goes same-origin or not at all (registry v3.30)")

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
