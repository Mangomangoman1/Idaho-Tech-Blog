/* Vercel Web Analytics loader for The Idaho Stack.
   ANALYTICS_BASE is rewritten at build time by scripts/analytics_path.py to the
   project's own unique path (VERCEL_OBSERVABILITY_BASEPATH), so the script and
   pageview endpoint are served from idahostack.com on a path that common ad
   blocker lists don't match. No cookies; Vercel hashes visitors daily. */
(function () {
  var ANALYTICS_BASE = "/_vercel/insights";
  var DEFAULT_BASE = "/_vercel/insights";
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
  var s = document.createElement("script");
  s.defer = true;
  s.src = ANALYTICS_BASE + "/script.js";
  if (ANALYTICS_BASE !== DEFAULT_BASE) s.dataset.endpoint = ANALYTICS_BASE;
  document.head.appendChild(s);
})();
