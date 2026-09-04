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

# RETRY, and why it is narrow: on 2026-08-31 the daily production run failed on
# its very first assertion with `000` (no response) after 6.1s, while every
# later request in the same run — including two more fetches of that same
# homepage — returned in ~0.3s. A cold DNS/TLS connection timing out, not a
# regression. Without this the whole production gate reds on any first-request
# hiccup, and a gate that cries wolf is one people stop reading.
#
# `--retry` covers transport failures and transient HTTP (timeout, 408, 429,
# 5xx) only. It deliberately does NOT use --retry-all-errors, which would also
# retry 404s and 301s — the very codes these checks assert, so masking them
# would turn a real regression into a pass.
RETRY=(--retry 2 --retry-connrefused --retry-delay 1)

# code URL [expected_code]  — no redirect follow; asserts the status of the URL itself
code() { curl -s -o /dev/null -A "$UA" "${RETRY[@]}" -w "%{http_code}" --max-time 20 "$1"; }
# body URL — follows redirects, returns body
body() { curl -sL -A "$UA" "${RETRY[@]}" --max-time 20 "$1"; }
# hdr URL — response headers only (no follow)
hdr()  { curl -sI -A "$UA" "${RETRY[@]}" --max-time 20 "$1"; }
# loc URL — the Location header of a single redirect (no follow), path only
loc()  { curl -sI -A "$UA" "${RETRY[@]}" --max-time 20 "$1" | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r' | sed -E 's#^https?://[^/]+##'; }

ok()   { pass=$((pass+1)); printf '  \033[32m✓\033[0m %s\n' "$1"; }
no()   { fail=$((fail+1)); printf '  \033[31m✗\033[0m %s\n' "$1"; }

echo "Smoke test against: $BASE"
echo

# Warm-up, deliberately unasserted: primes DNS and the TLS session so the first
# real assertion is not also the first connection. Its result is discarded, so
# it can never turn a failure into a pass.
curl -s -o /dev/null -A "$UA" --max-time 20 "$BASE/" || true

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

# The placements the live pages actually link to. An untagged partner link is
# invisible when it breaks -- it still goes somewhere sensible, it just arrives
# with no ref and no attribution -- so the destination is asserted per
# placement rather than trusting the :placement rule in the abstract.
#
# Editorial placements land on the HOMEPAGE, not /order/ (Strategy 2026-09-01):
# an article or author-page reader has not been sold anything yet. They are
# specific rules listed above :placement in _redirects, so this also asserts
# that the ordering still holds -- if those lines moved below the wildcard the
# destination would silently revert to /order/ and nothing else would notice.
for pl in intel-article author-page; do
  c=$(code "$BASE/costseg/$pl"); l=$(loc_raw "$BASE/costseg/$pl")
  want="https://costsegsmart.com/?ref=MARKETICS-Q0DZ&utm_source=marketics&utm_medium=partner&utm_campaign=costseg&utm_content=$pl"
  { [ "$c" = "301" ] && [ "$l" = "$want" ]; } \
    && ok "/costseg/$pl -> 301 homepage with ref + utm_content=$pl" \
    || no "/costseg/$pl = $c -> '$l' (want 301 '$want')"
done

# The card placements must still reach /order/ -- proves the editorial rules
# above did not swallow the shared behaviour they sit in front of.
c=$(code "$BASE/costseg/miami-card"); l=$(loc_raw "$BASE/costseg/miami-card")
want="https://costsegsmart.com/order/?ref=MARKETICS-Q0DZ&utm_source=marketics&utm_medium=partner&utm_campaign=costseg&utm_content=miami-card"
{ [ "$c" = "301" ] && [ "$l" = "$want" ]; } \
  && ok "/costseg/<card> still -> 301 /order/ (shared rule intact)" \
  || no "/costseg/miami-card = $c -> '$l' (want 301 '$want')"

echo "· Not-public artifacts (404)"
# Internal docs are plain files at the repo root, so they are servable by
# default and are only hidden by the force-shadow block in _redirects. That
# makes the shadow load-bearing and easy to forget: a new internal doc is
# public the moment it merges unless someone remembers to add two lines. Every
# one of them gets asserted here, in both the extensionless and .md forms,
# since the shadow lists both and a rule covering only one still leaks.
for d in "/marketics-site-audit-2026-07" "/CANON-REGISTRY" "/CANON-SWEEP-2026-08-25" \
         "/LEGAL-ROUTING-2026-08-27" "/LEGAL-ROUTING-2026-09-01" \
         "/LEGAL-REDLINE-2026-09-01"; do
  for f in "$d" "$d.md"; do
    c=$(code "$BASE$f"); [ "$c" = "404" ] && ok "$f 404 (internal)" || no "$f = $c (want 404 — internal doc is PUBLIC)"
  done
done

# ── Consent posture on the SERVED script (board addenda B1-B4, C1) ──────────
# mkx-consent.js decides the consent signals for every visitor on every page,
# and it is one file — which makes it the highest-leverage thing on the site to
# get wrong quietly. validate-site.py gates the repo copy; this is the deployed
# one, and a stale deploy or a bad rollback would restore ad_personalization
# without anything looking broken.
#
# C1 is asserted as the LITERAL, not just "denied appears somewhere": the
# pre-C1 shape was `ad_personalization: ad`, which reads correct at a glance and
# is exactly what a careless edit restores. Both directions are checked, so the
# derived form failing to appear is not mistaken for the literal being present.
echo
echo "· Consent posture (served mkx-consent.js)"
mc=$(body "$BASE/mkx-consent.js")
grep -q 'updateConsent' <<<"$mc" \
  && ok "mkx-consent.js fetched (checks below are meaningful)" \
  || no "mkx-consent.js did not fetch — every check below would pass on an empty body"
grep -qF "ad_personalization: 'denied'" <<<"$mc" \
  && ok "C1: ad_personalization hardcoded denied" \
  || no "C1 BROKEN: ad_personalization is not the hardcoded 'denied' literal"
grep -qE "ad_personalization:[[:space:]]*ad\b" <<<"$mc" \
  && no "C1 REVERTED: ad_personalization derived from the grant (the pre-C1 B1 shape)" \
  || ok "C1: ad_personalization is not derived from the grant"
grep -q 'globalPrivacyControl' <<<"$mc" \
  && ok "B1: Global Privacy Control honoured" || no "B1: GPC support missing"
grep -q 'mkx_ad_optout' <<<"$mc" \
  && ok "B1: Do Not Sell opt-out present" || no "B1: Do Not Sell opt-out missing"
grep -q 'America/Toronto' <<<"$mc" \
  && ok "B2: Canada inside the region gate" || no "B2: Canada missing from the region gate"

# The consent beacon was removed on 2026-09-03 (registry v3.30). It posted to a
# GHL inbound webhook via sendBeacon, which always sends with credentials mode
# 'include' -- so its preflight could never be satisfied by GHL's wildcard ACAO
# and it never delivered a single event. Asserted on the SERVED file because a
# rollback or a stale deploy is what would put it back, and the only symptom is
# console errors on a page nobody has open. The fetch guard above is what makes
# this absence check mean anything.
grep -q 'webhook-trigger/' <<<"$mc" \
  && no "v3.30 UNDONE: consent script posts to a CRM webhook again" \
  || ok "v3.30: consent script carries no CRM webhook"

echo
echo "· Security headers"
jc=$(hdr "$BASE/join/confirmation")
grep -qi 'content-security-policy' <<<"$jc" && grep -qi 'assets.calendly.com' <<<"$jc" \
  && ok "CSP present + allows Calendly" || no "CSP missing or lacks assets.calendly.com on /join/confirmation"
grep -qi 'fonts.googleapis.com' <<<"$jc" \
  && ok "CSP allows Google Fonts" || no "CSP lacks fonts.googleapis.com"

# ── CSP connect-src: the measurement beacons (registry v3.24) ────────────────
# script-src governs whether gtag.js LOADS; connect-src governs whether it can
# SEND. Get the second wrong and everything looks fine: the tag loads, page_view
# may arrive, and the conversion beacon is refused into a console the visitor
# never opens. Three days of paid-launch debugging on 2026-09-03.
#
# Asserted on the SERVED header on purpose. No local server sends a CSP, so this
# is structurally invisible to every other test here — a browser repro of the
# form submit passed while production was refusing every beacon.
#
# Checked against the connect-src DIRECTIVE, not the whole policy: www.google.com
# is in script-src already, so grepping the full header would have reported this
# bug as passing.
csp=$(grep -i '^content-security-policy:' <<<"$(hdr "$BASE/lp/keep-control")" | tr -d '\r')
cs=$(grep -o 'connect-src [^;]*' <<<"$csp")
[ -n "$cs" ] \
  && ok "connect-src directive found (checks below are meaningful)" \
  || no "no connect-src in the served CSP — every check below would pass vacuously"
for host in 'https://\*\.google-analytics\.com' 'https://analytics\.google\.com' \
            'https://www\.google\.com' 'https://google\.com' \
            'https://ad\.doubleclick\.net' 'https://googleads\.g\.doubleclick\.net' \
            'https://pagead2\.googlesyndication\.com' 'https://www\.googleadservices\.com'; do
  plain=$(sed 's/\\//g' <<<"$host")
  grep -qE "$host(\s|$)" <<<"$cs" \
    && ok "connect-src allows $plain" \
    || no "connect-src BLOCKS $plain — measurement beacons will be refused"
done
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
         "/story" "/markets" "/media" "/media-kit" "/lp/keep-control" \
         "/intel/airbnb-operations-at-cost" "/llms.txt"; do
  found=$(grep -Eoh "$RETIRED" <<<"$(body "$BASE$p")" | sort -u | tr '\n' ' ')
  [ -z "$found" ] && ok "clean ${p:-/}" || no "${p:-/} serves retired claim(s): $found"
done

# ── Click-identifier capture is consent-gated (registry v3.33) ───────────────
# Ruled Jason, Sep 4 2026: gclid/wbraid/gbraid are captured ONLY where
# ad_storage is granted. The gate is the ruling -- it is what moots the privacy
# question instead of deferring it to counsel -- so it is asserted on the SERVED
# file, not just the repo copy. An unconditional capture would look like a
# harmless simplification and would put an advertising identifier in the CRM for
# a visitor who was shown a banner and declined.
echo
echo "· Click identifiers (consent-gated)"
ut=$(body "$BASE/mkx-utm.js")
grep -q 'mkxGetUTM' <<<"$ut" \
  && ok "mkx-utm.js fetched (checks below are meaningful)" \
  || no "mkx-utm.js did not fetch -- every check below would pass on an empty body"
grep -q 'mkxCommitClickIds' <<<"$ut" \
  && ok "click-id capture present" || no "click-id capture missing from the served file"
grep -q 'adStorageGranted' <<<"$ut" \
  && ok "consent gate present on the served file" \
  || no "CONSENT GATE GONE: click ids captured without an ad_storage check"
ci_lp=$(body "$BASE/lp/keep-control")
grep -q 'lpAuditForm' <<<"$ci_lp" \
  && ok "LP fetched (checks below are meaningful)" \
  || no "LP did not fetch -- the gclid check below would pass on an empty body"
grep -q 'gclid_first' <<<"$ci_lp" \
  && ok "LP posts gclid_first (the provisioned GHL field key)" \
  || no "LP does not post gclid_first -- the GHL field will stay empty"
# Attribution keys must match GHL's field keys EXACTLY. Proven on a live contact
# 2026-09-04: fields whose key matches a transmitted key populate, and every
# field whose key differs was blank -- silently, with a contact that otherwise
# looks complete. There is no mapping bridge to fall back on.
for k in utm_source_first utm_medium_first utm_campaign_first utm_content_first utm_term_first first_touch_lp; do
  grep -q "$k" <<<"$ci_lp" \
    && ok "LP posts $k" \
    || no "LP does not post $k -- that GHL Attribution field will be silently blank"
done
ci_lg=$(body "$BASE/legal")
grep -q 'GoHighLevel' <<<"$ci_lg" \
  && ok "/legal fetched (check below is meaningful)" \
  || no "/legal did not fetch -- the disclosure check would pass on an empty body"
grep -q 'click identifier' <<<"$ci_lg" \
  && ok "/legal discloses the click identifier" \
  || no "/legal no longer discloses the click identifier (C2 ruling, Sep 4)"

# ── /intel/airbnb-operations-at-cost: partner claim + link (registry v3.31) ──
# Two things here are a PARTNER's, not ours, and both were supplied by Amy Plummer
# (Turno) rather than measured by us: the 126,000+ marketplace figure and the
# tracked referral URL. A partner statistic changes estate-wide in one pass when
# the partner corrects it, so the served page is where that is checked -- the repo
# being right is a different question from the visitor seeing it.
#
# The absence check is the load-bearing one and it runs behind a fetch guard:
# there is NO fee or referral arrangement with Turno, so no disclosure belongs on
# the page. Disclosure language appearing later would mean either an arrangement
# nobody recorded or a copy-paste from the Cost Seg Smart treatment, which is a
# genuinely different relationship.
echo
echo "· /intel/airbnb-operations-at-cost (partner claim + tracked link)"
ops=$(body "$BASE/intel/airbnb-operations-at-cost")
grep -q 'Airbnb Software Partner' <<<"$ops" \
  && ok "page fetched (checks below are meaningful)" \
  || no "/intel/airbnb-operations-at-cost did not fetch -- every check below would pass on an empty body"
grep -q '126,000+' <<<"$ops" \
  && ok "partner figure 126,000+ served" || no "partner figure 126,000+ MISSING (Amy's Sept 2 correction)"
grep -qE '25,000|25000|25k' <<<"$ops" \
  && no "RETIRED partner figure 25,000 is back on the page" || ok "no retired 25,000 figure"
grep -q 'utm_source=website&amp;utm_medium=partner&amp;utm_campaign=marketics_intel' <<<"$ops" \
  && ok "tracked Turno URL served with all three utm params" \
  || no "Turno link is NOT the tracked URL -- Amy cannot attribute referrals"
grep -qEi 'disclos|affiliate|we may receive' <<<"$ops" \
  && no "disclosure language present -- no Turno arrangement exists, nothing to disclose" \
  || ok "no disclosure language (correct: no arrangement exists)"
[ "$(grep -o '45%' <<<"$ops" | wc -l)" -eq 1 ] \
  && ok "45% appears exactly once" || no "45% does not appear exactly once (canon)"

# ── /legal disclosures (board addendum C3, 2026-09-01) ──────────────────────
# The policy drifted out of step with the site's actual tracking for five and a
# half months and nothing noticed, because nothing was watching. validate-site.py
# now gates the repo copy; this gates what is SERVED, which is the version a
# regulator or an ad platform would read. Both directions: the vendor we do not
# run must stay absent, and the vendor we do run must stay named.
echo
echo "· /legal disclosures"
lg=$(body "$BASE/legal")
# Prove the page actually arrived before trusting anything below. Absence checks
# pass VACUOUSLY on an empty body: a dead origin would cheerfully report "no Meta
# Pixel in /legal" and look green. Found by accident when the local origin died
# mid-run and four assertions reported clean against nothing at all.
grep -q 'Privacy Policy' <<<"$lg" \
  && ok "/legal fetched (absence checks below are meaningful)" \
  || no "/legal did not fetch — every absence check below would pass on an empty body"
grep -qi 'meta pixel' <<<"$lg" \
  && no "/legal names Meta Pixel — no Pixel exists on this site (C3 item 3)" \
  || ok "no Meta Pixel in /legal (vendor we do not run stays absent)"
grep -q 'Google Ads' <<<"$lg" \
  && ok "/legal names Google Ads (vendor we DO run stays named)" \
  || no "/legal does not name Google Ads — the omission the counsel routing was about"
grep -qi 'gross booking revenue' <<<"$lg" \
  && no "/legal still states the gross fee basis — contradicts the Co-Host Agreement" \
  || ok "no gross fee basis in /legal"
grep -q 'net payout' <<<"$lg" \
  && ok "/legal states the net payout fee basis" || no "/legal missing the net payout fee basis"
grep -q 'Do Not Sell or Share' <<<"$lg" \
  && ok "/legal describes the Do Not Sell control" || no "/legal omits the Do Not Sell control"
grep -q 'Global Privacy Control' <<<"$lg" \
  && ok "/legal describes GPC support" || no "/legal omits GPC support"

# ── Paid LP: the conversion path itself ─────────────────────────────────────
# The LP exists to put a lead into GHL off bought traffic. Everything below is
# a way that silently stops working: the form never renders, a CTA points at a
# page that no longer exists, or an edit reopens the exit the no-exit rule
# closed. CI checks the repo; this checks what visitors are actually served.
echo
echo "· /lp/keep-control conversion path"
lp=$(body "$BASE/lp/keep-control")

# Which trigger the SERVED page posts to. validate-site.py gates the repo copy;
# this is the deployed one, and they are different questions -- a stale deploy or
# a bad rollback puts the paid path back on the shared hook with nothing to see.
# Confirmed live 2026-09-03 after the owner turned out to be "Inbound Lead",
# which created contacts and never tagged them. Absence checks are meaningful
# here because the form-renders assertion above already proves the body arrived.
grep -q '3c750621-84a1-444d-b64a-5712e15cfb5e' <<<"$lp" \
  && ok "LP posts to its own paid trigger" \
  || no "LP is NOT on the paid trigger -- paid leads are going somewhere else"
grep -q '1297f709-5970-411d-b58c-e3a47721392e' <<<"$lp" \
  && no "LP posts to the SHARED organic trigger -- the separation has been reverted" \
  || ok "LP is off the shared organic trigger"
grep -q '2ebb4312-80b3-4ef6-9e78-10e3807abc40' <<<"$lp" \
  && no "LP posts to the RETIRED trigger -- leads are lost with no error" \
  || ok "no retired trigger on the LP"

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
