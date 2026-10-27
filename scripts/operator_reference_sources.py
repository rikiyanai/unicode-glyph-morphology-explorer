#!/usr/bin/env python3
"""Verify and index the originals behind the operator's eight crops and cup.

--write owns operator_reference_sources.v1.json only. --search-statues prints
image-match candidates for any unbound crops; it never admits a binding.
No artwork is redrawn or substituted for an original.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/glyphs/contextual"
OUTPUT = BASE / "operator_reference_sources.v1.json"
CONTEXT = BASE / "shallot_native_contexts.v1.json"
CROPS = BASE / "operator_construction_crops.v1.json"
STATUES = Path("/Users/r/Projects/ascii-art-archive/collections/aahub/shingu-butsugu-mingeihin-zou")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build():
    import operator_construction_crops as crops
    doc = crops.load()
    original = json.loads(gzip.decompress(Path(doc["archive_path"]).read_bytes()))
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in (Path(__file__), CROPS, CONTEXT)}
    records = []
    for record in doc["families"]:
        p = record["provenance"]
        bound = bool(record["passages"])
        if bound:
            raw = original["aa"][p["archive_piece_index"]]["value"]
            if (ROOT / p["raw_text_path"]).read_text() != raw:
                raise ValueError(f"Original archive mismatch: {record['id']}")
            if (ROOT / p["text_path"]).read_text() != html.unescape(raw):
                raise ValueError(f"Decoded archive mismatch: {record['id']}")
        variants = p.get("source_variants") or []
        for variant in variants:
            index = variant["archive_piece_index"]
            if (ROOT / variant["raw_text_path"]).read_text() != original["aa"][index]["value"]:
                raise ValueError(f"Original shared-variant mismatch: {index}")
        status = ("shared AAHub motif matched; unique full-artwork variant unresolved (105/106/107)" if variants
                  else "original AAHub text matched" if bound else "original AAHub artwork NOT YET MATCHED")
        item = {"id": record["id"], "title": record["title"],
                "status": status,
                "crop_path": p["image_path"], "crop_sha256": p["source_image_sha256"],
                "source_url": p.get("source_url"),
                "candidate_page_url_not_a_binding": None if bound else p["candidate_page_url"],
                "original_full_text_path": p.get("text_path") if not variants else None,
                "original_raw_text_path": p.get("raw_text_path") if not variants else None,
                "source_variants": variants,
                "original_full_native_image_path": None,
                "archive_path": doc["archive_path"] if bound else None,
                "archive_piece_index": p.get("archive_piece_index") if not variants else None,
                "archive_index_unit": "zero-based aa array index; not a verified live post ID" if bound else None,
                "regions": [{"line_start": s["line_start"], "line_end": s["line_start"] + len(s["rows"]) - 1} for s in record["passages"]]}
        records.append(item)
    cup = next(r for r in json.loads(CONTEXT.read_text())["families"] if r["id"] == "aramaki-cup-plate-surface-following-tone")
    p = cup["provenance"]
    path = ROOT / p["text_path"]
    archive = Path(p["archive_piece_path"])
    original_cup = json.loads(gzip.decompress(archive.read_bytes()))["aa"][p["archive_piece_index"]]["value"]
    if path.read_text().rstrip("\n") != original_cup.rstrip("\n") or sha(path) != p["source_text_sha256_file"]:
        raise ValueError("Cup is not the exact archived operator variant")
    records.append({"id": cup["id"], "title": cup["title"], "status": "complete operator drawing exactly matches original AAHub text",
                    "source_url": p["source_url"], "original_full_text_path": p["text_path"],
                    "original_full_text_sha256": sha(path), "original_full_native_image_path": None,
                    "archive_path": str(archive), "archive_sha256": sha(archive), "archive_piece_index": p["archive_piece_index"],
                    "archive_index_unit": p["archive_index_unit"],
                    "regions": [{"line_start": s["line_start"], "line_end": s["line_start"] + len(s["rows"]) - 1} for s in cup["passages"]],
                    "operator_note": p["operator_note"],
                    "not_a_substitute": "tabemono-01/resK-182 has different plate contents; it is not this original drawing"})
    for record in records:
        record["artwork_creation"] = {
            "verified": False,
            "creator": None,
            "editor": None,
            "production_workflow": None,
            "status": "UNVERIFIED: exact artwork located, but no artwork-specific creation workflow established",
            "findings_owner": "docs/code-provenance.md#artwork-specific-production-backtrace-2026-10-25",
        }
        for key in ("crop_path", "original_full_text_path", "original_raw_text_path"):
            if record.get(key):
                path = ROOT / record[key]
                inputs[str(path.relative_to(ROOT))] = sha(path)
        for variant in record.get("source_variants") or []:
            for key in ("text_path", "raw_text_path"):
                path = ROOT / variant[key]
                inputs[str(path.relative_to(ROOT))] = sha(path)
    result = {"schema": "glyph_morphology.operator_reference_sources.v1", "input_hashes": inputs,
              "records": records, "limit": "All eight local crop constructions have source references. Crop 04 matches a motif repeated in three full-artwork variants; no unique variant or repeated left/right occurrence is invented. Full source text is not an original native PNG. No guessed live post anchors."}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def load():
    result = json.loads(OUTPUT.read_text())
    if result.get("schema") != "glyph_morphology.operator_reference_sources.v1":
        raise ValueError("Unsupported operator source index")
    for path, expected in result["input_hashes"].items():
        if sha(ROOT / path) != expected:
            raise ValueError(f"Stale operator source index: {path}")
    return result


def attach(records):
    """Expose the central original-source status without changing raw records."""
    index = {r["id"]: r for r in load()["records"]}
    return [{**r, "provenance": {**r["provenance"],
             "reference_registry_path": str(OUTPUT.relative_to(ROOT)),
             "original_reference_status": index[r["id"]]["status"],
             "production_workflow_status": index[r["id"]]["artwork_creation"]["status"]}}
            if r["id"] in index else r for r in records]


def search_statues():
    """Image evidence discovery only, against one declared native PNG archive."""
    import cv2
    cv2.setNumThreads(1)
    doc = json.loads(CROPS.read_text())
    queries = {}
    for record in doc["families"]:
        if record["passages"]:
            continue
        image = cv2.imread(str(ROOT / record["provenance"]["image_path"]), cv2.IMREAD_GRAYSCALE)
        queries[record["id"]] = [(scale, cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA))
                                 for scale in (0.5, 0.5625, 0.625, 0.666667, 0.75)]
    if not queries:
        print("No unbound local constructions remain; crop04's full-variant ambiguity is retained separately.")
        return
    ranked = {key: [] for key in queries}
    images = sorted(STATUES.glob("res*.png"))
    for path in images:
        source = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if source is None:
            raise ValueError(f"Cannot read {path}")
        for key, variants in queries.items():
            best = None
            for scale, query in variants:
                if source.shape[0] < query.shape[0] or source.shape[1] < query.shape[1]:
                    continue
                response = cv2.matchTemplate(source, query, cv2.TM_CCOEFF_NORMED)
                _, score, _, pos = cv2.minMaxLoc(response)
                item = {"path": str(path), "score": score, "scale": scale, "xy": list(pos), "query_wh": [query.shape[1], query.shape[0]]}
                if best is None or score > best["score"]:
                    best = item
            if best:
                ranked[key].append(best)
    for key, matches in ranked.items():
        print(json.dumps({"crop": key, "candidates_only_not_bindings": sorted(matches, key=lambda r: -r["score"])[:3]}, ensure_ascii=False))
    print(f"Searched {len(images)} original native PNGs; original screenshot bytes unchanged.")


def inspect_ranges(ranges):
    archive = json.loads(CROPS.read_text())["archive_path"]
    page = json.loads(gzip.decompress(Path(archive).read_bytes()))
    for spec in ranges:
        index, start, end = map(int, spec.split(":"))
        rows = html.unescape(page["aa"][index]["value"]).splitlines()
        print(f"--- aa[{index}] full rows={len(rows)} ---")
        for n in range(max(1, start), min(len(rows), end) + 1):
            print(f"{n:03}: {rows[n - 1]}")


def inspect_metadata():
    """Print actual source fields without mistaking a subject caption for credit."""
    registry = json.loads(OUTPUT.read_text())
    wanted = {}
    for record in registry["records"]:
        if record.get("archive_path"):
            indices = wanted.setdefault(record["archive_path"], set())
            if record.get("archive_piece_index") is not None:
                indices.add(record["archive_piece_index"])
            indices.update(v["archive_piece_index"] for v in record.get("source_variants", []))
    for path, indices in wanted.items():
        page = json.loads(gzip.decompress(Path(path).read_bytes()))
        print(json.dumps({"archive_path": path, "page_fields": list(page),
                          "page_metadata": {k: v for k, v in page.items() if k != "aa"},
                          "selected_artwork_fields": {str(i): list(page["aa"][i]) for i in sorted(indices)}}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--search-statues", action="store_true")
    parser.add_argument("--inspect-range", action="append", metavar="INDEX:START:END")
    parser.add_argument("--inspect-metadata", action="store_true")
    args = parser.parse_args()
    if args.inspect_metadata:
        inspect_metadata()
    elif args.inspect_range:
        inspect_ranges(args.inspect_range)
    elif args.search_statues:
        search_statues()
    else:
        doc = build() if args.write else load()
        for record in doc["records"]:
            locator = record.get("original_full_text_path") or ", ".join(v["text_path"] for v in record.get("source_variants", [])) or "NO original binding"
            print(record["id"], record["status"], locator)
