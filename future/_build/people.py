"""인물 아카이브 — talks.json + talks/<id>.md → 인물 페이지·글 페이지.

build.py 가 import 해서 쓴다.
- future/people/<slug>/index.html : 인물 한 명의 영상 전체 목록 (글 있는 것 먼저)
- future/talks/<id>/index.html    : 영상 한 편을 글로 옮긴 페이지 (talks/<id>.md 가 있을 때만)
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://workzeroai.github.io/future/"
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230b0c0f'/%3E"
           "%3Ccircle cx='16' cy='16' r='4.5' fill='%23d4ff4f'/%3E%3Ccircle cx='16' cy='16' r='10' fill='none' stroke='%23d4ff4f' stroke-opacity='.45' stroke-width='2'/%3E%3C/svg%3E")


def e(s):
    return html.escape(str(s or ""), quote=True)


def fmt_dur(sec):
    m = round(sec / 60)
    return f"{m // 60}시간 {m % 60}분" if m >= 60 else f"{m}분"


def fmt_views(v):
    if v >= 100_000_000:
        return f"{v / 100_000_000:.1f}억".replace(".0억", "억")
    if v >= 1_000_000:
        return f"{v // 10_000:,}만"
    if v >= 10_000:
        return f"{v / 10_000:.1f}만".replace(".0만", "만")
    return f"{v:,}"


def fmt_date(s):
    return s.replace("-", ".")


def thumb(vid, q="hqdefault"):
    return f"https://i.ytimg.com/vi/{vid}/{q}.jpg"


# ---------- markdown (허용 문법만: 문단, ##, >, -, **) ----------
def inline(s):
    s = e(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def md_to_html(md):
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = [ln.rstrip() for ln in block.strip().split("\n") if ln.strip()]
        if not lines:
            continue
        if lines[0].startswith("## "):
            out.append(f"<h2>{inline(lines[0][3:].strip())}</h2>")
            lines = lines[1:]
            if not lines:
                continue
        if all(ln.startswith(">") for ln in lines):
            text = " ".join(ln.lstrip(">").strip() for ln in lines)
            m = re.match(r'^(.*?)\s+[—–-]{1,2}\s*([^"”—–]{1,30})$', text)
            cite = ""
            if m and ('"' in m.group(1) or "”" in m.group(1)):
                text, cite = m.group(1), m.group(2).strip()
            text = text.strip().strip('"“”').strip()
            out.append(f"<blockquote><p>“{inline(text)}”</p>{f'<cite>— {e(cite)}</cite>' if cite else ''}</blockquote>")
        elif all(ln.startswith("- ") for ln in lines):
            out.append("<ul>" + "".join(f"<li>{inline(ln[2:].strip())}</li>" for ln in lines) + "</ul>")
        else:
            out.append(f"<p>{inline(' '.join(ln.strip() for ln in lines))}</p>")
    return "\n".join(out)


def parse_article(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        raise SystemExit(f"{path}: front matter(---) 없음")
    meta = {}
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    for k in ("id", "headline", "dek"):
        if not meta.get(k):
            raise SystemExit(f"{path}: {k} 비어 있음")
    if meta["id"] != path.stem:
        raise SystemExit(f"{path}: id({meta['id']})와 파일 이름이 다름")
    body = m.group(2).strip()
    meta["keywords"] = [k.strip() for k in meta.get("keywords", "").split(",") if k.strip()]
    meta["html"] = md_to_html(body)
    meta["chars"] = len(re.sub(r"\s", "", body))
    meta["read_min"] = max(1, round(meta["chars"] / 500))
    return meta


def load():
    d = json.loads((ROOT / "talks.json").read_text(encoding="utf-8"))
    arts = {}
    for p in sorted((ROOT / "talks").glob("*.md")):
        a = parse_article(p)
        arts[a["id"]] = a
    ids = {t["id"] for t in d["talks"]}
    for k in arts:
        if k not in ids:
            raise SystemExit(f"talks/{k}.md 에 해당하는 영상이 talks.json 에 없음")
    pmap = {p["id"]: p for p in d["people"]}
    for t in d["talks"]:
        for pid in t["people"]:
            if pid not in pmap:
                raise SystemExit(f"{t['id']}: 없는 인물 {pid}")
    return d, arts, pmap


# ---------- 공통 껍데기 ----------
def shell(*, title, desc, canonical, og, depth, body, jsonld=None, og_type="website"):
    up = "../" * depth
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")}</script>' if jsonld else ""
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta name="theme-color" content="#0b0c0f">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="이미 온 미래">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(og)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{e(og)}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Noto+Serif+KR:wght@600;900&family=JetBrains+Mono:wght@500;700&display=swap">
<link rel="stylesheet" href="{up}assets/site.css">
{ld}
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{up}" aria-label="이미 온 미래 처음으로"><i class="mark" aria-hidden="true"></i><span class="bn">이미 온 미래</span></a>
    <nav class="nav" aria-label="섹션">
      <a href="{up}#people">인물</a>
      <a href="{up}#signals">흐름</a>
      <a href="{up}#archive">자료</a>
      <a href="{up}#learn">배우기</a>
    </nav>
  </div>
</header>
{body}
<footer>
  <div class="wrap">
    <div class="fine">
      <span class="q">미래는 이미 와 있다. 다만 널리 퍼지지 않았을 뿐.</span>
      <span><a href="{up}" style="color:inherit">이미 온 미래</a></span>
    </div>
  </div>
</footer>
</body>
</html>
'''


# ---------- 카드 ----------
def talk_card(t, arts, pmap, depth, me=None):
    up = "../" * depth
    a = arts.get(t["id"])
    others = [pmap[p]["name"] for p in t["people"] if p != me]
    with_ = f'<span class="with">함께: {e(", ".join(others))}</span>' if others else ""
    yt = f"https://www.youtube.com/watch?v={t['id']}"
    href = f"{up}talks/{t['id']}/" if a else yt
    tgt = "" if a else ' target="_blank" rel="noopener"'
    q = " ".join([t["title"], t["channel"], a["headline"] if a else "", a["dek"] if a else "",
                  " ".join(a["keywords"]) if a else ""] + others).lower()
    head = (f'<h3><a href="{href}"{tgt}>{e(a["headline"])}</a></h3><p class="dek">{e(a["dek"])}</p>'
            f'<p class="vt">원본: {e(t["title"])}</p>') if a else f'<h3><a href="{href}"{tgt}>{e(t["title"])}</a></h3>'
    links = (f'<a href="{href}">글 읽기 · {a["read_min"]}분 →</a><a class="sub" href="{yt}" target="_blank" rel="noopener">영상 ↗</a>'
             if a else f'<a href="{yt}" target="_blank" rel="noopener">영상 보기 ↗</a>')
    note = ""
    if not a and t.get("captions") == "none":
        note = '<span class="lang">자막 없음</span>'
    return f'''
<article class="tcard" data-art="{1 if a else 0}" data-date="{t["date"]}" data-views="{t["views"]}" data-q="{e(q)}">
  <a class="thumb" href="{href}"{tgt} tabindex="-1" aria-hidden="true"><img src="{thumb(t["id"])}" alt="" loading="lazy" decoding="async" width="480" height="270" onerror="this.remove()">{'<span class="has">글</span>' if a else ''}<span class="dur">{fmt_dur(t["seconds"])}</span></a>
  <div class="body">
    <div class="meta"><span>{e(t["channel"])}</span><span>{fmt_date(t["date"])}</span><span>조회 {fmt_views(t["views"])}</span>{note}</div>
    {head}
    {with_}
    <div class="links">{links}</div>
  </div>
</article>'''


def person_card(p, talks, arts):
    mine = [t for t in talks if p["id"] in t["people"]]
    n_art = sum(1 for t in mine if t["id"] in arts)
    hours = round(sum(t["seconds"] for t in mine) / 3600)
    picks = sorted(mine, key=lambda t: (t["id"] not in arts, -t["views"]))[:3]
    lis = "".join(f'<li><i class="{"" if t["id"] in arts else "v"}">{"글" if t["id"] in arts else "영상"}</i>'
                  f'{e(arts[t["id"]]["headline"] if t["id"] in arts else t["title"])}</li>' for t in picks)
    kw = "".join(f"<span>{e(k)}</span>" for k in p["keywords"])
    return f'''<a class="person" href="people/{p["slug"]}/">
  <div class="ph"><span class="pav" aria-hidden="true">{e(p["name"][0])}</span><span><span class="pn">{e(p["name"])}</span><br><span class="pr">{e(p["role"])}</span></span></div>
  <p class="pb">{e(p["bio"])}</p>
  <div class="pk">{kw}</div>
  <ul class="plist">{lis}</ul>
  <div class="pstat"><span><b>{len(mine)}</b>편 영상</span><span><b>{n_art}</b>편 글</span><span><b>{hours}</b>시간 분량</span></div>
  <span class="go">{e(p["name"])} 아카이브 전체 보기 →</span>
</a>'''


# ---------- 페이지 ----------
PERSON_JS = '''<script>
(function(){
  var list=document.getElementById('tlist'),cards=[].slice.call(list.children),q=document.getElementById('q'),
      count=document.getElementById('count'),empty=document.getElementById('empty'),st={f:'all',s:'art',q:''};
  function apply(){
    var w=st.q.toLowerCase().split(/\\s+/).filter(Boolean),n=0;
    cards.sort(function(a,b){
      if(st.s==='views')return b.dataset.views-a.dataset.views;
      if(st.s==='date')return a.dataset.date<b.dataset.date?1:-1;
      return (b.dataset.art-a.dataset.art)||(a.dataset.date<b.dataset.date?1:-1);
    }).forEach(function(c){
      var ok=(st.f==='all'||c.dataset.art==='1')&&w.every(function(x){return c.dataset.q.indexOf(x)>-1});
      c.hidden=!ok;if(ok)n++;list.appendChild(c);
    });
    count.textContent=n+'편';empty.classList.toggle('show',n===0);
    [].forEach.call(document.querySelectorAll('[data-k]'),function(b){b.setAttribute('aria-pressed',st[b.dataset.k]===b.dataset.v?'true':'false')});
  }
  document.addEventListener('click',function(ev){var b=ev.target.closest('[data-k]');if(!b)return;st[b.dataset.k]=b.dataset.v;apply()});
  q.addEventListener('input',function(){st.q=q.value.trim();apply()});
  apply();
})();
</script>'''


def person_page(p, d, arts, pmap):
    mine = [t for t in d["talks"] if p["id"] in t["people"]]
    mine.sort(key=lambda t: t["date"], reverse=True)
    n_art = sum(1 for t in mine if t["id"] in arts)
    hours = round(sum(t["seconds"] for t in mine) / 3600)
    chans = len({t["channel"] for t in mine})
    first = min(t["date"] for t in mine)[:4]
    cards = "".join(talk_card(t, arts, pmap, 2, me=p["id"]) for t in mine)
    kw = "".join(f"<span>{e(k)}</span>" for k in p["keywords"])
    body = f'''<main>
<div class="wrap">
  <p class="crumb"><a href="../../#people">인물 아카이브</a> / {e(p["name"])}</p>
  <section class="phero">
    <div class="ph"><span class="pav" aria-hidden="true">{e(p["name"][0])}</span><span><h1>{e(p["name"])}</h1><span class="pr">{e(p["role"])}</span></span></div>
    <p class="pb">{e(p["bio"])}</p>
    <div class="pk">{kw}</div>
    <ul class="stats"><li><b>{len(mine)}</b>편 영상</li><li><b>{n_art}</b>편 글로 읽기</li><li><b>{hours}</b>시간 분량</li><li><b>{chans}</b>개 채널 · {first}년부터</li></ul>
  </section>
  <section style="padding:40px 0 72px">
    <div class="filters">
      <div class="row" role="group" aria-label="보기">
        <button class="chip" type="button" data-k="f" data-v="all" aria-pressed="true">전체<span class="n">{len(mine)}</span></button>
        <button class="chip" type="button" data-k="f" data-v="art" aria-pressed="false">글로 읽기<span class="n">{n_art}</span></button>
        <span style="width:12px;flex:none"></span>
        <button class="chip" type="button" data-k="s" data-v="art" aria-pressed="true">글 먼저</button>
        <button class="chip" type="button" data-k="s" data-v="date" aria-pressed="false">최신순</button>
        <button class="chip" type="button" data-k="s" data-v="views" aria-pressed="false">많이 본 순</button>
      </div>
      <div class="searchrow">
        <label class="sr" for="q">{e(p["name"])} 영상 검색</label>
        <input id="q" class="search" type="search" placeholder="제목, 채널, 함께 나온 사람으로 찾기" autocomplete="off">
        <span class="count" id="count" aria-live="polite"></span>
      </div>
    </div>
    <div class="tlist" id="tlist">{cards}</div>
    <p class="empty" id="empty">조건에 맞는 영상이 없어요.</p>
    <p class="note">조회수는 {fmt_date(d["updated"])} 기준이에요. '글' 표시가 있는 영상은 자막을 바탕으로 한 편의 글로 다시 썼어요.</p>
  </section>
</div>
</main>
{PERSON_JS}'''
    url = f"{SITE}people/{p['slug']}/"
    best = max(mine, key=lambda t: t["views"])
    return shell(title=f"{p['name']} — 영상 {len(mine)}편 아카이브 · 이미 온 미래",
                 desc=f"{p['name']}({p['role']})이 여러 채널에 나와 한 이야기 {len(mine)}편을 한곳에. 긴 영상은 글로 읽을 수 있어요.",
                 canonical=url, og=thumb(best["id"], "maxresdefault"), depth=2, body=body,
                 jsonld={"@context": "https://schema.org", "@type": "ProfilePage", "url": url,
                         "mainEntity": {"@type": "Person", "name": p["name"], "description": p["role"]}})


VIDEO_JS = '''<script>
document.addEventListener('click',function(ev){var b=ev.target.closest('[data-yt]');if(!b)return;
var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+b.dataset.yt+'?autoplay=1&rel=0';
f.title=b.getAttribute('aria-label');f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';f.allowFullscreen=true;
b.parentNode.replaceChild(f,b);});
</script>'''


def talk_page(t, a, d, arts, pmap):
    names = [pmap[p]["name"] for p in t["people"]]
    first = pmap[t["people"][0]]
    more = [x for x in d["talks"] if x["id"] != t["id"] and x["id"] in arts and set(x["people"]) & set(t["people"])]
    more = sorted(more, key=lambda x: x["date"], reverse=True)[:5]
    if len(more) < 3:
        extra = [x for x in d["talks"] if x["id"] != t["id"] and x not in more and set(x["people"]) & set(t["people"])]
        more += sorted(extra, key=lambda x: -x["views"])[: 5 - len(more)]
    def li(x):
        xa = arts.get(x["id"])
        href = f"../{x['id']}/" if xa else f"https://www.youtube.com/watch?v={x['id']}"
        tgt = "" if xa else ' target="_blank" rel="noopener"'
        return (f'<li><a href="{href}"{tgt}><img src="{thumb(x["id"], "mqdefault")}" alt="" loading="lazy" width="320" height="180" onerror="this.remove()">'
                f'<span><span class="mt">{e(xa["headline"] if xa else x["title"])}</span><br>'
                f'<span class="ms">{"글 · " + str(xa["read_min"]) + "분" if xa else "영상 · " + fmt_dur(x["seconds"])} · {e(x["channel"])}</span></span></a></li>')
    people_links = " · ".join(f'<a href="../../people/{pmap[p]["slug"]}/" style="color:inherit">{e(pmap[p]["name"])}</a>' for p in t["people"])
    kw = "".join(f"<span>{e(k)}</span>" for k in a["keywords"])
    body = f'''<main>
<article class="art">
  <p class="crumb"><a href="../../#people">인물 아카이브</a> / <a href="../../people/{first["slug"]}/">{e(first["name"])}</a></p>
  <header class="art-head">
    <div class="art-kicker"><span>{people_links}</span><span>{e(t["channel"])}</span></div>
    <h1>{e(a["headline"])}</h1>
    <p class="art-dek">{e(a["dek"])}</p>
    <div class="art-meta"><span>읽는 데 {a["read_min"]}분</span><span>영상 {fmt_dur(t["seconds"])}</span><span>{fmt_date(t["date"])} 공개</span><span>조회 {fmt_views(t["views"])}</span></div>
  </header>
  <div class="video"><button type="button" data-yt="{t["id"]}" aria-label="원본 영상 재생: {e(t["title"])}"><img src="{thumb(t["id"])}" alt="" onerror="this.remove()"><span class="play" aria-hidden="true"></span></button></div>
  <div class="prose">
{a["html"]}
  </div>
  <div class="pk" style="margin-top:28px">{kw}</div>
  <p class="disclaim">이 글은 원본 영상 「{e(t["title"])}」({e(t["channel"])})의 자막을 바탕으로 내용을 다시 정리한 거예요. 인용문은 말한 내용을 살리고 군더더기만 다듬었어요. 정확한 표현과 맥락은 <a href="https://www.youtube.com/watch?v={t["id"]}" target="_blank" rel="noopener" style="color:inherit">원본 영상</a>에서 확인하세요. 영상의 권리는 원 채널에 있어요.</p>
  <section class="more" aria-labelledby="more-h">
    <h2 id="more-h">{e(" · ".join(names))}의 다른 이야기</h2>
    <ol>{"".join(li(x) for x in more)}</ol>
    <p style="margin-top:16px"><a class="btn" href="../../people/{first["slug"]}/">{e(first["name"])} 아카이브 전체 →</a></p>
  </section>
</article>
</main>
{VIDEO_JS}'''
    url = f"{SITE}talks/{t['id']}/"
    return shell(title=f"{a['headline']} — {', '.join(names)} · 이미 온 미래", desc=a["dek"], canonical=url,
                 og=thumb(t["id"], "maxresdefault"), depth=2, body=body, og_type="article",
                 jsonld={"@context": "https://schema.org", "@type": "Article", "headline": a["headline"],
                         "description": a["dek"], "inLanguage": "ko", "url": url, "dateModified": d["updated"],
                         "about": [{"@type": "Person", "name": n} for n in names],
                         "isBasedOn": {"@type": "VideoObject", "name": t["title"], "url": f"https://www.youtube.com/watch?v={t['id']}",
                                       "uploadDate": t["date"], "thumbnailUrl": thumb(t["id"])}})


def build():
    d, arts, pmap = load()
    for p in d["people"]:
        out = ROOT / "people" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(person_page(p, d, arts, pmap), encoding="utf-8")
    tmap = {t["id"]: t for t in d["talks"]}
    for vid, a in arts.items():
        out = ROOT / "talks" / vid / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(talk_page(tmap[vid], a, d, arts, pmap), encoding="utf-8")
    cards = "".join(person_card(p, d["talks"], arts) for p in d["people"])
    urls = [f"{SITE}people/{p['slug']}/" for p in d["people"]] + [f"{SITE}talks/{v}/" for v in arts]
    stats = (len(d["people"]), len(d["talks"]), len(arts))
    print(f"인물 {stats[0]}명 · 영상 {stats[1]}편 · 글 {stats[2]}편")
    return cards, urls, stats, d["updated"]
