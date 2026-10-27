"""Open one AAHub source region as exact TXT rows + a native-scale PNG crop (Lane B).

Inspection aid for hand-authoring role_lookup entries (trueff-shallot AGENTS.md,
"How to inspect", 2026-10-27): it prints the exact rows of ONE selected region with
every glyph's codepoint and pen offset, and renders the same region in Saitamaar
16 px / 17 px rows at native scale. It never sweeps a page or a list.

Sources (SRC):
  txt:<path>                     a resNN.txt / entry-NN.txt file
  mlt:<path.json.gz>#<index>     AAHub MLT record, zero-based aa[index] (html-unescaped)
  lib:<library-id>#<index>       explorer component library page, zero-based aa[index]

Commands:
  show SRC --rows A-B [--x X0-X1] [--png crop.png] [--zoom 4 --view view.png]
  rect SRC --rect X,Y,W,H [--pitch 18 --pad 8]   annotation rect -> native rows / px range
Row numbers are 1-based; --x is a pen-x range in px from line start ([X0, X1)). A row's
slice is every glyph (spaces included) whose pen falls in [X0, X1).
"""
from __future__ import annotations

import argparse
import gzip
import html
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aahub_native import PAD, PITCH, Native, read_rows  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
LIBDIR = REPO / "assets/glyphs/contextual/component-libraries-20261026"


def load_source(src: str) -> list[str]:
    kind, _, rest = src.partition(":")
    if kind == "txt":
        return read_rows(Path(rest))
    if kind in ("mlt", "lib"):
        path, _, idx = rest.partition("#")
        if kind == "lib":
            path = str(LIBDIR / f"{path}.original.json.gz")
        d = json.load(gzip.open(path))
        v = html.unescape(d["aa"][int(idx)]["value"])
        return v.rstrip("\n").split("\n")
    raise SystemExit(f"unknown source kind: {src}")


def slice_rows(nat: Native, rows: list[str], a: int, b: int, x0: int, x1: int):
    """Exact slices for 1-based rows a..b; returns [(row_no, text, pen_x_of_slice_start, glyphs)]."""
    out = []
    lay = nat.layout(rows)
    for r in range(a, b + 1):
        line = lay[r - 1] if r - 1 < len(lay) else []
        g = [(ch, x) for ch, x in line if x0 <= x < x1]
        out.append((r, "".join(ch for ch, _ in g), g[0][1] if g else None, g))
    return out


def crop(nat: Native, rows: list[str], a: int, b: int, x0: int, x1: int, pad: int = PAD) -> np.ndarray:
    """Render ONLY the sliced glyphs (pen kept at source position), cropped to [x0-pad, x1+pad)."""
    sl = slice_rows(nat, rows, a, b, x0, x1)
    H = (b - a + 1) * PITCH + 2 * pad
    W = (x1 - x0) + 2 * pad
    img = np.zeros((H, W), bool)
    for i, (_, _, _, g) in enumerate(sl):
        top = pad + i * PITCH
        for ch, x in g:
            _, xo, yo, m = nat.glyph(ch)
            if not m.size:
                continue
            X, Y = pad + (x - x0) + xo, top + yo
            ys, xs = max(0, -Y), max(0, -X)
            h, w = min(m.shape[0], H - Y) - ys, min(m.shape[1], W - X) - xs
            if h > 0 and w > 0:
                img[Y + ys:Y + ys + h, X + xs:X + xs + w] |= m[ys:ys + h, xs:xs + w]
    return img


def save_png(a: np.ndarray, path: Path, zoom: int = 1) -> None:
    im = Image.fromarray(np.where(a, 0, 255).astype(np.uint8))
    if zoom > 1:
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.convert("1").save(path, optimize=True)


def glyph_label(ch: str) -> str:
    if ch == "　":
        return "FULLSP"
    if ch == " ":
        return "halfsp"
    return ch


def cmd_show(a):
    nat = Native()
    rows = load_source(a.src)
    r0, r1 = map(int, a.rows.split("-"))
    if not (1 <= r0 <= r1 <= len(rows)):
        raise SystemExit(f"rows {a.rows} outside 1-{len(rows)}")
    if a.x:
        x0, x1 = map(int, a.x.split("-"))
    else:
        x0, x1 = 0, max(nat.row_width(r) for r in rows[r0 - 1:r1]) + 1
    print(f"source {a.src}  ({len(rows)} rows)  rows {r0}-{r1}  pen x [{x0},{x1})  "
          f"font {nat.font_sha256[:12]}  16px/{PITCH}px")
    for r, text, px, g in slice_rows(nat, rows, r0, r1, x0, x1):
        print(f"row {r:3d} pen_x={px!s:>4} | {text!r}")
        if a.glyphs:
            print("        " + " ".join(f"{glyph_label(ch)}@{x - x0}" for ch, x in g))
    img = crop(nat, rows, r0, r1, x0, x1)
    if a.png:
        save_png(img, Path(a.png))
        print(f"crop {a.png} {img.shape[1]}x{img.shape[0]} (native, pad {PAD})")
    if a.view:
        save_png(img, Path(a.view), a.zoom)
        print(f"view {a.view} x{a.zoom}")


def cmd_rect(a):
    nat = Native()
    rows = load_source(a.src)
    x, y, w, h = map(int, a.rect.split(","))
    r0 = max(1, (y - a.pad) // a.pitch + 1)
    r1 = min(len(rows), (y + h - 1 - a.pad) // a.pitch + 1)
    x0, x1 = max(0, x - a.pad), x + w - a.pad
    print(f"rect {a.rect} on {a.pitch}px rows/pad {a.pad} -> rows {r0}-{r1}, pen x [{x0},{x1})")
    print(f"next: role_crop.py show '{a.src}' --rows {r0}-{r1} --x {x0}-{x1} --glyphs")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show")
    s.add_argument("src")
    s.add_argument("--rows", required=True)
    s.add_argument("--x")
    s.add_argument("--glyphs", action="store_true")
    s.add_argument("--png")
    s.add_argument("--view")
    s.add_argument("--zoom", type=int, default=4)
    r = sub.add_parser("rect")
    r.add_argument("src")
    r.add_argument("--rect", required=True)
    r.add_argument("--pitch", type=int, default=18)
    r.add_argument("--pad", type=int, default=8)
    a = ap.parse_args()
    {"show": cmd_show, "rect": cmd_rect}[a.cmd](a)


if __name__ == "__main__":
    main()
