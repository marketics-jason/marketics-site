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

ok()   { pass=$((pass+1)); printf '  \033[32m✓\033[0m %s\n' "$1"; }
no()   { fail=$((fail+1)); printf '  \033[31m✗\033[0m %s\n' "$1"; }

echo "Smoke test against: $BASE"
echo

echo "· Status codes"
for p in "" "/method" "/pricing" "/results" "/intel/str-performance-index" "/markets/austin" "/join/confirmation"; do
  c=$(code "$BASE$p"); [ "$c" = "200" ] && ok "200 $p" || no "$p returned $c (want 200)"
done

echo "· Redirects (single 301 to canonical)"
c=$(code "$BASE/intel/miami/");  [ "$c" = "301" ] && ok "/intel/miami/ -> 301" || no "/intel/miami/ = $c (want 301 depth-2 slash)"
c=$(code "$BASE/method/");       [ "$c" = "301" ] && ok "/method/ -> 301"      || no "/method/ = $c (want 301)"
c=$(code "$BASE/privacy");       [ "$c" = "301" ] && ok "/privacy -> 301"      || no "/privacy = $c (want 301)"
c=$(code "$BASE/terms");         [ "$c" = "301" ] && ok "/terms -> 301"        || no "/terms = $c (want 301)"

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
grep -q '19 documented short-term-rental engagements' <<<"$h" && ok "homepage: 19-engagements canon" || no "homepage missing 19-engagements canon"
grep -Eq 'random sample|30 documented|~42' <<<"$h" && no "homepage still shows retired canon" || ok "homepage: no retired canon"
ix=$(body "$BASE/intel/str-performance-index")
grep -q '45%' <<<"$ix" && grep -q '42%+' <<<"$ix" && ok "Index: 45% median + 42%+ benchmark" || no "Index missing 45%/42%+"

echo
echo "Result: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
