#!/usr/bin/env python3
"""
extract_pdf.py - PDF text + page-image extractor for the study-notes-builder skill.

Why this exists: lecture-slide / textbook PDFs must be read EXHAUSTIVELY. The text
layer alone silently drops diagrams, plots, and text baked into images. So this
tool does two things: (1) dump the text layer per page, and (2) render every page
to a PNG so an agent can VISUALLY read it (the authoritative source when text and
image disagree). It needs no system tools beyond PyMuPDF (`pip install pymupdf`) --
in particular it does NOT need poppler/pdftoppm.

Usage:
  # Dump text layer (per-page markers) to a file:
  python extract_pdf.py text  deck.pdf  -o out/deck.txt

  # Render pages to PNGs (all pages, or a range) for visual reading:
  python extract_pdf.py images deck.pdf -o out/img/deck --dpi 125
  python extract_pdf.py images deck.pdf -o out/img/deck --pages 21-40

  # Scan: per-page text length + image count -> flags likely figure-only pages
  #       (low text + has images) that MUST be visually read, not trusted to text.
  python extract_pdf.py scan   deck.pdf

Recommended flow per deck: run `text` and `scan`, then `images` for the whole deck
(or at least every page `scan` flags), then have an agent read the PNGs in order.
"""
import argparse, os, sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF not installed. Run:  pip install pymupdf")


def parse_pages(spec, n):
    """'21-40' or '5' or None -> list of 0-based page indices."""
    if not spec:
        return list(range(n))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a) - 1, int(b)))
        else:
            out.append(int(part) - 1)
    return [p for p in out if 0 <= p < n]


def cmd_text(args):
    doc = fitz.open(args.pdf)
    chunks = []
    for i, p in enumerate(doc):
        chunks.append(f"\n----- PAGE {i+1} -----\n{p.get_text().rstrip()}")
    data = "".join(chunks)
    if args.o:
        os.makedirs(os.path.dirname(args.o) or ".", exist_ok=True)
        open(args.o, "w").write(data)
        print(f"wrote {len(data)} chars, {doc.page_count} pages -> {args.o}")
    else:
        print(data)


def cmd_images(args):
    doc = fitz.open(args.pdf)
    os.makedirs(args.o, exist_ok=True)
    pages = parse_pages(args.pages, doc.page_count)
    for i in pages:
        doc[i].get_pixmap(dpi=args.dpi).save(f"{args.o}/p{i+1:03d}.png")
    print(f"rendered {len(pages)} pages (dpi={args.dpi}) -> {args.o}/")


def cmd_scan(args):
    doc = fitz.open(args.pdf)
    print(f"{os.path.basename(args.pdf)}: {doc.page_count} pages")
    print(f"{'pg':>4} {'chars':>6} {'imgs':>4}  flag")
    flagged = []
    for i, p in enumerate(doc):
        t = len(p.get_text().strip())
        n_img = len(p.get_images(full=True))
        # likely figure-only / under-captured by text: few characters but has images
        flag = "VISUAL-READ" if (t < 200 and n_img > 0) else ""
        if flag:
            flagged.append(i + 1)
        print(f"{i+1:>4} {t:>6} {n_img:>4}  {flag}")
    print(f"\nPages that MUST be visually read (low text + images): {flagged or 'none'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("text"); t.add_argument("pdf"); t.add_argument("-o"); t.set_defaults(fn=cmd_text)
    im = sub.add_parser("images"); im.add_argument("pdf"); im.add_argument("-o", required=True)
    im.add_argument("--dpi", type=int, default=125); im.add_argument("--pages", default=None); im.set_defaults(fn=cmd_images)
    s = sub.add_parser("scan"); s.add_argument("pdf"); s.set_defaults(fn=cmd_scan)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
