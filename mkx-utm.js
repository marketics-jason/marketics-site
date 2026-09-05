/* ═══════════════════════════════════════════════════════
   Marketics UTM Capture — mkx-utm.js
   ~0.5KB. First-touch UTM capture, session-scoped.

   Persists utm_source/medium/campaign/content/term, the
   first-touch landing path and the first-touch timestamp to
   sessionStorage on the first page a visitor lands on with
   UTM params in the URL, so campaign attribution survives
   on-site navigation through to the conversion event (form
   submit on /get-started, checkout start on /join). Internal
   navigation with no UTM params in the URL leaves whatever
   was captured on landing untouched — first touch wins for
   the session, not last click.

   Consent-independent by design, matching the GHL webhook it
   feeds: the same lead-capture path that collects form data
   regardless of the analytics cookie consent decision
   (see mkx-consent.js).

   Consent-independent, NOT server-side — this comment used to
   say server-side and it was wrong. The POST originates in the
   visitor's browser, so a content blocker that blocks the vendor
   domain blocks the lead itself, not just its measurement. The
   two properties are unrelated; keep them apart.
   ═══════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var KEY = 'mkx_utm';
  var LAND_KEY = 'mkx_landing';
  var TS_KEY = 'mkx_ts';
  var PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];

  /* First-touch landing page. The lead form lives on /get-started, so every CRM
     record used to read source:"get-started" regardless of where the session
     actually began — landing pages were distinguishable only by utm_campaign,
     which comes from the ad and is absent if someone reaches an LP without one.
     Captured once per session, first page wins, same as the UTMs. */
  try {
    if (!sessionStorage.getItem(LAND_KEY)) {
      sessionStorage.setItem(LAND_KEY, window.location.pathname);

      /* First-touch TIMESTAMP (authorised by CTO, 2026-09-05). Written INSIDE
         the landing-page guard on purpose: the two record the SAME event, so
         they are set together or not at all.

         The case that guard exists for: a session that already carries a
         landing page had its first touch before this line shipped. Setting the
         timestamp there would record "now" for a moment that has already
         passed — a plausible wrong number, which is worse than blank and is the
         exact reason mapping `submittedAt` into this field was refused. That
         value is real, it is just a different moment, and a CRM field full of
         confidently wrong timestamps cannot be distinguished from a correct one
         after the fact. Those sessions get no value, correctly.

         ISO 8601 UTC, matching `submittedAt` so the two subtract cleanly. */
      sessionStorage.setItem(TS_KEY, new Date().toISOString());
    }
  } catch (e) { /* sessionStorage blocked */ }

  try {
    var params = new URLSearchParams(window.location.search);
    var found = {};
    var hasAny = false;
    PARAMS.forEach(function (p) {
      var v = params.get(p);
      if (v) { found[p] = v; hasAny = true; }
    });
    if (hasAny) {
      sessionStorage.setItem(KEY, JSON.stringify(found));
    }
  } catch (e) { /* sessionStorage blocked — proceed without persisting */ }

  /* ── Click identifiers (gclid / wbraid / gbraid) — CONSENT-GATED ──
     Ruled Jason, Sep 4 2026, amending Code's CTO brief of the same day.

     These are NOT treated like the UTM parameters above, and the difference is
     deliberate. `utm_campaign=spring_promo` describes an ad. A `gclid` names a
     single click, and once it sits in the CRM beside an email address it is
     tied to a person. So it is captured ONLY where `ad_storage` is granted:
     ungated traffic by default, gated regions on Accept, never for a visitor
     who was shown the banner and declined or ignored it.

     That gate is what MOOTS the privacy question rather than deferring it. The
     consent-independent variant was considered and NOT shipped; it goes to
     counsel (C4) first if it is ever wanted. Do not "simplify" this to an
     unconditional capture — the condition is the ruling.

     Held in memory until the grant arrives, because the URL carrying the id
     exists only on the landing page. A gated-region visitor who accepts while
     still on that page is captured; one who navigates away first is not, and
     that is correct rather than a gap. */
  var CLICK_KEY = 'mkx_click';
  var CLICK_PARAMS = ['gclid', 'wbraid', 'gbraid'];
  var pendingClick = null;

  try {
    var cparams = new URLSearchParams(window.location.search);
    var pend = {};
    CLICK_PARAMS.forEach(function (p) {
      var v = cparams.get(p);
      if (v) { pend[p] = v; }
    });
    for (var k in pend) { if (pend.hasOwnProperty(k)) { pendingClick = pend; break; } }
  } catch (e) { /* no URLSearchParams — nothing pending, nothing breaks */ }

  /* Effective ad_storage, read off the same dataLayer gtag reads. Region-scoped
     defaults are skipped: they apply only inside their region list, and this
     file cannot tell whether we are in it. Skipping them is the conservative
     read — it can only withhold capture, never grant it. */
  function adStorageGranted() {
    try {
      var dl = window.dataLayer || [];
      var state = 'denied';
      for (var i = 0; i < dl.length; i++) {
        var a = dl[i];
        if (!a || a[0] !== 'consent' || !a[2]) { continue; }
        if (a[2].region) { continue; }
        if (typeof a[2].ad_storage === 'string') { state = a[2].ad_storage; }
      }
      return state === 'granted';
    } catch (e) { return false; }
  }

  /* Idempotent, and safe to call before or after consent resolves. Called once
     below for ungated traffic (whose grant has already landed by the time this
     file runs) and again by mkx-consent.js the moment a gated visitor accepts. */
  window.mkxCommitClickIds = function () {
    try {
      if (!pendingClick) { return; }
      if (!adStorageGranted()) { return; }
      if (sessionStorage.getItem(CLICK_KEY)) { return; }   // first touch wins
      sessionStorage.setItem(CLICK_KEY, JSON.stringify(pendingClick));
    } catch (e) { /* sessionStorage blocked — proceed without persisting */ }
  };

  /* Read back anywhere on-site: window.mkxGetClickIds() -> {gclid} or {} */
  window.mkxGetClickIds = function () {
    try {
      var raw = sessionStorage.getItem(CLICK_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  };

  window.mkxCommitClickIds();

  /* Read back anywhere on-site: window.mkxGetFirstTouchTS() -> ISO 8601 or "" */
  window.mkxGetFirstTouchTS = function () {
    try { return sessionStorage.getItem(TS_KEY) || ''; } catch (e) { return ''; }
  };

  /* Read back anywhere on-site: window.mkxGetLanding() -> "/lp/keep-control" or "" */
  window.mkxGetLanding = function () {
    try { return sessionStorage.getItem(LAND_KEY) || ''; } catch (e) { return ''; }
  };

  /* Read back anywhere on-site: window.mkxGetUTM() -> {utm_source, ...} or {} */
  window.mkxGetUTM = function () {
    try {
      var raw = sessionStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  };
})();
