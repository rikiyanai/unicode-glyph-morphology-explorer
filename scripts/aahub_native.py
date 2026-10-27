"""Native AAHub raster: Saitamaar 16 px, natural advances, 17 px rows, 8 px pad, 1-bit.

Reproduces the ascii-art-archive collections/aahub resNN.png recipe (manifest.txt:
"PIL Saitamaar @16px natural advances, 17px line step, 8px pad, <128 threshold to
bilevel"). Shared by aahub_block_mine.py (Lane A) and role_crop.py (Lane B).

Glyphs are composited from cached per-glyph masks. Nearly every advance is a whole
pixel; the pen is kept as a float and a glyph is placed at the rounded pen, so the
rare fractional-advance glyph (frac_glyphs) can drift by <1 px from PIL line drawing.
--verify compares against the archive PNGs.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PX = 16
PITCH = 17
PAD = 8
DEFAULT_FONT = Path("/home/user/trueff-shallot/assets/font/Saitamaar.ttf")


class Native:
    def __init__(self, font_path: Path = DEFAULT_FONT):
        self.font_path = Path(font_path)
        self.font_sha256 = hashlib.sha256(self.font_path.read_bytes()).hexdigest()
        self.font = ImageFont.truetype(str(self.font_path), PX)
        self._cache: dict[str, tuple[float, int, int, np.ndarray]] = {}
        self.frac_glyphs: set[str] = set()

    def glyph(self, ch: str):
        """(advance_px, x_off, y_off, mask) with mask placed relative to pen (x, row top)."""
        g = self._cache.get(ch)
        if g is None:
            adv = self.font.getlength(ch)
            if abs(adv - round(adv)) > 1e-6:
                self.frac_glyphs.add(ch)
            else:
                adv = int(round(adv))
            box = 64
            im = Image.new("L", (box, box), 255)
            ImageDraw.Draw(im).text((16, 16), ch, font=self.font, fill=0)
            m = np.array(im) < 128
            ys, xs = np.nonzero(m)
            if len(xs):
                y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                g = (adv, int(x0) - 16, int(y0) - 16, m[y0:y1, x0:x1].copy())
            else:
                g = (adv, 0, 0, np.zeros((0, 0), bool))
            self._cache[ch] = g
        return g

    def layout(self, rows: list[str]):
        """Per row: list of (char, pen_x_px) with pen starting at 0 (pad excluded); the
        pen is rounded to whole px (exact unless a fractional-advance glyph precedes)."""
        out = []
        for r in rows:
            x, line = 0.0, []
            for ch in r:
                line.append((ch, int(round(x))))
                x += self.glyph(ch)[0]
            out.append(line)
        return out

    def row_width(self, row: str) -> int:
        return int(-(-sum(self.glyph(ch)[0] for ch in row) // 1))

    def raster(self, rows: list[str], pad: int = PAD) -> np.ndarray:
        """Bool ink mask, shape (len(rows)*17 + 2*pad, max_width + 2*pad)."""
        W = max((self.row_width(r) for r in rows), default=0) + 2 * pad
        H = len(rows) * PITCH + 2 * pad
        a = np.zeros((H, W), bool)
        for i, line in enumerate(self.layout(rows)):
            top = pad + i * PITCH
            for ch, x in line:
                _, xo, yo, m = self.glyph(ch)
                if m.size == 0:
                    continue
                X, Y = pad + x + xo, top + yo
                ys, xs = max(0, -Y), max(0, -X)
                h = min(m.shape[0], H - Y) - ys
                w = min(m.shape[1], W - X) - xs
                if h > 0 and w > 0:
                    a[Y + ys:Y + ys + h, X + xs:X + xs + w] |= m[ys:ys + h, xs:xs + w]
        return a

    def png(self, rows: list[str], path: Path, pad: int = PAD) -> None:
        a = self.raster(rows, pad)
        Image.fromarray(np.where(a, 0, 255).astype(np.uint8)).convert("1").save(path, optimize=True)


def read_rows(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").rstrip("\n").split("\n")


def verify(archive: Path, slugs: list[str], n: int, seed: int) -> int:
    nat = Native()
    pages = [p for s in slugs for p in sorted((archive / s).glob("res*.txt"))]
    random.Random(seed).shuffle(pages)
    bad = 0
    for p in pages[:n]:
        png = p.with_suffix(".png")
        if not png.exists():
            continue
        ref = np.array(Image.open(png).convert("L")) < 128
        a = nat.raster(read_rows(p))
        ok = a.shape == ref.shape and not (a != ref).any()
        bad += not ok
        if not ok:
            print("MISMATCH", p, a.shape, ref.shape)
    print(f"verified {min(n, len(pages))} pages, mismatches {bad}, font {nat.font_sha256}")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verify", type=Path, metavar="AAHUB_ROOT")
    ap.add_argument("--slugs", nargs="*", default=[])
    ap.add_argument("-n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    if a.verify:
        sys.exit(1 if verify(a.verify, a.slugs, a.n, a.seed) else 0)
