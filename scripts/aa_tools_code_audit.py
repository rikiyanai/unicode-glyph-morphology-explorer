#!/usr/bin/env python3
"""Audit recovered AA tool code and exact operator combinations.

--fetch-orinrin saves pinned source/archive bytes only in
.run/aa_tools_source_audit/. Never builds/runs a Windows program.
--write owns windows_aa_code_audit.v1.json and windows-aa/code-audit/ source
copies beneath assets/glyphs/contextual/ only.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import struct
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".run/aa_tools_source_audit"
BASE = ROOT / "assets/glyphs/contextual"
OUTPUT = BASE / "windows_aa_code_audit.v1.json"
COMMIT = "f5dd6da43198eccbf58fbe2eec71ebe8c7fdb874"
AAJ_SHA = "891dc66d0fe134e0002c7cfb1e296dec407ccb0afb0253418d77741b33756fb5"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fetch_orinrin():
    url = f"https://codeload.github.com/SikigamiHNQ/OrinrinEditor/zip/{COMMIT}"
    with urllib.request.urlopen(url, timeout=25) as response:
        data = response.read(32 * 1024 * 1024 + 1)
    if len(data) > 32 * 1024 * 1024:
        raise ValueError("Unexpected source archive size")
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "orinrin-source.zip").write_bytes(data)
    records = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            relative = Path(*Path(item.filename).parts[1:])
            if relative.suffix.lower() not in {".cpp", ".h", ".rc", ".txt", ".sln", ".vcproj", ".vcxproj", ".ast", ".ini"} and relative.name not in {"COPYING", "LICENSE"}:
                continue
            raw_path = (WORK / "orinrin/raw" / relative).resolve()
            decoded_path = (WORK / "orinrin/utf8" / relative).resolve()
            if not raw_path.is_relative_to((WORK / "orinrin/raw").resolve()) or not decoded_path.is_relative_to((WORK / "orinrin/utf8").resolve()):
                raise ValueError("Unsafe source path")
            raw = archive.read(item)
            if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
                text, encoding = raw.decode("utf-16"), "utf-16 BOM"
            else:
                try:
                    text, encoding = raw.decode("utf-8-sig"), "utf-8-sig"
                except UnicodeDecodeError:
                    text, encoding = raw.decode("cp932"), "cp932"
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            decoded_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(raw)
            decoded_path.write_bytes(text.encode("utf-8"))
            records.append({"path": str(relative), "raw_sha256": digest(raw), "encoding": encoding,
                            "utf8_sha256": digest(text.encode("utf-8")), "lines": len(text.splitlines())})
    receipt = {"url": url, "commit": COMMIT, "archive_sha256": digest(data), "files": records,
               "execution": "source read only; no build or Windows program execution"}
    (WORK / "orinrin-source.v1.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(f"Pinned Orinrin source: {len(records)} files, {sum(r['lines'] for r in records)} lines; archive SHA256 {receipt['archive_sha256']}")


def stage_aaj(path):
    """Read the pinned PE as data; native objdump does not execute that PE."""
    data = path.read_bytes()
    if digest(data) != AAJ_SHA:
        raise ValueError("Wrong AAJ binary build")
    target = WORK / "aaj/aaj.exe"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    result = subprocess.run(["/usr/bin/objdump", "-d", str(target)], capture_output=True, check=True)
    (target.parent / "aaj.disasm.txt").write_bytes(result.stdout)
    for helper in path.parent.iterdir():
        if helper.suffix.lower() == ".html":
            raw = helper.read_bytes()
            (target.parent / "aaj-help.cp932.html").write_bytes(raw)
            (target.parent / "aaj-help.utf8.html").write_bytes(raw.decode("cp932").encode("utf-8"))
    (target.parent / "source.json").write_text(json.dumps({"original_path": str(path), "sha256": AAJ_SHA,
        "bytes": len(data), "execution": "none; native objdump reads PE data only"}, indent=2) + "\n")
    print("AAJ hash verified; static disassembly saved:", target.parent / "aaj.disasm.txt")


def inspect_aaj_constants():
    import windows_aa_intake as windows
    pe = windows.PinnedPE((WORK / "aaj/aaj.exe").read_bytes())
    for address in (0x450C68, 0x450D08, 0x450D48, 0x450D6C, 0x450D98):
        offset = pe.offset(address)
        length = struct.unpack_from("<I", pe.data, offset - 4)[0]
        data = pe.data[offset:offset + length]
        print(json.dumps({"address": hex(address), "length_header": length,
              "first_bytes": data[:16].hex(), "cp932": data.decode("cp932", errors="backslashreplace"),
              "utf16le": data[:len(data) // 2 * 2].decode("utf-16le", errors="backslashreplace")}, ensure_ascii=False))


def recover_aaj_alphabet():
    """Pinned static candidate builder, not a Windows converter emulation.

    403de4 is wide-string concatenation: it allocates len(dst)+len(src),
    copies both strings, and assigns the result. Its self-call at 4504af
    therefore DUPLICATES the alphabet; it does not deduplicate it.
    """
    import windows_aa_intake as windows
    pe = windows.PinnedPE((WORK / "aaj/aaj.exe").read_bytes())
    converter = windows.recover(pe.data)
    constants = []
    for address, encoding in ((0x450C68, "utf-16le"), (0x450D08, "cp932"),
                              (0x450D48, "cp932"), (0x450D6C, "cp932"),
                              (0x450D98, "utf-16le")):
        offset = pe.offset(address)
        length = struct.unpack_from("<I", pe.data, offset - 4)[0]
        raw = pe.data[offset:offset + length]
        constants.append({"va": hex(address), "file_offset": hex(offset), "encoding": encoding,
                          "byte_length": length, "bytes_hex": raw.hex(), "sha256": digest(raw),
                          "text": raw.decode(encoding)})
    proportional = "".join(r["text"] for r in constants[:4]) * 2
    mono = constants[4]["text"] * 2
    substitutions = {r["label"]: r["text"] for r in converter["builder_mappings"]}
    candidates = [{"label": c, "raster_text": substitutions.get(c, c)}
                  for c in dict.fromkeys(proportional)]
    import re
    start = 0x451B99
    code = pe.data[pe.offset(start):pe.offset(0x451EC0)]
    tone = []
    for match in re.finditer(b"\x8d\x45\xa8\xba(.{4})\xe8(.{4})", code, re.DOTALL):
        va = start + match.start()
        target = va + 13 + struct.unpack("<i", match[2])[0]
        if target != 0x40391C:
            raise ValueError("Unexpected direct-tone string consumer")
        address = struct.unpack("<I", match[1])[0]
        text = pe.string(address)
        raw = text.encode("cp932")
        tone.append({"instruction_va": hex(va), "text_va": hex(address), "text": text,
                     "bytes_hex": raw.hex(), "sha256": digest(raw),
                     "mode": "proportional" if va < 0x451D18 else "monospaced"})
    if len(tone) != 18:
        raise ValueError("Expected eighteen direct tone/blank branches")
    # Space-to-underscore output handling is conditional. Both characters are
    # already present; use an availability upper bound, not a sequence claim.
    output_chars = "".join(dict.fromkeys("".join(r["raster_text"] for r in candidates)
                          + "".join(r["text"] for r in tone if r["mode"] == "proportional")))
    disassembly = (WORK / "aaj/aaj.disasm.txt").read_text()
    ranges = ((0x403DD8, 0x403E43), (0x4503D8, 0x4504B4), (0x450583, 0x450599),
              (0x450622, 0x45065B), (0x450B16, 0x450B65), (0x45200F, 0x452153),
              (0x452321, 0x45235E), (0x452805, 0x452834))
    excerpts = []
    for line in disassembly.splitlines():
        match = re.match(r"\s*([0-9a-f]+):", line)
        if match and any(start <= int(match[1], 16) < stop for start, stop in ranges):
            excerpts.append(line)
    return {"executable_sha256": AAJ_SHA, "execution": "none; static PE bytes and native objdump only",
            "constants": constants, "proportional_internal_alphabet": proportional,
            "monospaced_internal_alphabet": mono,
            "self_concatenation_va": "0x4504af", "wide_concat_function_va": "0x403de4",
            "proportional_unique_candidates": candidates,
            "raster_style_bytes": {"first_half": pe.data[pe.offset(0x45124C)], "second_half": pe.data[pe.offset(0x450E70)]},
            "direct_tone_or_blank_outputs": tone,
            "proportional_output_characters_upper_bound": output_chars,
            "monospaced_output_characters_upper_bound": "".join(dict.fromkeys(mono
                  + "".join(r["text"] for r in tone if r["mode"] == "monospaced"))),
            "reachable_multichar_mapping_count": sum(len(r["text"]) > 1 and r["label"] in proportional
                                                       for r in converter["builder_mappings"]),
            "unreachable_builder_mappings": [r for r in converter["builder_mappings"] if r["label"] not in proportional],
            "disassembly_excerpts": excerpts,
            "limits": ["Availability excludes absent glyphs, but does not prove that every sequence of available glyphs can be emitted.",
                       "CP932 conversion assumes the Japanese codepage used by the bundled strings/manual.",
                       "Duplicated candidate labels are rasterized in two halves with different style-byte settings at 450b3a/450b5a; this is not an accidental duplicate-template claim.",
                       "Conditional blank handling and line endings are not a complete converter port."]}


def mapping_rows(justice, windows, mapping, aaj):
    """Per-fragment capability rows for every construction_tool_mapping record."""
    aaj_chars = set(aaj["proportional_output_characters_upper_bound"] + aaj["monospaced_output_characters_upper_bound"])
    candidate_chars = set(justice["candidate_characters"])
    composites = [item["text"] for item in windows["converter"]["multichar_templates"]]
    palette = [{"text": row, "group": group["name"], "line": group["line_start"] + offset}
               for group in windows["palette_groups"] for offset, row in enumerate(group["rows"]) if row.strip()]
    other_rows = []
    other_paths = []
    for file in windows["files"]:
        path = ROOT / file["text_path"]
        if path.suffix != ".ast":
            continue
        other_paths.append(path)
        title = None
        for line, text in enumerate(path.read_text().splitlines(), 1):
            if text.startswith("[AA]["):
                title = text
                continue
            if text.strip():
                other_rows.append({"path": file["text_path"], "line": line, "text": text,
                                   "item_header": title,
                                   "kind": "illustrated manual; not a preset" if "manual" in file["kind"] else "saved AST library"})
    rows = []
    for record in mapping["records"]:
        parts = record["fragments"]
        rows.append({"id": record["id"], "source_path": record["source_path"],
                     "fragments": [{"line": p["line"], "text": p["text"],
                         "justice_missing_characters": list(dict.fromkeys(c for c in p["text"] if c not in candidate_chars)),
                         "aaj_missing_characters_both_modes": list(dict.fromkeys(c for c in p["text"] if c not in aaj_chars)),
                         "aaj_equal_composite": p["text"] in composites,
                         "orinrin_other_saved_text_contains_fragment": [item for item in other_rows if p["text"] in item["text"]],
                         "orinrin_palette_contains_entire_fragment": [item for item in palette if p["text"] in item["text"]]}
                         for p in parts]})
    return rows, other_paths


def audit():
    justice = json.loads((BASE / "ascii_justice_recovery.v1.json").read_text())
    windows = json.loads((BASE / "windows_aa_patterns.v1.json").read_text())
    mapping = json.loads((BASE / "construction_tool_mapping.v1.json").read_text())
    aaj = recover_aaj_alphabet()
    rows, other_paths = mapping_rows(justice, windows, mapping, aaj)
    inputs = {}
    for path in (Path(__file__), ROOT / "scripts/windows_aa_intake.py", ROOT / "scripts/orinrin_brush.py",
                 BASE / "ascii_justice_recovery.v1.json", BASE / "windows_aa_patterns.v1.json",
                 BASE / "construction_tool_mapping.v1.json", *other_paths):
        inputs[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    receipt = json.loads((WORK / "orinrin-source.v1.json").read_text())
    if receipt["commit"] != COMMIT:
        raise ValueError("Wrong Orinrin source revision")
    originals = {r["path"]: r for r in receipt["files"]}
    selected = ("ViewKeyButton.cpp", "DocSelect.cpp", "MaaCatalogue.cpp", "MaaItems.cpp", "ViewCentral.cpp",
                "LayerBox.cpp", "MoziScript.cpp", "UnicodePalette.cpp", "OrinrinEditor.rc")
    retained = []
    destination = BASE / "windows-aa/code-audit"
    destination.mkdir(parents=True, exist_ok=True)
    aaj_path = destination / "aaj-candidate-alphabet.v1.json"
    aaj_path.write_text(json.dumps(aaj, ensure_ascii=False, indent=2) + "\n")
    help_raw = (WORK / "aaj/aaj-help.cp932.html").read_bytes()
    # Preserve original manual text without publishing a new HTML report.
    from html.parser import HTMLParser
    class ManualText(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
        def handle_data(self, text):
            self.parts.append(text)
    manual = ManualText()
    manual.feed(help_raw.decode("cp932"))
    manual_path = destination / "aaj-bundled-help.txt"
    manual_path.write_text("".join(manual.parts))
    for name in selected:
        raw = (WORK / "orinrin/raw" / name).read_bytes()
        decoded = (WORK / "orinrin/utf8" / name).read_bytes()
        record = originals[name]
        if digest(raw) != record["raw_sha256"] or digest(decoded) != record["utf8_sha256"]:
            raise ValueError(f"Changed source: {name}")
        (destination / (name + ".cp932")).write_bytes(raw)
        (destination / name).write_bytes(decoded)
        retained.append({**record, "path": str((destination / name).relative_to(ROOT)),
                         "raw_path": str((destination / (name + ".cp932")).relative_to(ROOT)),
                         "source_url": f"https://github.com/SikigamiHNQ/OrinrinEditor/blob/{COMMIT}/{name}"})
    doc = {"schema": "glyph_morphology.windows_aa_code_audit.v1", "input_hashes": inputs,
           "orinrin_source": {"commit": COMMIT, "archive_sha256": receipt["archive_sha256"],
                "source_file_count": len(receipt["files"]), "source_line_count": sum(r["lines"] for r in receipt["files"]),
                "source_version": "0.34.1.920", "saved_manual_version": "0.341 Aurora",
                "source_binary_parity": "Not built or compared with the saved executable", "retained_source_files": retained,
                "license_path": "assets/glyphs/contextual/windows-aa/upstream/COPYING", "license": "GPL-3.0-or-later"},
           "justice_candidate_count": len(justice["candidate_characters"]), "aaj_composite_count": len(composites),
           "aaj_alphabet": {"path": str(aaj_path.relative_to(ROOT)), "sha256": digest(aaj_path.read_bytes()),
                 "executable_sha256": AAJ_SHA, "reachable_multichar_mapping_count": aaj["reachable_multichar_mapping_count"],
                 "proportional_candidate_slots": len(aaj["proportional_internal_alphabet"]),
                 "monospaced_candidate_slots": len(aaj["monospaced_internal_alphabet"]),
                 "bundled_help_text_path": str(manual_path.relative_to(ROOT)),
                 "bundled_help_text_sha256": digest(manual_path.read_bytes()),
                 "original_cp932_help_sha256": digest(help_raw)},
           "orinrin_palette_group_count": len(windows["palette_groups"]), "records": rows,
           "limits": ["Literal character/fragment coverage is not production-workflow attribution.",
                      "AAJ full pinned alphabet is now audited separately from its forty-composite table.",
                      "A fragment in a palette does not prove the source artwork was made in that editor."]}
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    print(f"Audited {sum(len(r['fragments']) for r in rows)} exact source fragments in {len(rows)} constructions")


def refresh_records():
    """Recompute only the per-fragment records after construction_tool_mapping.v1.json changed,
    reusing the AAJ alphabet this audit already saved. Every other recorded input must be
    unchanged; otherwise a full --write (which needs the .run source work directory) is required."""
    doc = json.loads(OUTPUT.read_text())
    mapping_name = str((BASE / "construction_tool_mapping.v1.json").relative_to(ROOT))
    self_name = str(Path(__file__).resolve().relative_to(ROOT))
    for name, expected in doc["input_hashes"].items():
        if name not in (mapping_name, self_name) and digest((ROOT / name).read_bytes()) != expected:
            raise ValueError(f"{name} changed too; run the full --write audit")
    aaj_path = ROOT / doc["aaj_alphabet"]["path"]
    if digest(aaj_path.read_bytes()) != doc["aaj_alphabet"]["sha256"]:
        raise ValueError("saved AAJ alphabet changed; run the full --write audit")
    rows, _ = mapping_rows(json.loads((BASE / "ascii_justice_recovery.v1.json").read_text()),
                           json.loads((BASE / "windows_aa_patterns.v1.json").read_text()),
                           json.loads((BASE / mapping_name.split("/")[-1]).read_text()),
                           json.loads(aaj_path.read_text()))
    doc["records"] = rows
    doc["input_hashes"][mapping_name] = digest((BASE / "construction_tool_mapping.v1.json").read_bytes())
    doc["input_hashes"][self_name] = digest(Path(__file__).read_bytes())
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    return doc


def load():
    doc = json.loads(OUTPUT.read_text())
    if doc.get("schema") != "glyph_morphology.windows_aa_code_audit.v1":
        raise ValueError("Unsupported code audit")
    for name, expected in doc["input_hashes"].items():
        if digest((ROOT / name).read_bytes()) != expected:
            raise ValueError(f"Stale code audit: {name}; regenerate explicitly")
    aaj = doc["aaj_alphabet"]
    if digest((ROOT / aaj["path"]).read_bytes()) != aaj["sha256"]:
        raise ValueError("Changed packaged AAJ alphabet")
    return doc


def detail_lines(identity):
    """Packaged evidence only: the browser needs no executable or source cache."""
    doc = load()
    record = next((r for r in doc["records"] if r["id"] == identity), None)
    if record is None:
        return []
    lines = ["--- SOURCE-CODE CAPABILITY AUDIT ---",
             "AAJ full pinned alphabet + direct tone branches checked, not just its 40 combination mappings.",
             "39 of 40 multi-character mappings are reachable from this build's candidate alphabet; W -> ^^ has no W candidate.",
             "Missing glyphs rule out untouched automatic output from these builds, NOT later editing or another tool."]
    for part in record["fragments"]:
        missing = part["aaj_missing_characters_both_modes"]
        lines.append(f"row {part['line']} {part['text']!r}: " +
                     ("AAJ cannot directly emit: " + " ".join(missing) if missing else
                      "AAJ character availability only; no whole-passage reproduction established."))
        for item in part["orinrin_other_saved_text_contains_fragment"]:
            lines.append(f"Literal occurrence in {item['kind']}: {item['path']}:{item['line']} {item['item_header']}; not proof of whole-construction reuse.")
    lines.extend(["Orinrin's actual MLT/AST selection -> multi-row layer placement is implemented; its brush repeats the selected string, not a surface-following rule.",
                  "Audit data: assets/glyphs/contextual/windows_aa_code_audit.v1.json",
                  "Full alphabet/addresses: " + doc["aaj_alphabet"]["path"]])
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-orinrin", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--refresh-records", action="store_true",
                        help="recompute records after construction_tool_mapping.v1.json changed (no .run needed)")
    parser.add_argument("--stage-aaj", type=Path)
    parser.add_argument("--inspect-aaj-constants", action="store_true")
    args = parser.parse_args()
    if args.fetch_orinrin:
        fetch_orinrin()
    if args.stage_aaj:
        stage_aaj(args.stage_aaj)
    if args.inspect_aaj_constants:
        inspect_aaj_constants()
    if args.write:
        audit()
    if args.refresh_records:
        refresh_records()
