/* Vercel Web Analytics loader for The Idaho Stack.
   SRC and DATA are filled in at deploy by scripts/analytics_path.py from the
   project's Vercel config, so the script and pageview endpoint are served from
   idahostack.com on a project-specific path that common ad blocker lists don't
   match. No cookies; Vercel resets its visitor hash daily. */
(function () {
  var SRC = "/_vercel/insights/script.js";
  var DATA = {};
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
  var s = document.createElement("script");
  s.defer = true;
  s.src = SRC;
  for (var k in DATA) s.dataset[k] = DATA[k];
  document.head.appendChild(s);
})();
