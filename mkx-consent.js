/* ═══════════════════════════════════════════════════════
   Marketics Cookie Consent — mkx-consent.js
   ~2KB inline. Replaces CookieYes entirely.
   
   Consent Mode v2 + region gating. Board ruling 2026-08-21, amended by
   Addendum B (2026-08-30, superseding A3) and Addendum C (2026-09-01, amending
   B1). Full rationale lives in CANON-REGISTRY.md v3.10 and v3.19 — kept there,
   not here, because this file ships to every visitor and /calculator has no
   performance headroom to spare.

   - GATED (EEA/UK/CH + Canada): banner; all denied until Accept. Accept grants
     analytics, functionality, personalization and the two ad MEASUREMENT
     signals, and permits Clarity and the chat widget; Decline denies
     everything.
   - ELSEWHERE: no banner. Analytics and the two ad measurement signals granted
     by default, reversible by the footer "Do Not Sell or Share" control or GPC.
     Clarity still does not load — see the ungated branch.
   - EVERYWHERE, no exceptions: ad_personalization DENIED (Addendum C1). It is
     not granted by an Accept, by the ungated default, or by anything else.

   Region detection is timezone-based and deliberately over-inclusive: a
   detection failure gets the banner. Google resolves the real region
   server-side for the signals themselves.

   Preference stored in localStorage (not a cookie); remembered 365 days;
   version bump forces re-consent when the policy changes.
   ═══════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var CONSENT_KEY = 'mkx_consent';
  var CONSENT_VER = '1'; // bump this to force re-consent after policy changes

  /* ── Gated regions: banner shown, everything denied until Accept ──
     EEA/UK/CH, plus CANADA as of Addendum B2 (Quebec Law 25 posture).
     Timezone-based: no network call, no dependency, and deliberately
     over-inclusive — a detection failure gets the banner, which is the
     safe direction. */
  var CA_ZONES = [
    'America/Toronto', 'America/Vancouver', 'America/Edmonton', 'America/Winnipeg',
    'America/Halifax', 'America/St_Johns', 'America/Regina', 'America/Moncton',
    'America/Whitehorse', 'America/Yellowknife', 'America/Iqaluit', 'America/Inuvik',
    'America/Dawson', 'America/Dawson_Creek', 'America/Fort_Nelson', 'America/Creston',
    'America/Swift_Current', 'America/Rankin_Inlet', 'America/Resolute',
    'America/Cambridge_Bay', 'America/Glace_Bay', 'America/Goose_Bay',
    'America/Blanc-Sablon', 'America/Atikokan', 'America/Nipigon',
    'America/Thunder_Bay', 'America/Pangnirtung', 'America/Rainy_River'
  ];
  function inGatedRegion() {
    try {
      var tz = (Intl.DateTimeFormat().resolvedOptions().timeZone || '');
      if (tz.indexOf('Europe/') === 0) return true;
      if (CA_ZONES.indexOf(tz) !== -1) return true;
      // EEA territories that don't sit under Europe/*
      return ['Atlantic/Reykjavik', 'Atlantic/Canary', 'Atlantic/Madeira',
              'Atlantic/Azores', 'Atlantic/Faroe'].indexOf(tz) !== -1;
    } catch (e) {
      return true; // can't tell -> show the banner
    }
  }

  /* ── Opt-out of advertising signals (B1) ──────────────
     Two routes, one effect. Either flips the ad measurement signals to denied
     and keeps them there (ad_personalization is already denied for everyone
     under C1, so the opt-out has nothing left to do for it): the visitor's "Do Not Sell or Share" click, stored; or
     Global Privacy Control, which several US state laws require be honoured as
     a valid opt-out signal without any further action from the visitor.
     Analytics is untouched — the opt-out is about sale/sharing, not measurement. */
  var OPTOUT_KEY = 'mkx_ad_optout';
  function gpcOn() {
    try { return navigator.globalPrivacyControl === true; } catch (e) { return false; }
  }
  function optedOut() {
    if (gpcOn()) return true;
    try { return localStorage.getItem(OPTOUT_KEY) === '1'; } catch (e) { return false; }
  }
  function setOptOut() {
    try { localStorage.setItem(OPTOUT_KEY, '1'); } catch (e) { /* proceed unstored */ }
  }

  /* ── Push a consent decision to Google ────────────────
     `granted` covers analytics/functionality/personalization. The two
     MEASUREMENT ad signals follow it too (Addendum B1/B3) unless the visitor
     has opted out, in which case they are denied no matter what else was
     accepted.

     ad_personalization is the exception and is DENIED unconditionally
     (Addendum C1, amending B1). Not a variable, not derived from `granted`,
     and not granted by an Accept in the gated regions either — a hardcoded
     literal, so there is no path through this function that turns it on.
     Remarketing audiences are unusable below ~1,000 users and the six-week
     test will not reach that, so personalization buys nothing today while
     making the privacy policy harder to write. Conversion measurement — the
     CAC read this whole build exists for — rides ad_storage and ad_user_data
     and is unaffected. Revisit is trigger-gated, not automatic: a scale
     ruling at activation + 6 weeks, with policy language to match. */
  function updateConsent(granted) {
    if (typeof gtag !== 'function') return;
    var v = granted ? 'granted' : 'denied';
    var ad = (granted && !optedOut()) ? 'granted' : 'denied';
    gtag('consent', 'update', {
      analytics_storage: v,
      functionality_storage: v,
      personalization_storage: v,
      ad_storage: ad,
      ad_user_data: ad,
      ad_personalization: 'denied'
    });
  }

  /* ── Consent-decision instrumentation — REMOVED 2026-09-03 (registry v3.30) ──
     A beacon here posted consent_impression / consent_accept / consent_decline /
     ad_optout to a GHL inbound webhook. It never delivered a single event, from
     the day it shipped.

     `navigator.sendBeacon()` always sends with credentials mode 'include' —
     specified behaviour, not a browser quirk and not an extension. The body was
     a Blob typed `application/json`, which is NOT CORS-safelisted, so the
     request required a preflight; GHL answers preflights with a wildcard
     `Access-Control-Allow-Origin: *`, which is invalid under credentials mode
     'include'. The preflight failed every time, and a failed preflight sends
     nothing at all. Four console errors per banner, zero data.

     It cost more than it ever returned: on 2026-09-03 those errors were read as
     a broken LEAD path and "fixed" with a Content-Type change GHL rejects,
     dropping ~20 minutes of real submissions (registry v3.29). The lead form was
     never involved — it is a different endpoint on the same page.

     Do not re-add it in this shape. If consent telemetry is wanted again it goes
     through a same-origin proxy, where CORS does not apply at all: it is a
     browser-enforced mechanism and a same-origin request never triggers it.
     Gated in validate-site.py and scripts/smoke.sh. */
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
  var GA4_ID = 'G-51HW9TQFTJ';
  var ADS_ID = 'AW-18418837499';
  var ADS_PAGES = ['/lp/keep-control'];
  function adsAllowedHere() {
    var p = location.pathname.replace(/\/+$/, '') || '/';
    return ADS_PAGES.indexOf(p) !== -1;
  }

  function loadGA4() {
    // Loaded for everyone now. Consent Mode decides whether it may use storage;
    // denied traffic still contributes cookieless pings. The inline <head> stub
    // has already queued the consent defaults + gtag('js') + gtag('config', ID)
    // into dataLayer, in that order; loading gtag.js flushes the queue.
    idle(function () {
      if (window.__mkxGA4) return;
      window.__mkxGA4 = true;

      /* ── Stamp automated traffic as internal (registry v3.25) ──
         Lighthouse CI loads three pages three times each on every PR, in
         headless Chrome with open internet and no CSP (lhci serves from its own
         static server, so netlify.toml never applies). Those hits are real GA4
         page_views: the 2026-09-03 Realtime panel showed /calculator/index.html
         and /lp/keep-control/index.html at 3 users each, which is numberOfRuns
         exactly. The `/index.html` suffix is the tell — no real visitor ever
         sees those paths.

         It matters more from today: opening connect-src means CI's full event
         stream now transmits, where before the header was refusing it.

         STAMPED, NOT SUPPRESSED. Skipping gtag.js under webdriver would also
         stop measuring what the tag COSTS, and v3.14 exists because the Ads tag
         cost /calculator ~1,850ms of LCP. A prettier score that hides real
         third-party weight is the wrong trade, especially with /calculator
         sitting on its 0.80 floor. So the tag loads exactly as it does for a
         visitor; only the data is marked.

         NO GAP, as of the config-time stamp (registry v3.26). The first version
         of this stamped via a separate gtag('set'), which left the stub's own
         page_view unstamped — the stub queues gtag('config') during parse, so it
         flushes first. The stub now carries the parameter on the config call
         itself, in all 53 pages, so nothing goes out unmarked. This `set` is the
         net for anything configured AFTER the stub — the Ads destination below
         being the case that exists today.

         There is no GA4 data filter that matches URL patterns. Data filters are
         Developer traffic and Internal traffic only, and Internal traffic tests
         `traffic_type`. That is why the stamp has to come from the page. */
      try {
        if (navigator.webdriver === true) gtag('set', { traffic_type: 'internal' });
      } catch (e) { /* never let instrumentation break the tag */ }

      // Ads is a second DESTINATION on this same library, never a second
      // library, and it is configured here rather than in page markup so it
      // lands after the region-aware grant above. Conversions are the audit
      // lead, not pageviews. Both rules and why: registry v3.12.
      //
      // Restricted to the paid landing page. A second destination is not free:
      // configuring it site-wide cost /calculator 1,850ms of mobile LCP and
      // failed the gate (registry v3.14). Paid traffic lands on the LP and the
      // no-exit rule keeps it there, so the LP is the whole paid path and the
      // only page where a conversion can happen. CI enforces all of this; see
      // validate-site.py.
      if (adsAllowedHere()) gtag('config', ADS_ID);

      var g = document.createElement('script');
      g.async = 1;
      g.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
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

  /* ── GHL chat widget (Addendum B4) ───────────────────
     One page only. It used to load on 34, and on 33 of them 5s after load with
     no interaction — a third-party script for a visitor who had done nothing.
     Never on /lp/keep-control, where the form is the only door. In gated
     regions it waits for Accept; elsewhere the 5s timer. No page exceptions.

     One page, not two: B4 also names /audit-request, which has never existed
     here — a stale name for /get-started. Not carried in the allowlist,
     because an entry for a path that does not exist is how the name survives
     to the next brief. */
  var WIDGET_PAGES = ['/get-started'];
  function widgetAllowedHere() {
    var p = location.pathname.replace(/\/+$/, '') || '/';
    return WIDGET_PAGES.indexOf(p) !== -1;
  }
  function loadWidget() {
    if (!widgetAllowedHere() || window.__mkxWidget) return;
    // Defensive: the per-page inline loaders this replaces keep their own
    // closure flag and cannot see window.__mkxWidget, so until every one of
    // them is removed, check the DOM for a loader that is already there. Two
    // copies of the widget is a worse bug than none.
    if (document.querySelector('script[src*="widgets.leadconnectorhq.com"]')) return;
    window.__mkxWidget = true;
    var s = document.createElement('script');
    s.src = 'https://widgets.leadconnectorhq.com/loader.js';
    s.setAttribute('data-resources-url', 'https://widgets.leadconnectorhq.com/chat-widget/loader.js');
    s.setAttribute('data-widget-id', '67322c9be99a3280cce39a8e');
    s.async = true;
    document.body.appendChild(s);
  }

  /* ── "Do Not Sell or Share My Personal Information" (B1) ──
     Required wherever the ungated default grants ad signals. Injected from here
     rather than hand-added to 51 footers: one implementation cannot drift, and
     a footer that silently lost the link on one page is what no template engine
     is here to prevent. A control, not a link — it acts in place and navigates
     nowhere, so it can sit on /lp/keep-control without breaking no-exit. Gated
     regions don't get it; there the banner is the mechanism. */
  function mountOptOut(gated) {
    if (gated) return;
    function mount() {
      var foot = document.querySelector('footer');
      if (!foot || document.getElementById('mkx-dns')) return;
      var st = document.createElement('style');
      st.textContent = '#mkx-dns{background:none;border:0;padding:0;margin:0;cursor:pointer;' +
        'font:inherit;color:inherit;opacity:.85;text-decoration:underline;text-underline-offset:2px;}' +
        '#mkx-dns:hover{opacity:1;}' +
        '#mkx-dns:focus-visible{outline:2px solid currentColor;outline-offset:3px;}' +
        '#mkx-dns[disabled]{cursor:default;text-decoration:none;opacity:.6;}';
      document.head.appendChild(st);

      var sep = document.createElement('span');
      sep.setAttribute('aria-hidden', 'true');
      sep.textContent = '·';
      sep.style.cssText = 'opacity:.4;margin:0 10px;';

      var b = document.createElement('button');
      b.id = 'mkx-dns';
      b.type = 'button';
      b.textContent = optedOut() ? 'Advertising opted out' : 'Do Not Sell or Share My Personal Information';
      if (optedOut()) b.disabled = true;
      b.addEventListener('click', function () {
        setOptOut();
        updateConsent(true);   // analytics stays; the three ad signals go denied
        b.textContent = 'Advertising opted out';
        b.disabled = true;
      });
      foot.appendChild(sep);
      foot.appendChild(b);
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', mount);
    } else {
      mount();
    }
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
        'We use cookies for analytics and advertising measurement if you accept. ',
        'No tracking if you decline. ',
        '<a href="/legal" target="_blank">Privacy Policy</a>',
      '</p>',
      '<div class="mkx-btns">',
        '<button id="mkx-accept">Accept</button>',
        '<button id="mkx-decline">Decline</button>',
      '</div>'
    ].join('');

    document.body.appendChild(banner);

    document.getElementById('mkx-accept').addEventListener('click', function () {
      setConsent(true);
      updateConsent(true);    // B3, as amended by C1: everything except ad_personalization
      loadClarity();          // GA4 is already loaded; this is the cookie-setting one
      loadWidget();           // B4: in gated regions the chat widget waits for this
      dismiss(banner);
    });

    document.getElementById('mkx-decline').addEventListener('click', function () {
      setConsent(false);
      updateConsent(false);   // explicit denial; GA4 keeps sending cookieless pings
      dismiss(banner);
    });
  }

  /* ── Entry point ──────────────────────────────────── */
  var consent = getConsent();
  var gated = inGatedRegion();

  mountOptOut(gated);

  // ORDERING, load-bearing: the inline <head> stub only QUEUES the defaults,
  // gtag('js') and gtag('config'). Nothing is sent until gtag.js loads, and
  // gtag.js is injected here inside idle(), after load — so every
  // updateConsent() below lands in the queue ahead of the flush. That is what
  // lets this file, not 51 duplicated stubs, decide consent: the stubs stay
  // deny-advertising as the fail-safe, the grant happens where the region is
  // known.
  loadGA4();

  if (consent === true) {
    updateConsent(true);
    loadClarity();
    loadWidget();           // accepted on a previous pageview
  } else if (consent === false) {
    updateConsent(false);   // declined: nothing loads, widget included
  } else if (!gated) {
    setTimeout(loadWidget, 5000);   // B4: the standard timer, ungated regions
    // B1: ad MEASUREMENT signals granted by default here, reversible by the
    // opt-out control or GPC — updateConsent() applies that itself. Explicit
    // rather than inherited, because the inline stubs deny advertising
    // everywhere as the fail-safe. ad_personalization is not among them: C1
    // denies it everywhere, so the stubs' denial simply stands.
    updateConsent(true);
    // Clarity still does NOT load here — explicit Accept only. Measured: it is
    // a session recorder whose DOM serialisation on load blew /calculator's 4s
    // LCP budget (CI bisect; main-thread, not bandwidth). Principled: session
    // recording has no cookieless mode to degrade to, so riding an implied
    // default is wrong for it. The Board's ruling was about GA4 measurement.
  } else {
    // Gated (EEA/UK/CH/CA), undecided: deny and ask. Explicit, because the
    // stubs' region list has no Canada and their ungated line grants analytics,
    // so a Canadian would otherwise be measured before answering.
    updateConsent(false);
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }

})();
