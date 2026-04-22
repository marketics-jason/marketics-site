/* ═══════════════════════════════════════════════════════
   Marketics Cookie Consent — mkx-consent.js
   ~2KB inline. Replaces CookieYes entirely.
   
   GDPR / PIPEDA compliant:
   - No non-essential cookies set before consent
   - Preference stored in localStorage (not a cookie)
   - Accept / Decline options clearly presented
   - Decision remembered for 365 days
   - Version bump forces re-consent when cookie policy changes
   ═══════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var CONSENT_KEY = 'mkx_consent';
  var CONSENT_VER = '1'; // bump this to force re-consent after policy changes

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

  /* ── Fire analytics (only after acceptance) ──────── */
  function loadAnalytics() {
    // Clarity — loaded idle to avoid main-thread congestion
    (function (fn) {
      if ('requestIdleCallback' in window) {
        requestIdleCallback(fn, { timeout: 4000 });
      } else {
        setTimeout(fn, 4000);
      }
    })(function () {
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
      '#mkx-consent a{color:rgba(214,173,96,.8);text-decoration:none;}',
      '#mkx-consent a:hover{text-decoration:underline;}',
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
        'color:rgba(248,246,242,.45);',
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

    document.getElementById('mkx-accept').addEventListener('click', function () {
      setConsent(true);
      loadAnalytics();
      dismiss(banner);
    });

    document.getElementById('mkx-decline').addEventListener('click', function () {
      setConsent(false);
      dismiss(banner);
    });
  }

  /* ── Entry point ──────────────────────────────────── */
  var consent = getConsent();

  if (consent === true) {
    // Already accepted — fire analytics immediately
    loadAnalytics();
  } else if (consent === false) {
    // Already declined — do nothing, no analytics
  } else {
    // No decision yet — show banner after DOM ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }

})();
