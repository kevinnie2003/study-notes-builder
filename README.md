# study-notes-builder

A [Claude Code](https://docs.claude.com/en/docs/claude-code) **skill** that turns a
folder of course PDFs — lecture slides, scribe notes, textbook chapters, or papers —
into a single **dense, print-ready, exam-focused cheat-sheet booklet** (LaTeX → PDF),
with a *verified* "drop-nothing" completeness guarantee.

Students bring it to a closed-book, cheat-sheets-allowed exam, so the output is
**information-first** (packed two-column, grayscale, B/W-printer safe) — not a pretty
booklet.

## Why it's different

The hard part of making study notes from slides isn't writing LaTeX — it's
(1) capturing *everything* from decks that are mostly figures and whitespace, and
(2) *proving* nothing important was dropped. This skill solves both:

- **Exhaustive multi-agent extraction** — one agent per source renders *every* page
  to an image and reads it visually (not just the text layer, which silently drops
  diagrams and image-baked text), capturing every concept, equation, number, figure,
  and in-class MCQ.
- **Audit → patch → re-audit loop** — independent agents diff each finished chapter
  against its source, flag any missing examinable item (high/med/low), patch them
  back in, then re-audit to confirm coverage. You get coverage numbers, not just a
  promise.
- **Organizes from actual content, not the syllabus** — deck titles and topic hints
  are often wrong; chapters are built from what the extractions really contain.

## Requirements

- **Claude Code** (this is a skill).
- **Python 3** with PyMuPDF: `pip install pymupdf` (used by `scripts/extract_pdf.py`;
  no poppler needed).
- A **LaTeX** distribution with `pdflatex` (e.g. TeX Live / MacTeX) to build the PDF.

## Install

Clone into your personal Claude Code skills directory:

```bash
git clone https://github.com/kevinnie2003/study-notes-builder.git \
  ~/.claude/skills/study-notes-builder
```

The skill is then available in **any** project. (Alternatively, package it with the
skill-creator's `package_skill.py` and install the resulting `.skill` via `/plugin`.)

## Usage

In Claude Code, point it at a folder of course PDFs and ask for notes — the skill
triggers on requests like:

> "Make study notes for my final from the slides in `./lectures`."
> "Condense these course PDFs into a cheat sheet for the exam."
> "Build me a revision booklet from these decks."

It will confirm scope (which PDFs are in, what to exclude), extract everything,
build the booklet, show you a sample to approve, then run the completeness audit and
patch loop. Output is a `main.pdf` plus an `AUDIT_REPORT.md` showing coverage.

## What's inside

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill: workflow, defaults, and triggering description |
| `scripts/extract_pdf.py` | PyMuPDF text dump, page→PNG render, and a `scan` mode that flags figure-only pages needing visual reading |
| `assets/cheatsheet-template.tex` | The dense B/W two-column LaTeX template (run-in tags, MCQ boxes, part dividers, overflow safeguards) |
| `references/workflow.md` | The full phase-by-phase pipeline + multi-agent mechanics |
| `references/latex-troubleshooting.md` | Toolchain fixes (missing packages, format mismatch, narrow-column overflows, common errors) |

## License

[MIT](LICENSE) — free to use, modify, and share.
