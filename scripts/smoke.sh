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
# These six keys are what the LP's GHL mapping rows point at BY NAME. The
# mechanism recorded on 2026-09-04 ("GHL matches on the transmitted key") was
# wrong and was corrected at v3.35: rows are required, and a row can point any
# key at any field. So these keys are not magic -- they are simply the names the
# existing rows reference, and a rename empties those fields with no error on
# either side.
for k in utm_source_first utm_medium_first utm_campaign_first utm_content_first utm_term_first first_touch_lp; do
  grep -q "$k" <<<"$ci_lp" \
    && ok "LP posts $k" \
    || no "LP does not post $k -- that GHL Attribution field will be silently blank"
done
# ── First-touch timestamp (CTO ruling 2026-09-05) ───────────────────────────
# The ruling authorised the capture AND refused the shortcut: submission time is
# a real value from the wrong moment, and a CRM field full of confidently wrong
# timestamps cannot be told apart from a correct one afterwards. So the served
# file is checked for the capture, for its reader, and for the thing that makes
# it first-touch -- exactly one write. A second write anywhere makes every
# returning visitor's value the current page load instead.
grep -q 'mkx_ts' <<<"$ut" \
  && ok "first-touch timestamp captured on the served file" \
  || no "mkx_ts capture missing from the served mkx-utm.js"
grep -q 'mkxGetFirstTouchTS' <<<"$ut" \
  && ok "mkxGetFirstTouchTS() reader present" \
  || no "no mkxGetFirstTouchTS() on the served file -- nothing can send the value"
n=$(grep -o 'setItem(TS_KEY' <<<"$ut" | wc -l)
[ "$n" -eq 1 ] \
  && ok "the timestamp is written exactly once (first touch)" \
  || no "TS_KEY is written $n time(s) on the served file, want 1 -- a second write is not first-touch"

# Both forms, because both lead paths carry attribution as of 2026-09-05. The
# value check is the one that matters: `first_touch_ts` set from new Date() is
# the refused shortcut, and it looks entirely reasonable in a diff.
gs=$(body "$BASE/get-started")
grep -q 'auditForm' <<<"$gs" \
  && ok "/get-started fetched (checks below are meaningful)" \
  || no "/get-started did not fetch -- the checks below would pass on an empty body"
for pg in "LP:$ci_lp" "get-started:$gs"; do
  nm="${pg%%:*}"; src="${pg#*:}"
  grep -q 'first_touch_ts' <<<"$src" \
    && ok "$nm posts first_touch_ts" \
    || no "$nm does not post first_touch_ts -- that GHL field stays blank"
  grep -qE '^\s*first_touch_ts\s*:\s*(new Date|Date\.now)' <<<"$src" \
    && no "$nm derives first_touch_ts from submission time -- the refused shortcut (CTO, Sep 5)" \
    || ok "$nm does not derive first_touch_ts from submission time"
done

# Jason wired six organic mapping rows against these keys on 2026-09-05, which
# made them load-bearing on the organic path for the first time. Before that a
# rename here cost nothing; now it silently empties a field on every organic lead.
for k in landingPage utm_source utm_medium utm_campaign utm_content utm_term; do
  grep -q "$k" <<<"$gs" \
    && ok "/get-started posts $k" \
    || no "/get-started does not post $k -- an organic mapping row points at it"
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

# ── Entity graph: founding claim + Wikidata reconciliation (v3.39) ──────────
# foundingDate read "2023" until 2026-09-06. It is entity formation and must
# match Wikidata Q141329164's `inception` (confirmed 2025 against the live item).
# A founding year is the anchor an AI engine dates everything else against, and
# the two sources disagreeing is the inconsistency that suppresses citation.
#
# RAW BODY, never the cleaned one. clean() strips <script>, which is exactly
# where JSON-LD lives -- the homepage ClaimReview check made that mistake and
# read green with the markup restored to the page (v3.37). Every assertion in
# this section inspects a schema block, so every one of them needs the raw body.
#
# The repo side is gated in validate-site.py. This is the deployed side, and
# they answer different questions: a stale deploy or a bad rollback serves the
# old value with CI still green.
echo
echo "· Entity graph (v3.39) — foundingDate + Wikidata reconciliation"
ent_home=$(body "$BASE/")
grep -q '"@type": "Organization"' <<<"$ent_home" \
  && ok "homepage Organization schema fetched (checks below are meaningful)" \
  || no "homepage Organization schema did not fetch — every check below would pass on an empty body"
grep -qF '"foundingDate": "2025"' <<<"$ent_home" \
  && ok "foundingDate is 2025 (matches Wikidata Q141329164 inception)" \
  || no "foundingDate is NOT 2025 on the served page — it read 2023 until 2026-09-06 and must match Q141329164's inception"
