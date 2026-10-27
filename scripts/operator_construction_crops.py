#!/usr/bin/env python3
"""Preserve operator screenshot bytes and source passages, without respelling them.

Only --write packages files in the declared contextual/operator-constructions
directory and writes operator_construction_crops.v1.json. Viewing is read-only.
Unresolved crop-to-source bindings remain explicitly unresolved.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/glyphs/contextual"
DEFINITION = BASE / "operator_construction_crops.sources.v1.json"
OUTPUT = BASE / "operator_construction_crops.v1.json"
PAIRS = BASE / "operator-constructions"
SCHEMA = "glyph_morphology.operator_construction_crops.v1"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


CANONICAL_ARCHIVE = "/Users/r/Projects/ascii-art-archive"


def readable(path: Path) -> Path:
    """The recorded path, or its copy under $AAHUB_ARCHIVE_ROOT when the recorded one is absent.
    Recorded provenance keeps the canonical path either way."""
    import os
    root = os.environ.get("AAHUB_ARCHIVE_ROOT")
    if not path.exists() and root and str(path).startswith(CANONICAL_ARCHIVE):
        return Path(root + str(path)[len(CANONICAL_ARCHIVE):])
    return path


def build() -> dict:
    definition = json.loads(DEFINITION.read_text(encoding="utf-8"))
    key = definition["archive_key"]
    archive = Path("/Users/r/Projects/ascii-art-archive/collections/aahub-mlt") / key[:2] / (key + ".json.gz")
    archived = readable(archive).read_bytes()
    page = json.loads(gzip.decompress(archived))
    PAIRS.mkdir(parents=True, exist_ok=True)
    sources = {}
    for index in definition["source_pieces"]:
        raw = page["aa"][index]["value"]
        decoded = html.unescape(raw)
        name = f"church-{index:03}"
        raw_path = PAIRS / (name + ".raw.txt")
        text_path = PAIRS / (name + ".txt")
        raw_path.write_bytes(raw.encode("utf-8"))
        text_path.write_bytes(decoded.encode("utf-8"))
        sources[index] = {"archive_piece_index": index, "raw_text_path": str(raw_path.relative_to(ROOT)),
                          "text_path": str(text_path.relative_to(ROOT)), "raw_sha256": digest(raw.encode("utf-8")),
                          "text_sha256": digest(decoded.encode("utf-8")), "decoded_rows": decoded.splitlines()}
    records = []
    for crop in definition["crops"]:
        original = Path(crop["path"])
        target = PAIRS / f"crop-{crop['number']:02}.png"
        # the operator's temporary screenshot may be gone; the packaged copy is those exact bytes
        data = original.read_bytes() if original.exists() else target.read_bytes()
        target.write_bytes(data)
        with Image.open(target) as image:
            width, height = image.size
        binding = crop["binding"]
        provenance = {"source_id": f"operator-crop-{crop['number']:02}",
                      "source_url": definition["page_url"] if binding else None,
                      "candidate_page_url": definition["page_url"],
                      "image_path": str(target.relative_to(ROOT)), "source_image_sha256": digest(data),
                      "origin_image_path": str(original),
                      "annotation_status": "operator-supplied construction witness; not a whole-page approval",
                      "native_image_status": "Exact operator screenshot bytes; do not infer a font pixel size or reconstruct its spacing.",
                      "source_binding_status": "source passage matched" if binding else "exact crop-to-row binding unresolved; no glyph identity guessed"}
        passages = []
        if binding:
            source = sources[binding["piece"]]
            rows = source["decoded_rows"][binding["line_start"] - 1:binding["line_end"]]
            for form in crop["focus_forms"]:
                if form not in "\n".join(rows):
                    raise ValueError(f"focus form absent from source passage: {crop['number']} {form}")
            provenance.update({"archive_piece_index": binding["piece"], "text_path": source["text_path"],
                               "source_text_sha256_file": source["text_sha256"],
                               "raw_text_path": source["raw_text_path"], "raw_text_sha256": source["raw_sha256"],
                               "decoding": "html.unescape; raw archived text also preserved"})
            passages.append({"id": f"crop-{crop['number']:02}-source-passage", "line_start": binding["line_start"], "rows": rows})
            if binding.get("equivalent_pieces"):
                variants = []
                for index in [binding["piece"], *binding["equivalent_pieces"]]:
                    alternative = sources[index]
                    alternative_rows = alternative["decoded_rows"][binding["line_start"] - 1:binding["line_end"]]
                    for form in crop["focus_forms"]:
                        if form not in "\n".join(alternative_rows):
                            raise ValueError(f"Shared motif absent from variant {index}: {form}")
                    variants.append({"archive_piece_index": index, "text_path": alternative["text_path"],
                                     "raw_text_path": alternative["raw_text_path"], "text_sha256": alternative["text_sha256"],
                                     "line_start": binding["line_start"], "line_end": binding["line_end"]})
                provenance.update({"source_binding_status": "shared source motif matched; unique full-artwork variant unresolved",
                                   "archive_piece_index_role": "representative context only; not unique identification",
                                   "context_limit": binding["ambiguity"], "source_variants": variants})
        records.append({"id": f"operator-curve-crop-{crop['number']:02}", "title": crop["title"],
                        "pattern_family": "operator-supplied-local-curve-construction", "focus_forms": crop["focus_forms"],
                        "native_reference": {"width": width, "height": height, "kind": "operator-screenshot"},
                        "provenance": provenance, "passages": passages,
                        "interpretation": {"observed_visual": "Operator supplied this exact local crop to identify the desired curve/construction examples. Inspect the complete neighboring ink and paper, not a round-subject label.",
                                           "drawn_analogy": "Glyph identities are asserted only for source-matched passages; remaining crops retain their screenshot evidence without guessed transcriptions.",
                                           "mathematical_family": "Not assigned; source construction, not a feature-detector classification.",
                                           "historical_implementation_limit": "No renderer consumption, animation quality or universal glyph meaning is established."}})
    doc = {"schema": SCHEMA, "definition_sha256": digest(DEFINITION.read_bytes()),
           "archive_path": str(archive), "archive_file_sha256": digest(archived),
           "page_url": definition["page_url"], "sources": list(sources.values()), "families": records}
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def load() -> dict:
    doc = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA or doc.get("definition_sha256") != digest(DEFINITION.read_bytes()):
        raise ValueError("operator crop definition is stale; package explicitly with --write")
    checks = [(r["provenance"]["image_path"], r["provenance"]["source_image_sha256"]) for r in doc["families"]]
    checks += [(s[k], s[h]) for s in doc["sources"] for k, h in (("text_path", "text_sha256"), ("raw_text_path", "raw_sha256"))]
    for name, expected in checks:
        path = (ROOT / name).resolve()
        if not path.is_relative_to(PAIRS.resolve()) or digest(path.read_bytes()) != expected:
            raise ValueError(f"operator source artifact changed: {name}")
    return doc


class ConstructionCorpus:
    def __init__(self, doc: dict):
        self.cps = sorted({ord(ch) for r in doc["families"] for form in r["focus_forms"] for ch in form})
        self.indices = {cp: i for i, cp in enumerate(self.cps)}

    def i(self, cp: int) -> int | None:
        return self.indices.get(cp)


def raster_rows(record: dict, width: int, native: bool = False, x: int = 0) -> tuple[list[str], int, int]:
    """A labelled ink-pooled overview or an unresampled source-pixel viewport."""
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    doc = build() if args.write else load()
    print(f"{len(doc['families'])} operator crops; {len(doc['sources'])} full source texts; write={args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
