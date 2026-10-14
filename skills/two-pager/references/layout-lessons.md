# Faster two-page authoring

These are lessons from real layout revisions, not requirements to copy one company's document.

| Observed problem | Reusable correction |
| --- | --- |
| A supporting percentage dominated the proposal | Put the percentage in body copy. Emphasize the recommendation or decision, not whichever number is available. |
| A generic slide renderer split Korean syllables and ignored authored newlines | Use native HTML text with `word-break: keep-all`. Use `<br>` at meaningful phrase boundaries. Don't patch a Japanese wrapping engine for each brief. |
| Bold Korean text touched nearby lines | Use line height around 1.3–1.45 and explicit row heights. Leave clearance under two-line headings. |
| Linux CJK font leading triggered false overlap reports | Compare glyph ink bounds instead of the entire font box; keep heading and highlight line heights explicit. Inspect both page previews after changing fonts. |
| Three-line black stage labels expanded every row and pushed the last stage into the footer | Use a short two-line label such as `02 / 퀘스트`; put the full name in adjacent copy. |
| Content barely fit, then an image pushed it over | Budget image width before writing the neighboring copy. A cropped UI fragment communicates more at the same width than a full collage. |
| A generated UI showed rewards incompatible with the written proposal | Use another crop or omit the conflicting area. Label it AI-generated; don't silently treat illustration details as requirements. |
| Every export recreated a virtualenv | Use the cached helper. First-run setup and subsequent rendering are different costs. |
| PDF export, screenshots, page checks, and overlap scans were separate commands | Run `render` once; it writes all QA evidence before promoting final artifacts. |
| A layout failure overwrote a working export | Stage output, inspect validation, then replace final files only after checks pass. |

## Default geometry

The starter is a 1760 × 990 landscape canvas. It uses a wide header, two-line summary, body sections, and a source footer. Page 1 uses three columns; page 2 uses two. The second page includes optional space for a narrow UI image.

At this canvas, use roughly 40–44px page titles, 26–29px executive summaries, 23–25px section titles, and 20–22px body copy. Sources may be smaller. The important ratio is title / body / footnote; a single absolute font size isn't portable across canvas sizes.

The starter's grid and print size must stay in sync. When matching a different reference, change `.page` width/height, `@page`, and column widths together. The renderer accepts other canvas sizes and checks that the PDF matches them.

## Working budget

- One two-line recommendation plus at most two summary bullets per page.
- About 4–5 rows in the main strategy or roadmap section.
- Two short lines per row; cut duplicated implications before shrinking text.
- Prefer 3–6 concise benchmark examples with citations over a long explanation of your own redesign.
- Don't add a separate agenda, cover, glossary, or technical appendix by default.

These are starting points. Preserve the user's required evidence and structure when it warrants a different allocation.

## Image handling

The `crop` box is `(x, y, width, height)` measured in the original image, before resizing. The helper rejects out-of-bounds or zero-size crops. PNG preserves UI text and transparency. Rendering embeds local images; the original stays where it was.

Use `alt` text and a caption such as `AI 생성 UI 시안`. Do not publish user-supplied screenshots, internal metrics, or company logos as examples for the skill itself without authorization. An image heading, reward amount, or button label can be material evidence and deserves the same accuracy check as body copy.

## Repair order

Read `.qa/<stem>/report.json`, inspect the affected page, and fix the actual cause:

1. Remove repeated or unnecessary copy.
2. Shorten stage labels and author sensible line breaks.
3. Adjust grid allocation or spacing to match the reference.
4. Reduce image extent or use a tighter crop.
5. Change font size only when the current size is unsuitable for the reference.

`data-qa-ignore` is available for an intentionally overlapping caption or decorative label. Use it on the smallest relevant element and inspect the result; never use it to hide clipped body copy.

The geometry checker checks text, images, column boundaries, and content bands. It does not establish source truth, infer missing fonts, evaluate contrast, or prove behavior in PowerPoint. PDF is the export format; editable PPTX is outside this helper's scope.
