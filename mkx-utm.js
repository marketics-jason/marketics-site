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
   feeds: same server-side lead-capture path that already
   collects form data regardless of the analytics cookie
   consent decision (see mkx-consent.js).
   ═══════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var KEY = 'mkx_utm';
  var PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];

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

  /* Read back anywhere on-site: window.mkxGetUTM() -> {utm_source, ...} or {} */
  window.mkxGetUTM = function () {
    try {
      var raw = sessionStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  };
})();
