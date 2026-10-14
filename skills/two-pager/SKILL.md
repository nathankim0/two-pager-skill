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

For density, troublesome wraps, or a new reference layout, read [references/layout-lessons.md](references/layout-lessons.md). For command details, use `two_pager.py --help` and subcommand `--help`.