grep -q 'wikidata.org/wiki/Q141329164' <<<"$ent_home" \
  && ok "Organization sameAs carries the Wikidata entity" \
  || no "Organization sameAs has lost the Wikidata entity — the reconciliation target for the other six profiles"

# The founder Person is defined in FULL on two pages under one @id. Both are
# checked: a deploy that updates one and not the other leaves the two
# definitions disagreeing about who this person is, which is the single thing a
# sameAs exists to settle -- and it is invisible from either page alone.
for pg in "story:/story" "media:/media"; do
  nm="${pg%%:*}"; path="${pg#*:}"
  src=$(body "$BASE$path")
  if ! grep -q '"@id": "https://marketics.io/story#jason"' <<<"$src"; then
    no "/$nm did not fetch or carries no founder Person node — the check below would pass vacuously"
    continue
  fi
  grep -q 'wikidata.org/wiki/Q141330011' <<<"$src" \
    && ok "$nm Person sameAs carries the founder Wikidata entity" \
    || no "$nm Person sameAs has lost the founder Wikidata entity (Q141330011)"
done

# ── GEO batch (registry v3.36, #143) ────────────────────────────────────────
# Flagged in the Sep 5 weekly and asked for by Jason the same day: the
# production run after that batch passed at exactly the same assertion count as
# the run before it. The suite proved nothing REGRESSED and verified not one
# thing the batch actually changed. These four close that gap.
#
# All four assert on the SERVED page, which is where a stale deploy or a bad
# rollback shows up and where CI cannot look. Note what they are NOT: the repo
# side of items 1 and 3 is gated by validate-site.py and gen-llms.py, and item 4
# has NO repo-side gate at all -- the <br> removal can be undone in a PR without
# failing CI, so until that is fixed this is the only thing watching it, and it
# only speaks after a merge. Reported, not silently papered over.
echo
echo "· GEO batch (v3.36) — H1, llms.txt coverage, no self-review, no <br> in headings"

# Strips comments, <script> and <style> before any tag matching. The heading
# sweep in #143 corrupted /calculator by matching an <h1> inside an HTML COMMENT
# and swallowing 93 lines to the next </h1>. A regex that finds tags will find
# them in comments too, and a live check has the same exposure the sweep did.
clean() { perl -0777 -pe 's/<!--.*?-->//gs; s/<(script|style)\b[^>]*>.*?<\/\1>//gs'; }

# ── 1. The homepage H1 (Strategy sign-off, 2026-09-05) ──────────────────────
H1_RULED='Performance-based Airbnb revenue management'
# TWO bodies of the same page, deliberately. clean() strips <script>, and the
# JSON-LD lives in one -- so the ClaimReview check below MUST run against the raw
# body or it inspects a document with every schema block already removed and can
# never fire. Found by negative control; it read green with ClaimReview restored.
home_raw=$(body "$BASE/")
home=$(printf '%s' "$home_raw" | clean)
grep -q '<h1' <<<"$home" \
  && ok "homepage fetched and carries an h1 (checks below are meaningful)" \
  || no "homepage did not fetch or has no h1 — every check below would pass on an empty body"

n=$(grep -o '<h1' <<<"$home" | wc -l)
[ "$n" -eq 1 ] && ok "homepage has exactly one h1" \
               || no "homepage has $n h1 elements (want exactly 1)"

# Extracted rather than grepped page-wide: the string existing SOMEWHERE and the
# string being the H1 are different facts, and only the second is the ruling.
h1=$(grep -o '<h1[^>]*>.*</h1>' <<<"$home")
[ -n "$h1" ] && ok "h1 element extracted (the string check below is meaningful)" \
             || no "could not extract the h1 element — the string check below would pass vacuously"
grep -qF "$H1_RULED" <<<"$h1" \
  && ok "h1 is the ruled string: \"$H1_RULED\"" \
  || no "h1 does NOT carry the ruled string — served h1: $h1"

# The wordmark was the h1 until #143. If a revert puts it back, the count above
# catches it; this catches the subtler case where it returns AS the h1.
grep -qE '<h1[^>]*>.*MASTERED' <<<"$h1" \
  && no "the wordmark is the h1 again — #143 reverted" \
  || ok "the wordmark is not the h1"

# "One string, one slot" (Strategy, 2026-09-05): a second copy in the reach strip
# is the redundant-repetition pattern the content analysis already docked.
n=$(grep -oF "$H1_RULED" <<<"$home" | wc -l)
[ "$n" -eq 1 ] && ok "the ruled string appears exactly once on the page" \
               || no "the ruled string appears $n times (want exactly 1)"

