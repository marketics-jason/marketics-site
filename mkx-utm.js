/* ═══════════════════════════════════════════════════════
   Marketics UTM Capture — mkx-utm.js
   ~0.5KB. First-touch UTM capture, session-scoped.

   Persists utm_source/medium/campaign/content/term to
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
  var PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];

  /* First-touch landing page. The lead form lives on /get-started, so every CRM
     record used to read source:"get-started" regardless of where the session
     actually began — landing pages were distinguishable only by utm_campaign,
     which comes from the ad and is absent if someone reaches an LP without one.
     Captured once per session, first page wins, same as the UTMs. */
  try {
    if (!sessionStorage.getItem(LAND_KEY)) {
      sessionStorage.setItem(LAND_KEY, window.location.pathname);
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
