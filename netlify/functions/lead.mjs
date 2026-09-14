/* ══════════════════════════════════════════════════════════════════════════
   /api/lead — server-side lead forwarder
   CTO ruling 2026-09-14, deliverables 1 and 2. Registry v3.56.

   WHY THIS EXISTS

   1. CORS-class kill. Every form POSTs SAME-ORIGIN to /api/lead and this
      Function forwards to GoHighLevel server-side. That removes the browser
      from the cross-origin path entirely -- the class that took out the
      consent beacon (sendBeacon against GHL's wildcard ACAO, deterministic,
      silent). A same-origin POST has no preflight, no ACAO negotiation, and
      no opaque failure mode.

   2. The webhook URLs leave public source. They live in Netlify env vars
      (GHL_HOOK_ORGANIC / GHL_HOOK_PAID / GHL_HOOK_INTEL) and appear nowhere
      in the deploy.

   WHAT THIS DOES NOT DO, and it is written here so the entry is not read as
   closing more than it closes: anyone who already scraped a hook UUID can
   still POST to GHL directly. This narrows the surface; it does not close it.
   Server-side honeypot/timing enforcement IN THIS FUNCTION is the follow-on.

   ── THE FORWARD IS BYTE-FOR-BYTE, AND THAT IS LOAD-BEARING ──────────────

   The body is read as TEXT and forwarded as TEXT. It is never parsed into an
   object and re-serialized on the way out.

   The reason is the v3.51 P1. GHL writes a transmitted empty string OVER a
   populated field and leaves an ABSENT key alone, so the browser strips every
   ''-valued key before sending. If this Function parsed the payload and
   re-serialized it, any normalisation -- a default, a schema fill, a
   JSON.stringify of a reconstructed object -- could put a '' key back on the
   wire. The clobber would return THROUGH THE BACK DOOR, downstream of every
   gate that watches the browser, and nothing upstream would show it.

   Routing therefore reads a SEPARATE COPY (JSON.parse of the same text) and
   the parsed object is never the thing that gets sent. `outbound === inbound`
   is asserted, not assumed -- see assertOutboundUnchanged below.

   ── ROUTING IS A HEADER, NOT THE PAYLOAD ────────────────────────────────

   X-Marketics-Form names the trigger. Deliberately NOT derived from the
   payload's `source` field, for two reasons: reading routing out of the body
   would mean the body's shape decides where a lead lands (a renamed source
   value silently misroutes), and a header changes nothing about the bytes GHL
   receives -- which matters because GHL's field picker learns from a captured
   sample request, and a changed request shape makes the Mapping Reference
   rows read stale with no failure (v3.51 §6a, "capture wide, transmit
   narrow").

   An unknown or missing route is a 400 that forwards nothing. Loud, not a
   default -- a default here would send paid leads to the organic trigger and
   look like it worked.
   ══════════════════════════════════════════════════════════════════════ */

const ROUTES = {
  'get-started':    'GHL_HOOK_ORGANIC',
  'lp-keep-control': 'GHL_HOOK_PAID',
  'intel':          'GHL_HOOK_INTEL',
};

const MAX_BODY_BYTES = 64 * 1024;

/* The outbound body must be the inbound body. Cheap, and it is the only thing
   standing between the empty-key fix and a server-side regression that no
   browser-side gate could see. */
function assertOutboundUnchanged(inbound, outbound) {
  if (inbound !== outbound) {
    throw new Error('outbound body differs from inbound — refusing to forward');
  }
}

export default async (req) => {
  if (req.method !== 'POST') {
    return new Response('method not allowed', { status: 405 });
  }

  const route = (req.headers.get('x-marketics-form') || '').trim();
  const envName = ROUTES[route];
  if (!envName) {
    console.log(JSON.stringify({ evt: 'lead_rejected', reason: 'unknown_route', route }));
    return new Response('unknown form route', { status: 400 });
  }

  const hook = process.env[envName];
  if (!hook) {
    /* Configuration failure, not a visitor failure. 502 rather than 200: a
       silent success here would drop a real lead and report that it landed,
       which is the exact failure shape this codebase spent a week removing. */
    console.log(JSON.stringify({ evt: 'lead_misconfigured', route, envName }));
    return new Response('lead endpoint not configured', { status: 502 });
  }

  const inbound = await req.text();
  if (inbound.length > MAX_BODY_BYTES) {
    console.log(JSON.stringify({ evt: 'lead_rejected', reason: 'too_large', route, bytes: inbound.length }));
    return new Response('payload too large', { status: 413 });
  }

  /* Parsed ONLY to validate and to count. Never serialized back onto the wire. */
  let parsed;
  try {
    parsed = JSON.parse(inbound);
  } catch {
    console.log(JSON.stringify({ evt: 'lead_rejected', reason: 'bad_json', route }));
    return new Response('bad payload', { status: 400 });
  }
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    console.log(JSON.stringify({ evt: 'lead_rejected', reason: 'not_an_object', route }));
    return new Response('bad payload', { status: 400 });
  }

  /* The browser already strips these. Observed here as a TRIPWIRE rather than
     repaired: if empty keys start arriving, something upstream regressed and
     the count is how we find out, because GHL would accept them silently. */
  const emptyKeys = Object.keys(parsed).filter((k) => parsed[k] === '');

  const outbound = inbound;
  assertOutboundUnchanged(inbound, outbound);

  let status = 0;
  let failed = null;
  try {
    const res = await fetch(hook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: outbound,
    });
    status = res.status;
  } catch (err) {
    failed = String(err && err.message ? err.message : err);
  }

  /* Deliverable 3, first half: a server-side record of EVERY forwarded POST,
     independent of consent and of GA4. One structured line per submission, so
     the denominator exists in the function log even before a durable counter
     is wired. `keys` and `emptyKeys` are counts, never values -- client-level
     data does not travel downstream. */
  console.log(JSON.stringify({
    evt: 'lead_forwarded',
    route,
    ok: failed === null && status >= 200 && status < 300,
    status,
    failed,
    bytes: inbound.length,
    keys: Object.keys(parsed).length,
    emptyKeys: emptyKeys.length,
    ts: new Date().toISOString(),
  }));

  if (failed !== null) {
    return new Response('upstream unreachable', { status: 502 });
  }
  return new Response(JSON.stringify({ ok: status >= 200 && status < 300 }), {
    status: status >= 200 && status < 300 ? 202 : 502,
    headers: { 'Content-Type': 'application/json' },
  });
};

export const config = { path: '/api/lead' };
