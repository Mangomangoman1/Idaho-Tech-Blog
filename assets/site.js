/* The Idaho Stack: small interface behaviours. Analytics live in stack.js. */
(function () {
  var doc = document, root = doc.documentElement;
  var bar = doc.querySelector('.topbar');

  // Menu sheet on small screens.
  if (bar) {
    var toggle = bar.querySelector('.nav-toggle');
    var setOpen = function (open) {
      bar.classList.toggle('nav-open', open);
      doc.body.classList.toggle('nav-locked', open);
      if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    if (toggle) toggle.addEventListener('click', function () { setOpen(!bar.classList.contains('nav-open')); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    window.matchMedia('(min-width: 901px)').addEventListener('change', function (e) { if (e.matches) setOpen(false); });
  }

  // Mark the section the reader is in.
  var here = location.pathname.replace(/index\.html$/, '');
  var section = here.indexOf('/articles/') === 0 ? '/news.html' : here;
  doc.querySelectorAll('.navlinks a, .nav-sheet nav a').forEach(function (a) {
    if (a.getAttribute('href') === section) a.setAttribute('aria-current', 'page');
  });

  // Hairline under the bar once the page scrolls; on the homepage, bring the name in after the masthead.
  if (bar && 'IntersectionObserver' in window) {
    var flag = doc.querySelector('.flag-title');
    var sentinel = doc.createElement('div');
    sentinel.style.cssText = 'position:absolute;top:0;height:1px;width:1px';
    doc.body.prepend(sentinel);
    new IntersectionObserver(function (e) { bar.classList.toggle('is-stuck', !e[0].isIntersecting); }).observe(sentinel);
    if (flag) new IntersectionObserver(function (e) { bar.classList.toggle('show-brand', !e[0].isIntersecting); },
      { rootMargin: '-60px 0px 0px 0px' }).observe(flag);
  } else if (bar) {
    bar.classList.add('show-brand');
  }

  // Today's date in Idaho for the masthead dateline.
  var today = doc.querySelector('[data-today]');
  if (today) {
    try {
      today.textContent = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Boise', weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(new Date());
    } catch (e) { /* keep the static text */ }
  }

  // Docket: count down to each date, drop the ones that have passed.
  var docket = doc.querySelector('.docket');
  if (docket) {
    var now = new Date(), shown = 0;
    var start = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    docket.querySelectorAll('li[data-date]').forEach(function (li) {
      var p = li.getAttribute('data-date').split('-');
      var days = Math.round((Date.UTC(+p[0], p[1] - 1, +p[2]) - start) / 864e5);
      var label = li.querySelector('.until');
      if (days < 0 || shown >= 4) { li.hidden = true; return; }
      shown++;
      if (label) {
        label.textContent = days === 0 ? 'Today' : days === 1 ? 'Tomorrow' : 'In ' + days + ' days';
        if (days <= 14) label.classList.add('soon');
      }
    });
    if (!shown) { var empty = docket.querySelector('.docket-empty'); if (empty) empty.hidden = false; }
  }

  // Reading progress on articles.
  var article = doc.querySelector('.article-body');
  if (article && doc.querySelector('.article-page')) {
    var bar2 = doc.createElement('div');
    bar2.className = 'read-progress';
    bar2.setAttribute('aria-hidden', 'true');
    doc.body.appendChild(bar2);
    var tick = false;
    var update = function () {
      var r = article.getBoundingClientRect();
      var total = r.height - window.innerHeight * 0.6;
      var done = Math.min(1, Math.max(0, -r.top / (total > 0 ? total : 1)));
      bar2.style.transform = 'scaleX(' + done + ')';
      tick = false;
    };
    window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }
  root.classList.add('js');
})();
