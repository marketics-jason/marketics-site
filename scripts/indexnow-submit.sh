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
if [ "$code" = "200" ] || [ "$code" = "202" ]; then
  echo "OK: submission accepted"
  exit 0
else
  echo "WARN: unexpected response code, not failing the build over this" >&2
  exit 0
fi
