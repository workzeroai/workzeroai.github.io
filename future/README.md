# 이미 온 미래 (`/future/`)

> 미래는 이미 와 있다. 다만 널리 퍼지지 않았을 뿐. — William Gibson

워크제로 랜딩(튜터링·제작·자료실)과 **분리된 별도 사이트**. 흩어진 AI 인사이트(해외 롱폼 영상, X, 공식 학습자료, 에세이·연구)를
"지금 와 있는 미래 6가지" 흐름으로 묶어 보여 준다. 워크제로 페이지에서 링크하지 않고, 자체 브랜드·OG 이미지를 쓴다.

## 파일

| 파일 | 역할 |
|---|---|
| `data.json` | **유일한 원본 데이터.** 신호·자료·X 계정 |
| `_build/build.py` | `data.json` → `index.html` 정적 빌드 (목록을 HTML로 미리 그림: JS 없이도 읽히고 검색엔진에 잡힘) |
| `_build/template.html` | 페이지 뼈대·CSS·필터 JS. `{{...}}` 자리를 빌드가 채움 |
| `_build/og.html` → `og.png` | 공유 미리보기 이미지 (1200×630) |
| `talks.json` | **인물 아카이브 원본.** 인물(`people`)과 출연 영상(`talks`) 목록 |
| `talks/<영상ID>.md` | 영상 한 편을 글로 옮긴 원고. 있으면 글 페이지가 생긴다 |
| `_build/people.py` | 인물 페이지(`people/<slug>/`)·글 페이지(`talks/<id>/`) 생성 |
| `assets/site.css` | 모든 페이지 공통 스타일 |
| `index.html`, `people/`, `talks/*/` | 빌드 결과물. **직접 고치지 말 것** |

## 인물 아카이브 — 영상을 글로

한 사람이 여러 채널에 나와 한 강연·대담을 모으고, 긴 영상을 한 편씩 읽을 수 있는 글로 옮긴다.

1. **수집**: Apify `delicious_zebu/youtube-video-scraper-by-keyword`로 인물 이름 검색 (20분 이상, 국가 KR)
2. **출연 확인**: 제목·설명란에 이름이 있는지 확인. 다른 채널 영상을 짜깁기한 재업로드(예: '지식 쇼츠')는 빼고 원본을 쓴다
3. **자막**: Apify `johnvc/YoutubeTranscripts` (`languages: ["ko"]`) — 결과 dataset ID와 순서를 `talks.json`의 `src`에 적어 둔다
4. **글쓰기**: 자막을 읽고 `talks/<영상ID>.md` 작성 (형식은 아래)
5. `python3 future/_build/build.py`

글 원고 형식:

```
---
id: <영상ID>
headline: 핵심 주장을 담은 제목 (18~34자)
dek: 한 문장 부제 (40~80자)
keywords: 키워드1, 키워드2, 키워드3
---
도입 1~2문단 (누가, 어떤 자리에서, 무슨 질문)

## 소제목 (그 절의 요지)
본문…

> "말한 그대로의 인용" — 송길영

## 정리
- 한 문장 요점 3~5개
```

- 평서문(~다), 3,500~6,000자. 영상을 안 봐도 논리·사례·숫자를 따라갈 수 있게
- 자동 자막의 오인식은 맥락으로 바로잡되, 자막에 없는 사실·숫자는 넣지 않는다
- 허용 문법: 문단, `##`, `>`, `-`, `**굵게**` (링크·이미지·표·HTML 없음)
- 글 페이지에는 원본 영상(클릭해야 불러옴)과 "자막 기반 재구성, 권리는 원 채널" 안내가 자동으로 붙는다

에어테이블로 옮길 때: **People**(`id`·`slug`·`name`·`role`·`bio`·`keywords`) / **Talks**(`id`=영상ID·`people`→People 링크·`title`·`channel`·`date`·`seconds`·`views`·`captions`) / 글 원고는 Talks의 Long text 필드(`headline`·`dek`·`keywords`·`body`)로 두면 된다.

## 업데이트 순서

1. `data.json`에 항목 추가·수정
2. `python3 future/_build/build.py` — 필수 필드·신호 id·URL을 검사하고, 틀리면 멈춤
3. 커밋·푸시 (GitHub Pages 자동 배포)

## 데이터 구조 (에어테이블 테이블과 1:1)

에어테이블로 옮길 때 테이블 3개, 필드 이름을 그대로 쓰면 export → `data.json` 변환이 단순해진다.

**Signals** — 지금 와 있는 미래(큰 흐름)

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | Single line (Primary) | 영문 소문자. 필터 URL에 쓰임 (`#archive?signal=solo`) |
| `short` | Single line | 필터 칩 이름 (예: 작아지는 회사) |
| `headline` | Single line | 카드 제목 |
| `metric` / `metric_label` | Single line | 큰 숫자와 출처 포함 설명 |
| `now` | Long text | 지금 실제로 일어나는 일 |
| `shift` | Long text | 그래서 바뀌는 것 |
| `spread` | Number 1~3 | 퍼진 정도: 1 최전선에서만 · 2 얼리어답터까지 · 3 모두에게 |

**Items** — 아카이브 자료

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | Single line (Primary) | 영상은 YouTube ID, 나머지는 영문 슬러그 |
| `type` | Single select | `video` · `x` · `official` · `essay` · `data` |
| `title` / `title_orig` | Single line | 한국어 제목 / 원제 |
| `source` | Single line | 채널·저자·기관 |
| `date` | Single line | `YYYY-MM-DD` 또는 `상시`·`매년 발간` (날짜 아닌 값은 목록 뒤로) |
| `url` | URL | 원본 (https 필수) |
| `yt` | Single line | YouTube ID — 있으면 썸네일 표시 |
| `lang` | Single select | `ko` · `en` |
| `note` | Single line | 한국어 정리 페이지 경로 (선택, 예: `../library/notes/<id>/`) |
| `summary` | Long text | 2~3문장 요약 |
| `why` | Long text | **왜 미래 신호인가** 한 줄 (필수) |
| `signals` | Link → Signals | 여러 개 가능 |
| `learn` | Single select | `intro` · `work` · `deep` — 넣으면 '어디서부터 배울까'에도 나옴 |

**Accounts** — X 레이더: `handle`(@ 없이) · `name` · `role` · `why`

X 게시물은 `type: "x"`, `url`에 게시물 주소(`https://x.com/<handle>/status/<id>`), `source`에 계정 이름을 넣으면
아카이브에 'X 게시물' 필터가 자동으로 생긴다.

## 큐레이션 기준

- 원본 링크가 먼저. 요약은 원본을 볼지 판단하는 길잡이
- 학습자료는 모델을 만드는 회사·연구 기관의 공식 자료 우선. 수치에는 출처 표기
- '새롭다'가 아니라 **'이미 누군가에겐 일상이 됐다'는 증거**가 있는 것만
