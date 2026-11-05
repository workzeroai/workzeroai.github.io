# 영상 → 글 작성 지침 (이미 온 미래 · 인물 아카이브)

Korean talk/interview videos are turned into readable long-form articles. You get a transcript, you write one Markdown file per video. Do NOT commit or push; only write files.

## 1. Get the transcript
Load the tool once: ToolSearch query `select:mcp__apfiy_mcp__get-dataset-items`.
Call `mcp__apfiy_mcp__get-dataset-items` with the given `datasetId`, `offset`, `limit: 1`, `fields: "video_id,title,channel_name,description,text"`.
- Check that the returned `video_id` equals the one you were given. If not, stop for that video and report it.
- If `text` is empty, retry with `fields: "video_id,non_timestamped"`.
- Write the article for a video BEFORE fetching the next transcript (keeps your context small).

Captions are auto-generated Korean: no punctuation, many mis-hearings. Infer intended words from context and fix proper nouns/terms (송길영, 시대예보, 핵개인, 호명사회, 경량문명, 수고인류, 김대식, KAIST, AGI, LLM, 에이전트, 엔비디아, 피지컬 AI, 바이브 코딩, product names…). **Never add facts, numbers, names or claims that are not in the transcript.** If a number, name or who-said-what is unclear, leave it out. Do not "correct" the speaker's opinions; you may silently drop a claim that is plainly garbled or arithmetically wrong.

## 2. Focus
The article is about what **the featured person** (given to you: 송길영 and/or 김대식) says. In panel shows with several guests (e.g. 손석희의 12시 with 송길영·이종범·김겨울, joint 대담), center the featured person's ideas; mention other speakers by name only when the title/description/transcript makes clear who they are, otherwise "진행자" / "함께 출연한 ○○" / "다른 출연자". In book-talk episodes (인생책, 책과사람, 사람산책), it is fine to cover the books he recommends and why.

## 3. Output file
`/home/user/workzeroai.github.io/future/talks/<video_id>.md`

```
---
id: <video_id>
headline: <Korean, 18–34 chars, states the core claim plainly; no clickbait, no wrapping quote marks>
dek: <one sentence, 40–80 chars>
keywords: <3–5 comma-separated Korean keywords>
---
```

Body:
- Korean magazine long-read in 평서문(~다). Quotes keep the spoken voice.
- Length: 3,500–6,000 chars incl. spaces for talks ≥ 30 min; 2,500–4,500 for shorter ones. A reader who never watches the video should get the full argument, examples and numbers, in the order the talk builds it.
- Structure: 1–2 opening paragraphs (who, in what setting/channel, the central question) → 4–6 sections each starting `## ` + a heading that states that section's point → last section `## 정리` with 3–5 one-sentence bullets (`- `).
- 3–6 direct quotes, each alone in its paragraph: `> "인용문" — 송길영` (use the actual speaker's name). Faithful to what was said; only filler removed.
- Allowed Markdown ONLY: paragraphs, `## `, `> `, `- `, `**bold**` (sparingly). No links, images, tables, H1, HTML, emoji.
- No meta talk ("이 영상에서는", "자막에 따르면", "이번 에피소드는").

## 4. Report back (short)
For each video: file path, headline, char count, and a one-line list of anything uncertain you left out or interpreted.
