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

  // Signal ticker -- NYSE-tape style: streams continuously to the left,
  // stops the instant the pointer enters the lane (hover-to-pause), and
  // is click-and-drag scrubbable in either direction while paused.
  // ticker_track_html() in generate.py renders the item list twice back
  // to back; auto-scroll and drag both wrap at the halfway point of the
  // doubled track so the loop has no visible seam.
  document.querySelectorAll('.ticker-viewport').forEach(function (vp) {
    var track = vp.querySelector('.ticker-track-inner');
    if (!track) return;

    var half = 0;
    function measure() { half = track.scrollWidth / 2; }
    measure();
    window.addEventListener('resize', measure);

    var hovered = false, isDown = false, moved = false, startX, scrollLeft;
    var SPEED = 0.5; // px/frame -- a slow, readable tape, not a marquee blur

    function wrap(x) {
      if (half <= 0) return x;
      return ((x % half) + half) % half;
    }

    function frame() {
      if (!hovered && !isDown && half > 0) {
        vp.scrollLeft = wrap(vp.scrollLeft + SPEED);
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);

    function pause() { hovered = true; }
    function resume() {
      hovered = false;
      isDown = false;
      vp.classList.remove('dragging');
    }
    vp.addEventListener('mouseenter', pause);
    vp.addEventListener('mouseleave', resume);
    vp.addEventListener('touchstart', pause, { passive: true });
    vp.addEventListener('touchend', resume);
    // touchcancel fires (INSTEAD of touchend) whenever a touch that started
    // on the ticker turns into a page-level scroll -- easy to trigger by
    // accident since the ticker sits right under the header. Without this,
    // "hovered" gets stuck true forever after the first such touch and the
    // tape never resumes -- this was the actual "ticker doesn't run" bug.
    vp.addEventListener('touchcancel', resume);

    vp.addEventListener('mousedown', function (e) {
      isDown = true; moved = false;
      vp.classList.add('dragging');
      startX = e.pageX - vp.offsetLeft;
      scrollLeft = vp.scrollLeft;
    });
    vp.addEventListener('mouseup', function () {
      isDown = false;
      vp.classList.remove('dragging');
    });
    vp.addEventListener('mousemove', function (e) {
      if (!isDown) return;
      e.preventDefault();
      var x = e.pageX - vp.offsetLeft;
      var walk = x - startX;
      if (Math.abs(walk) > 5) moved = true;
      vp.scrollLeft = wrap(scrollLeft - walk);
    });
    vp.addEventListener('click', function (e) {
      if (moved) { e.preventDefault(); e.stopPropagation(); }
    }, true);
  });

  // Homepage "Research Spotlight" -- one .spotlight-slide visible at a
  // time (spotlight_html() in generate.py renders all of them, hidden via
  // CSS except .is-active). Auto-advances on a timer, pauses on hover so
  // it doesn't flip out from under someone reading, and the .spotlight-dot
  // buttons jump straight to a slide (and reset the timer so it doesn't
  // immediately auto-advance away from the one just picked).
  document.querySelectorAll('[data-spotlight]').forEach(function (widget) {
    var slides = Array.prototype.slice.call(widget.querySelectorAll('.spotlight-slide'));
    var dots = Array.prototype.slice.call(widget.querySelectorAll('.spotlight-dot'));
    if (slides.length < 2) return; // nothing to slide between

    var AUTO_MS = 5000;
    var FADE_MS = 320; // must match .spotlight-slide's transition-duration in styles.css
    var current = 0;
    var timer = null;
    var transitioning = false;

    // Crossfades rather than hard-cutting: fade the current slide out,
    // THEN (once that finishes) swap which slide is .is-active and fade
    // the new one in. Sequential rather than a true overlapping crossfade
    // so we don't need to give .spotlight-track a fixed height to hold two
    // different-length slides on screen at once.
    function show(i) {
      var next = (i % slides.length + slides.length) % slides.length;
      if (next === current || transitioning) return;
      transitioning = true;

      var oldSlide = slides[current];
      var newSlide = slides[next];

      oldSlide.classList.remove('is-visible');
      setTimeout(function () {
        oldSlide.classList.remove('is-active');
        newSlide.classList.add('is-active');
        void newSlide.offsetWidth; // force layout so the opacity transition below actually runs
        newSlide.classList.add('is-visible');
        current = next;
        dots.forEach(function (d, idx) { d.classList.toggle('is-active', idx === current); });
        setTimeout(function () { transitioning = false; }, FADE_MS);
      }, FADE_MS);
    }
    function stopAuto() { if (timer) clearInterval(timer); }
    function startAuto() {
      stopAuto();
      timer = setInterval(function () { show(current + 1); }, AUTO_MS);
    }

    dots.forEach(function (d, idx) {
      d.addEventListener('click', function () { show(idx); startAuto(); });
    });
    widget.addEventListener('mouseenter', stopAuto);
    widget.addEventListener('mouseleave', startAuto);

    startAuto();
  });

  // Homepage calendar -- pages between pre-rendered month panels (one
  // per month that actually has an event; see calendar_widget_html() in
  // generate.py) with prev/next, wrapping around at either end.
  document.querySelectorAll('.cal-widget').forEach(function (widget) {
    var panels = Array.prototype.slice.call(widget.querySelectorAll('.cal-month'));
    var title = widget.querySelector('.cal-title');
    if (!panels.length) return;
    var current = panels.findIndex(function (p) { return p.classList.contains('active'); });
    if (current < 0) current = 0;
    function show(i) {
      panels[current].classList.remove('active');
      current = (i % panels.length + panels.length) % panels.length;
      panels[current].classList.add('active');
      if (title) title.textContent = panels[current].dataset.label;
    }
    widget.querySelectorAll('.cal-nav').forEach(function (btn) {
      btn.addEventListener('click', function () {
        show(current + parseInt(btn.dataset.dir, 10));
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
