#!/usr/bin/env python3
"""이미 온 미래 — data.json → index.html 정적 빌드.

사용: python3 future/_build/build.py
- future/data.json 을 읽어 template.html 의 {{...}} 자리를 채운다.
- 목록을 HTML로 미리 그려 두므로 JS 없이도 읽히고 검색엔진에도 잡힌다.
- data.json 의 필드는 에어테이블 컬럼과 1:1 로 맞춰 두었다 (README.md 참고).
"""
import html
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import people  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SITE = "https://workzeroai.github.io/future/"

TYPES = [
    ("video", "롱폼 영상", "VIDEO"),
    ("x", "X 게시물", "X POST"),
    ("official", "공식 학습", "OFFICIAL"),
    ("essay", "에세이", "ESSAY"),
    ("data", "데이터·연구", "DATA"),
]
TYPE_LABEL = {k: v for k, v, _ in TYPES}
TYPE_BADGE = {k: b for k, _, b in TYPES}
LEARN = [
    ("intro", "STEP 1", "감 잡기", "AI가 무엇이고 무엇을 할 수 있는지, 한 번 제대로 이해하기."),
    ("work", "STEP 2", "일에 붙이기", "내 업무와 자동화에 바로 쓰는 공식 가이드와 실무 강의."),
    ("deep", "STEP 3", "원리와 최전선", "모델의 빈틈과 다음 변화를 먼저 읽는 단계."),
]
SPREAD = {1: "최전선에서만", 2: "얼리어답터까지", 3: "모두에게"}


def e(s):
    return html.escape(str(s or ""), quote=True)


def is_date(s):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", s or ""))


def fmt_date(s):
    return s.replace("-", ".") if is_date(s) else (s or "")


def validate(d):
    errs = []
    sig_ids = {s["id"] for s in d["signals"]}
    seen = set()
    for it in d["items"]:
        iid = it.get("id")
        if not iid:
            errs.append(f"id 없음: {it.get('title')}")
        if iid in seen:
            errs.append(f"id 중복: {iid}")
        seen.add(iid)
        for k in ("type", "title", "source", "url", "summary", "why"):
            if not it.get(k):
                errs.append(f"{iid}: {k} 비어 있음")
        if it.get("type") not in TYPE_LABEL:
            errs.append(f"{iid}: 알 수 없는 type {it.get('type')}")
        for s in it.get("signals", []):
            if s not in sig_ids:
                errs.append(f"{iid}: 없는 signal {s}")
        if it.get("learn") and it["learn"] not in {k for k, *_ in LEARN}:
            errs.append(f"{iid}: 알 수 없는 learn {it['learn']}")
        if not str(it.get("url", "")).startswith("https://"):
            errs.append(f"{iid}: url은 https:// 로 시작해야 함")
    for s in d["signals"]:
        if not s.get("short"):
            errs.append(f"signal {s['id']}: short 비어 있음")
        if s.get("spread") not in SPREAD:
            errs.append(f"signal {s['id']}: spread 는 1~3")
    if errs:
        sys.exit("data.json 확인 필요:\n  " + "\n  ".join(errs))


def sort_key(it):
    d = it.get("date", "")
    return (1, d) if is_date(d) else (0, "")


def spread_html(n):
    bars = "".join("<i class=\"on\"></i>" if i < n else "<i></i>" for i in range(3))
    return (f'<span class="spread" aria-label="퍼진 정도: {SPREAD[n]}">'
            f'<span class="bars" aria-hidden="true">{bars}</span>{SPREAD[n]}</span>')


def render_signals(d, counts):
    out = []
    for i, s in enumerate(d["signals"], 1):
        out.append(f'''
<article class="sig" id="sig-{e(s["id"])}">
  <span class="no">{i:02d}</span>
  <div class="metric">{e(s["metric"])}</div>
  <div class="mlabel">{e(s["metric_label"])}</div>
  <h3>{e(s["headline"])}</h3>
  <p>{e(s["now"])}</p>
  <p class="shift"><b>그래서 바뀌는 것</b>{e(s["shift"])}</p>
  <div class="sig-foot">
    {spread_html(s["spread"])}
    <button class="linkbtn" type="button" data-group="signal" data-val="{e(s["id"])}" data-jump="1">근거 자료 {counts.get(s["id"], 0)}개 보기 →</button>
  </div>
</article>''')
    return "".join(out)


