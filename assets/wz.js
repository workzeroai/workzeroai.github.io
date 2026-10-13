/* ───────────────────────── 워크제로 공용 측정 (WZ) ─────────────────────────
   모든 페이지에 한 줄로 붙는다:  <script src="/assets/wz.js" defer></script>
   (publish.py 가 배포할 때 자동으로 넣는다. 손으로 넣지 않는다.)

   수집처
     GA4      — 이벤트·퍼널·리텐션.  page_view·session_start 는 GA4 가 자동으로 잡는다.
     Clarity  — 스크롤 히트맵·방문 녹화. 아래 이벤트 중 전환 관련만 태그로 같이 보낸다.

   이 스크립트가 보내는 이벤트 (이름 바꾸면 GA4 맞춤 측정기준·보고서가 깨진다)
     scroll_depth      percent(30/50/70/90)
     section_view      section, section_order          — 섹션별 도달, 어디서 멈추는지
     cta_click         cta_name, cta_section, link_url — 본문 주요 버튼
     navigation_click  nav_type(top_nav/floating/footer), link_text, link_url
     faq_expand        faq_question, faq_index
     form_submit       form_name, method, level        — "양식 복사하고 DM 열기"(실제 폼이 없어 이걸 문의 완료로 본다)
     form_copy         form_name                       — 양식만 복사(DM 은 안 엶)
     level_select      level, via(quiz/tab)            — 과외 레벨 진단·탭
     quiz_complete     step                            — 제작 문의 시작점 진단 (build.html 이 직접 보낸다)
     select_content    content_type, item_id, item_name — 자료실 목록에서 글 열기
     search            search_term                     — 자료실 검색
     page_exit         deepest_pct, last_section, engaged_sec
   공통 파라미터: page_type (tutoring / build / build_recipe / library / library_note /
                 library_guide / report / lesson / other) — GA4 에서는 content_group 으로도 들어간다.

   확인·제외
     ?wzdebug=1     콘솔에 [WZ] 로 찍히고 GA4 DebugView 에 뜬다.  콘솔에서 wzLog() 로 전체 확인.
     ?wzinternal=1  이 브라우저를 내부 트래픽으로 표시 — 이후 GA4·Clarity 로 아무것도 보내지 않는다.
     ?wzinternal=0  표시 해제.
   측정이 페이지를 깨뜨리면 안 되므로 전부 try 로 감싼다. */