# ── 2. llms.txt coverage, checked against the SERVED sitemap ────────────────
# Deliberately not a hardcoded count. A fixed number goes stale the day a page
# ships and turns main red for a reason that has nothing to do with coverage —
# and a check that flaps gets ignored, which is the vacuous-pass family from the
# other direction. The sitemap is the source on the repo side (gen-llms.py), so
# it is the source here too; the only hardcoded value is the exclusion, which is
# a decision and belongs in a diff.
LLMS_EXCLUDED='/authors/jamie-melgar'
lt=$(body "$BASE/llms.txt")
sm=$(body "$BASE/sitemap.xml")
grep -q '^# Marketics' <<<"$lt" \
  && ok "llms.txt fetched (coverage checks below are meaningful)" \
  || no "llms.txt did not fetch — coverage would compare against an empty file"
grep -q '<loc>' <<<"$sm" \
  && ok "sitemap.xml fetched" \
  || no "sitemap.xml did not fetch — coverage would compare against an empty file"

lt_paths=$(grep -oE '\(https://marketics\.io[^)]*\)' <<<"$lt" \
           | sed -E 's#^\(https://marketics\.io##; s#\)$##; s#^$#/#' | sort -u)
sm_paths=$(grep -oE '<loc>[^<]*</loc>' <<<"$sm" \
           | sed -E 's#</?loc>##g; s#^https://marketics\.io##; s#^$#/#' | sort -u)

phantom=$(comm -23 <(printf '%s\n' "$lt_paths") <(printf '%s\n' "$sm_paths") | tr '\n' ' ')
[ -z "${phantom// }" ] && ok "llms.txt links no page that is absent from the sitemap" \
                       || no "llms.txt links page(s) not in the sitemap: $phantom"

missing=$(comm -13 <(printf '%s\n' "$lt_paths") <(printf '%s\n' "$sm_paths") | tr '\n' ' ')
missing="${missing% }"
if [ "$missing" = "$LLMS_EXCLUDED" ]; then
  ok "llms.txt covers every sitemap URL except the one excluded ($LLMS_EXCLUDED)"
elif [ -z "$missing" ]; then
  no "llms.txt now covers $LLMS_EXCLUDED too — if that is the decision, update LLMS_EXCLUDED here AND 'exclude' in scripts/llms-config.json"
else
  no "llms.txt coverage drifted — sitemap URLs absent from llms.txt: '$missing' (want exactly '$LLMS_EXCLUDED')"
fi

# ── 3. No self-review markup (GEO finding 3) ────────────────────────────────
# ClaimReview was Marketics rating a Marketics claim five stars: fact-checking
# markup for accredited publishers, used to cite ourselves. Removed from these
# two pages in #143.
res=$(body "$BASE/results")
grep -q '"@type"' <<<"$res" \
  && ok "/results fetched (absence checks below are meaningful)" \
  || no "/results did not fetch — the absence checks below would pass vacuously"
grep -q 'ClaimReview' <<<"$home_raw" \
  && no "ClaimReview is back on the homepage — self-review markup" \
  || ok "no ClaimReview on the homepage"
grep -q 'ClaimReview' <<<"$res" \
  && no "ClaimReview is back on /results — self-review markup" \
  || ok "no ClaimReview on /results"

# The false-positive control, and the reason this is not just an absence check:
# the three CUSTOMER Review nodes are legitimate — their authors are Person
# nodes, which is exactly the distinction that made the ClaimReview illegitimate.
# Stripping all review markup would satisfy the two checks above and be wrong.
n=$(grep -oE '"@type":[[:space:]]*"Review"' <<<"$res" | wc -l)
[ "$n" -eq 3 ] && ok "the three customer Review nodes survive on /results" \
               || no "/results carries $n Review nodes (want 3 — the customer reviews)"
grep -qE '"author":[^}]*"Marketics' <<<"$res" \
  && no "a Marketics-authored Review is on /results — self-review by another name" \
  || ok "no Marketics-authored Review on /results"

# ── 4. No <br> inside headings (GEO finding 6) ──────────────────────────────
# A <br> yields NO whitespace when tags are stripped, so extraction read
# "YOURMARKET.MASTERED." as one token. #143 replaced 60 of them across 28 files
# with block spans joined by a REAL space. The pages below are the two named test
# cases plus the two heaviest heading pages; /calculator is included because it
# is the page the sweep corrupted, and it is the reason clean() exists.
for p in "" "/markets" "/results" "/calculator" "/intel/miami"; do
  pg=$(body "$BASE$p" | clean)
  if ! grep -q '<h1\|<h2' <<<"$pg"; then
    no "${p:-/} did not fetch or has no headings — the <br> check would pass vacuously"
    continue
  fi
  if grep -qzoP '(?s)<h[1-6][^>]*>(?:(?!</h[1-6]>).)*?<br' <<<"$pg"; then
    no "${p:-/} has a <br> inside a heading — extraction will glue the words"
  else
    ok "${p:-/} — no <br> in any heading"
  fi
done

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