def render_card(it, sig_name):
    t = it["type"]
    sigs = it.get("signals", [])
    lang = "한국어" if it.get("lang") == "ko" else "영어"
    search = " ".join([it["title"], it.get("title_orig", ""), it["source"], it["summary"], it["why"],
                       TYPE_LABEL[t], lang] + [sig_name[s] for s in sigs]).lower()
    if it.get("yt"):
        top = (f'<a class="thumb" href="{e(it["url"])}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">'
               f'<img src="https://i.ytimg.com/vi/{e(it["yt"])}/hqdefault.jpg" alt="" loading="lazy" decoding="async" width="480" height="270" onerror="this.remove()">'
               f'<span class="badge">{TYPE_BADGE[t]}</span></a>')
    else:
        top = (f'<div class="band" aria-hidden="true"><span class="bt">{TYPE_LABEL[t]}</span>'
               f'<span class="bs">{e(it["source"])}</span><span class="bo">{e(it.get("title_orig") or "")}</span></div>')
    orig = ""
    if it.get("title_orig") and it["title_orig"] != it["title"] and it.get("yt") and it.get("lang") != "ko":
        orig = f'<p class="orig" lang="{e(it.get("lang", "en"))}">{e(it["title_orig"])}</p>'
    tags = "".join(f'<button class="tag" type="button" data-group="signal" data-val="{e(s)}"># {e(sig_name[s])}</button>'
                   for s in sigs)
    links = f'<a href="{e(it["url"])}" target="_blank" rel="noopener">원본 보기 ↗</a>'
    if it.get("note"):
        links += f'<a class="sub" href="{e(it["note"])}" target="_blank" rel="noopener">한국어 정리 →</a>'
    return f'''
<article class="card" data-type="{t}" data-signals="{e(" ".join(sigs))}" data-q="{e(search)}">
  {top}
  <div class="body">
    <div class="meta"><span>{e(it["source"])}</span><span>{e(fmt_date(it.get("date")))}</span><span class="lang">{lang}</span></div>
    <h3><a href="{e(it["url"])}" target="_blank" rel="noopener">{e(it["title"])}</a></h3>
    {orig}
    <p class="sum">{e(it["summary"])}</p>
    <p class="why"><b>WHY · 왜 미래 신호인가</b>{e(it["why"])}</p>
    {f'<div class="tags">{tags}</div>' if tags else ""}
    <div class="links">{links}</div>
  </div>
</article>'''


def render_learn(d):
    out = []
    for key, sn, title, desc in LEARN:
        lis = []
        for it in [x for x in d["items"] if x.get("learn") == key]:
            ty = {"video": "영상", "official": "공식", "essay": "글", "data": "자료", "x": "X"}[it["type"]]
            sub = f'{it["source"]} · {"한국어" if it.get("lang") == "ko" else "영어"}'
            lis.append(f'<li><a href="{e(it["url"])}" target="_blank" rel="noopener">'
                       f'<span class="ty">{ty}</span><span class="lt">{e(it["title"])}</span>'
                       f'<span class="ls">{e(sub)} — {e(it["why"])}</span></a></li>')
        out.append(f'<div class="step"><span class="sn">{sn}</span><h3>{title}</h3><p>{desc}</p><ol>{"".join(lis)}</ol></div>')
    return "".join(out)


