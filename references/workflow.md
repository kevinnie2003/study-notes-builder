# Study-notes pipeline (detailed)

This is the full multi-agent pipeline for turning a folder of source PDFs into a
verified, dense exam cheat-sheet booklet. SKILL.md gives the overview; read this
when you're actually executing a phase. The engine is **fan-out parallelism**:
one agent per source for extraction, one agent per chapter for auditing/patching.
Scale agent counts to the number of sources/chapters.

## Phase 0 — Scope (confirm with the user, ~per run)

These vary by class, so confirm even though format defaults are baked in:
- **Which PDFs are in scope?** List the source files; get the user to confirm.
- **Exclusions.** Guest lectures, admin/logistics decks, weeks not on the exam.
  Topic hints and filenames lie (see Phase 3) — confirm by the deck's own title page.
- **Sources & priority.** Slides primary; scribe notes / textbook / papers as
  backup to fill detail. Ask which is authoritative if they conflict.
- **Length tolerance.** "Maximal detail, dense" is the default; confirm there's no
  hard page cap (there usually isn't — the user can print as many sheets as needed).
- **Output location.** A dedicated folder (e.g. `study-notes/`). Add a `.gitignore`
  with `*` inside it so it never pollutes the user's git status. NEVER commit/push.

## Phase 1 — Tooling

- Text + page images: `scripts/extract_pdf.py` (PyMuPDF; no poppler needed).
- LaTeX: confirm `pdflatex` exists. If the toolchain misbehaves, see
  `references/latex-troubleshooting.md` (format/version mismatch, missing packages).
- Pre-extract text for every in-scope deck: `extract_pdf.py text deck.pdf -o ...`.

## Phase 2 — Exhaustive extraction (one agent per source)

Fan out a workflow with one agent per deck. **The mandate is: drop nothing.**
Each agent must:
1. Read the deck's extracted text file.
2. **Render every page to PNG and VISUALLY read all of them** (text extraction
   alone is insufficient — diagrams, plots, and image-baked text are common).
   For big decks, render+read in batches (~10-20 images) to avoid image-budget caps.
3. Write an exhaustive per-deck markdown capturing, in slide order with page
   numbers `(pN)`: every definition, equation (as LaTeX), algorithm/pseudocode,
   number/benchmark/spec, comparison/table, figure (describe what it shows + the
   takeaway), worked example, and **every in-class MCQ verbatim with options and
   the answer** (MCQs are gold exam signal).
4. **Flag any page it could not visually read / OCR** (e.g. code screenshots) so a
   gap-fill pass can target it.

These per-deck `.md` files are the **ground truth** for everything downstream and
the audit trail proving nothing was dropped. Keep them.

## Phase 3 — Gap-fill (targeted)

Re-read the specific pages agents flagged (small page-range agents, low image
count each). Append "visually-recovered figures" sections to the affected `.md`
files. Don't skip this — flagged pages are often the figure-dense, examinable ones.

## Phase 4 — Organize chapters from ACTUAL content

**Critical lesson: do NOT organize from the syllabus, schedule, or topic hints —
they are frequently wrong.** In the source course several decks' real content
differed from their filename/hint (a "graph optimization" deck was actually memory
optimization; an "autodiff" deck was actually GPUs/CUDA; the "FlashAttention" deck
was actually inference/serving). Read the extractions, then group related concepts
into chapters and parts. Build a deck→chapter map (some decks split across
chapters; some chapters draw from several decks). Put the map in the appendix.

## Phase 5 — Build the booklet

Copy `assets/cheatsheet-template.tex` to `main.tex`, fill the masthead, and create
`chapters/chNN_topic.tex` files (each starts with `\section{...}\label{...}`).
Wire them into `main.tex` grouped by `\coursepart{...}`. Use the run-in tags
(`\Def \Key \Trap \Why \Eg \Cmp`, `\dt{}`) and `mcqbox` for MCQs. Compile with
`pdflatex` (twice for TOC); fix errors and overfull boxes (troubleshooting ref).
Keep content dense and telegraphic but complete.

## Phase 6 — Checkpoint

Build 1-2 chapters first, compile, and show the user a sample PDF to confirm
depth/density/style BEFORE writing all chapters. Cheap insurance on a big effort.

## Phase 7 — Write all chapters

Fan out or write sequentially, each chapter sourced from its deck `.md`(s) at full
detail. Compile incrementally. Reproduce MCQs verbatim with answers.

## Phase 8 — Completeness audit (one agent per chapter)

Fan out: each agent diffs its chapter `.tex` against its source `.md`(s) and lists
every examinable item present in the source but MISSING from the chapter, rated
high/med/low, with a suggested LaTeX snippet. Rules for the auditors: ignore pure
wording differences, non-examinable logistics, and content intentionally placed in
another chapter. Materialize the results into a human-readable `AUDIT_REPORT.md`
(summary table of coverage % + per-chapter items) so the user can see it.

## Phase 9 — Patch

Fan out: each agent folds its chapter's missing items (high+med+low, per the
user's "drop nothing" preference) back in, verifying each fact against the source,
using only existing template macros, keeping narrow-column-safe LaTeX. Recompile,
fix any errors the parallel edits introduced.

## Phase 10 — Re-audit (verify the fix)

Re-run Phase 8 against the patched chapters to confirm coverage rose and few/no
high/med items remain. If a chapter still has high/med items, do one more targeted
patch (Phase 9) on just those. This verify-then-fix loop is what turns "I think I
captured everything" into evidence.

## Multi-agent mechanics

- Use a Workflow with `parallel(...)` over sources/chapters; give each agent a
  schema so it returns structured results.
- Have extraction/patch agents WRITE to files and return short summaries (keeps the
  orchestrator's context lean); read the files when synthesizing.
- After any parallel edit pass, ALWAYS recompile and fix — agents occasionally
  introduce LaTeX errors (e.g. `\*` in math, unescaped `_`).