(() => {
  const GA = "G-5RDNB1891B";         // GA4 측정 ID — 속성 "워크제로 사이트"(558788642), workzeroai@gmail.com
  const CLARITY = "yx4ygp1vdh";     // Microsoft Clarity Project ID

  const q = location.search;
  const DEBUG = /[?&]wzdebug=1/.test(q);
  try {
    if (/[?&]wzinternal=1/.test(q)) localStorage.setItem("wz_internal", "1");
    if (/[?&]wzinternal=0/.test(q)) localStorage.removeItem("wz_internal");
  } catch (e) {}
  let INTERNAL = false;
  try { INTERNAL = localStorage.getItem("wz_internal") === "1"; } catch (e) {}

  const p = location.pathname;
  const PAGE =
    /^\/tutoring\/lesson/.test(p) ? "lesson" :
    /^\/tutoring\//.test(p) ? "tutoring" :
    /^\/build\/[^/]+\//.test(p) ? "build_recipe" :
    /^\/build\//.test(p) ? "build" :
    /^\/library\/notes\//.test(p) ? "library_note" :
    /^\/library\/[^/]+\//.test(p) ? "library_guide" :
    /^\/library\//.test(p) ? "library" :
    /^\/reports\//.test(p) ? "report" : "other";

  const send = !INTERNAL;
  if (send && GA) {
    const t = document.createElement("script");
    t.async = true; t.src = "https://www.googletagmanager.com/gtag/js?id=" + GA;
    document.head.appendChild(t);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date());
    gtag("config", GA, Object.assign({content_group: PAGE}, DEBUG ? {debug_mode: true} : {}));
  }
  if (send && CLARITY) {
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", CLARITY);
    try { clarity("set", "page_type", PAGE); } catch (e) {}
  }

  const log = [];
  const TO_CLARITY = {cta_click: 1, form_submit: 1, form_copy: 1, faq_expand: 1, level_select: 1, quiz_complete: 1};
  const ev = (name, params, beacon) => {
    const prm = Object.assign({page_type: PAGE}, params || {});
    log.push(Object.assign({ev: name, t: Math.round(performance.now())}, prm));
    if (DEBUG) console.log("[WZ]" + (INTERNAL ? "[내부·미전송]" : ""), name, prm);
    if (!send) return;
    try { if (GA && window.gtag) gtag("event", name, beacon ? Object.assign({transport_type: "beacon"}, prm) : prm); } catch (e) {}
    try { if (CLARITY && TO_CLARITY[name] && window.clarity) clarity("event", name); } catch (e) {}
  };
  window.WZ = {ev: ev, page: PAGE};
  window.wzLog = () => log;

  const txt = (el, n) => (el && el.textContent || "").replace(/\s+/g, " ").trim().slice(0, n || 60);

  /* ── 섹션 도달 — 한 번씩만 ── */
  const secs = [...document.querySelectorAll("main section, body > section")];
  const secName = s => {
    if (s.id) return s.id;
    const e = s.querySelector(".eyebrow") || s.querySelector("h2");
    return e ? txt(e, 30).toLowerCase() : (s.classList.contains("hero") ? "hero" : "section-" + (secs.indexOf(s) + 1));
  };
  const seen = [];
  const lastSec = () => seen.length ? seen[seen.length - 1] : "(top)";
  try {
    if (secs.length && "IntersectionObserver" in window) {
      const io = new IntersectionObserver(es => es.forEach(e => {
        if (!e.isIntersecting) return;
        const n = secName(e.target);
        if (seen.indexOf(n) >= 0) return;
        seen.push(n);
        ev("section_view", {section: n, section_order: secs.indexOf(e.target) + 1});
      }), {threshold: .25});
      secs.forEach(s => io.observe(s));
    }
  } catch (e) {}
  const secOf = el => { const s = el.closest && el.closest("section"); return s ? secName(s) : "(none)"; };

  /* ── 스크롤 깊이 30/50/70/90 ── */
  const MARKS = [30, 50, 70, 90], hit = {};
  let deepest = 0;
  const onScroll = () => {
    const h = document.documentElement.scrollHeight - innerHeight;
    const pct = h <= 0 ? 100 : Math.round(scrollY / h * 100);
    if (pct > deepest) deepest = Math.min(100, pct);
    MARKS.forEach(m => { if (deepest >= m && !hit[m]) { hit[m] = 1; ev("scroll_depth", {percent: m}); } });
  };
  addEventListener("scroll", onScroll, {passive: true});

  /* ── 클릭 ── */
  const FORM = PAGE === "build" ? "build_inquiry" : "tutoring_inquiry";
  const level = () => {
    const f = document.getElementById("formText");
    const m = f && f.textContent.match(/희망 레벨[^:]*:\s*(.+)/);
    return m ? m[1].trim().slice(0, 20) : "(none)";
  };
  addEventListener("click", e => {
    try {
      const el = e.target.closest("a, button, summary");
      if (!el || el.tagName === "SUMMARY") return;
      const href = el.getAttribute("href") || "";

      if (el.id === "copyDm") return ev("form_submit", {form_name: FORM, method: "instagram_dm", level: level()});
      if (el.id === "copyBtn") return ev("form_copy", {form_name: FORM});

      const nav = el.closest("nav, footer, #sticky");
      if (nav) {
        const type = nav.id === "sticky" ? "floating" : nav.tagName === "FOOTER" ? "footer" : "top_nav";
        return ev("navigation_click", {nav_type: type, link_text: txt(el, 40), link_url: href});
      }

      if (el.matches(".opt[data-lv]")) return ev("level_select", {level: txt(el, 40), via: "quiz"});
      if (el.matches(".tab[data-tab]")) return ev("level_select", {level: txt(el, 20), via: "tab"});

      if (PAGE === "library" && el.tagName === "A" && href && href.charAt(0) !== "#" && !/^https?:/.test(href)) {
        const type = /notes\//.test(href) ? "note" : /reports\//.test(href) ? "report" : /tutoring|build/.test(href) ? "" : "guide";
        if (type) {
          // 자료 카드는 버튼만 링크라 제목이 바깥에 있다 → 카드 안의 제목을 찾는다
          const h = el.querySelector("h3, h4") || (el.closest(".card, li, article") || el).querySelector("h3, h4, b, strong");
          return ev("select_content", {content_type: type, item_id: href.replace(/^(\.\.\/|\.\/)+/, "").slice(0, 100), item_name: txt(h || el, 80)});
        }
      }

      const isCta = el.matches(".btn, .go, .pick, .plink, .pnode.out, .card.svc, [data-ev]")
        || /^#(contact|price|level|pair|diagnosis)$/.test(href)
        || /ig\.me|instagram\.com|kakao|kmong/.test(href)
        || (/(^|\/)(tutoring|build)\//.test(href) && PAGE !== "tutoring" && PAGE !== "build");
      if (isCta) {
        // 카드형 링크는 안의 제목만 이름으로 쓴다 (전체 글자를 붙이면 문구가 뭉개진다)
        const head = el.matches(".pnode, .card") && el.querySelector("b, h3, h4");
        ev("cta_click", {cta_name: el.dataset.ev || txt(head || el, 40), cta_section: secOf(el), link_url: href});
      }
    } catch (err) {}
  }, true);

  /* ── FAQ 펼침 — toggle 은 버블링이 안 돼서 capture 로 받는다 ── */
  addEventListener("toggle", e => {
    try {
      const d = e.target;
      if (d.tagName !== "DETAILS" || !d.open) return;
      const box = d.closest(".faq");
      if (!box) return;
      ev("faq_expand", {faq_question: txt(d.querySelector("summary"), 60), faq_index: [...box.querySelectorAll("details")].indexOf(d) + 1});
    } catch (err) {}
  }, true);

  /* ── 자료실 검색 — 입력이 멈추고 1.5초 뒤 한 번 ── */
  if (PAGE === "library") {
    let tm, lastQ = "";
    addEventListener("input", e => {
      const i = e.target;
      if (!i.matches || !i.matches("input[type=search], input#nq, input[type=text]")) return;
      clearTimeout(tm);
      tm = setTimeout(() => {
        const v = (i.value || "").trim().slice(0, 50);
        if (v.length >= 2 && v !== lastQ) { lastQ = v; ev("search", {search_term: v}); }
      }, 1500);
    }, true);
  }

  /* ── 나갈 때 한 번: 가장 깊이 내려간 곳·마지막 섹션·머문 시간 ── */
  let left = false;
  addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "hidden" || left) return;
    left = true;
    ev("page_exit", {deepest_pct: deepest, last_section: lastSec(), engaged_sec: Math.round(performance.now() / 1000)}, true);
  });

  setTimeout(onScroll, 800);   // 화면보다 짧은 페이지는 스크롤 없이도 깊이를 채운다
})();