def render_radar(d):
    out = []
    for a in d["accounts"]:
        initials = "".join(w[0] for w in a["name"].split()[:2]).upper()
        out.append(f'''<a class="acct" href="https://x.com/{e(a["handle"])}" target="_blank" rel="noopener">
  <span class="av" aria-hidden="true">{e(initials)}</span>
  <span><span class="an">{e(a["name"])}</span> <span class="ah">@{e(a["handle"])}</span>
  <span class="ar" style="display:block">{e(a["role"])}</span>
  <p>{e(a["why"])}</p></span></a>''')
    return "".join(out)


def update_sitemap(urls, lastmod):
    """저장소 루트 sitemap.xml 에서 /future/ 줄을 지우고 다시 넣는다."""
    p = ROOT.parent / "sitemap.xml"
    lines = [ln for ln in p.read_text(encoding="utf-8").split("\n") if "/future/" not in ln]
    i = next(k for k, ln in enumerate(lines) if "<url>" in ln)
    new = [f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod></url>" for u in urls]
    p.write_text("\n".join(lines[:i] + new + lines[i:]), encoding="utf-8")


def main():
    d = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    validate(d)
    sig_name = {s["id"]: s["short"] for s in d["signals"]}

    items = sorted(d["items"], key=sort_key, reverse=True)
    counts = {}
    for it in items:
        for s in it.get("signals", []):
            counts[s] = counts.get(s, 0) + 1
    tcount = {}
    for it in items:
        tcount[it["type"]] = tcount.get(it["type"], 0) + 1

    type_chips = [f'<button class="chip" type="button" data-group="type" data-val="all" aria-pressed="true">전체<span class="n">{len(items)}</span></button>']
    type_chips += [f'<button class="chip" type="button" data-group="type" data-val="{k}" aria-pressed="false">{lab}<span class="n">{tcount[k]}</span></button>'
                   for k, lab, _ in TYPES if tcount.get(k)]
    sig_chips = ['<button class="chip" type="button" data-group="signal" data-val="all" aria-pressed="true">모든 흐름</button>']
    sig_chips += [f'<button class="chip" type="button" data-group="signal" data-val="{e(s["id"])}" aria-pressed="false">{e(sig_name[s["id"]])}<span class="n">{counts.get(s["id"], 0)}</span></button>'
                  for s in d["signals"]]

    people_cards, people_urls, (n_people, n_talks, n_arts), _ = people.build()
    stats = [
        (n_people, "명의 인물"),
        (n_talks, "편 강연·대담"),
        (n_arts, "편 글로 읽기"),
        (tcount.get("video", 0), "롱폼 영상"),
        (tcount.get("official", 0), "공식 학습자료"),
        (tcount.get("essay", 0) + tcount.get("data", 0), "에세이·연구"),
        (len(d["accounts"]), "X 계정"),
    ]
    if tcount.get("x"):
        stats.insert(1, (tcount["x"], "X 게시물"))
    stats_html = "".join(f"<li><b>{n}</b>{lab}</li>" for n, lab in stats)

    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "이미 온 미래",
        "url": SITE,
        "inLanguage": "ko",
        "dateModified": d["updated"],
        "description": "흩어진 AI 인사이트를 '지금 와 있는 미래 6가지'로 묶은 아카이브",
        "hasPart": [{"@type": "CreativeWork", "name": it["title"], "url": it["url"]} for it in items],
    }

    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    rep = {
        "UPDATED": e(d["updated"].replace("-", ".")),
        "STATS": stats_html,
        "PEOPLE": people_cards,
        "SIGNALS": render_signals(d, counts),
        "TYPE_CHIPS": "".join(type_chips),
        "SIGNAL_CHIPS": "".join(sig_chips),
        "ARCHIVE": "".join(render_card(it, sig_name) for it in items),
        "LEARN": render_learn(d),
        "RADAR": render_radar(d),
        "JSONLD": json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/"),
    }
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: rep[m.group(1)], tpl)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    update_sitemap([SITE] + people_urls, d["updated"])
    print(f"future/index.html 생성 — 자료 {len(items)}개, 신호 {len(d['signals'])}개, 계정 {len(d['accounts'])}개")


if __name__ == "__main__":
    main()
