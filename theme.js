/* theme.js — light / dark theme for bradleycantrell.com
 *
 * Load in <head> before any stylesheet paints (plain <script>, no defer) so
 * the right theme is set before first paint and there is no flash.
 *
 * - With no stored choice the site follows the visitor's system setting
 *   (prefers-color-scheme) and keeps following it if the setting changes.
 * - The nav toggle stores an explicit choice in localStorage ("theme").
 * - Sets <html data-theme="light|dark"> and fires a "themechange" event on
 *   window ({ detail: { theme } }) so canvas backgrounds can repaint.
 * - window.BCTheme.isLight() is the shared check for scripts.
 */
(function () {
  var KEY = 'theme';
  var root = document.documentElement;
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null;

  function stored() {
    try { var v = localStorage.getItem(KEY); return v === 'light' || v === 'dark' ? v : null; }
    catch (e) { return null; }
  }
  function system() { return mq && mq.matches ? 'light' : 'dark'; }

  function apply(theme) {
    var changed = root.getAttribute('data-theme') !== theme;
    root.setAttribute('data-theme', theme);
    root.style.colorScheme = theme;
    updateButtons(theme);
    if (changed) {
      try { window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: theme } })); }
      catch (e) { /* very old browsers: no event */ }
    }
  }

  window.BCTheme = {
    isLight: function () { return root.getAttribute('data-theme') === 'light'; },
    get: function () { return root.getAttribute('data-theme') || 'dark'; },
    set: function (theme) {
      try { localStorage.setItem(KEY, theme); } catch (e) {}
      apply(theme);
    },
    toggle: function () { this.set(this.isLight() ? 'dark' : 'light'); }
  };

  apply(stored() || system());

  if (mq) {
    var onSystem = function () { if (!stored()) apply(system()); };
    if (mq.addEventListener) mq.addEventListener('change', onSystem);
    else if (mq.addListener) mq.addListener(onSystem);
  }

  // Another tab changed the choice
  window.addEventListener('storage', function (e) {
    if (e.key === KEY) apply(stored() || system());
  });

  // ── Toggle button ────────────────────────────────────────────────────
  var SUN = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">' +
    '<circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.4"/>' +
    '<g stroke="currentColor" stroke-width="1.4" stroke-linecap="round">' +
    '<path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></g></svg>';
  var MOON = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">' +
    '<path d="M19.5 14.6A8 8 0 0 1 9.4 4.5a8 8 0 1 0 10.1 10.1z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>';

  function updateButtons(theme) {
    var btns = document.querySelectorAll('.theme-toggle');
    for (var i = 0; i < btns.length; i++) {
      var b = btns[i];
      var next = theme === 'light' ? 'dark' : 'light';
      // Show the mode you will switch TO
      b.innerHTML = theme === 'light' ? MOON : SUN;
      b.setAttribute('aria-label', 'Switch to ' + next + ' mode');
      b.setAttribute('title', 'Switch to ' + next + ' mode');
    }
  }

  function makeButton() {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'theme-toggle';
    b.addEventListener('click', function () { window.BCTheme.toggle(); });
    return b;
  }

  // Button styles live here so every page gets them, including the teaching
  // mini-sites that use their own stylesheets.
  var CSS =
    '.theme-toggle{display:inline-flex;align-items:center;justify-content:center;flex:0 0 auto;' +
    'width:2rem;height:2rem;margin-left:1.5rem;padding:0;border-radius:999px;cursor:pointer;' +
    'background:transparent;color:var(--text-dim,currentColor);' +
    'border:1px solid color-mix(in srgb,currentColor 30%,transparent);' +
    'transition:color .2s,border-color .2s,background-color .2s;}' +
    '.theme-toggle:hover{color:var(--accent,currentColor);border-color:currentColor;}' +
    '.theme-toggle:focus-visible{outline:2px solid var(--accent,currentColor);outline-offset:2px;}' +
    '.theme-toggle svg{display:block}' +
    'nav .theme-toggle{margin-left:auto;}' +
    'nav .nav-links + .theme-toggle,nav ul + .theme-toggle{margin-left:1.5rem;}' +
    // Teaching mini-sites: the brand's auto margin already pushes links right
    'nav.site-nav .theme-toggle{margin-left:0;width:1.7rem;height:1.7rem;}' +
    '.theme-toggle--floating{position:fixed;top:1rem;right:1rem;z-index:1000;' +
    'background:var(--bg,transparent);}' +
    '@media (max-width:768px){nav .theme-toggle,nav .nav-links + .theme-toggle,nav ul + .theme-toggle{margin-left:1rem;}}' +
    '@media print{.theme-toggle{display:none!important}}';

  function injectCSS() {
    if (document.getElementById('theme-toggle-css')) return;
    var s = document.createElement('style');
    s.id = 'theme-toggle-css';
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  function mount() {
    injectCSS();
    if (document.querySelector('.theme-toggle')) { updateButtons(window.BCTheme.get()); return; }
    // Put it in the first site nav; pages with no nav get a floating button.
    var nav = document.querySelector('nav');
    var b = makeButton();
    if (nav) {
      nav.appendChild(b);
    } else {
      b.classList.add('theme-toggle--floating');
      document.body.appendChild(b);
    }
    updateButtons(window.BCTheme.get());
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
