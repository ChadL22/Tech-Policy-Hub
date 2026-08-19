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

  // Dropdown toggle -- on mobile (where the CSS collapses nav into a full
  // panel, see the 720px breakpoint in styles.css), tapping "Research" or
  // "Events" opens the submenu instead of navigating, since there's no
  // hover to reveal it any other way. On desktop the dropdown already
  // opens on hover/focus via CSS, so a click there follows the link
  // normally -- Research and Events are real pages, not just menu labels.
  document.querySelectorAll('.has-dropdown > .nav-link').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (window.innerWidth > 720) return;
      e.preventDefault();
      var parent = link.parentElement;
      var willOpen = !parent.classList.contains('open');
      document.querySelectorAll('.has-dropdown.open').forEach(function (li) {
        if (li !== parent) {
          li.classList.remove('open');
          var otherLink = li.querySelector('.nav-link');
          if (otherLink) otherLink.setAttribute('aria-expanded', 'false');
        }
      });
      parent.classList.toggle('open', willOpen);
      link.setAttribute('aria-expanded', String(willOpen));
    });
  });

  // Close any open dropdown when clicking outside the nav, or on Escape
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-dropdown')) {
      document.querySelectorAll('.has-dropdown.open').forEach(function (li) {
        li.classList.remove('open');
        var link = li.querySelector('.nav-link');
        if (link) link.setAttribute('aria-expanded', 'false');
      });
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.has-dropdown.open').forEach(function (li) {
        li.classList.remove('open');
        var link = li.querySelector('.nav-link');
        if (link) link.setAttribute('aria-expanded', 'false');
      });
    }
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

  // Signal ticker channel tabs (Tech Policy Hub / Phronesis / Tech Policy
  // Press) -- all channels are pre-rendered in the page, so switching is
  // just a show/hide, no re-fetch.
  document.querySelectorAll('.ticker-tabs').forEach(function (tabs) {
    var wrap = tabs.closest('.signal-ticker');
    if (!wrap) return;
    tabs.querySelectorAll('.ticker-tab').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var channel = btn.dataset.channel;
        tabs.querySelectorAll('.ticker-tab').forEach(function (b) {
          var isActive = b === btn;
          b.classList.toggle('active', isActive);
          b.setAttribute('aria-selected', String(isActive));
        });
        wrap.querySelectorAll('.ticker-track').forEach(function (track) {
          track.classList.toggle('active', track.dataset.channel === channel);
        });
      });
    });
  });

  // "Ideas We're Reading" carousel arrows
  document.querySelectorAll('.carousel-wrap').forEach(function (wrap) {
    var track = wrap.querySelector('.carousel-track');
    if (!track) return;
    wrap.querySelectorAll('.carousel-arrows button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var card = track.querySelector('.read-card');
        var step = card ? card.getBoundingClientRect().width + 24 : 300;
        track.scrollBy({ left: step * parseInt(btn.dataset.dir, 10), behavior: 'smooth' });
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
