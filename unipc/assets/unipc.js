/* UNIPC — progressive enhancement only.
   Everything here is optional: pages render and forms submit (native mailto)
   with this file absent or blocked. JS only improves the experience. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Scroll reveal ------------------------------------------------- */
  function initFade() {
    var nodes = document.querySelectorAll('[data-fade]');
    if (!nodes.length) return;
    if (reduce || !('IntersectionObserver' in window)) return; // stay fully visible
    // Hide only now that we can animate; each element carries its own hidden state.
    nodes.forEach(function (n) { n.classList.add('u-fade'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -5% 0px' });
    nodes.forEach(function (n) { io.observe(n); });
    // Safety net: whatever happens, never leave content hidden.
    setTimeout(function () {
      nodes.forEach(function (n) { n.classList.add('is-in'); });
    }, 1600);
  }

  /* ---- Mailto forms with inline success ------------------------------ */
  /* A form opts in with data-unipc-form and data-subject="…".
     On submit we build a plain-text mailto to eosg@unipc.info from the
     fields, then flip the card to its .form-success view. Without JS the
     form still posts natively (action=mailto) so it degrades cleanly. */
  function serialize(form) {
    var out = [];
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || el.type === 'submit' || el.type === 'button') return;
      var label = el.getAttribute('data-label') || el.name;
      out.push(label + ': ' + (el.value || ''));
    });
    return out.join('\n');
  }
  function initForms() {
    document.querySelectorAll('[data-unipc-form]').forEach(function (form) {
      var card = form.closest('[data-form-card]') || form.parentNode;
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var subject = form.getAttribute('data-subject') || 'UNIPC';
        var extra = form.getAttribute('data-body-prefix');
        var body = (extra ? extra + '\n' : '') + serialize(form);
        window.location.href = 'mailto:eosg@unipc.info?subject=' +
          encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
        if (card) card.classList.add('is-submitted');
      });
    });
  }

  /* ---- Donate: amount selector, card formatting, submit -------------- */
  function initDonate() {
    var root = document.querySelector('[data-donate]');
    if (!root) return;

    var amountBtns = root.querySelectorAll('[data-amount]');
    var otherBtn = root.querySelector('[data-amount-other]');
    var otherWrap = root.querySelector('[data-other-wrap]');
    var customInput = root.querySelector('[data-custom-amount]');
    var submitLabel = root.querySelector('[data-give-label]');
    var amountField = root.querySelector('[data-amount-field]'); /* hidden, for mailto body */

    var state = { amount: 50, isOther: false, custom: '' };

    function effective() {
      if (state.isOther) { var n = parseInt(state.custom, 10); return isNaN(n) ? 0 : n; }
      return state.amount;
    }
    function label() { var a = effective(); return a > 0 ? '$' + a : 'your gift'; }

    function paint() {
      amountBtns.forEach(function (b) {
        var v = b.hasAttribute('data-amount-other') ? 'other' : parseInt(b.getAttribute('data-amount'), 10);
        var active = state.isOther ? (v === 'other') : (v === state.amount);
        b.classList.toggle('is-selected', active);
        b.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
      if (otherWrap) otherWrap.hidden = !state.isOther;
      if (submitLabel) submitLabel.textContent = label();
      if (amountField) amountField.value = label();
    }

    amountBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        if (b.hasAttribute('data-amount-other')) { state.isOther = true; }
        else { state.amount = parseInt(b.getAttribute('data-amount'), 10); state.isOther = false; }
        paint();
        if (state.isOther && customInput) customInput.focus();
      });
    });
    if (customInput) customInput.addEventListener('input', function () { state.custom = customInput.value; paint(); });

    var cardNum = root.querySelector('[data-card-number]');
    if (cardNum) cardNum.addEventListener('input', function () {
      var d = cardNum.value.replace(/\D/g, '').slice(0, 16);
      cardNum.value = d.replace(/(.{4})/g, '$1 ').trim();
    });
    var exp = root.querySelector('[data-expiry]');
    if (exp) exp.addEventListener('input', function () {
      var d = exp.value.replace(/\D/g, '').slice(0, 4);
      exp.value = d.length > 2 ? d.slice(0, 2) + '/' + d.slice(2) : d;
    });
    var cvc = root.querySelector('[data-cvc]');
    if (cvc) cvc.addEventListener('input', function () {
      cvc.value = cvc.value.replace(/\D/g, '').slice(0, 4);
    });

    var confirmAmount = root.querySelector('[data-confirm-amount]');
    var form = root.querySelector('[data-donate-form]');
    if (form) form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = (root.querySelector('[data-card-name]') || {}).value || '';
      var email = (root.querySelector('[data-receipt-email]') || {}).value || '';
      var body = 'Intended gift: ' + label() + '\nName: ' + name + '\nEmail: ' + email +
        '\n(Demonstration form — no payment processed)';
      window.location.href = 'mailto:eosg@unipc.info?subject=' +
        encodeURIComponent('Donation intent — UNIPC') + '&body=' + encodeURIComponent(body);
      if (confirmAmount) confirmAmount.textContent = label();
      var card = root.querySelector('[data-form-card]');
      if (card) card.classList.add('is-submitted');
    });

    paint();
  }

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }
  ready(function () { initFade(); initForms(); initDonate(); });
})();
