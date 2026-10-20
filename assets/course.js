/* 자료실 글 페이지의 코스 안내 — 제목 옆 "코스 2/5" 배지와 본문 끝 이전/다음·목차.
 * 글 페이지는 고정 HTML이라 코스를 바꿀 때마다 다시 만들지 않도록, 코스 정보는
 * /library/items.json 의 courses 를 읽어 여기서 붙인다. publish.py 가 notes 페이지에만 이 스크립트를 넣는다. */
(function () {
  var m = location.pathname.match(/\/library\/notes\/([^\/]+)\/?/);
  if (!m) return;
  var vid = decodeURIComponent(m[1]);
  var esc = function (s) {
    return String(s || '').replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  };
  var href = function (id) { return '/library/notes/' + encodeURIComponent(id) + '/'; };

  fetch('/library/items.json', { cache: 'no-cache' }).then(function (r) {
    return r.ok ? r.json() : null;
  }).then(function (d) {
    if (!d || !d.courses) return;
    var byId = {};
    (d.notes || []).forEach(function (n) { if (n.ready && n.url) byId[n.video_id] = n; });
    var course = null, posts = [];
    d.courses.some(function (c) {
      var p = (c.items || []).filter(function (id) { return byId[id]; });
      if (p.indexOf(vid) < 0) return false;
      course = c; posts = p; return true;
    });
    if (!course || posts.length < 2) return;
    var i = posts.indexOf(vid), n = posts.length;

    var css = document.createElement('style');
    css.textContent =
      '.cbadge{font-style:normal;background:var(--ink);color:#fff;padding:5px 9px;border-radius:7px;white-space:nowrap}' +
      '.cbadge:hover{background:var(--primary)}' +
      '.cnav{margin:44px 0 8px;border:1px solid var(--hair);border-radius:18px;padding:20px;background:var(--soft)}' +
      '.cnav-h{font-size:12px;font-weight:900;letter-spacing:.06em;color:var(--primary-deep)}' +
      '.cnav-h b{display:block;font-size:17px;letter-spacing:-.02em;color:var(--ink);margin-top:4px}' +
      '.cnav-pn{display:grid;grid-template-columns:1fr;gap:10px;margin:16px 0 4px}' +
      '@media (min-width:560px){.cnav-pn{grid-template-columns:1fr 1fr}}' +
      '.cnav-pn a{display:block;background:#fff;border:1px solid var(--hair);border-radius:14px;padding:13px 15px}' +
      '.cnav-pn a:hover{border-color:var(--primary)}' +
      '.cnav-pn small{display:block;font-size:12px;font-weight:800;color:var(--primary);margin-bottom:4px}' +
      '.cnav-pn span{font-size:14px;font-weight:700;line-height:1.45;color:var(--ink)}' +
      '.cnav-pn .nx{text-align:right}' +
      '.cnav details{margin-top:12px}' +
      '.cnav summary{cursor:pointer;font-size:13.5px;font-weight:800;color:var(--ink2)}' +
      '.cnav ol{margin:10px 0 0 20px;font-size:14px;color:var(--ink2)}' +
      '.cnav li{margin:6px 0}.cnav li a:hover{color:var(--primary)}' +
      '.cnav li.on{font-weight:800;color:var(--ink)}';
    document.head.appendChild(css);

    var meta = document.querySelector('.head .m');
    if (meta) {
      var b = document.createElement('a');
      b.className = 'cbadge'; b.href = '#course-nav';
      b.textContent = '코스 ' + (i + 1) + '/' + n;
      b.title = course.title;
      meta.appendChild(b);
    }

    var prev = i > 0 ? byId[posts[i - 1]] : null;
    var next = i < n - 1 ? byId[posts[i + 1]] : null;
    var pn =
      (prev ? '<a href="' + href(posts[i - 1]) + '"><small>← 이전 ' + i + '편</small><span>' + esc(prev.title) + '</span></a>' : '') +
      (next ? '<a class="nx" href="' + href(posts[i + 1]) + '"><small>다음 ' + (i + 2) + '편 →</small><span>' + esc(next.title) + '</span></a>'
            : '<a class="nx" href="/library/#notes"><small>코스 완주 →</small><span>다른 코스 둘러보기</span></a>');
    var toc = posts.map(function (id, k) {
      var t = esc(byId[id].title);
      return k === i ? '<li class="on">' + t + '</li>' : '<li><a href="' + href(id) + '">' + t + '</a></li>';
    }).join('');

    var nav = document.createElement('nav');
    nav.className = 'cnav'; nav.id = 'course-nav'; nav.setAttribute('aria-label', '코스 목차');
    nav.innerHTML = '<div class="cnav-h">코스 ' + (i + 1) + '/' + n + '<b>' + esc(course.title) + '</b></div>' +
      '<div class="cnav-pn">' + pn + '</div>' +
      '<details><summary>코스 전체 목차 (' + n + '편)</summary><ol>' + toc + '</ol></details>';
    var bd = document.querySelector('.bd');
    if (bd && bd.parentNode) bd.parentNode.insertBefore(nav, bd.nextSibling);
  }).catch(function () {});
})();
