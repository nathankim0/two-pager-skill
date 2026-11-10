---
name: two-pager
description: Create or revise a concise two-page executive proposal or decision brief, especially Korean 2pager/투페이저 requests with a slide screenshot reference. Produces HTML and PDF with reusable layout, image crops, and overflow checks. Use for two-page briefs, not long slide decks or general documents.
license: MIT
---

# Two Pager

Turn source notes into **exactly two pages** supporting one decision. Default to the user's language and preserve their reference layout, facts, caveats, and requested emphasis. This skill works unchanged in Codex and Claude Code.

## Fast path

Resolve `scripts/` and `assets/` relative to **this skill directory**, not the user's working directory. Do not hardcode an author's home path or require another skill.

1. Read the source and any reference images. Identify the reader, decision, evidence, proposal, expected effect, and next action. Ask only for missing information that would materially change the brief; otherwise proceed.
2. Scaffold once, then edit the resulting HTML. The example contains fictional library-service data: replace it with the user's content rather than presenting example values as facts.

   ```bash
   python3 /path/to/two-pager/scripts/two_pager.py scaffold ./work/brief --title "서비스 고도화 제안" --brand "회사명"
   ```

3. Compress before typesetting. A useful default is page 1: current situation / proposal / benchmark evidence, and page 2: economics / validation / roadmap. Follow the user's reference or requested order when it differs. No cover or third page.
4. Keep the supplied CSS initially. Korean uses `word-break: keep-all`, intentional `<br>` breaks, and generous line height. Choose emphasis by decision importance: a supporting percentage belongs in normal copy, not a giant number card. Use flat sections and thin rules; do not rebuild the design as a dashboard.
5. If a relevant image is supplied, use a focused crop instead of generating a replacement. The crop utility validates bounds and keeps the original file. Label AI-generated UI as a concept and avoid slices whose rewards, prices, or flows contradict the proposal.

   ```bash
   python3 /path/to/two-pager/scripts/two_pager.py crop "ui.png" --box 344 112 312 600 --output ./work/brief/quest.png
   ```

   Use a local quoted `<img src="quest.png" alt="AI 생성 퀘스트 UI 시안">` in the HTML. `render` embeds local images into the final HTML automatically. Crop coordinates are an example, not a preset for new images.
6. Render once. The helper caches dependencies, reuses installed Chrome when available, checks geometry and PDF page count, and produces both page previews in one browser run.

   ```bash
   python3 /path/to/two-pager/scripts/two_pager.py render ./work/brief/two-pager.html --output-dir ./output/brief
   ```

7. Open both `.qa/two-pager/page-*.png` previews at full size. Checks catch layout mistakes, not factual or design quality. Fix the affected HTML, rerun, and stop when the two pages read clearly and no unresolved issue remains. Prefer cutting copy or fixing spacing over shrinking fonts.
8. Deliver the final HTML and PDF, with a short note only for limitations affecting use. Keep QA reports and build dependencies out of the handoff.

The first render may download Python packages and a browser. Later runs reuse the cache. A failed layout check writes previews and `report.json` but preserves any existing final PDF and HTML. Do not treat failed output as finished.

## Facts and scope

- Keep units, time periods, denominators, and conditional economics explicit. Recalculate totals from supplied values; do not invent growth rates or target dates.
- Distinguish competitor feature evidence from proof of revenue or retention lift. Put compact source links next to the claim or in the footer. Research only claims that need verification; reuse already verified sources in the current task.
- Preserve constraints that could change the decision. Compress a supplied policy caveat instead of deleting it to make room; don't add hypothetical warnings unrelated to the proposal.
- Never silently imply that generated UI is implemented or verified. Don't embed contradictory image details merely because the image looks appealing.
- A two-page brief does not imply permission to publish source material or change a product. Upload, push, or publish only within the user's authorization.
- When changes shipped together, label them together (`A·B 개선 +12%`) unless event-level data separates them. Treat the user's knowledge of shared ad slots, fallbacks, or rollout as evidence and recheck the code or data instead of defending the first attribution.
- Count what the decision metric counts. Requests, loads, or clicks are not impressions or revenue; don't present a request spike as a result.

## Copy rules

Executives scan; they don't read paragraphs. These rules came from repeated review rounds.

- **Evidence is bullets in one shape: `항목: 이전 → 이후`.** Every bullet starts with a short label (`방문:`, `매출:`, `전환율:`) followed by the value. Don't write sentences such as `1위는 …, 2위는 …. 단가 상승은 …` in a note box; use `1위: …` / `2위: …` / `단가: …`.
- **Every change states its baseline.** Write `하루 1.2만 회 → 3.4만 회`, not `하루 3.4만 회`. If the baseline is zero because the item is new, choose a comparable baseline the reader cares about, such as the whole app or the previous period.
- **No vague labels or reader-facing internal names.** Avoid labels such as `늘어난 곳:` and internal identifiers such as slot or event codes. Use concrete nouns (`추가된 위치: …`).
- **No dangling fragments.** A bullet such as `신규 기능 3.2 시작` attached to an unrelated metric reads as an afterthought. Either give it its own labeled metric or delete it. Delete a number that only covers part of the claim.
- **Don't repeat the bullets in a page summary.** If the summary restates the evidence below, delete the summary and give the space to the content. Keep a summary only when it states the conclusion the bullets don't.
- **No default "next steps", hedges, or apologies.** Don't add `다음 확인`, `원인을 몰라 …`, `…에 확인하겠습니다`, or similar unless the user asks. A brief that a manager presents must not contain the author's personal perspective, such as `입사 전`.
- **Footnotes follow the content.** When a metric or data source is removed, remove its mention from the source line. State the comparison period for each metric group when they differ.

For density, troublesome wraps, or a new reference layout, read [references/layout-lessons.md](references/layout-lessons.md). For command details, use `two_pager.py --help` and subcommand `--help`.
