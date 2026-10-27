"""Validate role_lookup entry files: JSON schema, roles, ids, and source fidelity.

For every entry the native rows are re-sliced from the cited source and must match
byte-for-byte (spaces included), and the crop PNG must equal a fresh native render
of the same slice. This checks transcription, not artistic judgement: entries stay
hand-written after inspection.

  role_lookup_check.py FILE.json [FILE.json ...] [--archive PATH]
  role_lookup_check.py --merge OUT.json GROUP.json ...   validate, de-duplicate, merge
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aahub_native import Native  # noqa: E402
import role_crop  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
ROLES = REPO / "assets/glyphs/roles"
ARCHIVE = Path("/home/user/ascii-art-archive")

TAXONOMY = {
    "rim_cap": "top of a convex turn / crest where the contour reverses vertical direction (e.g. ⌒, ＿ over ／ ＼)",
    "shoulder": "transition from a cap/crest into a steep flank (e.g. ／￣, ￣＼)",
    "flank": "steep near-vertical run of a rounded form below or above a shoulder",
    "side": "straight side of a non-rounded form (box/wall/pole edge)",
    "return_base": "lower turn that closes a form back toward the other side (e.g. ＼＿／, ヽ_ノ)",
    "closed_ring": "small closed contour, e.g. an eye or pupil ring",
    "paired_aperture": "two matched small openings, e.g. nostrils",
    "upper_tooth_row": "upper row of teeth / periodic serrated edge seen from below",
    "lower_tooth_row": "lower row of teeth / periodic serrated edge seen from above",
    "periodic_band": "repeated glyph rhythm carrying a material band (fence, stitch, grille, pattern)",
    "fold_crease": "short interior stroke explaining a fold, crease or joint without closing it",
    "contact_junction": "where two forms meet/attach (branch entry, finger to palm, root to ground)",
    "opening_paper_gap": "deliberately empty paper that separates or opens forms",
    "tone_core": "densest part of a bounded tone field",
    "tone_mid": "thinning band of a tone field",
    "tone_fringe": "sparse outer dots/marks where tone dissolves into paper",
    "cast_shadow_edge": "edge of a cast shadow on a ground/surface",
    "effect_line": "motion/impact/convergence line",
    "small_face": "whole small face construction, 1-6 rows",
    "small_mouth": "whole small mouth construction",
    "ear": "whole ear construction",
}


def resolve_src(repo: str, src: str) -> str:
    kind, _, rest = src.partition(":")
    if kind == "lib":
        return src
    root = ARCHIVE if repo == "ascii-art-archive" else REPO
    return f"{kind}:{root / rest}"


def check_entry(nat: Native, e: dict, base: Path) -> list[str]:
    errs = []
    src = resolve_src(e["source"]["repo"], e["source"]["src"])
    try:
        rows = role_crop.load_source(src)
    except Exception as ex:  # noqa: BLE001
        return [f"source unreadable: {src}: {ex}"]
    a, b = e["native"]["row_numbers"]
    x0, x1 = e["native"]["x_px"]
    if not (1 <= a <= b <= len(rows)):
        return [f"row_numbers {a}-{b} outside 1-{len(rows)}"]
    sl = role_crop.slice_rows(nat, rows, a, b, x0, x1)
    want = [t for _, t, _, _ in sl]
    pen = [p for _, _, p, _ in sl]
    if want != e["native"]["rows"]:
        for i, (w, g) in enumerate(zip(want, e["native"]["rows"] + [None] * len(want))):
            if w != g:
                errs.append(f"row {a + i}: source {w!r} != entry {g!r}")
        if len(e["native"]["rows"]) != len(want):
            errs.append(f"row count {len(e['native']['rows'])} != {len(want)}")
    if pen != e["native"]["row_pen_x"]:
        errs.append(f"row_pen_x {e['native']['row_pen_x']} != {pen}")
    if e["size_band"]["rows"] != b - a + 1:
        errs.append(f"size_band.rows {e['size_band']['rows']} != {b - a + 1}")
    crop = base / e["crop"]
    if not crop.exists():
        errs.append(f"missing crop {crop}")
    else:
        got = np.array(Image.open(crop).convert("L")) < 128
        ref = role_crop.crop(nat, rows, a, b, x0, x1)
        if got.shape != ref.shape or (got != ref).any():
            errs.append(f"crop {e['crop']} differs from native render of the slice")
    lay = nat.layout(rows)
    for sp in e.get("split_stroke", []):
        line = lay[sp["row"] - 1] if 1 <= sp["row"] <= len(lay) else []
        if (sp["glyph"], sp["pen_x"]) not in line:
            errs.append(f"split_stroke {sp['glyph']!r}@{sp['pen_x']} not on source row {sp['row']}")
        elif not (a <= sp["row"] <= b and x0 <= sp["pen_x"] < x1):
            errs.append(f"split_stroke {sp['glyph']!r} row {sp['row']} pen {sp['pen_x']} outside the entry's slice")
    if not "".join(e["native"]["rows"]).strip("　 "):
        errs.append("slice has no ink glyphs")
    return errs


def load_and_check(paths, nat):
    schema = json.loads((ROLES / "schema.json").read_text())
    docs, bad = [], 0
    for p in paths:
        p = Path(p)
        d = json.loads(p.read_text())
        try:
            jsonschema.validate(d, schema)
        except jsonschema.ValidationError as ex:
            print(f"{p}: SCHEMA {ex.message} at {list(ex.absolute_path)}")
            bad += 1
            continue
        roles = set(TAXONOMY) | set(d.get("role_extensions", {}))
        ids = set()
        for e in d["entries"]:
            errs = []
            for r in [e["role"], *e.get("also_roles", [])]:
                if r not in roles:
                    errs.append(f"role {r!r} not in taxonomy or role_extensions")
            if e["id"] in ids:
                errs.append("duplicate id")
            ids.add(e["id"])
            errs += check_entry(nat, e, ROLES)
            for x in errs:
                print(f"{p.name} {e['id']}: {x}")
            bad += bool(errs)
        print(f"{p}: {len(d['entries'])} entries checked")
        docs.append(d)
    return docs, bad


def merge(out: Path, docs: list[dict], nat: Native):
    merged, seen, dups = [], {}, []
    ext = {}
    logs, gaps, revisions = [], [], []
    for d in docs:
        revisions += [f"[{d.get('group')}] {x}" for x in d.get("revision_log", [])]
        ext.update(d.get("role_extensions", {}))
        logs += [f"[{d.get('group')}] {x}" for x in d.get("inspection_log", [])]
        gaps += [f"[{d.get('group')}] {x}" for x in d.get("gaps", [])]
        for e in d["entries"]:
            k = (e["source"]["src"], tuple(e["native"]["row_numbers"]), tuple(e["native"]["x_px"]), e["role"])
            if k in seen:
                dups.append(f"{e['id']} duplicates {seen[k]}")
                continue
            if any(m["id"] == e["id"] for m in merged):
                raise SystemExit(f"id collision across groups: {e['id']}")
            seen[k] = e["id"]
            merged.append(e)
    merged.sort(key=lambda e: (e["role"], e["size_band"]["rows"], e["size_band"]["px_wide"], e["id"]))
    doc = {"schema": "role_lookup.v1",
           "font": "Saitamaar.ttf (trueff-shallot assets/font)", "font_sha256": nat.font_sha256,
           "metrics": "16 px glyphs, natural advances, 17 px row pitch; pen x from line start",
           "authoring": "Each entry hand-written by its source-group inspector after viewing the native crop with "
                        "its exact TXT rows; rows and crops are mechanically re-verified against the source by "
                        "scripts/role_lookup_check.py. Corpus statistics (aahub_blocks.v1) never select entries.",
           "taxonomy": TAXONOMY, "role_extensions": ext,
           "groups": sorted({d.get("group", "?") for d in docs}),
           "deduplicated": dups, "gaps": gaps, "revision_log": revisions, "inspection_log": logs,
           "entries": merged}
    if out.exists():  # parent-written fields survive a re-merge
        old = json.loads(out.read_text())
        for k in ("parent_audit", "parent_audits"):
            if k in old:
                doc[k] = old[k]
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(f"merged {len(merged)} entries ({len(dups)} duplicates dropped) -> {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--merge", type=Path)
    ap.add_argument("--archive", type=Path)
    a = ap.parse_args()
    global ARCHIVE
    if a.archive:
        ARCHIVE = a.archive
    nat = Native()
    docs, bad = load_and_check(a.files, nat)
    if bad:
        raise SystemExit(f"{bad} problem(s)")
    if a.merge:
        merge(a.merge, docs, nat)


if __name__ == "__main__":
    main()
