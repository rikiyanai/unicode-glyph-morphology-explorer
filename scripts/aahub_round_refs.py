#!/usr/bin/env python3
"""Package exact archived AAHub PNG/TXT references; no fonts or caches needed.

Explicit --write outputs only the declared round-reference JSON and source-pair
directory. Ordinary load/view is read-only and checks the packaged byte hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "assets/glyphs/contextual/aahub_round_refs.sources.v1.json"
OUTPUT = ROOT / "assets/glyphs/contextual/aahub_round_refs.v1.json"
PAIRS = ROOT / "assets/glyphs/contextual/aahub-round-refs"
SCHEMA = "glyph_morphology.round_references.v1"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package(write: bool = False) -> dict:
    definition = json.loads(SOURCES.read_text(encoding="utf-8"))
    archive = Path(definition["archive_root"])
    records = []
    for source in definition["records"]:
        original = archive / source["slug"] / source["piece"]
        image_bytes = original.with_suffix(".png").read_bytes()
        text_bytes = original.with_suffix(".txt").read_bytes()
        image_path = PAIRS / (source["id"] + ".png")
        text_path = PAIRS / (source["id"] + ".txt")
        with Image.open(original.with_suffix(".png")) as image:
            width, height = image.size
        if write:
            PAIRS.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(image_bytes)
            text_path.write_bytes(text_bytes)
        records.append({
            "id": source["id"], "title": source["title"],
            "pattern_family": "round-contour-source-construction",
            "focus_forms": source["focus_forms"],
            "provenance": {
                "source_id": f"aahub/{source['slug']}/{source['piece']}",
                "source_url": source["source_url"],
                "image_path": str(image_path.relative_to(ROOT)),
                "text_path": str(text_path.relative_to(ROOT)),
                "origin_image_path": str(original.with_suffix(".png")),
                "origin_text_path": str(original.with_suffix(".txt")),
                "source_image_sha256": sha(image_bytes),
                "source_text_sha256_file": sha(text_bytes),
                "native_image_status": "Exact archived native PNG bytes; Saitamaar 16px source profile, not terminal-font text.",
                "annotation_status": source["review"],
                "live_url_status": "Page URL retained from archived HTML when known; exact drawings are identified by the archived piece ID and packaged byte hashes, not current live post numbering.",
            },
            "native_reference": {"width": width, "height": height},
            "passages": [{"id": source["id"] + "-full-text", "line_start": 1,
                          "rows": text_bytes.decode("utf-8").splitlines()}],
            "interpretation": {
                "observed_visual": source["observed_visual"],
                "drawn_analogy": source["drawn_analogy"],
                "mathematical_family": "Not assigned; a depicted rounded form does not prove a mathematical feature detector.",
                "historical_implementation_limit": "No renderer behavior, temporal quality, corpus-wide frequency or operator acceptance is established.",
            },
        })
    doc = {"schema": SCHEMA, "input_sha256": sha(SOURCES.read_bytes()), "families": records}
    if write:
        OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def load() -> dict:
    doc = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA or doc.get("input_sha256") != sha(SOURCES.read_bytes()):
        raise ValueError("round-reference definition changed; package explicitly with --write")
    for record in doc["families"]:
        for key, hash_key in (("image_path", "source_image_sha256"),
                              ("text_path", "source_text_sha256_file")):
            path = (ROOT / record["provenance"][key]).resolve()
            if not path.is_relative_to(PAIRS.resolve()):
                raise ValueError("round-reference pair must remain in its packaged directory")
            if sha(path.read_bytes()) != record["provenance"][hash_key]:
                raise ValueError(f"round-reference pair hash mismatch: {path.name}")
    return doc


def raster_rows(record: dict, width: int, native: bool = False, x: int = 0) -> tuple[list[str], int, int]:
    """Return an honest overview OR unscaled native pixel viewport.

    Overview is integer block pooling (any ink in each square block), not a
    new glyph rendering or native-fit evidence. Native mode never resamples.
    """
    import numpy as np
    with Image.open(ROOT / record["provenance"]["image_path"]) as image:
        ink = np.asarray(image.convert("L")) < 128
    height, source_width = ink.shape
    width = max(1, width)
    scale = 1 if native else max(1, (source_width + width - 1) // width,
                                 (height + 47) // 48)
    if scale > 1:
        pad_y, pad_x = (-height) % scale, (-source_width) % scale
        ink = np.pad(ink, ((0, pad_y), (0, pad_x))).reshape(
            (height + pad_y) // scale, scale,
            (source_width + pad_x) // scale, scale).any(axis=(1, 3))
    offset = min(max(0, x), max(0, ink.shape[1] - width)) if native else 0
    ink = ink[:, offset:offset + width]
    return ["".join("#" if p else "." for p in row) for row in ink], scale, offset


class ReferenceCorpus:
    def __init__(self, doc: dict):
        self.cps = sorted({ord(ch) for r in doc["families"] for form in r["focus_forms"] for ch in form})
        self.indices = {cp: i for i, cp in enumerate(self.cps)}

    def i(self, cp: int) -> int | None:
        return self.indices.get(cp)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    doc = package(write=True) if args.write else load()
    print(f"{len(doc['families'])} packaged round references; write={args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
