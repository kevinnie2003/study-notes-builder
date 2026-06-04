# LaTeX / PDF toolchain troubleshooting

Real issues hit while building a dense booklet, with fixes. Consult when a build
fails or output looks wrong.

## PDF reading

- **`pdftoppm`/poppler not installed** (the built-in PDF→image path may fail).
  Don't fight it — use `scripts/extract_pdf.py` (PyMuPDF). It renders pages to PNG
  and extracts text without poppler.
- **Image-budget cap during extraction**: an agent reading dozens of page-images in
  one context can hit a cap and silently stop reading later pages. Mitigate by
  rendering+reading in batches (~10-20 pages) and at moderate DPI (~115-125), and
  by having agents explicitly flag any page they didn't visually read.

## Compilation: missing packages / format mismatch

- **`! LaTeX Error: File 'X.sty' not found`** (e.g. `multirow`, `pdfcol`,
  `tikzfill`): the install is missing packages. Install into the user tree without
  admin via user-mode tlmgr:
  ```
  tlmgr --usermode install <pkg> [<pkg> ...]
  ```
  (No `init-usermode` action needed on recent tlmgr; it auto-detects usermode.)
- **`! Undefined control sequence ... \NewStructureName` (or similar) when loading
  tcolorbox/other newer packages**: a precompiled LaTeX *format* older than the
  installed packages (e.g. format kernel `2024-11-01` but packages dated `2025-xx`,
  which call newer kernel macros). Rebuild the format from the newer kernel — no
  admin needed:
  ```
  fmtutil-user --byfmt pdflatex
  ```
  The user-format then takes precedence and defines the new macros.
- **tcolorbox pulls `tikzfill.image` via `[most]`**: the dense template avoids this
  by not using `[most]` and not relying on tcolorbox at all (it uses lightweight
  `\colorbox` tags + a plain `mcqbox` env). Prefer that over heavy box packages —
  fewer dependencies, and breakable boxes are fragile inside `multicol` anyway.

## Narrow two-column layout (the dense format)

- **Overfull \hbox (line runs into the gutter)**:
  - Long single inline-math chains can't line-break. Split into separate `$...$`
    atoms: write `$a{=}1$, $b{=}2$` not one long `$a{=}1,\ b{=}2,\ \dots$`.
  - Long monospace tokens (e.g. `\texttt{cudaDeviceSynchronize()}`) can't break —
    add discretionary breaks: `\texttt{cuda\-Device\-Synchronize()}`.
  - Wide bracketed math: break at a comma into two groups,
    `$[-(2^{n-1}{-}1),$ $2^{n-1}{-}1]$`.
  - As a general safety net, the template sets `\emergencystretch=2.5em` and a
    relaxed `\tolerance` — this absorbs most minor (<~15pt) overflows automatically.
  - Keep tables at `\scriptsize` inside `\tabularx{\linewidth}{...}`; favor 2-col
    tables; for genuinely wide tables, present as compact bullet lists instead.

## Common agent-introduced LaTeX errors (check after any parallel edit pass)

- **`\*` in math** (`! Missing { inserted`): agents sometimes write `N^\*` for an
  optimal-superscript. Fix: `N^*` or `N^{*}`. Global fix: `sed -i '' 's/\^\\\*/^*/g' chapters/*.tex`.
- **Unescaped `_`** in text/`\texttt`: must be `\_`.
- **Undefined environment/macro**: an agent used a macro the template doesn't
  define. Either add the content with existing macros, or (rarely) define the macro
  in the preamble.

## Workflow / file-management pitfalls

- **Writing chapters to the wrong path after moving the project**: if you `mv` the
  build folder, update ALL absolute paths in your tooling. A silent symptom is the
  compiled PDF not growing when you add chapters (the `\input` points elsewhere, or
  the Write tool re-created the old directory). Verify page count increases as you
  add chapters.
- **Compile signal**: after each change run `pdflatex` and check the PDF page count
  actually changed; grep the log for `^! ` (errors) and `Overfull \hbox (` (layout).
- **Never `git commit`/`push`** the notes — keep them as untracked working files
  (the `.gitignore` with `*` inside the notes folder keeps git status clean).
