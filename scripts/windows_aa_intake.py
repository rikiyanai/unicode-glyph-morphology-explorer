#!/usr/bin/env python3
"""Statically recover saved AAJ motifs and Orinrin templates; never run a PE.

--write owns only windows-aa/, windows_aa_patterns.v1.json, three summary records
and 24 palette-group records in shallot_native_contexts.v1.json. Default is read-only.
The PE recognizer is intentionally pinned to this one executable, not a decompiler.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/glyphs/contextual"
OUTPUT = BASE / "windows_aa_patterns.v1.json"
FILES = BASE / "windows-aa"
CONTEXT = BASE / "shallot_native_contexts.v1.json"
SAVED = Path("/Users/r/Desktop/shift_jis_research/inspection-20261015")
AAJ_HASH = "891dc66d0fe134e0002c7cfb1e296dec407ccb0afb0253418d77741b33756fb5"
IDS = {"aa-judgment-composite-matching-templates", "orinrin-brush-presets", "orinrin-multiline-insertions"}
PALETTE_IDS = {f"orinrin-palette-{number:02}" for number in range(1, 25)}
UPSTREAM_COMMIT = "f5dd6da43198eccbf58fbe2eec71ebe8c7fdb874"
SOURCE_INDEX = BASE / "windows_aa_source.v1.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PinnedPE:
    def __init__(self, data: bytes):
        if sha(data) != AAJ_HASH:
            raise ValueError("Unrecognized executable; do not infer mappings from another build")
        self.data = data
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\0\0":
            raise ValueError("Not a PE")
        count = struct.unpack_from("<H", data, pe + 6)[0]
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        self.base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
        start = pe + 24 + optional_size
        self.sections = [struct.unpack_from("<IIII", data, start + i * 40 + 8) for i in range(count)]

    def offset(self, va: int) -> int:
        rva = va - self.base
        for virtual_size, virtual_address, raw_size, raw_offset in self.sections:
            if virtual_address <= rva < virtual_address + min(virtual_size, raw_size):
                return raw_offset + rva - virtual_address
        raise ValueError(f"Unbacked VA {va:#x}")

    def string(self, va: int) -> str:
        offset = self.offset(va)
        size = struct.unpack_from("<I", self.data, offset - 4)[0]
        if not 1 <= size <= 16 or self.data[offset + size] != 0:
            raise ValueError("Not a bounded Delphi AnsiString")
        return self.data[offset:offset + size].decode("cp932")

    def mappings(self, start: int, stop: int, slot: bytes) -> list[dict]:
        # mov eax,[ebp+slot]; mov edx,label; call compare; jne +13;
        # lea eax,[ebp+slot]; mov edx,replacement; call assign.
        pattern = (b"\x8b\x45" + slot + b"\xba(.{4})\xe8(.{4})\x75\x0d"
                   + b"\x8d\x45" + slot + b"\xba(.{4})\xe8(.{4})")
        offset = self.offset(start)
        code = self.data[offset:self.offset(stop)]
        found = []
        for match in re.finditer(pattern, code, re.DOTALL):
            va = start + match.start()
            compare = va + 13 + struct.unpack("<i", match[2])[0]
            assign = va + 28 + struct.unpack("<i", match[4])[0]
            if (compare, assign) != (0x403A24, 0x403730):
                raise ValueError("Unexpected call targets")
            label_va, text_va = (struct.unpack("<I", match[i])[0] for i in (1, 3))
            text = self.string(text_va)
            found.append({"label": self.string(label_va), "text": text,
                          "codepoints": [f"U+{ord(ch):04X}" for ch in text],
                          "instruction_va": hex(va), "text_va": hex(text_va)})
        return found


def recover(data: bytes) -> dict:
    pe = PinnedPE(data)
    builder = pe.mappings(0x45065B, 0x450AD7, b"\xf0")
    output = pe.mappings(0x45235E, 0x452805, b"\x9c")
    pairs = lambda rows: [(r["label"], r["text"]) for r in rows]
    if len(builder) != 41 or pairs(builder) != pairs(output[:41]):
        raise ValueError(f"Builder/output mismatch: {len(builder)}/{len(output)}")
    motifs = [r for r in builder if len(r["text"]) > 1]
    if len(motifs) != 40:
        raise ValueError("Expected forty multi-character motifs")
    return {"executable_sha256": AAJ_HASH, "execution": "none; static PE bytes only",
            "builder_mappings": builder, "output_mappings": output,
            "multichar_templates": motifs,
            "limit": "Local image-matching candidates, not AAHub artist presets or an architectural grammar."}


def palette_groups(rows: list[str]) -> list[dict]:
    """Retain grouped source rows, including blank-separated construction samples.

    The C++ insertion parser splits nonempty rows. Source adjacency does not
    imply that a complete multi-row sample is inserted by one click.
    """
    groups = []
    active = None
    for index, row in enumerate(rows, 1):
        if row.startswith("[ListName=") and row.endswith("]"):
            if active is not None:
                raise ValueError("Unclosed palette group")
            active = {"name": row[len("[ListName="):-1], "line_start": index + 1, "rows": []}
        elif row == "[end]":
            if active is None:
                raise ValueError("Unexpected palette group terminator")
            active["line_end"] = index - 1
            groups.append(active)
            active = None
        elif active is not None:
            active["rows"].append(row)
    if active is not None or len(groups) != 24:
        raise ValueError("Expected all 24 closed Orinrin palette groups")
    return groups


def build(saved: Path) -> dict:
    converter = recover((saved / "aaj/aaj.exe").read_bytes())
    FILES.mkdir(parents=True, exist_ok=True)
    orin = saved / "orinrin/OrinrinEditor"
    selected = [(orin / "Templates" / name, name) for name in
                ("aabrush.txt", "aalist.txt", "UserItem.ast")]
    # Three lettering libraries plus the bundled illustrated manual; filenames
    # in this old extraction are mojibake. Do not count the manual as a preset.
    libraries = sorted(orin.glob("*.ast"))
    selected += [(path, f"lettering-{i + 1}.ast") for i, path in enumerate(libraries)]
    selected += [(orin / "readme.txt", "orinrin-readme.txt"),
                 (saved / "ascii-justice/aj_14.txt", "ascii-justice-readme.txt")]
    records = []
    for source, name in selected:
        raw = source.read_bytes()
        text = raw.decode("cp932")
        raw_path = FILES / (name + ".cp932")
        decoded_path = FILES / name
        raw_path.write_bytes(raw)
        decoded_path.write_bytes(text.encode("utf-8"))
        records.append({"source_path": str(source), "raw_path": str(raw_path.relative_to(ROOT)),
                        "raw_sha256": sha(raw), "text_path": str(decoded_path.relative_to(ROOT)),
                        "text_sha256": sha(text.encode("utf-8")),
                        "decoding": "CP932, strict; original line endings retained",
                        "kind": ("illustrated manual, not a lettering preset" if text.count("[AA][") == 36
                                 else "bundled text/template; inspect its headings"),
                        "template_tags": text.count("[AA]["), "rows": text.splitlines()})
    palette = next(r for r in records if r["text_path"].endswith("/aalist.txt"))
    groups = palette_groups(palette["rows"])
    doc = {"schema": "glyph_morphology.windows_aa_patterns.v1", "converter": converter,
           "palette_groups": groups,
           "files": records, "scope": "Saved Windows packages inspected statically; no execution, font rendering, or screenshot attribution."}
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contexts = json.loads(CONTEXT.read_text(encoding="utf-8"))
    contexts["families"] = [r for r in contexts["families"] if r["id"] not in IDS | PALETTE_IDS]
    def context(id, title, forms, passages, provenance):
        return {"id": id, "title": title, "pattern_family": "windows-editor-presets-not-aahub-attribution",
                "focus_forms": forms, "provenance": {"source_id": id, "paired_native_png": None,
                    "native_image_status": "Exact text evidence only; terminal text is not native-font fit evidence.",
                    "annotation_status": "static inspection, not operator artwork approval", **provenance},
                "passages": passages, "interpretation": {
                    "observed_visual": "No Windows output or native-font rendering was observed in this intake.",
                    "drawn_analogy": "Compare whole short sequences and insertion layouts, not isolated glyph names.",
                    "mathematical_family": "Not assigned; these are templates, not geometric line detectors.",
                    "historical_implementation_limit": "No evidence these tools made the supplied AAHub drawings; no motion or renderer validation."}}
    motifs = converter["multichar_templates"]
    contexts["families"].append(context("aa-judgment-composite-matching-templates",
        "AA Judgment: all 40 recovered composite matching candidates", [r["text"] for r in motifs],
        [{"id": "aaj-40", "line_start": 1, "rows": [r["text"] for r in motifs]}],
        {"executable_sha256": AAJ_HASH, "pattern_index": str(OUTPUT.relative_to(ROOT)),
         "evidence": "41 builder mappings agree with first 41 output mappings; includes one separate ideographic space."}))
    brushes = next(r for r in records if r["text_path"].endswith("/aabrush.txt"))
    items = next(r for r in records if r["text_path"].endswith("/UserItem.ast"))
    for id, title, record, forms in [
        ("orinrin-brush-presets", "Orinrin: exact brush groups, including spaces", brushes, [".,", ".;", ":;", ";:", "l|", "i!", "!i", "彡", "ミ"]),
        ("orinrin-multiline-insertions", "Orinrin: bundled multiline insertion templates (not scene motifs)", items, ["┏━━━━━┓", "…━…"]),
    ]:
        contexts["families"].append(context(id, title, forms,
            [{"id": id + "-rows", "line_start": 1, "rows": record["rows"]}],
            {k: record[k] for k in ("source_path", "raw_path", "raw_sha256", "text_path", "text_sha256")}))
    for number, group in enumerate(groups, 1):
        id = f"orinrin-palette-{number:02}"
        forms = [row.strip() for row in group["rows"] if row.strip() and not row.startswith("**")]
        # Focus is a navigation aid; the complete untrimmed source remains below.
        focus = list(dict.fromkeys([row for row in forms if len(row) > 1][:8] or forms[:8]))
        record = context(id, f"Orinrin palette {group['name']} — complete original rows", focus,
            [{"id": id + "-source-rows", "line_start": group["line_start"], "rows": group["rows"]}],
            {**{k: palette[k] for k in ("source_path", "raw_path", "raw_sha256", "text_path", "text_sha256")},
             "context_limit": "Original palette grouping and row adjacency, including multi-character and multi-row samples. The C++ insertion parser handles individual nonempty lines; this is NOT evidence of an atomic multi-row macro or automatic tracing."})
        record["pattern_family"] = "orinrin-grouped-palette-and-construction-samples"
        contexts["families"].append(record)
    CONTEXT.write_text(json.dumps(contexts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def fetch_source() -> dict:
    """Fetch only pinned source text and its license; never compile or run it."""
    target = FILES / "upstream"
    target.mkdir(parents=True, exist_ok=True)
    records = []
    for name in ("TraceCtrl.cpp", "BrushTemplate.cpp", "LineTemplate.cpp", "DocAdjustant.cpp"):
        url = f"https://raw.githubusercontent.com/SikigamiHNQ/OrinrinEditor/{UPSTREAM_COMMIT}/{name}"
        with urllib.request.urlopen(url, timeout=20) as response:
            raw = response.read()
        decoded = raw.decode("cp932").encode("utf-8")
        original = target / (name + ".cp932")
        text = target / name
        original.write_bytes(raw)
        text.write_bytes(decoded)
        records.append({"url": url, "raw_path": str(original.relative_to(ROOT)), "raw_sha256": sha(raw),
                        "text_path": str(text.relative_to(ROOT)), "text_sha256": sha(decoded),
                        "decoding": "strict CP932 to UTF-8; line endings preserved"})
    license_url = "https://www.gnu.org/licenses/gpl-3.0.txt"
    with urllib.request.urlopen(license_url, timeout=20) as response:
        license_bytes = response.read()
    license_path = target / "COPYING"
    license_path.write_bytes(license_bytes)
    doc = {"schema": "glyph_morphology.windows_aa_source.v1", "repository": "https://github.com/SikigamiHNQ/OrinrinEditor",
           "commit": UPSTREAM_COMMIT, "license": "GPL-3.0-or-later, per source headers",
           "license_url": license_url, "license_path": str(license_path.relative_to(ROOT)),
           "license_sha256": sha(license_bytes), "files": records,
           "limit": "Source inspection only; source/binary reproducibility not established."}
    SOURCE_INDEX.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def load() -> dict:
    doc = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if doc["schema"] != "glyph_morphology.windows_aa_patterns.v1":
        raise ValueError("Unknown schema")
    for record in doc["files"]:
        for key, digest in (("raw_path", "raw_sha256"), ("text_path", "text_sha256")):
            path = (ROOT / record[key]).resolve()
            if not path.is_relative_to(FILES.resolve()) or sha(path.read_bytes()) != record[digest]:
                raise ValueError(f"Changed template evidence: {record[key]}")
    return doc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fetch-source", action="store_true", help="fetch four pinned upstream source files and GPL text")
    parser.add_argument("--saved", type=Path, default=SAVED)
    args = parser.parse_args()
    if args.fetch_source:
        source = fetch_source()
        print("Saved", len(source["files"]), "source files at", source["commit"])
        raise SystemExit(0)
    doc = build(args.saved) if args.write else load()
    print("AA Judgment:", len(doc["converter"]["multichar_templates"]), "composite candidates")
    print(" / ".join(r["text"] for r in doc["converter"]["multichar_templates"]))
    for record in doc["files"]:
        print(record["text_path"], len(record["rows"]), "rows;", record["template_tags"], "AA tags")
