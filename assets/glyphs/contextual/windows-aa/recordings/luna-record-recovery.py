#!/usr/bin/env python3
"""Make exact-mask and recovered-kernel GIFs from the committed recovery JSON."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "assets/glyphs/contextual/ascii_justice_recovery.v1.json"
KERNEL = ROOT / "scripts/ascii_justice_kernels.py"


def font(size):
    for path in ("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F16, F20, F30 = font(16), font(20), font(30)
BG, FG, DIM, INK = "#10151c", "#e9f0f6", "#9aabbc", "#75dcad"


def load_doc():
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    if len(doc["glyphs"]) < 93:
        raise ValueError("Recovery index does not contain 93 original mappings")
    return doc, doc["glyphs"][:93]


def glyph_pages(doc, glyphs):
    frames = []
    page_size, cols, rows = 16, 4, 4
    cell_w, cell_h = 300, 178
    for offset in range(0, len(glyphs), page_size):
        batch = glyphs[offset:offset + page_size]
        im = Image.new("RGB", (cols * cell_w, 105 + rows * cell_h), BG)
        d = ImageDraw.Draw(im)
        d.text((24, 12), "ASCII JUSTICE 1.4 — ORIGINAL RECOVERED GLYPH MASKS", font=F20, fill=FG)
        d.text((24, 43), f"JSON rasters · mappings {offset + 1}–{offset + len(batch)} of 93 · density is recorded ink_px", font=F16, fill=DIM)
        for idx, g in enumerate(batch):
            x, y = (idx % cols) * cell_w + 16, 86 + (idx // cols) * cell_h
            d.rounded_rectangle((x, y, x + cell_w - 18, y + cell_h - 12), radius=8, fill="#1b2530", outline="#384757")
            ch = g["char"]
            label = "SPACE" if ch == " " else repr(ch)
            d.text((x + 12, y + 8), f"{g['index']:02d}  {label}", font=F20, fill=FG)
            d.text((x + 172, y + 12), f"density {g['density_value']}  ·  ink {g['ink_px']}/128", font=F16, fill=DIM)
            raster = g["raster_rows"]
            # Display the source's 8×16 binary mask directly, not a rendered font glyph.
            for ry, line in enumerate(raster):
                for rx, pix in enumerate(line):
                    if pix == "#":
                        px, py = x + 14 + rx * 14, y + 44 + ry * 7
                        d.rectangle((px, py, px + 11, py + 5), fill=INK)
            d.text((x + 155, y + 58), "".join(raster), font=F16, fill=DIM, spacing=2)
        frames.append(im)
    # Explain that the JSON intentionally carries further recovered evidence.
    return frames


def import_kernels():
    import importlib.util
    spec = importlib.util.spec_from_file_location("luna_ascii_justice_kernels", KERNEL)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def demo_frames():
    kernels = import_kernels()
    # Explicit synthetic RGB sample: two contrasting blocks inside one 8×16 tile.
    rgb = [[(238, 238, 238) if (x < 4 or y < 7) else (24, 24, 24)
            for x in range(8)] for y in range(16)]
    title = "RECOVERED EDGE KERNEL — SYNTHETIC RGB TILE, NOT ORIGINAL PROGRAM EXECUTION"
    frames = []
    for thickness in (1, 2, 3):
        mask = kernels.outline_mask(rgb, thickness=thickness, darkness=2)
        scores = kernels.outline_scores(mask, "highest")
        best = max(range(len(scores)), key=scores.__getitem__)
        glyph = kernels.glyphs()[best % 93]
        im = Image.new("RGB", (1000, 480), BG)
        d = ImageDraw.Draw(im)
        d.text((24, 18), title, font=F20, fill=FG)
        d.text((24, 57), f"Recovered Python kernel · darkness=2 · edge thickness={thickness} · highest-quality scoring", font=F16, fill=DIM)
        # RGB source tile shown as actual colored samples.
        for y in range(16):
            for x in range(8):
                color = rgb[y][x]
                px, py = 60 + x * 28, 140 + y * 16
                d.rectangle((px, py, px + 25, py + 13), fill=color)
        d.text((35, 110), "RGB input", font=F16, fill=FG)
        d.text((47, 415), "8×16", font=F16, fill=DIM)
        d.text((310, 110), "binary edge mask", font=F16, fill=FG)
        for y in range(16):
            for x in range(8):
                px, py = 330 + x * 28, 140 + y * 16
                d.rectangle((px, py, px + 25, py + 13), fill=INK if mask[y][x] else "#26313c")
        d.text((580, 110), "top recovered candidate mask", font=F16, fill=FG)
        for y, row in enumerate(glyph["raster_rows"]):
            for x, ch in enumerate(row):
                px, py = 640 + x * 30, 140 + y * 30
                d.rectangle((px, py, px + 26, py + 26), fill=INK if ch == "#" else "#26313c")
        d.text((640, 400), f"{glyph['index']:02d} {glyph['char']!r}  score {scores[best]}", font=F20, fill=FG)
        d.text((24, 452), "Kernel demo only: recovered Python edge/scoring routines; not a full converter or Windows EXE/DLL run.", font=F16, fill=DIM)
        frames.append(im)
    return frames


def save_gif(frames, path, durations):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=False, disposal=2)


def main():
    doc, glyphs = load_doc()
    glyph = glyph_pages(doc, glyphs)
    save_gif(glyph, OUT / "luna-original-recovered-masks.gif", [1400] * len(glyph))
    save_gif(demo_frames(), OUT / "luna-recovered-edge-kernel-demo.gif", [1800] * 3)
    manifest = {
        "source": str(DATA.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "kernel_source": str(KERNEL.relative_to(ROOT)),
        "kernel_sha256": hashlib.sha256(KERNEL.read_bytes()).hexdigest(),
        "scope": "93 exact JSON masks; edge demo uses a synthetic RGB tile and recovered Python kernels; not complete converter parity",
    }
    (OUT / "luna-recordings.source.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(glyph)} mask pages and 3 edge-kernel frames")


if __name__ == "__main__":
    main()
