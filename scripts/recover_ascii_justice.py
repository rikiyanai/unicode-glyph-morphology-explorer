#!/usr/bin/env python3
"""Static ASCII Justice recovery workspace; never execute its Windows PE.

--fetch-tool downloads pinned deHSP source into .run/aa_algorithm_recovery/dehsp.
Only reviewed native .NET tooling will be built there; the target PE is data.
"""
import argparse
import hashlib
import io
import json
import os
import re
import struct
import subprocess
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".run/aa_algorithm_recovery"
TOOL_COMMIT = "491d12d935758a7563b6588b934247536f185b44"
TARGET = Path("/Users/r/Desktop/shift_jis_research/inspection-20261015/ascii-justice/aj_14.exe")
TARGET_HASH = "e640f35c4ff70506e2db76d2c6bcf83e8670277fd53ad3319f4f50b9a5dc4ac7"
OUTPUT = ROOT / "assets/glyphs/contextual/windows-aa/ascii-justice"
INDEX = ROOT / "assets/glyphs/contextual/ascii_justice_recovery.v1.json"


def fetch_tool():
    url = f"https://codeload.github.com/xsyetopz/deHSP/zip/{TOOL_COMMIT}"
    with urllib.request.urlopen(url, timeout=20) as response:
        data = response.read()
    destination = WORK / "dehsp"
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            relative = Path(*Path(member.filename).parts[1:])
            path = (destination / relative).resolve()
            if not path.is_relative_to(destination.resolve()):
                raise ValueError("Unsafe archive path")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.read(member))
    (WORK / "tool-download.json").write_text(json.dumps({"url": url, "commit": TOOL_COMMIT,
        "archive_sha256": hashlib.sha256(data).hexdigest()}, indent=2) + "\n")
    print("Downloaded source only:", destination)


def inspect_target():
    data = TARGET.read_bytes()
    if hashlib.sha256(data).hexdigest() != TARGET_HASH:
        raise ValueError("Unexpected ASCII Justice executable build")
    for magic in (b"DPMX", b"HSP2", b"HSP3", b"start.ax"):
        positions = []
        at = data.find(magic)
        while at >= 0:
            positions.append(hex(at))
            at = data.find(magic, at + 1)
        print(magic.decode(), positions)


def prepare_input():
    data = TARGET.read_bytes()
    if hashlib.sha256(data).hexdigest() != TARGET_HASH:
        raise ValueError("Unexpected ASCII Justice executable build")
    path = WORK / "input/aj_14.exe"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print("Static decompiler input copy:", path)


def decompile():
    """Build the reviewed native CLI and treat the copied target as file data."""
    if not (WORK / "dehsp/src/HspDecompiler.Cli/HspDecompiler.Cli.csproj").exists():
        raise ValueError("Fetch the pinned tool source explicitly with --fetch-tool first")
    prepare_input()
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1",
               DOTNET_GENERATE_ASPNET_CERTIFICATE="false", DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1",
               DOTNET_CLI_HOME=str(WORK / "dotnet-home"), NUGET_PACKAGES=str(WORK / "nuget"),
               DOTNET_ROLL_FORWARD="Major")
    subprocess.run(["dotnet", "build", str(WORK / "dehsp/src/HspDecompiler.Cli/HspDecompiler.Cli.csproj"),
                    "--artifacts-path", str(WORK / "build"), "-p:AnalysisLevel=8.0", "--verbosity", "quiet"],
                   cwd=ROOT, env=env, check=True)
    subprocess.run(["dotnet", str(WORK / "build/bin/HspDecompiler.Cli/debug/dehsp.dll"),
                    str(WORK / "input/aj_14.exe"), "-o", str(WORK / "output"), "--no-decrypt", "--verbose"],
                   cwd=ROOT, env=env, check=True)
    # The upstream EXE handler auto-increments its extraction directory on
    # repeated runs. Locate the new source-bearing extraction, not an old output.
    candidates = [p for p in (WORK / "input").iterdir()
                  if p.is_dir() and (p / "start.as").exists()]
    if not candidates:
        raise ValueError("Decompiler produced no source-bearing extraction")
    return max(candidates, key=lambda p: (p / "start.as").stat().st_mtime_ns)


