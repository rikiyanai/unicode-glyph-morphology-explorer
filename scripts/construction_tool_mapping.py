#!/usr/bin/env python3
"""Compare actual AAHub constructions with recovered tool vocabulary.

This is evidence annotation/string comparison, NOT a recovered converter.
--write owns construction_tool_mapping.v1.json only; viewing needs no local font.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/glyphs/contextual"
OUTPUT = BASE / "construction_tool_mapping.v1.json"
WINDOWS = BASE / "windows_aa_patterns.v1.json"
JUSTICE = BASE / "ascii_justice_recovery.v1.json"
FONT = Path("/Users/r/Library/Fonts/Saitamaar.ttf")
FONT_HASH = "592bf6be803ed76311841b95a10b20db3df0ec693a15f858757d47420b9b3a28"

# Exact source fragments and observed roles, not an assertion of artist intent.
# Row numbers are 1-based; substring positions below remain 0-based codepoints.
CASES = [
    ("operator-curve-crop-01", "operator-constructions/church-161.txt",
     "Godless Shrine: a cap using ｧ宀v and a lower 弋__人 return cooperate with an open gap; not an isolated round glyph.",
     [(11, "ｧ宀v", "upper cap"), (12, "弋__人", "lower return and meeting"), (13, "∧", "continuation below the opening")]),
    ("operator-curve-crop-03", "operator-constructions/church-036.txt",
     "Two-row opening: cap/shoulders above a lower return; the empty middle belongs to the construction.",
     [(7, "γ⌒ヽ", "upper cap and shoulders"), (8, "乂__ノ", "lower return and base")]),
    ("operator-curve-crop-06", "operator-constructions/church-073.txt",
     "A thick arch changes tangent and band articulation across rows; the foreground pillar interrupts it, not a join through the pillar.",
     [(8, "x≪ニ二ﾆ", "left shallow upper band"), (9, "／二-＞''~", "left turning band"),
      (10, "ｲ二㌃゜", "left shoulder"), (11, "ｲﾆア゜", "left steeper shoulder"),
      (12, "/ﾆｱ", "left steep band"), (13, "/ﾆ'′", "left near-vertical transition"),
      (8, "二二ﾆ≫ｘ", "right shallow upper band"), (9, "＜二≫,、", "right turning band"),
      (10, "くﾆ心、", "right shoulder"), (11, "寸ム", "right steeper shoulder"),
      (12, "寸ﾊ", "right steep band"), (13, "∨i,", "right near-vertical transition"),
      (14, "Ⅵｉ", "right near-vertical band"), (16, "|ﾆ", "right upright band")]),
    ("operator-curve-crop-02", "operator-constructions/church-165.txt",
     "Column-cap arc: a shallow central run turns into fuller end glyphs; do not classify every component as one isolated line.",
     [(9, "jI斗-─--ミ", "shallow cap with turning end constructions")]),
    ("operator-curve-crop-04", "operator-constructions/church-105.txt",
     "Paired lobes and central stem. This identical local motif occurs in church entries 105/106/107 and repeats within each; entry105 is representative context, not unique attribution.",
     [(6, "（(⌒Y⌒)）", "paired curved lobes with a central meeting"), (7, ")Ｉi(", "lower stem and side returns")]),
    ("operator-curve-crop-05", "operator-constructions/church-097.txt",
     "A rounded small head, torso cap, lower return and adjacent support form one local figure/ornament beside punctuation.",
     [(4, "(　)", "small upper round"), (5, "/⌒Ｙ", "larger rounded cap and meeting"),
      (6, "乂__ﾉ", "lower round return"), (7, "しく__", "lower continuation and support")]),
    ("operator-curve-crop-07", "operator-constructions/church-057.txt",
     "Kraków St Mary's: a small upper round and a larger lower cap/return stay aligned as a stacked construction.",
     [(12, "(__)", "small round above"), (13, "γ⌒ヽ", "larger lower cap"), (14, "乂__ソ", "lower return")]),
    ("operator-curve-crop-08", "operator-constructions/church-057.txt",
     "Kraków St Mary's: upper cap, tall sides and lower returns; inspect the lower neighboring round in the full passage, not one isolated character.",
     [(9, "γ⌒ヽ", "upper cap"), (10, "{　　　}", "tall paired sides and protected paper"), (11, "乂__乂", "paired lower returns")]),
    ("aramaki-cup-plate-surface-following-tone", "aramaki-cup-plate-176.txt",
     "Sparse punctuation and fuller directional glyphs cooperate: a rim, side tone bands and lower returns, not independent uniform-density fill.",
     [(7, "ヾ<:;_", "left rim return"), (7, "_,.ン", "right rim return"),
      (8, "...:;:彡", "side band combines dots and directional strokes"),
      (9, "...::::;:;;;;;彡", "denser side band"),
      (13, ":;:=:彳", "lower side turn"), (14, "....::::;;;ジ", "lower return")]),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def occurrences(text, needle):
    return [i for i in range(len(text) - len(needle) + 1) if text.startswith(needle, i)]


def overlaps(fragment, candidates):
    """Maximal exact shared substrings >=2, with both original source locators.

    A substring overlap is explicitly not whole-construction equivalence.
    Never normalize full/half width, whitespace, punctuation or Unicode.
    """
    result = []
    for candidate in candidates:
        text = candidate["text"]
        shared = {fragment[a:b] for a in range(len(fragment))
                  for b in range(a + 2, len(fragment) + 1) if fragment[a:b] in text}
        for part in sorted(shared, key=lambda s: (-len(s), s)):
            if any(part != other and part in other for other in shared):
                continue
            result.append({**candidate, "shared_text": part,
                           "fragment_offsets": occurrences(fragment, part),
                           "candidate_offsets": occurrences(text, part),
                           "covers_entire_fragment": part == fragment,
                           "equals_entire_candidate": part == text})
    return result


def build():
    from PIL import ImageFont
    from fontTools.ttLib import TTFont
    if digest(FONT) != FONT_HASH:
        raise ValueError("Use the pinned Saitamaar comparison font")
    font = ImageFont.truetype(str(FONT), 16)
    with TTFont(FONT) as tt:
        available = set(tt.getBestCmap())
    windows = json.loads(WINDOWS.read_text(encoding="utf-8"))
    justice_chars = {g["char"] for g in json.loads(JUSTICE.read_text(encoding="utf-8"))["glyphs"][:93]}
    palette = [{"text": row, "group": group["name"], "line": group["line_start"] + offset,
                "path": "assets/glyphs/contextual/windows-aa/aalist.txt"}
               for group in windows["palette_groups"] for offset, row in enumerate(group["rows"])
               if row.strip() and not row.startswith("**")]
    aaj = [{"text": row["text"], "builder_va": row["instruction_va"], "number": n}
           for n, row in enumerate(windows["converter"]["multichar_templates"], 1)]
    brush_file = next(f for f in windows["files"] if f["text_path"].endswith("/aabrush.txt"))
    brush = [{"text": row, "line": n, "path": brush_file["text_path"]}
             for n, row in enumerate(brush_file["rows"], 1) if row and not row.startswith("[")]
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (WINDOWS, JUSTICE, Path(__file__), BASE / "windows-aa/aalist.txt", BASE / "windows-aa/aabrush.txt")}
    records = []
    for identity, source, reading, fragments in CASES:
        path = BASE / source
        inputs[str(path.relative_to(ROOT))] = digest(path)
        rows = path.read_text(encoding="utf-8").splitlines()
        parts = []
        for line, text, role in fragments:
            row = rows[line - 1]
            missing = sorted({ord(ch) for ch in row if ord(ch) not in available})
            if missing:
                raise ValueError(f"Characters absent from pinned font: {missing}")
            starts = occurrences(row, text)
            if not starts:
                raise ValueError(f"Absent source fragment {identity}:{line}:{text!r}")
            start = starts[0]
            x = sum(font.getlength(ch) for ch in row[:start])
            placements = []
            for offset, char in enumerate(text):
                advance = float(font.getlength(char))
                placements.append({"char": char, "codepoint": f"U+{ord(char):04X}",
                                   "source_codepoint": start + offset, "x_px": x, "advance_px": advance})
                x += advance
            parts.append({"line": line, "text": text, "source_codepoint_start": start,
                          "source_codepoint_starts": starts,
                          "placement_status": "unique text occurrence" if len(starts) == 1 else "repeated motif; all codepoint starts retained; displayed positions represent first occurrence only",
                          "role": role, "placements": placements,
                          "palette_overlaps": overlaps(text, palette), "aaj_overlaps": overlaps(text, aaj),
                          "brush_items_inside_fragment": [item for item in brush if item["text"] in text],
                          "ascii_justice_unavailable_characters": list(dict.fromkeys(ch for ch in text if ch not in justice_chars))})
        records.append({"id": identity, "source_path": str(path.relative_to(ROOT)), "reading": reading, "fragments": parts})
    doc = {"schema": "glyph_morphology.construction_tool_mapping.v1", "input_hashes": inputs,
           "font": {"sha256": FONT_HASH, "name": "Saitamaar", "px": 16, "row_pitch_px": 17},
           "limit": "Exact text overlaps and annotated construction roles, NOT recovered converter output or artist/tool attribution. AAJ comparison covers its 40 recovered composite candidates, NOT its complete character vocabulary or every sequence it could emit. Absence of a whole preset does not rule out assembly by successive selections. Positions are Saitamaar comparisons, not measurements of the screenshot font. No glyph stretching.",
           "records": records}
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def load():
    doc = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if doc.get("schema") != "glyph_morphology.construction_tool_mapping.v1":
        raise ValueError("Unsupported construction mapping")
    for name, expected in doc["input_hashes"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"Stale construction mapping: {name}; regenerate explicitly")
    return doc


def attach(records):
    """Copy records, retaining all existing source/image evidence unchanged."""
    mapping = load()
    by_id = {r["id"]: r for r in mapping["records"]}
    return [{**r, "tool_mapping": {**by_id[r["id"]], "limit": mapping["limit"]}}
            if r["id"] in by_id else r for r in records]


def detail_lines(mapping):
    lines = ["--- CONSTRUCTION / TOOL COMPARISON ---", mapping["reading"], mapping["limit"]]
    for part in mapping["fragments"]:
        lines.append(f"row {part['line']}: {part['text']} — {part['role']}")
        if len(part["source_codepoint_starts"]) > 1:
            lines.append(f"{part['placement_status']}: {part['source_codepoint_starts']}")
        lines.append("Saitamaar positions: " + "; ".join(f"{p['char']}@{p['x_px']:g}px +{p['advance_px']:g}" for p in part["placements"]))
        for key, label in (("palette_overlaps", "Orinrin palette"), ("aaj_overlaps", "AAJ candidate")):
            matches = part[key]
            if not matches:
                lines.append(f"{label}: no shared substring >=2 codepoints for this fragment.")
            grouped = {}
            for match in matches:
                grouped.setdefault(match["shared_text"], []).append(match)
            for shared, group in grouped.items():
                # Keep every locator in JSON; group repeated trivial overlaps in
                # the pane so punctuation does not bury the construction.
                match = sorted(group, key=lambda m: (not m["equals_entire_candidate"], len(m["text"])))[0]
                where = f"row {match['line']} {match['group']}" if "group" in match else f"#{match['number']:02} @ {match['builder_va']}"
                kind = "entire fragment occurs" if match["covers_entire_fragment"] else "PARTIAL substring only"
                lines.append(f"{label} {where}: {shared!r}; {kind}; saved item {match['text']!r}; {len(group)} saved row/candidate matches (all locators in JSON).")
        items = list(dict.fromkeys(m["text"] for m in part["brush_items_inside_fragment"]))
        if items:
            lines.append("Orinrin brush items present (not an arrangement rule): " + " / ".join(repr(s) for s in items))
        if part["ascii_justice_unavailable_characters"]:
            lines.append("ASCII Justice cannot directly emit: " + " ".join(part["ascii_justice_unavailable_characters"]))
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    doc = build() if args.write else load()
    for record in doc["records"]:
        print(record["id"], len(record["fragments"]), "source fragments")
