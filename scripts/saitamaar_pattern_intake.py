#!/usr/bin/env python3
"""Reproduce the supplied bundle measurements and package native pattern rasters.

Writes only the declared evidence snapshot with --write. Viewing that tracked
snapshot needs neither the external font nor the original temporary scripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "assets/glyphs/contextual/saitamaar_pattern_intake.v1.json"
OUTPUT = ROOT / "assets/glyphs/contextual/saitamaar_pattern_evidence.v1.json"
SCHEMA = "glyph_morphology.pattern_evidence.v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(ch: str, font: ImageFont.FreeTypeFont, profile: dict) -> dict:
    """Same threshold, advance, canvas and 8-connected PCA as bundles.py.

    The original stdout calls these 'strokes'; expose the actual quantity as
    connected ink components. PCA does not decompose a crossing into strokes.
    """
    advance = float(font.getlength(ch))
    pitch = profile["row_pitch_px"]
    canvas = Image.new("L", (int(advance) + profile["padding_right_px"], pitch), 255)
    ImageDraw.Draw(canvas).text((0, 0), ch, font=font, fill=0, anchor=profile["anchor"])
    ink = np.asarray(canvas) < profile["ink_threshold_lt"]
    labels, count = label(ink, structure=np.ones((3, 3)))
    components = []
    for number in range(1, count + 1):
        points = np.argwhere(labels == number).astype(float)
        component = {"ink_px": len(points), "axis_deg": None, "axis_ratio": None}
        if len(points) >= 3:
            _, singular, vt = np.linalg.svd(points - points.mean(0), full_matrices=False)
            dy, dx = vt[0]
            component["axis_deg"] = float(np.degrees(np.arctan2(-dy, dx)) % 180)
            component["axis_ratio"] = (float(singular[0] / singular[1])
                                       if singular[1] > 1e-12 else None)
        components.append(component)
    points = np.argwhere(ink)
    bbox = ([int(points[:, 1].min()), int(points[:, 0].min()),
             int(points[:, 1].max()), int(points[:, 0].max())] if len(points) else None)
    return {"char": ch, "codepoint": f"U+{ord(ch):04X}", "advance_px": advance,
            "ink_px": int(ink.sum()), "ink_per_advance_row": float(ink.sum() / (advance * pitch)),
            "ink_bbox_xyxy_inclusive": bbox, "components": components}


def native_rows(rows: list[str], font: ImageFont.FreeTypeFont, profile: dict) -> list[str]:
    """Whole glyphs, native advances, no normalization/rotation/scaling/mirroring."""
    width = math.ceil(max(sum(font.getlength(ch) for ch in row) for row in rows))
    canvas = Image.new("L", (max(1, width) + profile["padding_right_px"],
                              profile["row_pitch_px"] * len(rows)), 255)
    draw = ImageDraw.Draw(canvas)
    for number, row in enumerate(rows):
        x = 0.0
        for ch in row:
            draw.text((x, number * profile["row_pitch_px"]), ch,
                      font=font, fill=0, anchor=profile["anchor"])
            x += font.getlength(ch)
    ink = np.asarray(canvas) < profile["ink_threshold_lt"]
    return ["".join("#" if pixel else "." for pixel in row) for row in ink]


def reported_checks(stdout: str, measurements: dict) -> list[dict]:
    """Preserve duplicate source rows and compare precisely at their printed precision."""
    checks = []
    for row in stdout.splitlines():
        match = re.fullmatch(r"(.) adv\s+([\d.]+) ink\s+(\d+) px \(([\d.]+)\) strokes (\d+): (.*)", row)
        if not match:
            raise ValueError(f"unrecognized source measurement: {row!r}")
        ch, advance, ink, density, count, angles = match.groups()
        metric = measurements[ch]
        actual_angles = " ".join("dot" if c["axis_deg"] is None else f"{c['axis_deg']:.0f}"
                                 for c in metric["components"])
        actual = (f"{metric['advance_px']:.1f}", str(metric["ink_px"]),
                  f"{metric['ink_per_advance_row']:.2f}", str(len(metric["components"])), actual_angles)
        expected = (advance, ink, density, count, angles)
        checks.append({"reported_row": row, "matches": actual == expected})
    return checks


def build(font_path: Path, definition: dict | None = None) -> dict:
    definition = definition or json.loads(INPUT.read_text(encoding="utf-8"))
    if digest(font_path) != definition["source"]["font_sha256"]:
        raise ValueError("font hash differs from the supplied measurement source")
    profile = definition["measurement"]
    chars = set()
    for family in definition["families"]:
        for variant in family["variants"]:
            chars.update("".join(variant["rows"]))
    chars.update(row[0] for row in definition["source"]["reported_stdout"].splitlines())
    with TTFont(font_path) as tt:
        missing = sorted(ord(ch) for ch in chars if ord(ch) not in tt.getBestCmap())
    if missing:
        raise ValueError(f"glyphs absent from pinned font: {missing}")
    font = ImageFont.truetype(str(font_path), profile["px"])
    measurements = {ch: measure(ch, font, profile) for ch in sorted(chars)}
    checks = reported_checks(definition["source"]["reported_stdout"], measurements)
    if not all(check["matches"] for check in checks):
        raise ValueError("source measurements do not reproduce; preserve and investigate the mismatch")
    families = []
    for family in definition["families"]:
        comparisons = []
        for variant in family["variants"]:
            comparisons.append({"text_rows": variant["rows"],
                                "raster_rows": native_rows(variant["rows"], font, profile),
                                "glyph_metrics": [measurements[ch] for ch in
                                                  dict.fromkeys("".join(variant["rows"]))]})
        families.append({
            "id": family["id"], "title": family["title"], "pattern_family": "native-pattern-comparison",
            "focus_forms": [" / ".join(v["rows"]) for v in family["variants"]],
            "provenance": {"source_id": definition["source"]["session_id"],
                           "annotation_status": "operator-supplied comparison candidates, not art approval",
                           "native_image_status": "packaged thresholded native-font rasters; not terminal-font glyphs",
                           "source_font_sha256": digest(font_path)},
            "interpretation": {"observed_visual": family["note"],
                               "drawn_analogy": "Comparison proposals, not universal glyph meanings or validated source-region targets.",
                               "mathematical_family": "Connected components and PCA axes are raster descriptors, not pen-stroke decomposition or semantic feature lines.",
                               "historical_implementation_limit": "No renderer behavior, view variant, motion quality or lighting/value acceptance is established."},
            "native_comparisons": comparisons,
        })
    return {"schema": SCHEMA, "version": 1, "input_sha256": digest(INPUT),
            "generator_sha256": digest(Path(__file__)), "source": definition["source"],
            "measurement": profile, "reported_checks": checks, "families": families}


def load(path: Path = OUTPUT) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA or doc.get("input_sha256") != digest(INPUT):
        raise ValueError("pattern snapshot schema or input hash is stale; regenerate it explicitly")
    if doc.get("generator_sha256") != digest(Path(__file__)):
        raise ValueError("pattern generator changed; regenerate the snapshot explicitly")
    return doc


class PatternCorpus:
    """Small index for the standalone pattern axis; never builds morphology caches."""
    def __init__(self, doc: dict):
        self.cps = sorted({ord(ch) for record in doc["families"]
                           for variant in record["native_comparisons"]
                           for row in variant["text_rows"] for ch in row})
        self.idx_of = {cp: i for i, cp in enumerate(self.cps)}

    def i(self, cp: int) -> int | None:
        return self.idx_of.get(cp)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, required=True, help="original hash-pinned Saitamaar.ttf")
    parser.add_argument("--write", action="store_true", help=f"write only {OUTPUT.relative_to(ROOT)}")
    args = parser.parse_args()
    doc = build(args.font)
    if args.write:
        OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(doc['families'])} comparison groups; "
          f"{len(doc['reported_checks'])} source rows reproduced; write={args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
