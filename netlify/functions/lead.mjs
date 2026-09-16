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
  /* /join is not a lead form -- it posts `deposit_checkout_started` at the
     checkout step. It rides the ORGANIC hook, as it always has, but under its
     own route label so the counter can tell a deposit event from a lead.
     In scope here for one reason: deliverable 2's success criterion is ZERO
     hook-UUID hits in the deploy, and /join carried one. */
  'join':           'GHL_HOOK_ORGANIC',
  'partner':        'GHL_HOOK_PARTNER',   /* see PARTNER_ROUTE below */
};

/* Deliverable 4: the consent denominator. This route is NOT a lead route --
   it is counted here and forwarded NOWHERE. It shares the endpoint on CTO's
   instruction, and the separation is enforced by returning before the hook
   lookup can happen, not by remembering not to forward. */
/* The partner APPLICATION route (build sheet FINAL, 2026-09-16). A different
   contact type, a different pipeline and a different hook: a Referring Partner
   applying about themselves, never an owner lead.

   PATH-DERIVED, NOT HEADER-DERIVED, and that is the whole point. Every other
   route is named by a header the page sets, which is fine when the worst case
   is a mislabelled lead. Here the worst case is a partner landing in the owner
   pipeline -- forbidden by spec §2 B4, and the doorway to the open email-dedup
   problem where a partner already on an owner contact merges last-write-wins.
   Deriving it from /api/partner makes that structurally impossible rather than
   a rule someone has to keep. A header can never reach this route, and this
   route can never reach an owner hook. */
const PARTNER_ROUTE = 'partner';
const PARTNER_PATH = '/api/partner';

const CONSENT_ROUTE = 'consent';
const CONSENT_ACTIONS = ['impression', 'accept', 'deny', 'ignore'];

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

  /* Routing travels in the URL or a header, never in the payload -- the body
     must stay byte-identical, and a renamed `source` value must not be able to
     misroute a lead. The ?f= fallback exists because navigator.sendBeacon
     CANNOT SET HEADERS, and the consent 'ignore' event has to be a beacon: it
     fires while the page is unloading, which is the one moment a fetch is not
     guaranteed to survive. Header wins where both are present. */
  const url = new URL(req.url);
  const onPartnerPath = url.pathname === PARTNER_PATH;

  const route = onPartnerPath
    ? PARTNER_ROUTE
    : (req.headers.get('x-marketics-form') || url.searchParams.get('f') || '').trim();

  /* Both directions are closed, not just the dangerous one. A header cannot
     reach the partner hook, and the partner path cannot be talked into an
     owner route or into the consent counter. */
  if (!onPartnerPath && route === PARTNER_ROUTE) {
    console.log(JSON.stringify({ evt: 'lead_rejected', reason: 'partner_route_is_path_only' }));
    return new Response('unknown form route', { status: 400 });
  }
  if (route === CONSENT_ROUTE) {
    return await handleConsent(req);
  }

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
    evt: onPartnerPath ? 'partner_forwarded' : 'lead_forwarded',
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

/* ── Consent denominator (deliverable 4) ────────────────────────────────────
   Four counts for a dated window: impression / accept / deny / ignore. Unknown
   since 2026-09-04, when the original consent beacon died -- it used
   sendBeacon against GHL cross-origin, and GHL's wildcard ACAO made every send
   fail silently. Four console errors per banner, zero data. Same-origin is
   what makes a beacon safe here, so this deliverable only became possible
   BECAUSE deliverable 1 removed the cross-origin path.

   PRIVACY, and it is the reason this is shaped the way it is: these events
   necessarily fire BEFORE the visitor has answered the banner, so the payload
   is strictly anonymous and non-identifying -- an action name, whether the
   region is gated, and a pathname. No identifiers, no cookies, no storage
   read, nothing client-level. Anything more would be measuring people who have
   not yet agreed to be measured, which is the thing the banner exists to ask.
   ────────────────────────────────────────────────────────────────────────── */
async function handleConsent(req) {
  const raw = await req.text();
  let ev;
  try { ev = JSON.parse(raw); } catch { ev = null; }

  const action = ev && typeof ev.a === 'string' ? ev.a : '';
  if (!CONSENT_ACTIONS.includes(action)) {
    console.log(JSON.stringify({ evt: 'consent_rejected', reason: 'unknown_action' }));
    return new Response(null, { status: 400 });
  }

  console.log(JSON.stringify({
    evt: 'consent_event',
    action,
    gated: !!(ev && ev.g),
    page: typeof ev.p === 'string' ? ev.p.slice(0, 120) : '',
    ts: new Date().toISOString(),
  }));

  /* 204: nothing to say, and nothing to forward. A beacon ignores the body
     anyway, and a lead hook must never be reachable from this branch. */
  return new Response(null, { status: 204 });
}

/* Two paths, ONE implementation. A second file would mean a second copy of the
   empty-key filter, the byte-identical forwarding and the 502-before-read
   ordering -- and this month is a long argument about what a second copy costs.
   The paths differ; the plumbing does not. */
export const config = { path: ['/api/lead', '/api/partner'] };
/* LITERALS, NOT `PARTNER_PATH`. Netlify parses this export STATICALLY -- it
   reads the file, it does not execute it -- so an identifier here is
   unresolvable and the bundling stage fails the whole deploy, every function
   with it. The first version used the constant, `node` loaded the module
   happily, and the deploy died at "Build script returned non-zero exit code: 2".
   "The module loads" was the wrong test for a property that is never evaluated
   at runtime. The constant still governs the handler below, where it IS
   evaluated; gate 11q keeps the two in agreement. */
