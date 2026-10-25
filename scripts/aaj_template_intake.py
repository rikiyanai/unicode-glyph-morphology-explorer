#!/usr/bin/env python3
"""Package all recovered AAJ combinations as individual native-font previews.

--write owns aaj_templates.native.v1.json only. Saitamaar previews are explicitly
not recovered Windows/MS Gothic output. The original template text is unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import saitamaar_pattern_intake as patterns
import windows_aa_intake as windows

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/glyphs/contextual/aaj_templates.native.v1.json"
FONT = Path("/Users/r/Library/Fonts/Saitamaar.ttf")
FONT_HASH = "592bf6be803ed76311841b95a10b20db3df0ec693a15f858757d47420b9b3a28"
PROFILE = {"font": "Saitamaar", "px": 16, "row_pitch_px": 17,
           "padding_right_px": 8, "anchor": "la", "ink_threshold_lt": 128}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(font_path=FONT):
    from fontTools.ttLib import TTFont
    from PIL import ImageFont

    source = windows.load()
    if digest(font_path) != FONT_HASH:
        raise ValueError("Use the pinned Saitamaar font, not a substitute")
    motifs = source["converter"]["multichar_templates"]
    with TTFont(font_path) as font_file:
        available = font_file.getBestCmap()
        missing = {ord(ch) for motif in motifs for ch in motif["text"] if ord(ch) not in available}
    if missing:
        raise ValueError(f"Missing font characters: {missing}")
    font = ImageFont.truetype(str(font_path), PROFILE["px"])
    families = []
    for number, motif in enumerate(motifs, 1):
        text = motif["text"]
        x = 0.0
        placements = []
        for ch in text:
            advance = float(font.getlength(ch))
            placements.append({"char": ch, "x_px": x, "advance_px": advance})
            x += advance
        families.append({"id": f"aaj-template-{number:02}", "title": f"AA Judgment {number:02}/40: {text}",
            "pattern_family": "recovered-converter-composite-template", "focus_forms": [text],
            "provenance": {"source_id": "aa-judgment-3.0", "executable_sha256": windows.AAJ_HASH,
                "internal_label": motif["label"], "builder_instruction_va": motif["instruction_va"],
                "text_va": motif["text_va"], "font_sha256": FONT_HASH},
            "converter_template": {"text": text, "codepoints": motif["codepoints"],
                "raster_rows": patterns.native_rows([text], font, PROFILE),
                "placements": placements, "advance_px": x, "profile": PROFILE,
                "limit": "Saitamaar comparison rendering, NOT the original Windows/MS Gothic template bitmap. No glyph deformation, semantic admission or motion evidence."}})
    doc = {"schema": "glyph_morphology.aaj_templates.native.v1", "input_sha256": digest(windows.OUTPUT),
           "generator_sha256": digest(__file__), "font_sha256": FONT_HASH, "families": families}
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def load():
    doc = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if (doc.get("schema") != "glyph_morphology.aaj_templates.native.v1"
            or doc["input_sha256"] != digest(windows.OUTPUT)
            or doc["generator_sha256"] != digest(__file__)):
        raise ValueError("AAJ native template snapshot stale; regenerate explicitly")
    motifs = windows.load()["converter"]["multichar_templates"]
    if [f["converter_template"]["text"] for f in doc["families"]] != [m["text"] for m in motifs]:
        raise ValueError("AAJ preview coverage/order differs from recovered combinations")
    return doc


class TemplateCorpus:
    def __init__(self, doc):
        self.cps = sorted({ord(ch) for f in doc["families"] for ch in f["converter_template"]["text"]})
        self.indices = {cp: i for i, cp in enumerate(self.cps)}

    def i(self, cp):
        return self.indices.get(cp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--font", type=Path, default=FONT)
    args = parser.parse_args()
    doc = build(args.font) if args.write else load()
    print(len(doc["families"]), "individually selectable AA Judgment composite previews")
