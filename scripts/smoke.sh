#!/usr/bin/env bash
# smoke.sh — post-deploy verification against a real deployment.
#
# Asserts the things Lighthouse-on-a-local-server can't see: live response
# headers (CSP, X-Robots), redirect behavior, and that canon copy actually
# shipped. Born from the July 2026 audit, where an enforced CSP silently broke
# the Calendly widget and Google Fonts for weeks with nothing testing it.
#
# Usage:
#   scripts/smoke.sh https://deploy-preview-NN--marketicsio.netlify.app
#   scripts/smoke.sh https://marketics.io          # prod (may 403 non-browser UAs)
#
# Prefer a Netlify deploy-preview URL: previews don't bot-block, prod does.
set -u
BASE="${1:?usage: smoke.sh BASE_URL}"
BASE="${BASE%/}"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
pass=0 fail=0

# code URL [expected_code]  — no redirect follow; asserts the status of the URL itself
code() { curl -s -o /dev/null -A "$UA" -w "%{http_code}" --max-time 20 "$1"; }
# body URL — follows redirects, returns body
body() { curl -sL -A "$UA" --max-time 20 "$1"; }
# hdr URL — response headers only (no follow)
hdr()  { curl -sI -A "$UA" --max-time 20 "$1"; }
# loc URL — the Location header of a single redirect (no follow), path only
loc()  { curl -sI -A "$UA" --max-time 20 "$1" | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r' | sed -E 's#^https?://[^/]+##'; }

ok()   { pass=$((pass+1)); printf '  \033[32m✓\033[0m %s\n' "$1"; }
no()   { fail=$((fail+1)); printf '  \033[31m✗\033[0m %s\n' "$1"; }

echo "Smoke test against: $BASE"
echo

echo "· Status codes"
for p in "" "/method" "/pricing" "/results" "/intel/str-performance-index" "/markets/san-antonio" "/join/confirmation"; do
  c=$(code "$BASE$p"); [ "$c" = "200" ] && ok "200 $p" || no "$p returned $c (want 200)"
done

echo "· Canonical URL form (no-slash resolves 200; slash deduped by canonical tag)"
# The no-slash form is canonical and must resolve directly (no redirect).
c=$(code "$BASE/method");        [ "$c" = "200" ] && ok "/method -> 200 (canonical)" || no "/method = $c (want 200 canonical)"
# The slash form returns 200 via Netlify's directory index. A strict
# slash->no-slash 301 is NOT achievable on this platform without flattening
# every index.html to a .html file — both a netlify.toml force=true rule and
# the same rule in _redirects were tried against a deploy preview on
# 2026-08-21 and failed (see the trailing-slash comment in netlify.toml).
# Known SEO cost, tracked: GSC is indexing both variants. Until that
# structural decision is made, the canonical tag is the only lever, so assert
# it points back to no-slash on the slash-form response.
grep -q '<link rel="canonical" href="https://marketics.io/method">' <<<"$(body "$BASE/method/")" \
  && ok "/method/ served with no-slash canonical tag" || no "/method/ missing no-slash canonical tag"
grep -q '<link rel="canonical" href="https://marketics.io/intel/miami">' <<<"$(body "$BASE/intel/miami/")" \
  && ok "/intel/miami/ served with no-slash canonical tag" || no "/intel/miami/ missing no-slash canonical tag"

echo "· Legacy path redirects (Squarespace migration, single 301)"
c=$(code "$BASE/privacy");       [ "$c" = "301" ] && ok "/privacy -> 301"      || no "/privacy = $c (want 301)"
c=$(code "$BASE/terms");         [ "$c" = "301" ] && ok "/terms -> 301"        || no "/terms = $c (want 301)"

# Regression guard: the no-slash 200 rewrites (/:seg, /:a/:b) must NOT shadow the
# legacy 301s for paths that have no page. Assert both the 301 status AND the
# target — a soft-200 or wrong target would silently drop old link equity.
# depth-1 legacy (rewrite target /performance-based-pricing/index.html doesn't exist):
c=$(code "$BASE/performance-based-pricing"); t=$(loc "$BASE/performance-based-pricing")
{ [ "$c" = "301" ] && [ "$t" = "/pricing" ]; } && ok "/performance-based-pricing -> 301 /pricing" || no "/performance-based-pricing = $c -> '$t' (want 301 /pricing)"
c=$(code "$BASE/home"); t=$(loc "$BASE/home")
{ [ "$c" = "301" ] && [ "$t" = "/" ]; } && ok "/home -> 301 /" || no "/home = $c -> '$t' (want 301 /)"
# depth-2 legacy (rewrite target /markets/austin/index.html doesn't exist):
c=$(code "$BASE/markets/austin"); t=$(loc "$BASE/markets/austin")
{ [ "$c" = "301" ] && [ "$t" = "/markets" ]; } && ok "/markets/austin -> 301 /markets" || no "/markets/austin = $c -> '$t' (want 301 /markets)"
c=$(code "$BASE/intel/economics"); t=$(loc "$BASE/intel/economics")
{ [ "$c" = "301" ] && [ "$t" = "/intel/money" ]; } && ok "/intel/economics -> 301 /intel/money" || no "/intel/economics = $c -> '$t' (want 301 /intel/money)"

echo "· Partner referral redirect (Cost Seg Smart) — guards against generic-rule shadowing"
# /costseg and /costseg/:placement are listed BEFORE the generic /:seg and
# /:a/:b rewrite rules in netlify.toml specifically so they aren't shadowed.
# This is an external redirect (costsegsmart.com), so check the raw Location
# header rather than the loc() helper, which strips the host.
loc_raw() { hdr "$1" | awk 'tolower($1)=="location:"{ $1=""; print }' | tr -d '\r' | sed -E 's/^ //'; }
c=$(code "$BASE/costseg/partner-page"); l=$(loc_raw "$BASE/costseg/partner-page")
{ [ "$c" = "301" ] && [ "$l" = "https://costsegsmart.com/order/?ref=MARKETICS-Q0DZ&utm_source=marketics&utm_medium=partner&utm_campaign=costseg&utm_content=partner-page" ]; } \
  && ok "/costseg/partner-page -> 301 costsegsmart.com (utm_content=partner-page)" \
  || no "/costseg/partner-page = $c -> '$l' (want 301 costsegsmart.com utm_content=partner-page)"
c=$(code "$BASE/costseg"); l=$(loc_raw "$BASE/costseg")
{ [ "$c" = "301" ] && [ "$l" = "https://costsegsmart.com/order/?ref=MARKETICS-Q0DZ&utm_source=marketics&utm_medium=partner&utm_campaign=costseg&utm_content=direct" ]; } \
  && ok "/costseg -> 301 costsegsmart.com (utm_content=direct)" \
  || no "/costseg = $c -> '$l' (want 301 costsegsmart.com utm_content=direct)"

echo "· Not-public artifacts (404)"
# Internal docs are plain files at the repo root, so they are servable by
# default and are only hidden by the force-shadow block in _redirects. That
# makes the shadow load-bearing and easy to forget: a new internal doc is
# public the moment it merges unless someone remembers to add two lines. Every
# one of them gets asserted here, in both the extensionless and .md forms,
# since the shadow lists both and a rule covering only one still leaks.
for d in "/marketics-site-audit-2026-07" "/CANON-REGISTRY" "/CANON-SWEEP-2026-08-25" "/LEGAL-ROUTING-2026-08-27"; do
  for f in "$d" "$d.md"; do
    c=$(code "$BASE$f"); [ "$c" = "404" ] && ok "$f 404 (internal)" || no "$f = $c (want 404 — internal doc is PUBLIC)"
  done
done

echo "· Security headers"
jc=$(hdr "$BASE/join/confirmation")
grep -qi 'content-security-policy' <<<"$jc" && grep -qi 'assets.calendly.com' <<<"$jc" \
  && ok "CSP present + allows Calendly" || no "CSP missing or lacks assets.calendly.com on /join/confirmation"
grep -qi 'fonts.googleapis.com' <<<"$jc" \
  && ok "CSP allows Google Fonts" || no "CSP lacks fonts.googleapis.com"
grep -qi 'x-robots-tag:.*noindex' <<<"$jc" \
  && ok "/join noindex header" || no "/join missing X-Robots noindex"

echo "· Canon copy actually shipped"
h=$(body "$BASE/")
grep -q '45% median lift, net of market' <<<"$h" && ok "homepage: 45% net-of-market canon" || no "homepage missing 45% net-of-market canon"
ix=$(body "$BASE/intel/str-performance-index")
grep -q '45% median benchmark' <<<"$ix" && ok "Index: 45% median benchmark canon" || no "Index missing 45% median benchmark canon"

# Retired-claim sweep across every public claim surface (Aug 25 2026 canon-sweep
# brief). validate-site.py gates the REPO; this gates what is actually SERVED --
# the gap that made "stale deploy or search cache?" unanswerable without a
# manual fetch. Replaces the old homepage-only retired-canon check, which
# covered four phrasings on one page.
#
# Each alternative is scoped tightly enough to match only the retired claim:
# the bare words all appear in legitimate copy ("we make no guarantee", a case
# study's "two consecutive disasters", "34-42%" market occupancy, 28px in CSS).
# The dash alternatives are spelled out rather than written as a bracket class:
# [–-] is a BYTE range once grep sees UTF-8, and silently fails to match the
# en-dash form -- which is the exact phrasing the retired claim used. Entity
# forms are covered too, since the copy could return encoded.
#
# Verified against every surface below before shipping, in both directions:
# zero matches on live copy, and every retired phrasing caught. Widen only with
# both checks re-run.
RETIRED='50(-|–|—|‐|&#45;|&#8211;|&#8212;|&#x2013;|&ndash;|&mdash;| to )75|28\+? documented|documented client outcomes|consecutive quarters|90.Day Guarantee|42%\+|~42|\+32%|20 years|\{\{|random sample|30 documented|met or exceeded'
echo "· Retired-claim sweep (rendered copy + inline JSON-LD + meta tags)"
for p in "" "/results" "/pricing" "/method" "/intel/str-performance-index" "/sample-audit" \
         "/calculator" "/faq" "/case-studies" "/case-studies/montreal-hotel" \
         "/case-studies/anthony-san-antonio" "/case-studies/wally-puerto-rico" \
         "/story" "/markets" "/media" "/media-kit" "/lp/keep-control" "/llms.txt"; do
  found=$(grep -Eoh "$RETIRED" <<<"$(body "$BASE$p")" | sort -u | tr '\n' ' ')
  [ -z "$found" ] && ok "clean ${p:-/}" || no "${p:-/} serves retired claim(s): $found"
done

# ── Paid LP: the conversion path itself ─────────────────────────────────────
# The LP exists to put a lead into GHL off bought traffic. Everything below is
# a way that silently stops working: the form never renders, a CTA points at a
# page that no longer exists, or an edit reopens the exit the no-exit rule
# closed. CI checks the repo; this checks what visitors are actually served.
echo
echo "· /lp/keep-control conversion path"
lp=$(body "$BASE/lp/keep-control")

grep -q 'id="lp-audit-form"' <<<"$lp" \
  && ok "form anchor present" || no "form anchor #lp-audit-form missing"
grep -q 'id="lpAuditForm"' <<<"$lp" \
  && ok "audit form renders" || no "audit form missing from served page"
for f in 'name="listing_url"' 'name="email"' 'name="pricing_owner"' 'name="source"'; do
  grep -q "$f" <<<"$lp" && ok "field $f" || no "field $f missing"
done
grep -q 'leadconnectorhq.com/hooks/' <<<"$lp" \
  && ok "GHL webhook wired" || no "GHL webhook missing — leads would go nowhere"
[ "$(grep -c 'href="#lp-audit-form"' <<<"$lp")" -ge 2 ] \
  && ok "CTAs anchor to the form" || no "CTAs no longer anchor to the form"

# No-exit rule: in-page anchors and the fine-print footer only.
exits=$(grep -Eoh 'href="[^"#][^"]*"' <<<"$lp" \
        | grep -Ev 'href="(/legal|/legal\?tab=terms|/assets/|/images/|/fonts/|/favicon|/apple-touch-icon|https://marketics.io/lp/keep-control|https://widgets.leadconnectorhq.com|https://www.clarity.ms)' \
        | sort -u | tr '\n' ' ')
[ -z "$exits" ] && ok "no-exit rule holds" || no "outbound link(s) on the paid LP: $exits"

grep -q 'noindex, follow' <<<"$lp" \
  && ok "noindex, follow" || no "robots meta wrong on the paid LP"

echo
echo "Result: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
