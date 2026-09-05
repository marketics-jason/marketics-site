#!/usr/bin/env bash
# indexnow-submit.sh — bulk-submits every sitemap URL to IndexNow after each deploy.
#
# Aug 21 2026 CTO brief (P6): the site-audit tool was flagging "1 page to submit"
# on IndexNow weekly, with no automation to clear it. IndexNow accepts repeat
# submission of unchanged URLs without penalty, so the simplest durable fix is a
# full-sitemap bulk submit on every push to main, rather than diffing for the
# single changed page each time.
#
# Verification key: the plain-text key file at the repo root
# (6ba2a8f4c560ed1d1aaa4f43e8fbe083.txt) must keep serving its own filename's
# key string at https://marketics.io/6ba2a8f4c560ed1d1aaa4f43e8fbe083.txt —
# IndexNow checks it matches the `key` field below before accepting a submission.
#
# Usage: scripts/indexnow-submit.sh [sitemap-path]
set -euo pipefail

SITEMAP="${1:-sitemap.xml}"
HOST="marketics.io"
KEY="6ba2a8f4c560ed1d1aaa4f43e8fbe083"
KEY_LOCATION="https://marketics.io/${KEY}.txt"

if [ ! -f "$SITEMAP" ]; then
  echo "indexnow-submit: $SITEMAP not found" >&2
  exit 1
fi

urls=$(grep -oE '<loc>[^<]+</loc>' "$SITEMAP" | sed -E 's#</?loc>##g')
url_count=$(echo "$urls" | grep -c .)
echo "Submitting $url_count URLs from $SITEMAP to IndexNow..."

url_json=$(echo "$urls" | python3 -c "import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")

payload=$(python3 -c "
import json
print(json.dumps({
    'host': '$HOST',
    'key': '$KEY',
    'keyLocation': '$KEY_LOCATION',
    'urlList': $url_json
}))
")

code=$(curl -s -o /tmp/indexnow-response.txt -w "%{http_code}" \
  -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$payload")

echo "IndexNow response: HTTP $code"
cat /tmp/indexnow-response.txt 2>/dev/null || true
echo

# IndexNow returns 200 or 202 on accepted submissions.
#
# This block used to `exit 0` on ANY response code, with the note "not failing
# the build over this". That made the workflow green whether or not IndexNow
# accepted a single URL: a check that cannot fail is not a check. It was found
# on 2026-09-04 while confirming an audit finding, and the only reason we knew
# the submission had actually worked was that someone read the log body.
#
# It joins the vacuous-pass family (registry v3.33/v3.35): a CSP whole-header
# grep, a mock that validated its own assumption, a payload-key gate satisfied
# by its own comment, and a GHL mapping reference labelled "Active" that was a
# day-old snapshot. Same shape every time -- a green signal that is green
# regardless of outcome.
#
# A non-2xx now fails. That means a genuine IndexNow outage will show red on
# main, which is the correct trade: a red check that means something beats a
# green one that means nothing, and the response body is echoed above so the
# failure is diagnosable rather than mysterious.
case "$code" in
  200|202)
    echo "OK: submission accepted (HTTP $code)"
    exit 0
    ;;
  *)
    echo "FAIL: IndexNow rejected the submission (HTTP $code)" >&2
    echo "      Response body is echoed above. Common causes: the key file at" >&2
    echo "      $KEY_LOCATION stopped serving, or the key no longer matches." >&2
    exit 1
    ;;
esac