def intake_recovery(extracted=None):
    extracted = extracted or WORK / "input/aj_14"
    original = TARGET.read_bytes()
    if hashlib.sha256(original).hexdigest() != TARGET_HASH:
        raise ValueError("Unexpected ASCII Justice executable build")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for name in ("start.ax", "mjdata14.dat", "mjnodo14.dat", "hlpmes14.txt"):
        data = (extracted / name).read_bytes()
        at = original.find(data)
        if at < 0:
            raise ValueError(f"Extracted payload is not present byte-for-byte in executable: {name}")
        record = {"name": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                  "offset_in_executable": hex(at)}
        if name.endswith(".dat"):
            path = OUTPUT / name
            path.write_bytes(data)
            record["path"] = str(path.relative_to(ROOT))
        artifacts.append(record)
    raw = (extracted / "start.as").read_bytes()
    text = raw.decode("cp932")
    raw_path, text_path = OUTPUT / "start.as.cp932", OUTPUT / "start.as"
    raw_path.write_bytes(raw)
    text_path.write_bytes(text.encode("utf-8"))
    literal = re.search(r'^\s*var_28 = (".*")$', text, re.MULTILINE)
    if not literal:
        raise ValueError("Cannot identify candidate-character string")
    chars = json.loads(literal[1])
    mask_bytes = (extracted / "mjdata14.dat").read_bytes()
    masks = struct.unpack("<12288i", mask_bytes)
    densities = struct.unpack("<96i", (extracted / "mjnodo14.dat").read_bytes())
    if set(masks) != {0, 1} or len(chars) != 93:
        raise ValueError(f"Unexpected mask values or character count: {set(masks)}, {len(chars)}")
    glyphs = []
    for i in range(96):
        rows = ["".join("#" if masks[i + 96 * x + 96 * 8 * y] == 0 else "." for x in range(8))
                for y in range(16)]
        glyphs.append({"index": i, "char": chars[i] if i < len(chars) else None,
                       "raster_rows": rows, "ink_px": sum(row.count("#") for row in rows),
                       "density_value": densities[i]})
    lines = text.splitlines()
    headings = [(i + 1, row.strip()) for i, row in enumerate(lines) if re.fullmatch(r"\*label_\d+", row.strip())]
    labels = [{"name": title, "line_start": start,
               "line_end": headings[i + 1][0] - 1 if i + 1 < len(headings) else len(lines)}
              for i, (start, title) in enumerate(headings)]
    tool = json.loads((WORK / "tool-download.json").read_text())
    doc = {"schema": "glyph_morphology.ascii_justice_recovery.v1", "executable_sha256": TARGET_HASH,
           "method": "deHSP native .NET static HSP2 decompilation; Windows target never executed",
           "tool": tool, "build": "SDK 10.0.101; AnalysisLevel=8.0; .NET runtime roll-forward Major; source unmodified",
           "embedded_payloads": artifacts, "raw_source_path": str(raw_path.relative_to(ROOT)),
           "raw_source_sha256": hashlib.sha256(raw).hexdigest(), "source_path": str(text_path.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
           "source_lines": len(lines), "labels": labels, "candidate_characters": chars, "glyphs": glyphs,
           "limits": ["Decompiler-generated labels/variables are not original names.",
                      "Two negative-value clamp lines contain malformed decompiler output; do not execute this listing or claim full source equivalence.",
                      "Original Windows rendering, HSP expression evaluation, plugin sort/tie behavior and whole-converter output parity are not validated.",
                      "Raster-table ordering is first index fastest; masks use 0=ink, 1=paper. Three trailing table slots are not in the 93-character map."]}
    INDEX.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Recovered", len(lines), "source lines;", len(chars), "mapped 8x16 masks")
    print("First 8 density/table ink pairs:", [(r["char"], r["density_value"], r["ink_px"]) for r in glyphs[:8]])
    return doc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-tool", action="store_true")
    parser.add_argument("--prepare-input", action="store_true")
    parser.add_argument("--intake", action="store_true")
    parser.add_argument("--decompile", action="store_true", help="build/run native deHSP CLI; target PE remains data")
    args = parser.parse_args()
    if args.fetch_tool:
        fetch_tool()
    if args.prepare_input:
        prepare_input()
    extracted = decompile() if args.decompile else None
    if args.intake:
        intake_recovery(extracted)
    inspect_target()
