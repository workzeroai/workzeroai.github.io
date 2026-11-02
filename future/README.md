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
| `index.html` | 빌드 결과물. **직접 고치지 말 것** |

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
