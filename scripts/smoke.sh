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
# The slash form returns 200 via Netlify's directory index (a strict 301 isn't
# achievable on this platform); the canonical tag must point back to no-slash.
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

echo "· Not-public artifacts (404)"
c=$(code "$BASE/marketics-site-audit-2026-07.md"); [ "$c" = "404" ] && ok "audit report 404" || no "audit report = $c (want 404)"

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
grep -Eq 'random sample|30 documented|~42|42%\+' <<<"$h" && no "homepage still shows retired canon" || ok "homepage: no retired canon"
ix=$(body "$BASE/intel/str-performance-index")
grep -q '45% median benchmark' <<<"$ix" && ok "Index: 45% median benchmark canon" || no "Index missing 45% median benchmark canon"

echo
echo "Result: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
