# Marketics Site Audit — July 2026

**Run:** 2026-07-04 · full-repo + config audit against `main` (post-PR #31) per the CTO audit brief of 2026-07-03.
**Author:** Code.
**Note on live checks:** this session's network policy blocks outbound requests to `marketics.io` and all external hosts, so live header/redirect behavior and external-link liveness are diagnosed from config and marked **[verify live]** where applicable. Verification commands are at the bottom.
**Public visibility:** this file is force-shadowed to 404 in `_redirects` so it never serves from the live site. Sensitive values (the /audits token) are deliberately omitted.

---

## P0 — live-wrong (broken behavior, schema errors, canon violations)

### P0-1 · CSP blocks the Calendly booking widget on /join/confirmation — **FIXED**
`join/confirmation/index.html` loads `assets.calendly.com/widget.js` + `widget.css` and embeds a `calendly.com` iframe. The site-wide CSP in `netlify.toml` allowed none of those hosts (script-src, style-src, frame-src). If the CSP header is enforced, **a paying customer landing on the post-checkout page gets a blank box where the onboarding-call scheduler should be.** Lighthouse CI cannot catch this (local static server = no headers; `csp-xss` assertion is off).
**Fix shipped:** `assets.calendly.com` added to script-src + style-src, `calendly.com` to frame-src. **[verify live: book-flow test after deploy]**

### P0-2 · CSP blocks Google Fonts on ~45 pages — **FIXED (allowlist); migration → P2-1**
Only `/` (home), `/results`, and the audit deliverable use self-hosted `/fonts/fonts.css`. The other ~45 pages still load `fonts.googleapis.com/css2` stylesheets — and CSP style-src/font-src allowed neither `fonts.googleapis.com` nor `fonts.gstatic.com`. If enforced, all those pages silently render in fallback system fonts (brand fonts Josefin Sans / DM Sans / DM Mono never load).
**Fix shipped:** both hosts added to CSP. The correct long-term fix is finishing the self-hosted migration (P2-1), then removing these hosts again.

### P0-3 · Cloudflare `email-protection` artifacts — contact emails render as "[email protected]" and link to 404s
Leftovers from the Squarespace/Cloudflare era: `<a href="/cdn-cgi/l/email-protection#…">` plus `/cdn-cgi/scripts/.../email-decode.min.js`. Netlify has no `/cdn-cgi/` — the decoder 404s, so visitors see literal **"[email protected]"** and clicking leads to a 404. Decoded addresses (XOR): `jason@`, `privacy@`, `legal@`, `guarantee@marketics.io`.
- **/pricing** (enterprise card "Contact Jason directly →"): **FIXED** — now a plain `mailto:jason@marketics.io`; dead decoder script removed. Link text unchanged.
- **/join** (signature line of the embedded Co-Host Agreement): **ROUTED to counsel** — inside the agreement block, which Code does not touch (Part B guardrail). Bundle with the §-rewrite.
- **/legal** (3 instances: privacy@, legal@, guarantee@): **ROUTED to counsel** — same guardrail. Note **`guarantee@marketics.io`** is also a refund-canon stray; counsel should pick the replacement address (e.g. `deposits@` or `legal@`) as part of the Part B language rewrite.

### P0-4 · /legal links to `/privacy` and `/terms` — both 404 — **FIXED (via redirects; page untouched)**
`legal/index.html` links to `/privacy` and `/terms`; neither path exists and neither had a redirect. Fixed without touching /legal: `_redirects` now 301s `/privacy → /legal` and `/terms → /legal?tab=terms`.

### P0-5 · /case-studies/wally-puerto-rico has **no structured data at all** — **FIXED**
The other two case studies carry Article JSON-LD; Wally had none. Added a complete Article block (headline, description, image, author+url, publisher+url, ISO-8601+tz dates matching the page's actual 2026-04-15 git publish date).

### P0-6 · Case-study Article schemas incomplete (montreal-hotel, anthony-san-antonio) — **FIXED**
Both were missing `image`, `dateModified`, `author.url`, and used date-only `datePublished` (fails the site's own schema standard). Completed both; dates normalized to `2026-04-15T09:00:00-04:00`.

### P0-7 · /markets FAQPage schema drifted from rendered copy — **FIXED**
The "how fast do properties improve" answer: rendered copy includes "— including algorithm positioning, review velocity, and seasonal calibration — … which is why we benchmark against that window"; the schema had a truncated older version. Schema synced to the rendered text verbatim (schema follows copy — the /markets refund lesson applied). All other FAQPage instances site-wide verified in sync (two initial flags on intel pages were tooling false-positives from anchor-tag normalization; hand-verified identical).

### P0-8 · Six internal links carry trailing slashes → forced 301 hops — **FIXED**
`/intel/*/thank-you → /intel/*/report/` (4×) and `/intel/{montreal,nashville}/report → /intel/{market}/#audit` (2×). All now slash-less. (Noindexed pages, so low SEO impact, but zero-cost fix.)

### P0-9 · Trailing-slash normalization only covered depth-1 URLs — **FIXED**
`netlify.toml`'s rule `from = "/:splat/"` uses a **named placeholder, which matches exactly one path segment** — so `/method/` → 301 `/method` works, but `/intel/miami/`, `/markets/austin/`, `/case-studies/x/` were never normalized and (via Netlify's native folder serving) return **duplicate 200s** at the slash variant. Canonical tags mitigate indexing damage, but this feeds GSC duplicate/redirect noise. Added depth-2 and depth-3 rules. **[verify live: `curl -I https://marketics.io/intel/miami/` → expect 301 to `/intel/miami`]**

**P0 tally: 9 findings — 7 fixed in this PR, 2 routed to counsel (P0-3 /join + /legal instances).**

---

## P1 — indexing blockers (the GSC buckets)

### P1-1 · "Page with redirect" (34 entries) — expected, verify against export
Structural accounting: 19 Squarespace-migration 301s + `/call` + junk-numeric + `http→https` / `www→apex` variants + depth-1 trailing-slash variants ≈ the reported 34. These are **working as intended** — GSC reports them as excluded-by-design, not errors. Two real contributors are now fixed: internal links that hit redirects (P0-8) and the depth-2/3 duplicate-200s (P0-9), which after deploy become clean single-hop 301s.
**Action (Jason, 5 min):** export the 34 URLs from GSC → confirm every entry is either a migration source, a protocol/host variant, or a trailing-slash variant. Anything outside those three buckets, send to Code. No redirect chains >1 hop exist in config; no sitemap URL redirects; sitemap ↔ live tree match 1:1 (39 URLs, all canonical-to-self, all indexable).

### P1-2 · "Crawled – currently not indexed" (33 pages) — classified into four buckets
Without the GSC URL export I classify by page evidence; the export will confirm proportions.
- **Bucket A — thin templated market pages (9):** all `/markets/*` city pages run 243–268 words of near-identical template. Classic thin-content exclusions. **Route to Strategy:** expand each with market-specific data (the intel reports already hold Miami/Nashville material), consolidate into `/markets`, or accept non-indexing.
- **Bucket B — near-duplicate pair:** `/intel/trust` ("The Trust Architecture: Marketics") vs `/intel/trust-architecture` ("The Trust Architecture: How Every Signal…"). Same topic, near-same title; Google will typically index at most one. **Route to Strategy:** consolidate (301 one into the other) or re-title/re-scope the older `/intel/trust`.
- **Bucket C — thin hub:** `/case-studies` at 237 words. Route with Bucket A.
- **Bucket D — remainder:** young-domain crawl-budget lag (site relaunched 2026); no structural defect found — canonicals, sitemap, robots all clean. Time + internal links (P1-3) are the lever.

### P1-3 · /intel hub omits three live intel pages
`/intel` cards + its ItemList (11 entries, internally consistent) skip **/intel/economics, /intel/trust-architecture, /intel/airbnb-cohost-revenue-share-model** — all live, in sitemap, and competing for indexing with weak internal linking. **Route to Strategy (needs card copy):** proposed card text = each page's existing meta description (no new claims). Code can wire it same-day on approval; ItemList count goes 11 → 14 in the same edit.

### P1-4 · Index-PR wiring gaps (staged branch, ships with the Index)
- `/results` mentions the 42%+ benchmark but doesn't link `/intel/str-performance-index` (hub-wiring rule: every gated benchmark mention links to the Index). Code adds the link to the staging commit before the Index PR.
- `/intel` hub has no card for the Index page (fold into P1-3's approval).
- Reminder (out of Code scope until data): live `~42` instances (homepage, 4 intel pages, method, pricing, results, llms.txt) are all already corrected to `42%+` in the staging commit and go live with the Index PR — deliberately not shipped here.

---

## P2 — hygiene / performance / a11y

- **P2-1 · Finish the self-hosted-fonts migration** (~45 pages still on Google Fonts). Kills two third-party origins, removes a GDPR surface, and lets us re-tighten CSP. Mechanical head-block swap replicating the homepage pattern; note self-hosted set lacks DM Mono 300 (falls back to 400 — acceptable) . One PR, no copy changes.
- **P2-2 · Nav wordmark served from `assets.cdn.filesafe.space`** (LeadConnector CDN) on every page; local logo assets (`/assets/logo*.svg`, `/images/marketics-logo.svg`) sit unused. Third-party single point of failure for the site's logo. Needs a visual-parity check before swapping — route, then mechanical.
- **P2-3 · Lighthouse CI only audits `/` and `/calculator`.** Intel/article, market, and join templates are never measured; CSP-dependent failures are invisible locally. Recommend adding one URL per template family to `lighthouserc.json` (and a periodic live-URL run so headers are exercised).
- **P2-4 · No `<main>` landmark on ~30 pages** (intel articles have it; most non-article pages don't). `/join` + `/join/confirmation` also lack `<footer>`. Report-level; fold into the next template-touching pass per page.
- **P2-5 · `/legal` has two `<h1>`s** — counsel-scoped file; bundle with Part B.
- **P2-6 · Spotify embed iframes on /media lacked accessible titles** — **FIXED** (title attributes added).
- **P2-7 · `.DS_Store` ×6 tracked in repo** — **FIXED** (removed + `.gitignore` added).
- **P2-8 · External links unverifiable from this environment** — notably the nav-logo CDN URL, `link.crmvo.com` booking redirect, `youtu.be`/`@revlabs` links, `airbnb.ca/rp/fifa2026miami`, podcast links. **[verify live: run the link-check block below]**
- **P2-9 · `netlify.toml` placeholder naming:** the original rule's placeholder is named `:splat`, shadowing Netlify's reserved splat keyword — it works as a single-segment placeholder but reads as a wildcard. Rename to `/:seg/` for clarity next time the file is touched (kept as-is now to avoid churning a working rule).

## P3 — nice-to-have

- **P3-1 · "guarantee" as CSS class/anchor names** (`.guarantee*` on /pricing /results /join, `#guarantee` anchor → visible in URLs via `/pricing#guarantee`). Not rendered copy; rename to `.deposit*`/`#deposit-terms` opportunistically (anchor rename needs the 3 inbound `#guarantee` links updated in the same pass).
- **P3-2 · Calculator "16 markets"** (benchmark-table count) vs "22 markets" (operated) — parked with Strategy on 2026-07-02; inventory only.
- **P3-3 · Unused files:** `og/*.webp` variants (og images must be jpg/png; webp never referenced), `images/mobile/*` set, `images/jason-photo-2/3/4.*`, `images/jason-section-1.*`, `images/podcast/str-investing-podcast.jpg`, `images/marketics-logo.svg`. Delete or wire on a future pass.
- **P3-4 · Internal .md files publicly fetchable** (`/CLAUDE.md`, `/intel/SCHEMA-CHECKLIST.md`). Mildly informative to competitors, harmless otherwise. This audit file is already 404-shadowed; consider the same for those two.
- **P3-5 · Canon clean bills:** zero `+32%`, zero "20 years"-near-STR, zero token leakage outside /audits/, consent gating present on every tracked page, /audits/ page carries no GA4/consent/Clarity, llms.txt format confirmed llmstxt.org-compliant, GA4 `generate_lead`/`begin_checkout` wiring intact. Sample-phrase inventory (for the Index PR update) recorded in the PR body.

---

## Post-deploy verification (Jason or Code-after-merge, ~3 min)

```bash
# 1. Trailing-slash depth-2 (expect: 301 → /intel/miami)
curl -sI -A "Mozilla/5.0" https://marketics.io/intel/miami/ | grep -i "HTTP\|location"
# 2. CSP now includes calendly + google fonts (expect both hosts in the header)
curl -sI -A "Mozilla/5.0" https://marketics.io/join/confirmation | grep -i content-security-policy
# 3. Booking widget renders: open /join/confirmation in a browser — Calendly loads, no console CSP errors
# 4. Fonts on an intel page: open /intel/algorithm — Josefin Sans headline (not system sans), no CSP errors
# 5. /privacy and /terms now redirect (expect 301s)
curl -sI -A "Mozilla/5.0" https://marketics.io/privacy | grep -i "HTTP\|location"
# 6. This file is not public (expect 404)
curl -s -o /dev/null -w "%{http_code}\n" -A "Mozilla/5.0" https://marketics.io/marketics-site-audit-2026-07.md
```
