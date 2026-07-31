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

  // Newsletter form (front-end only demo)
  document.querySelectorAll('.newsletter-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('button');
      var original = btn.textContent;
      btn.textContent = 'Thanks — you\'re subscribed!';
      setTimeout(function () { btn.textContent = original; form.reset(); }, 2500);
    });
  });
});
