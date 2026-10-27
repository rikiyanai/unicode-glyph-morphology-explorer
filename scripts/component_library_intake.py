#!/usr/bin/env python3
"""Package role-organized AAHub source libraries, preserving complete entries.

--write owns contextual/component-libraries-20261026/ and
component_libraries.v1.json only. No runtime, corpus train split or profile is
changed. Section headings and source notes are not counted as artistic presets.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/glyphs/contextual"
OUT = BASE / "component_libraries.v1.json"
ART = BASE / "component-libraries-20261026"
ARCHIVE = Path("/Users/r/Projects/ascii-art-archive/collections/aahub-mlt")
FONT = Path("/Users/r/Projects/ascii-art-archive/collections/aahub/Saitamaar.ttf")
SCHEMA = "glyph_morphology.component_libraries.v1"
LIBRARIES = [
    ("faces-small", "aa4a08aa52d30eb30ac42f64f068c157", "Small eyes / mouths / faces", [2, 17, 29, 33, 45, 46, 68, 69, 318, 434]),
    ("shapes", "a7065b14a8fb85fd61e0a2e01e91501b", "Circles / spheres / lines / curves / diagrams", [2, 3, 6, 7, 8, 20, 50, 100, 148, 150, 326, 327, 328]),
    ("eyes-large", "ddd5a07a469de526bc78d56073e70b03", "Large eyes / pupils", [115, 117, 219, 220]),
    ("mouths-large", "af6646eda0c94b59a270d543e6b8c209", "Large mouths / faces", [1, 2, 3]),
    ("ears", "9af1cf9526781e5a9a08a3ad5a6fcdad", "Ears", [1, 2, 3]),
    ("patterns", "88f4fa069651e1b1172f26a9a9bf409e", "Patterns / gradients / geometric patterns", [1, 2, 76, 77, 89]),
    ("effect-lines", "c1802704629a0f9e68ec8ed766fb5cc4", "Effect / convergence line constructions", [1, 2, 3]),
    ("mechanical-parts", "22a982ab68a83aa73b812d855eb686ac", "Mechanical arms / fists / legs / silhouettes", [1, 2, 69]),
]
HEADING = re.compile(r"【[^\n]+】")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_sections(page):
    """Retain actual headings and their hierarchy; never infer a fixed glyph role."""
    section, role = [], None
    for n, item in enumerate(page["aa"]):
        text = html.unescape(item["value"])
        stripped = text.strip()
        if HEADING.fullmatch(stripped):
            if page["name"] == "顔・表情01（小型）":
                if re.fullmatch(r"【[1-6]行】", stripped) or stripped == "【その他】":
                    section = ([role] if role else []) + [stripped]
                else:
                    role, section = stripped, [stripped]
            else:
                section = [stripped]
            yield n, text, list(section), True
        else:
            yield n, text, list(section), False


def discovery():
    rows = [json.loads(s) for s in (ARCHIVE / "index.jsonl").read_text().splitlines()]
    candidates = [r for r in rows if "エロ描写用" not in r["path"] and
                  (r["path"].startswith("汎用AA/体/") or r["path"].startswith("汎用AA/エフェクト/") or
                   (r["path"].startswith("汎用AA/") and re.search("パーツ|記号|枠|罫線|図形", r["name"])))]
    selected = {key for _, key, _, _ in LIBRARIES}
    result = []
    for r in candidates:
        path = ARCHIVE / r["key"][:2] / (r["key"] + ".json.gz")
        page = json.loads(gzip.decompress(path.read_bytes()))
        headings = [{"archive_piece_index": n, "label": text.strip()} for n, text, _, is_head in source_sections(page) if is_head]
        result.append({"key": r["key"], "title": r["name"], "path": r["path"], "entry_count": len(page["aa"]),
                       "source_url": "https://aahub.org/mlt/" + r["key"], "section_headings": headings,
                       "intake_status": "packaged library" if r["key"] in selected else "candidate metadata only; not a new visual inspection or approval"})
    return {"index_rows_scanned": len(rows), "index_sha256": digest((ARCHIVE / "index.jsonl").read_bytes()),
            "scope": "Generic body/effect categories plus generic parts/symbol/frame/shape titles; adult depiction category excluded. Not an exhaustive search of every artwork.",
            "candidates": result}


def build():
    from PIL import Image, ImageDraw, ImageFont
    from fontTools.ttLib import TTFont
    font = ImageFont.truetype(str(FONT), 16)
    with TTFont(FONT) as table:
        supported = set(table.getBestCmap())
    ART.mkdir(parents=True, exist_ok=True)
    hashes, libraries, records = {}, [], []
    advances = {}

    def adv(ch):
        if ch not in advances:
            advances[ch] = float(font.getlength(ch))
        return advances[ch]

    for slug, key, label, checked in LIBRARIES:
        src = ARCHIVE / key[:2] / (key + ".json.gz")
        data = src.read_bytes()
        page = json.loads(gzip.decompress(data))
        target = ART / (slug + ".original.json.gz")
        target.write_bytes(data)
        source_path = str(target.relative_to(ROOT))
        hashes[source_path] = digest(data)
        sections, count = [], 0
        for n, text, section, is_head in source_sections(page):
            if is_head:
                sections.append({"archive_piece_index": n, "label": text.strip(), "section_path": section})
                continue
            rows = text.splitlines() or [""]
            missing = sorted({ord(ch) for row in rows for ch in row if not ch.isspace() and ord(ch) not in supported})
            width = max(1, math.ceil(max(sum(adv(ch) for ch in row) for row in rows))) + 16
            height = max(1, len(rows)) * 17 + 16
            canvas = Image.new("L", (width, height), 255)
            draw = ImageDraw.Draw(canvas)
            for y, row in enumerate(rows):
                x = 8.0
                for ch in row:
                    draw.text((x, y * 17 + 8), ch, font=font, anchor="la", fill=0)
                    x += adv(ch)
            png = ART / f"{slug}-{n:03}.png"
            canvas.save(png)
            image_path = str(png.relative_to(ROOT))
            hashes[image_path] = digest(png.read_bytes())
            # Whole rows remain intact, including whitespace; there is no n-gram
            # or source-backed-shape heuristic reducing these constructions.
            forms = [r for r in rows if r.strip()][:3] or [""]
            record = {"id": f"component-{slug}-{n:03}",
                "title": f"{label} / {' / '.join(section) or 'introductory source note'} / aa[{n}]",
                "pattern_family": "role-organized-source-library", "focus_forms": forms,
                "native_reference": {"width": width, "height": height, "kind": "saitamaar-comparison"},
                "component_library": {"id": slug, "title": page["name"], "section_path": section,
                                      "archive_piece_index": n, "row_count": len(rows),
                                      "missing_comparison_font_codepoints": [f"U+{cp:04X}" for cp in missing]},
                "provenance": {"source_id": f"{page['name']} aa[{n}]", "source_url": "https://aahub.org/mlt/" + key,
                    "image_path": image_path, "source_image_sha256": hashes[image_path],
                    "source_page_path": source_path, "source_json_pointer": f"/aa/{n}/value",
                    "reference_registry_path": str(OUT.relative_to(ROOT)),
                    "source_binding_status": "complete original entry; raw source page preserved byte-for-byte; html.unescape for display only",
                    "annotation_status": "source-library entry, not an operator-approved preset; one-line notes remain source notes",
                    "review_state": "selected original TXT inspected; new comparison image available; no whole-catalog visual approval" if n in checked else "indexed original entry; NOT personally visually reviewed or operator-approved",
                    "native_image_status": "NEW Saitamaar16px/17px-row comparison; NOT a recovered original native PNG or browser screenshot",
                    "context_limit": "Source row-height groups are not proven matched LOD/animation families. Original creator/editor and automated selection unverified."},
                "passages": [{"id": f"original-aa-{n}", "line_start": 1, "rows": rows}],
                "interpretation": {"observed_visual": "Inspect this complete source entry and surrounding section; no automatic semantic or artistic acceptance is assigned.",
                    "drawn_analogy": "Role and footprint organize lookup; retain neighboring rows, native spacing, asymmetry, openings and any purposeful tone.",
                    "mathematical_family": "Source section labels, not inferred detector predicates.",
                    "historical_implementation_limit": "Reference library, not a runtime solver, original tool attribution, or proof of scale/temporal behavior."}}
            records.append(record)
            count += 1
        libraries.append({"id": slug, "title": page["name"], "label": label, "source_url": "https://aahub.org/mlt/" + key,
                          "archive_key": key, "archive_entry_count": len(page["aa"]), "section_headings": sections,
                          "source_entry_count_excluding_section_headings": count, "source_path": source_path,
                          "selected_text_inspection_indices": checked})
        print(f"{slug}: {count} complete source entries; {len(sections)} headings", flush=True)
    doc = {"schema": SCHEMA, "inspection_date": "2026-10-26", "libraries": libraries,
           "discovery": discovery(), "producer_sha256": digest(Path(__file__).read_bytes()),
           "font_sha256": digest(FONT.read_bytes()), "artifact_hashes": hashes, "families": records,
           "limit": "Counts are source entries, NOT unique presets or visually accepted art. Selected observations do not certify a whole library. Existing corpus splits/statistics unchanged."}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


@lru_cache(maxsize=1)
def load():
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise ValueError("Unsupported component library snapshot")
    for name, expected in doc["artifact_hashes"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ART.resolve()) or digest(path.read_bytes()) != expected:
            raise ValueError(f"Component source artifact changed: {name}")
    return doc


def select(doc, library=None, section=None):
    return [r for r in doc["families"] if (not library or r["component_library"]["id"] == library)
            and (not section or section.casefold() in " / ".join(r["component_library"]["section_path"]).casefold())]


class ComponentCorpus:
    def __init__(self, records):
        self.cps = sorted({ord(ch) for r in records
                           for row in [*r.get("focus_forms", []),
                                       *(row for p in r.get("passages", []) for row in p.get("rows", []))]
                           for ch in row})
        self.indices = {cp: n for n, cp in enumerate(self.cps)}

    def i(self, cp):
        return self.indices.get(cp)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    doc = build() if args.write else load()
    print(f"{len(doc['libraries'])} component libraries; {len(doc['families'])} non-heading source entries")
