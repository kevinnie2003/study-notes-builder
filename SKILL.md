---
name: study-notes-builder
description: >-
  Build ONE dense, print-ready, exam-focused cheat-sheet booklet (LaTeX to PDF)
  from a folder of course PDFs -- lecture slides, scribe notes, textbook chapters,
  or papers -- with a verified "drop-nothing" completeness guarantee via exhaustive
  multi-agent extraction, a completeness audit, a patch pass, and a re-audit. Use
  this whenever the user wants to make study notes, a study guide, a cheat sheet, a
  crib/revision sheet, exam-prep notes, or to condense/summarize lecture slides or
  course readings for a class or final -- even if they don't say "LaTeX" or "PDF",
  and even for a single large deck. Trigger on things like "make study notes for my
  final", "summarize these lecture slides", "build me a cheat sheet for the exam",
  "condense these PDFs into a revision booklet", "turn my course slides into notes".
  Do NOT use for one-off "summarize this one short doc" requests that don't need a
  printable booklet, or for general writing/research unrelated to exam prep.
---

# Study Notes Builder

Turn a set of course PDFs into a single dense, B/W, print-ready exam cheat-sheet
booklet — **without dropping examinable content**. The output is information-first
(packed two-column LaTeX), not a pretty booklet: students bring it to a closed-book,
cheat-sheets-allowed exam, so density and completeness beat aesthetics.

The hard part isn't writing LaTeX — it's (a) capturing *everything* from slides that
are mostly figures/whitespace, and (b) *proving* nothing was dropped. This skill
solves both with a fan-out extraction + an audit→patch→re-audit verification loop.

## Baked-in defaults (don't re-litigate these)

- **Format:** dense **two-column, 9pt, grayscale-only** LaTeX → PDF (B/W-printer
  safe). Use `assets/cheatsheet-template.tex`. No color, minimal decoration.
- **Density:** maximal content, telegraphic phrasing, no wasted whitespace; no hard
  page cap (the user prints as many sheets as needed).
- **MCQs:** reproduce every in-class multiple-choice / quiz question **verbatim with
  options and the answer** — high-value exam signal. Use the `mcqbox` environment.
- **Exclusions:** drop guest lectures and pure logistics/admin slides.
- **Git:** treat the booklet as a personal artifact — **never commit or push**; add a
  `.gitignore` containing `*` inside the output folder to keep git status clean.

Still confirm the **per-run** specifics (which PDFs are in scope, which to exclude,
which source is authoritative) — these change every class.

## Workflow

Read `references/workflow.md` for the detailed, phase-by-phase playbook. In short:

1. **Scope** — confirm the in-scope PDFs, exclusions, and authoritative source.
2. **Extract (fan-out, one agent per source)** — render *every* page to an image and
   read it visually + read the text layer; dump an exhaustive per-source markdown
   (every concept, equation, number, figure, and MCQ). Text alone silently drops
   diagrams — always read the page images. Use `scripts/extract_pdf.py`.
3. **Gap-fill** — re-read any page an agent couldn't OCR/visually read.
4. **Organize from ACTUAL content** — build chapters from what the extractions say,
   **not** from the syllabus/filenames/topic hints (they are often wrong). Make a
   deck→chapter map for the appendix.
5. **Build** — copy the template, write `chapters/chNN_topic.tex`, wire them under
   `\coursepart{...}`, compile with `pdflatex` (twice), fix errors/overflows.
6. **Checkpoint** — show the user a 1-2 chapter sample PDF before writing all of it.
7. **Write all chapters** at full detail.
8. **Audit (fan-out, one agent per chapter)** — diff each chapter vs its source;
   flag missing examinable items high/med/low; write a readable `AUDIT_REPORT.md`.
9. **Patch (fan-out)** — fold every flagged item back in; recompile and fix.
10. **Re-audit** — rerun the audit to confirm coverage rose; targeted re-patch any
    chapter still missing high/med items.

Steps 2, 8, 9 are parallel **Workflow** fan-outs (one agent per source/chapter) —
this is the engine. Scale agent count to the number of sources/chapters.

## Non-negotiables (the lessons that make output good)

- **Drop nothing, and verify it.** The audit→patch→re-audit loop is the whole point;
  don't declare done on assertion — show coverage numbers from the re-audit.
- **Read the page images, not just the text layer.** Slides hide content in figures.
- **Trust extractions over topic hints.** Decks frequently cover something other than
  their title/filename suggests; organize chapters from the extracted reality.
- **Checkpoint a sample early** so the user can correct depth/style cheaply.
- **Recompile after every parallel edit pass** — agents sometimes introduce LaTeX
  errors (`\*` in math, unescaped `_`). See `references/latex-troubleshooting.md`.
- **Keep the per-source extraction `.md` files** — they're the ground truth and the
  audit trail proving completeness.

## Bundled resources

- `scripts/extract_pdf.py` — PyMuPDF text dump, page→PNG render, and a `scan` mode
  that flags low-text/figure-only pages that must be visually read. No poppler needed.
- `assets/cheatsheet-template.tex` — the dense B/W two-column LaTeX preamble with the
  run-in tags (`\Def \Key \Trap \Why \Eg \Cmp`, `\dt{}`), the `mcqbox` environment,
  and `\coursepart` dividers. Start every booklet from this.
- `references/workflow.md` — the full phase-by-phase pipeline + multi-agent mechanics.
- `references/latex-troubleshooting.md` — toolchain fixes (missing packages via
  `tlmgr --usermode`, format/version mismatch via `fmtutil-user`, narrow-column
  overflow fixes, common agent-introduced errors, file-path pitfalls).
