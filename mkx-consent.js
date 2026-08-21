/* ═══════════════════════════════════════════════════════
   Marketics Cookie Consent — mkx-consent.js
   ~2KB inline. Replaces CookieYes entirely.
   
   Consent Mode v2 + EEA/UK/CH region gating (Board ruling 2026-08-21).

   Prior behaviour was a hard block: gtag.js was never requested until an Accept
   click, so declined and undecided traffic was invisible to GA4 entirely. That
   produced 2 measured users against 28 GSC clicks. Now:

   - The Consent Mode v2 defaults live INLINE in each page's head (they must sit
     in dataLayer before the config command). Denied in EEA/UK/CH, analytics
     granted elsewhere.
   - gtag.js now loads for EVERYONE. Under Consent Mode, denied traffic sends
     cookieless pings instead of nothing, so GA4 gets modelled aggregates.
   - The banner is shown only in EEA/UK/CH. Elsewhere consent is granted by
     default per the ruling, so the core market measures normally.
   - Clarity has no consent-mode equivalent and sets cookies unconditionally, so
     it stays gated on actual consent (explicit accept, or the granted default
     outside the EEA).
   - ad_storage / ad_user_data / ad_personalization stay DENIED everywhere, in
     every path, including after an Accept. The banner text promises "No
     advertising or third-party tracking" — granting them would contradict the
     notice the visitor just read. Changing that requires changing the banner
     copy first, which is a Strategy/Board call.

   Region detection for the banner is timezone-based (no network call, no
   dependency) and deliberately over-inclusive: any Europe/* zone gets the
   banner, and a detection failure gets the banner. Both mismatch directions
   degrade safely — Google resolves the actual region server-side for the
   consent signals themselves, so the measurement half is authoritative
   regardless of what the browser reports.

   Preference stored in localStorage (not a cookie); remembered 365 days;
   version bump forces re-consent when the policy changes.
   ═══════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var CONSENT_KEY = 'mkx_consent';
  var CONSENT_VER = '1'; // bump this to force re-consent after policy changes

  /* ── Region gate for the BANNER only ─────────────────
     The consent SIGNALS are region-scoped by Google server-side (see the inline
     defaults in each page head). This only decides whether a human sees a
     banner. Over-inclusive and fail-safe by design. */
  function looksEEA() {
    try {
      var tz = (Intl.DateTimeFormat().resolvedOptions().timeZone || '');
      if (tz.indexOf('Europe/') === 0) return true;
      // EEA territories that don't sit under Europe/*
      return ['Atlantic/Reykjavik', 'Atlantic/Canary', 'Atlantic/Madeira',
              'Atlantic/Azores', 'Atlantic/Faroe'].indexOf(tz) !== -1;
    } catch (e) {
      return true; // can't tell -> show the banner
    }
  }

  /* ── Push a consent decision to Google ────────────────
     ad_* deliberately omitted from the granted set; see the header note. */
  function updateConsent(granted) {
    if (typeof gtag !== 'function') return;
    var v = granted ? 'granted' : 'denied';
    gtag('consent', 'update', {
      analytics_storage: v,
      functionality_storage: v,
      personalization_storage: v,
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });
  }

  /* ── Consent-decision instrumentation (Aug 21 2026 CTO brief, P1) ──
     GA4 is gated behind this banner and was reporting ~2 users in 4 weeks
     against 28 GSC clicks on the homepage alone — consistent with most
     visitors never reaching Accept. This beacon is the denominator GA4
     can't see: it fires server-side (same consent-independent GHL webhook
     already used for lead capture, distinguished by the `event` field —
     same pattern as /join's `deposit_checkout_started`) on banner
     impression, accept, and decline, regardless of the visitor's answer.
     Best-effort only: swallow failures, never block the banner. */
  var GHL_HOOK = 'https://services.leadconnectorhq.com/hooks/Hdy5evIhEWpOMeRW92XG/webhook-trigger/1297f709-5970-411d-b58c-e3a47721392e';
  function beacon(event) {
    try {
      var body = JSON.stringify({ event: event, source: 'consent-banner', path: location.pathname, timestamp: new Date().toISOString() });
      if (navigator.sendBeacon) {
        navigator.sendBeacon(GHL_HOOK, new Blob([body], { type: 'application/json' }));
      } else {
        fetch(GHL_HOOK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: body, keepalive: true }).catch(function () {});
      }
    } catch (e) { /* non-critical */ }
  }

  /* ── Read stored consent ──────────────────────────── */
  function getConsent() {
    try {
      var raw = localStorage.getItem(CONSENT_KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (data.version !== CONSENT_VER) return null;
      // Expire after 365 days
      if (Date.now() - data.timestamp > 365 * 24 * 60 * 60 * 1000) return null;
      return data.accepted; // true or false
    } catch (e) {
      return null;
    }
  }

  /* ── Store consent decision ───────────────────────── */
  function setConsent(accepted) {
    try {
      localStorage.setItem(CONSENT_KEY, JSON.stringify({
        accepted: accepted,
        version: CONSENT_VER,
        timestamp: Date.now()
      }));
    } catch (e) { /* localStorage blocked — proceed without storing */ }
  }

  /* ── Idle delivery, gated on the load event ───────────
     Waits for `load` BEFORE scheduling on idle. Under Consent Mode these tags
     load for every non-EEA visitor rather than only after an Accept click, so
     for the first time they sit on the critical path of an ordinary pageview.
     requestIdleCallback alone can fire while the page is still painting.

     Measured, not assumed: /calculator's LCP regressed to ~5.5s against a 4s
     budget, reproducibly, across two CI runners — while the same commit's
     parent passed on a third. Blocking the two third-party scripts under
     matched throttling recovers ~430ms, and /calculator is the heaviest page
     so it tipped first. Gating on load keeps analytics off the render path.

     Trade-off, accepted: a visitor who leaves before the load event isn't
     measured. On a static site with self-hosted fonts that window is small,
     and Consent Mode feeds modelled aggregates regardless. */
  function idle(fn) {
    function schedule() {
      if ('requestIdleCallback' in window) {
        requestIdleCallback(fn, { timeout: 4000 });
      } else {
        setTimeout(fn, 1000);
      }
    }
    if (document.readyState === 'complete') schedule();
    else window.addEventListener('load', schedule, { once: true });
  }

  /* ── Fire analytics (only after acceptance) ──────── */
  function loadGA4() {
    // Loaded for everyone now. Consent Mode decides whether it may use storage;
    // denied traffic still contributes cookieless pings. The inline <head> stub
    // has already queued the consent defaults + gtag('js') + gtag('config', ID)
    // into dataLayer, in that order; loading gtag.js flushes the queue.
    idle(function () {
      if (window.__mkxGA4) return;
      window.__mkxGA4 = true;
      var g = document.createElement('script');
      g.async = 1;
      g.src = 'https://www.googletagmanager.com/gtag/js?id=G-51HW9TQFTJ';
      document.head.appendChild(g);
    });
  }

  function loadClarity() {
    // No consent-mode equivalent and it sets cookies unconditionally, so this
    // only runs on an actual grant.
    idle(function () {
      if (window.__mkxClarity) return;
      window.__mkxClarity = true;
      (function (c, l, a, r, i, t, y) {
        c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
        t = l.createElement(r); t.async = 1;
        t.src = 'https://www.clarity.ms/tag/' + i;
        y = l.getElementsByTagName(r)[0];
        y.parentNode.insertBefore(t, y);
      })(window, document, 'clarity', 'script', 'vx9dwjri01');
    });
  }

  /* ── Remove the banner ────────────────────────────── */
  function dismiss(banner) {
    banner.style.opacity = '0';
    banner.style.transform = 'translateY(8px)';
    setTimeout(function () {
      if (banner.parentNode) banner.parentNode.removeChild(banner);
    }, 300);
  }

  /* ── Render the consent banner ───────────────────── */
  function showBanner() {
    var styles = [
      /* Banner container */
      '#mkx-consent{',
        'position:fixed;bottom:24px;left:24px;right:24px;max-width:480px;',
        'background:#161616;border:1px solid rgba(214,173,96,.2);border-radius:6px;',
        'padding:20px 24px;z-index:99999;',
        'font-family:"DM Sans",system-ui,sans-serif;font-size:13px;line-height:1.55;',
        'color:rgba(248,246,242,.75);',
        'box-shadow:0 8px 40px rgba(0,0,0,.6);',
        'opacity:1;transform:translateY(0);',
        'transition:opacity .3s ease,transform .3s ease;',
      '}',
      /* Brand line */
      '#mkx-consent .mkx-brand{',
        'font-family:"Josefin Sans","DM Sans",system-ui,sans-serif;',
        'font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;',
        'color:rgba(214,173,96,.8);margin-bottom:10px;',
      '}',
      /* Text */
      '#mkx-consent p{margin:0 0 16px;color:rgba(248,246,242,.7);}',
      /* Underlined, not colour-only: the banner's gold sits at just 1.45:1
         against its own body text, well under the 3:1 that colour-alone
         differentiation needs. Applies to every page that loads the banner. */
      '#mkx-consent a{color:rgba(214,173,96,.8);text-decoration:underline;}',
      '#mkx-consent a:hover{color:rgba(214,173,96,1);}',
      /* Button row */
      '#mkx-consent .mkx-btns{display:flex;gap:10px;}',
      /* Accept button */
      '#mkx-accept{',
        'flex:1;padding:10px 16px;border:none;border-radius:4px;cursor:pointer;',
        'background:rgba(214,173,96,.9);color:#0f0f0f;',
        'font-family:"DM Sans",system-ui,sans-serif;font-size:12px;font-weight:600;',
        'letter-spacing:.04em;text-transform:uppercase;',
        'transition:background .15s;',
      '}',
      '#mkx-accept:hover{background:rgba(214,173,96,1);}',
      /* Decline button */
      '#mkx-decline{',
        'flex:1;padding:10px 16px;border:1px solid rgba(255,255,255,.1);border-radius:4px;',
        'cursor:pointer;background:transparent;',
        'color:rgba(248,246,242,.62);',
        'font-family:"DM Sans",system-ui,sans-serif;font-size:12px;',
        'letter-spacing:.04em;text-transform:uppercase;',
        'transition:border-color .15s,color .15s;',
      '}',
      '#mkx-decline:hover{border-color:rgba(255,255,255,.25);color:rgba(248,246,242,.7);}',
      /* Mobile */
      '@media(max-width:480px){',
        '#mkx-consent{left:12px;right:12px;bottom:12px;padding:16px 18px;}',
        '#mkx-consent .mkx-btns{flex-direction:column;}',
      '}'
    ].join('');

    var style = document.createElement('style');
    style.textContent = styles;
    document.head.appendChild(style);

    var banner = document.createElement('div');
    banner.id = 'mkx-consent';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Cookie consent');
    banner.innerHTML = [
      '<div class="mkx-brand">Marketics</div>',
      '<p>',
        'We use analytics cookies to understand how visitors use this site. ',
        'No advertising or third-party tracking. ',
        '<a href="/legal" target="_blank">Privacy Policy</a>',
      '</p>',
      '<div class="mkx-btns">',
        '<button id="mkx-accept">Accept</button>',
        '<button id="mkx-decline">Decline</button>',
      '</div>'
    ].join('');

    document.body.appendChild(banner);
    // Once per session — the banner re-renders on every pageview until answered,
    // and one webhook call per pageview would swamp the CRM.
    try {
      if (!sessionStorage.getItem('mkx_imp')) {
        sessionStorage.setItem('mkx_imp', '1');
        beacon('consent_impression');
      }
    } catch (e) { beacon('consent_impression'); }

    document.getElementById('mkx-accept').addEventListener('click', function () {
      setConsent(true);
      beacon('consent_accept');
      updateConsent(true);
      loadClarity();          // GA4 is already loaded; this is the cookie-setting one
      dismiss(banner);
    });

    document.getElementById('mkx-decline').addEventListener('click', function () {
      setConsent(false);
      beacon('consent_decline');
      updateConsent(false);   // explicit denial; GA4 keeps sending cookieless pings
      dismiss(banner);
    });
  }

  /* ── Entry point ──────────────────────────────────── */
  var consent = getConsent();
  var eea = looksEEA();

  // GA4 loads on every path now. Under Consent Mode the signals, not the script
  // tag, decide what it may store — which is the whole point of the change.
  loadGA4();

  if (consent === true) {
    updateConsent(true);
    loadClarity();
  } else if (consent === false) {
    updateConsent(false);
  } else if (!eea) {
    // Outside the EEA/UK/CH the inline defaults already grant analytics, so
    // there's nothing to ask and nothing to update — just the cookie-setting
    // tool to start.
    loadClarity();
  } else {
    // EEA/UK/CH, undecided: defaults are denied for this region; ask.
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }

})();
