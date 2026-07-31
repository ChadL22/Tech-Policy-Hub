// Tech Policy Hub — shared interactions
document.addEventListener('DOMContentLoaded', function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', nav.classList.contains('open'));
    });
  }

  // Mobile dropdown toggle (tap to expand submenu instead of hover)
  document.querySelectorAll('.has-dropdown > .nav-link').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (window.innerWidth <= 720) {
        e.preventDefault();
        var parent = link.parentElement;
        parent.classList.toggle('mobile-open');
        var dd = parent.querySelector('.dropdown');
        if (dd) dd.style.display = parent.classList.contains('mobile-open') ? 'block' : 'none';
      }
    });
  });

  // Tabs (used on topic pages: Projects / Publications / People)
  document.querySelectorAll('.tabs').forEach(function (tabGroup) {
    var buttons = tabGroup.querySelectorAll('.tab-btn');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var target = btn.getAttribute('data-tab');
        var panelGroup = tabGroup.parentElement;
        panelGroup.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
        panelGroup.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });
        btn.classList.add('active');
        var panel = panelGroup.querySelector('.tab-panel[data-tab="' + target + '"]');
        if (panel) panel.classList.add('active');
      });
    });
  });

  // Newsletter signup -- submits to The Phronesis Institute's live subscribe
  // API (same endpoint their own site uses: POST /api/subscribe on
  // phronesisresearch.org, which is CORS-open and also syncs to their
  // Substack). This duplicates their real subscribe functionality here
  // rather than just linking out.
  var PHRONESIS_SUBSCRIBE_URL = 'https://phronesisresearch.org/api/subscribe';

  document.querySelectorAll('.newsletter-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var input = form.querySelector('input[type="email"]');
      var button = form.querySelector('button');
      var email = input.value.trim();

      var existing = form.parentElement.querySelector('.newsletter-message');
      if (existing) existing.remove();

      function showMessage(text, type) {
        var msg = document.createElement('p');
        msg.className = 'newsletter-message newsletter-message--' + type;
        msg.textContent = text;
        form.insertAdjacentElement('afterend', msg);
      }

      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showMessage('Please enter a valid email address.', 'error');
        return;
      }

      var originalText = button.textContent;
      button.disabled = true;
      button.textContent = 'Subscribing…';

      fetch(PHRONESIS_SUBSCRIBE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      })
        .then(function (res) {
          return res.json().then(function (data) { return { ok: res.ok, data: data }; });
        })
        .then(function (result) {
          if (result.ok && result.data.success) {
            showMessage(result.data.message || 'Successfully subscribed!', 'success');
            form.reset();
          } else {
            showMessage(result.data.error || 'Subscription failed. Please try again.', 'error');
          }
        })
        .catch(function () {
          showMessage('Network error. Please try again.', 'error');
        })
        .finally(function () {
          button.disabled = false;
          button.textContent = originalText;
        });
    });
  });
});
