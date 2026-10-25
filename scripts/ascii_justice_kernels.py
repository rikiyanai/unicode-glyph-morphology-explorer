"""Selected recovered ASCII Justice 1.4 kernels, not a complete converter port.

Transcribed from the packaged HSP2 decompilation: label_14/73/76 (edge mask),
label_16/17/18/19 (candidate scores). Numeric checks do not establish Windows
rendering or plugin sort/tie parity. Source mask coordinates are [y][x] here.
"""
from __future__ import annotations

import json
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "assets/glyphs/contextual/ascii_justice_recovery.v1.json"


def glyphs():
    doc = json.loads(INDEX.read_text(encoding="utf-8"))
    return doc["glyphs"][:93]


def outline_mask(rgb, thickness=1, darkness=2):
    """Exact tile-local directional differences and forward thickening.

    Preserve the original loop bounds: vertical pairs y=0..13; horizontal
    pairs x=0..5. No Sobel filter, Euclidean RGB distance, border extension or
    cross-tile derivative is invented. Any channel exceeding the threshold wins.
    """
    if thickness not in (1, 2, 3) or darkness not in range(5):
        raise ValueError("thickness must be 1..3 and darkness 0..4")
    if len(rgb) != 16 or any(len(row) != 8 for row in rgb):
        raise ValueError("Expected one 8x16 RGB tile")
    if any(len(p) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in p)
           for row in rgb for p in row):
        raise ValueError("RGB samples must be three integer channels in 0..255")
    threshold = (darkness * 12 + 16) ** 2
    ink = [[False] * 8 for _ in range(16)]
    for x in range(8):
        for y in range(14):
            if any((rgb[y][x][c] - rgb[y + 1][x][c]) ** 2 > threshold for c in range(3)):
                for offset in range(thickness):
                    ink[y + offset][x] = True
    for x in range(6):
        for y in range(16):
            if any((rgb[y][x][c] - rgb[y][x + 1][c]) ** 2 > threshold for c in range(3)):
                for offset in range(thickness):
                    ink[y][x + offset] = True
    return ink


def pixel_reward(source_ink, template_ink):
    """HSP sums: source dark→18/3; source white→-18/6 for ink/paper."""
    return (18 if template_ink else 3) if source_ink else (-18 if template_ink else 6)


def outline_scores(mask, quality="highest"):
    """Score slots before HSPDA sorting/density gating; preserve unused zeros.

    fast/normal: 15/48 glyphs, 64 staggered samples. nice/highest:
    48/93 glyphs at each of three horizontal alignments, 56 samples per slot.
    The HSP array has 285 slots, with alignment blocks starting at 0/93/186.
    """
    if quality not in ("fast", "normal", "nice", "highest"):
        raise ValueError("Unknown quality")
    if len(mask) != 16 or any(len(row) != 8 for row in mask):
        raise ValueError("Expected one 8x16 ink mask")
    templates = glyphs()
    result = [0] * 285
    if quality in ("fast", "normal"):
        count = 15 if quality == "fast" else 48
        for index in range(count):
            raster = templates[index]["raster_rows"]
            for x in range(8):
                for row in range(8):
                    y = row * 2 + ((x // 2) % 2)
                    result[index] += pixel_reward(bool(mask[y][x]), raster[y][x] == "#")
    else:
        count = 48 if quality == "nice" else 93
        for alignment in range(3):
            for index in range(count):
                raster = templates[index]["raster_rows"]
                for x in range(7):
                    for row in range(8):
                        y = row * 2 + ((x // 2) % 2)
                        source_x = x + (alignment == 1)
                        template_x = x + (alignment == 2)
                        result[index + alignment * 93] += pixel_reward(
                            bool(mask[y][source_x]), raster[y][template_x] == "#")
    return result
