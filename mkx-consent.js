/* ═══════════════════════════════════════════════════════
   Marketics Cookie Consent — mkx-consent.js
   ~2KB inline. Replaces CookieYes entirely.
   
   Consent Mode v2 + region gating. Board ruling 2026-08-21, amended by
   Addendum B (2026-08-30), which supersedes Addendum A3.

   Two populations, and the difference is the whole design:

   - GATED REGIONS — EEA/UK/CH and, as of B2, CANADA. Banner shown. Everything
     denied until an explicit Accept. On Accept all four signal families are
     granted, Clarity may load, and the chat widget may load. On Decline
     nothing loads.
   - EVERYWHERE ELSE — no banner. Analytics AND the three advertising signals
     are granted by default (B1), disclosed in the privacy policy, and
     reversible by the visitor at any time through the "Do Not Sell or Share My
     Personal Information" control in the footer, or automatically by a Global
     Privacy Control signal. Clarity still does not load here — see the note at
     the ungated branch.

   WHY THE GRANT LIVES IN THIS FILE AND NOT IN THE 51 INLINE STUBS. The inline
   Consent Mode defaults must sit in dataLayer before the config command, so
   they are duplicated in every page head. They deny advertising everywhere,
   and that stays true: it is the fail-safe if this script is blocked or fails.
   gtag.js is injected from here, on idle, after the load event — so nothing is
   ever SENT until this file has run, and every update it pushes is queued
   ahead of the flush. One file decides; 51 copies stay conservative. It also
   means Canada could join the gated set without editing 51 region lists.

   Region detection is timezone-based (no network call, no dependency) and
   deliberately over-inclusive: any Europe/* zone or Canadian zone gets the
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
     Two routes, one effect. Either flips the three ad signals to denied and
     keeps them there: the visitor's "Do Not Sell or Share" click, stored; or
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
     `granted` covers analytics/functionality/personalization. Advertising
     signals follow it too (Addendum B1/B3) unless the visitor has opted out,
     in which case they are denied no matter what else was accepted. */
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
      ad_personalization: ad
    });
  }

  /* ── Consent-decision instrumentation (Aug 21 2026 CTO brief, P1) ──
     GA4 is gated behind this banner and was reporting ~2 users in 4 weeks
     against 28 GSC clicks on the homepage alone — consistent with most
     visitors never reaching Accept. This beacon is the denominator GA4
     can't see: it posts to the same CONSENT-INDEPENDENT GHL webhook already
     used for lead capture, distinguished by the `event` field (same pattern as
     /join's `deposit_checkout_started`), on banner impression, accept and
     decline, regardless of the visitor's answer.

     CONSENT-INDEPENDENT IS NOT SERVER-SIDE. This comment used to say
     "server-side" and it was wrong: the request originates in the browser, so a
     content blocker that blocks the vendor domain blocks it. The two properties
     are unrelated and the conflation was relied on downstream — hence the
     distinction is spelled out here rather than assumed.

     Second limitation, worth knowing before citing the number: the beacon only
     fires where a banner renders, i.e. gated regions. It is not a site-wide
     accept rate and never was.

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

  /* ── GHL chat widget (Addendum B4) ───────────────────
     Restricted to the audit-request form page, where a question mid-form is a
     real support need. It used to load on 34 pages, and on 33 of them five
     seconds after load with no interaction at all — a third-party script and
     its storage for a visitor who had done nothing and, outside the gated
     regions, been asked nothing.

     Never on /lp/keep-control: that page's whole discipline is that the form is
     the only door, and a chat widget is a second one.

     One behaviour, no per-page exceptions: in gated regions it waits for an
     explicit Accept (called from the banner handler); everywhere else it loads
     on the standard 5s timer. */
  // One page, not two. Addendum B4 names "/get-started and /audit-request", but
  // /audit-request has never existed on this site — it is a stale name for
  // /get-started that has travelled through the Aug 30 design handoff and both
  // board memos. Recorded here rather than kept in the allowlist, because an
  // allowlist entry for a path that does not exist is how the name survives to
  // the next brief.
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
     Required wherever the ungated default grants advertising signals. Injected
     from here rather than hand-added to 51 hand-authored footers, for the same
     reason the banner is: one implementation cannot drift out of sync with
     itself, and a footer that silently lost the link on one page is exactly the
     failure this site has no template engine to prevent.

     It is a control, not a link — it acts in place and navigates nowhere, which
     is why it can also sit on /lp/keep-control without breaking the no-exit
     rule. Gated regions don't get it: there the banner is the mechanism, and
     advertising is denied until someone opts IN. */
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
        beacon('ad_optout');
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
      updateConsent(true);    // B3: all four signals, advertising included
      loadClarity();          // GA4 is already loaded; this is the cookie-setting one
      loadWidget();           // B4: in gated regions the chat widget waits for this
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
  var gated = inGatedRegion();

  // The "Do Not Sell or Share" control is a legal requirement wherever the
  // ungated default grants advertising signals, so it is mounted before any
  // branch below decides what those signals are.
  mountOptOut(gated);

  // GA4 loads on every path now. Under Consent Mode the signals, not the script
  // tag, decide what it may store — which is the whole point of the change.
  //
  // ORDERING, and it is load-bearing: the inline <head> stub only QUEUES the
  // defaults, gtag('js') and gtag('config') into dataLayer. Nothing is sent
  // until gtag.js itself loads, and gtag.js is injected here — inside idle(),
  // after the load event. Every updateConsent() call below therefore lands in
  // the queue ahead of the flush. That is what lets this file, rather than 51
  // duplicated inline stubs, be the single place that decides consent: the
  // inline defaults stay deny-advertising everywhere as a fail-safe, and the
  // grant happens here where the region is actually known.
  loadGA4();

  if (consent === true) {
    updateConsent(true);
    loadClarity();
    loadWidget();           // accepted on a previous pageview
  } else if (consent === false) {
    updateConsent(false);   // declined: nothing loads, widget included
  } else if (!gated) {
    setTimeout(loadWidget, 5000);   // B4: the standard timer, ungated regions
    // Addendum B1 — outside the gated regions the advertising signals are
    // GRANTED by default, disclosed in the privacy policy, and reversible by
    // the "Do Not Sell or Share" control or a GPC header. updateConsent()
    // applies the opt-out itself, so this one call is correct either way.
    //
    // This is an explicit update rather than a reliance on the inline default,
    // because the inline default denies advertising on every page (fail-safe if
    // this script never runs) and Canada now falls under the gated branch
    // without the region list in those 51 stubs having to know about it.
    updateConsent(true);
    //
    // Clarity deliberately does NOT load here. It only runs on an explicit
    // Accept (the branch above). Two reasons, one measured and one principled:
    //
    //  - Measured: Clarity is a session recorder. It instruments the DOM and
    //    serialises the page on load, and on /calculator — the heaviest, most
    //    DOM-dense page on the site — that main-thread work delays the <h1>
    //    paint enough to blow the 4s LCP budget. CI bisect isolated item 1 as
    //    the cause; the network timeline shows every third-party file finishing
    //    by 816ms while main-thread work runs to 2.1s and LCP lands at 5.3s,
    //    equal to TTI. It was never bandwidth.
    //  - Principled: session recording is a bigger ask than analytics, it has
    //    no Consent Mode equivalent so it can't degrade to a cookieless mode,
    //    and riding an implied default is the wrong default for it. The Board's
    //    ruling was about GA4 measurement; it did not ask for this.
  } else {
    // Gated region (EEA/UK/CH/CA), undecided: deny everything and ask.
    //
    // The deny is explicit rather than inherited. The inline stubs' region list
    // covers EEA/UK/CH but not Canada, and their ungated line grants analytics —
    // so a Canadian visitor would otherwise be measured before answering. This
    // call closes that without editing 51 pages.
    updateConsent(false);
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }

})();
