#!/usr/bin/env python3
"""Enumerate useful 2- and 3-cell glyph combinations for authoring review.

This is an offline FL-4512 authoring tool. It does not read or write atlas,
compiler, shader, renderer, or runtime state.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import unicodedata
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import glyph_audit as ga  # noqa: E402

REPO_ROOT = SCRIPTS_DIR.parent

# Source-named line-art alphabet from the archived Stone Story tutorial passages:
# low/mid/high horizontals, mirrored accents, vertical/curve/diagonal line marks,
# anti-aliasing marks, negative-space dots, and the overline/underscore pair.
USEFUL_LINE_GLYPHS = (
    "_", ".", ",", "-", "'", "`", ":", "|", "/", "\\", "(", ")", "!",
    "\u00a1", "\u00b7", "\u203e",
)

# The source names these alphanumerics as sometimes useful, but they carry the
# language-recognition distraction flag. Keep them opt-in.
SOURCE_ALNUM_GLYPHS = tuple("oOvTl7ucCx")

SHAPES = {
    2: {
        "domino_h": ((0, 0), (1, 0)),
        "domino_v": ((0, 0), (0, 1)),
    },
    3: {
        "line_h": ((0, 0), (1, 0), (2, 0)),
        "line_v": ((0, 0), (0, 1), (0, 2)),
        "corner_ne": ((0, 1), (0, 0), (1, 0)),
        "corner_se": ((0, 0), (0, 1), (1, 1)),
        "corner_sw": ((1, 0), (1, 1), (0, 1)),
        "corner_nw": ((1, 1), (1, 0), (0, 0)),
    },
}

FALLBACK_MIRRORS = {
    "/": "\\",
    "\\": "/",
    "(": ")",
    ")": "(",
    "'": "`",
    "`": "'",
}


def _dims(offsets: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    return max(c for c, _r in offsets) + 1, max(r for _c, r in offsets) + 1


def _mirror_map(c: ga.Corpus | None, glyphs: tuple[str, ...]) -> dict[str, str]:
    mirrors = {ch: FALLBACK_MIRRORS.get(ch, ch) for ch in glyphs}
    if c is None:
        return mirrors
    cp_to_ch = {ord(ch): ch for ch in glyphs}
    for a, b in ga.find_mirror(c):
        acp, bcp = int(c.cps[a]), int(c.cps[b])
        if acp in cp_to_ch and bcp in cp_to_ch:
            mirrors[cp_to_ch[acp]] = cp_to_ch[bcp]
            mirrors[cp_to_ch[bcp]] = cp_to_ch[acp]
    return mirrors


def _metrics(c: ga.Corpus | None, glyphs: tuple[str, ...]) -> dict[str, dict]:
    if c is None:
        return {ch: {"renderable": True, "weight": 0.0, "alnum": ch.isalnum()}
                for ch in glyphs}
    out: dict[str, dict] = {}
    for ch in glyphs:
        i = c.i(ord(ch))
        if i is None:
            out[ch] = {"renderable": False, "weight": 1.0, "alnum": ch.isalnum()}
            continue
        row = ga.distraction_row(c, i)
        out[ch] = {
            "renderable": True,
            "weight": round(float(row["weight"]), 4),
            "alnum": bool(row["alnum"]),
        }
    return out


def enumerate_candidates(
    *,
    c: ga.Corpus | None = None,
    max_size: int = 3,
    include_source_alnum: bool = False,
    max_distraction: float = 0.05,
) -> list[dict]:
    """Return every connected 2- or 3-cell ordered glyph arrangement in scope."""
    glyphs = USEFUL_LINE_GLYPHS + (SOURCE_ALNUM_GLYPHS if include_source_alnum else ())
    glyphs = tuple(dict.fromkeys(glyphs))
    metrics = _metrics(c, glyphs)
    mirrors = _mirror_map(c, glyphs)

    rows: list[dict] = []
    for size in range(2, max_size + 1):
        for shape_id, offsets in SHAPES.get(size, {}).items():
            cols, rows_count = _dims(offsets)
            for chars in itertools.product(glyphs, repeat=size):
                cell_metrics = [metrics[ch] for ch in chars]
                if not all(m["renderable"] for m in cell_metrics):
                    continue
                if any(m["alnum"] for m in cell_metrics) and not include_source_alnum:
                    continue
                distract_max = max(m["weight"] for m in cell_metrics)
                if distract_max > max_distraction:
                    continue
                cells = [
                    {"col": col, "row": row, "cp": ord(ch), "char": ch}
                    for (col, row), ch in zip(offsets, chars)
                ]
                mirror_cells = [
                    {
                        "col": cols - 1 - col,
                        "row": row,
                        "cp": ord(mirrors[ch]),
                        "char": mirrors[ch],
                    }
                    for (col, row), ch in zip(offsets, chars)
                ]
                mirror_cells.sort(key=lambda d: (d["row"], d["col"]))
                cps = "_".join(f"{ord(ch):04X}" for ch in chars)
                rows.append({
                    "id": f"auto_{shape_id}_{cps}",
                    "shape": shape_id,
                    "cols": cols,
                    "rows": rows_count,
                    "chars": "".join(chars),
                    "cells": cells,
                    "mirror_chars": "".join(d["char"] for d in mirror_cells),
                    "mirror": {"method": "horizontal", "cells": mirror_cells},
                    "distract_max": round(distract_max, 4),
                    "names": [unicodedata.name(ch, "") for ch in chars],
                })
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-size", type=int, default=3, choices=[2, 3])
    p.add_argument("--include-source-alnum", action="store_true")
    p.add_argument("--max-distraction", type=float, default=0.05)
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true",
                   help="write .run/glyph_audit/glyph_combo_candidates.json")
    p.add_argument("--no-cache", action="store_true",
                   help="skip renderability/distraction checks and enumerate by source alphabet only")
    args = p.parse_args(argv)

    c = None
    if not args.no_cache:
        try:
            c = ga.Corpus()
        except SystemExit as exc:
            sys.stderr.write(f"cache unavailable; rerun with --no-cache or build glyph_features: {exc}\n")
            return 2

    rows = enumerate_candidates(
        c=c,
        max_size=args.max_size,
        include_source_alnum=args.include_source_alnum,
        max_distraction=args.max_distraction,
    )
    by_shape: dict[str, int] = {}
    for row in rows:
        by_shape[row["shape"]] = by_shape.get(row["shape"], 0) + 1

    print(f"{len(rows)} useful glyph-combination candidates")
    print("shapes: " + ", ".join(f"{k}:{by_shape[k]}" for k in sorted(by_shape)))
    for row in rows[:args.limit]:
        print(f"{row['id']}  {row['chars']!r}  mirror {row['mirror_chars']!r}  "
              f"shape={row['shape']}  distract={row['distract_max']:.4f}")

    if args.json:
        out = REPO_ROOT / ".run" / "glyph_audit" / "glyph_combo_candidates.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "schema": "fl4512.glyph_combo_candidates.v1",
            "source": "Stone Story archived transcripts 2026-09-07",
            "max_size": args.max_size,
            "include_source_alnum": args.include_source_alnum,
            "max_distraction": args.max_distraction,
            "count": len(rows),
            "candidates": rows,
        }, indent=2) + "\n")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
