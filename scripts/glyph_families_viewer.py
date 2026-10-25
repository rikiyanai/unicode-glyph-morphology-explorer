#!/usr/bin/env python3
"""Browse ALL discovered glyph families in one animated curses viewer.

Left pane: every family (spinners, ramps, fill-pairs, cycles) in one scrollable
list. Right pane: the selected family ANIMATING in place, so a spinner spins, a
ramp ramps and a fill pulses while you browse. Reads the catalog written by
``glyph_audit.py families --json`` for instant startup; if it is missing the
families are computed on launch (slower).

Run:
    python3 scripts/glyph_audit.py families --json   # build catalog once
    python3 scripts/glyph_families_viewer.py
    python3 scripts/glyph_families_viewer.py --saved  # replay your reviewed families
    python3 scripts/glyph_families_viewer.py --foliage-strokes
        # review real stroked glyph sets for tree outer/mid/interior roles
    python3 scripts/glyph_families_viewer.py --mode cycle  # browse every discovered cycle
    python3 scripts/glyph_families_viewer.py --block Arrows
    python3 scripts/glyph_families_viewer.py --mode distract
        # every glyph ranked by DISTRACTION weight, alphanumerics flagged
    python3 scripts/glyph_families_viewer.py --mode combo
        # useful combinations plus source-context evidence
    python3 scripts/glyph_families_viewer.py --mode context
        # browse source rows, provenance, annotations, and interpretation limits
    python3 scripts/glyph_families_viewer.py --mode patterns
        # native Saitamaar bundle/combination comparisons; no discovery cache build
    python3 scripts/glyph_families_viewer.py --mode round
        # operator-supplied construction crops: source pixels and matched source rows
    python3 scripts/glyph_families_viewer.py --mode authored
        # the nine authored seed combinations, each beside its mirror
    python3 scripts/glyph_families_viewer.py --mode dir8 --dump
        # text dump of the groups; no TTY needed (headless verification)

Axes (top legend, switch with m):
    ALL  ROTATE(spin)  DIR8  DENSITY(ramp)  FILL  CYCLE  MIRROR  STRUCT(topo)
    FOLIAGE STROKES  DISTRACT  COMBOS  CONTEXT EVIDENCE  AUTHORED  NATIVE PATTERNS
Rotation is its own axis; CYCLE holds animation cycles of every length (3..16),
filterable by length so each band is browsable on its own. With no --mode, ALL
loads discovered families plus the local review surfaces: foliage stroke sets,
authored combinations, mined usage, measured seam candidates, discovered runs,
and curated source-context records. DISTRACT is intentionally explicit because
it is a one-glyph ranking over the whole corpus, not a family list.

Controls:
    up/down or j/k   select family
    PgUp/PgDn        page
    m                next axis (ALL / ROTATE / DENSITY / FILL / CYCLE / STRUCT)
    1-9              show only families of that length (e.g. 4 = 4-frame cycles)
    0                clear the length filter (all lengths)
    space            pause / resume animation
    + / -            faster / slower
    This standalone viewer is read-only; source-repository family saving and
    runtime handoff stay in the Asciicker workspace.
    [ / ]            scroll contextual source details
    w                toggle raw vs normalized rendering
    q or Esc         quit
"""

from __future__ import annotations

import argparse
import curses
import json
import locale
import sys
import time
import unicodedata
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import glyph_features as gf  # noqa: E402
import glyph_audit as ga  # noqa: E402

N = gf.N
CATALOG = gf.CACHE_DIR / "families.jsonl"
META = gf.CACHE_DIR / "families.meta.json"
MODES = ["all", "spin", "dir8", "ramp", "fill", "cycle", "mirror", "topo", "stroke",
         "distract", "combo", "context", "authored", "sjis", "patterns", "round", "aaj"]
# Each discovery mode IS an axis; rotation (spin) is its own first-class axis,
# distinct from the near-identical animation cycles. Display names make that
# explicit so "view all axes" reads as real categories. dir8 = 8-way directed
# rotation orbits (up to 8 frames); mirror = left/right chirality pairs.
# distract = every glyph ranked by DISTRACTION weight; combo = the useful
# combination review surface (authored seeds + mined usage + measured Unicode
# runs + curated source context); context = source-backed multi-row evidence.
AXIS_LABEL = {"all": "ALL", "spin": "ROTATE", "dir8": "DIR8", "ramp": "DENSITY",
              "fill": "FILL", "cycle": "CYCLE", "mirror": "MIRROR", "topo": "STRUCT",
              "stroke": "FOLIAGE STROKES", "distract": "DISTRACT", "combo": "COMBOS",
              "context": "CONTEXT EVIDENCE", "authored": "AUTHORED", "sjis": "SJIS CORPUS",
              "patterns": "NATIVE PATTERNS", "round": "CONSTRUCTION CROPS", "aaj": "AA JUDGMENT"}
# Axes whose row order carries meaning (ranking / authored/evidence file order)
# and must therefore survive the list pane's size sort.
ORDERED_MODES = {"distract", "combo", "context", "authored", "sjis", "patterns", "round", "aaj"}
# Measured candidate data written by scripts/glyph_combo_gallery.py.
MEASURED = gf.CACHE_DIR / "glyph_combo_measured.json"
# The authored combination dictionary (offsets + codepoints + generated mirrors).
COMBINATIONS = gf.REPO_ROOT / "assets" / "glyphs" / "authored" / "glyph_combinations.v1.json"
# Corpus-derived Shift_JIS AA combinations (AAHub training slugs), written and
# rendered by scripts/sjis_corpus_combos.py. Tracked, so no build step is needed.
SJIS_CORPORA = {
    "aa003": gf.REPO_ROOT / "assets" / "glyphs" / "corpus" / "aahub_aa003_train.sjis_combos.v1.json",
    "aa004": gf.REPO_ROOT / "assets" / "glyphs" / "corpus" / "aahub_aa004_train.sjis_combos.v1.json",
}
SJIS_CORPUS = SJIS_CORPORA["aa003"]
# Source-context evidence paired with authored / measured / corpus-derived
# combinations. Records retain their evidence class and are not runtime rules.
CONTEXT_EVIDENCE = (gf.REPO_ROOT / "assets" / "glyphs" / "contextual"
                    / "shallot_native_contexts.v1.json")
# the original four are REQUIRED for a usable catalog; topo is optional (present
# only when the catalog was built after the global topology cache existed), so a
# pre-topo catalog stays valid and simply shows no topo families.
CATALOG_MODES = {"spin", "ramp", "fill", "cycle"}


def _catalog_usable(block: str | None) -> tuple[bool, str]:
    if not CATALOG.exists():
        return False, "missing catalog"
    if not META.exists():
        return False, "missing catalog metadata"
    try:
        meta = json.loads(META.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"bad catalog metadata: {exc}"
    if int(meta.get("schema", 0)) != 1:
        return False, "unsupported catalog metadata schema"
    modes = set(meta.get("modes") or [])
    if not CATALOG_MODES.issubset(modes):
        return False, f"catalog modes are narrowed: {sorted(modes)}"
    cached_block = meta.get("block")
    if cached_block and (not block or block.upper() != str(cached_block).upper()):
        return False, f"catalog block is narrowed: {cached_block}"
    return True, ""


def load_families(c: ga.Corpus, block: str | None) -> list[dict]:
    """Families as {mode, members:[corpus idx], block, size}. Prefer the catalog."""
    usable, reason = _catalog_usable(block)
    if usable:
        fams = []
        try:
            for line in CATALOG.read_text().splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                members = [c.i(cp) for cp in r["cps"]]
                members = [m for m in members if m is not None]
                if len(members) < 2:
                    continue
                if block and block.upper() not in (r.get("block", "") or "").upper():
                    continue
                fams.append({"mode": r["mode"], "members": members,
                             "block": r.get("block", ""), "size": len(members)})
            if fams:
                return fams
            reason = "catalog had no usable rows"
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            reason = f"bad catalog rows: {exc}"
    # fallback: compute now
    sys.stderr.write(f"computing families ({reason}; run `families --json` to cache)…\n")
    return ga.collect_families(c, block=block)


def load_saved_families(c: ga.Corpus, block: str | None) -> list[dict]:
    """Load the durable operator-reviewed sequences in their saved order.

    The discovery catalog remains the owner of *new* candidate families.  This
    reader only replays JSONL records the reviewer explicitly saved, so the
    ``--saved`` screen cannot be diluted by regenerated catalog output.
    """
    if not gf.SAVED_FAMILIES.exists():
        return []
    families: list[dict] = []
    try:
        lines = gf.SAVED_FAMILIES.read_text().splitlines()
    except OSError:
        return []
    for line in lines:
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            cps = [int(cp) for cp in record["cps"]]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
        members = [c.i(cp) for cp in cps]
        if len(members) < 2 or any(member is None for member in members):
            continue
        name = str(record.get("block", ""))
        if block and block.upper() not in name.upper():
            continue
        families.append({
            "mode": str(record.get("mode", "cycle")),
            "members": members,
            "block": name,
            "size": len(members),
            "role_hint": str(record.get("role_hint", "")),
            "note": str(record.get("note", "")),
        })
    return families


def load_foliage_stroke_families(c: ga.Corpus) -> list[dict]:
    """Load review-only real-glyph sets for non-uniform tree foliage.

    These are deliberately not similarity clusters. Each sequence is selected
    for a distinct visible tree role, so reviewers can judge stroke language
    rather than inherit the uniform Katakana texture from the retired canopy
    palette. The atlas and runtime pools remain unchanged.
    """
    candidates = (
        ("CJK Strokes", "outer_leaf_sweep", "thin directional leaf contours",
         (0x31C0, 0x31C1, 0x31C2, 0x31C3, 0x31C4, 0x31C5)),
        ("CJK Strokes", "outer_leaf_hook", "hooked leaf-edge contour variation",
         (0x31CA, 0x31CB, 0x31CC, 0x31CD, 0x31CE, 0x31CF)),
        ("CJK Strokes", "twig_and_vein", "short branch and vein strokes",
         (0x31D0, 0x31D1, 0x31D2, 0x31D3, 0x31D4, 0x31D5)),
        ("CJK Strokes", "outer_leaf_fork", "forked and split leaf-edge strokes",
         (0x31D6, 0x31D7, 0x31D8, 0x31D9, 0x31DA, 0x31DB, 0x31DC, 0x31DD)),
        ("CJK Strokes", "outer_leaf_turn", "long turning strokes for wind-facing edges",
         (0x31DE, 0x31DF, 0x31E0, 0x31E1, 0x31E2, 0x31E3)),
        ("CJK Radicals Supplement", "grass_radical_marks", "radical-scale grass and moss marks",
         (0x2E80, 0x2E81, 0x2E82, 0x2E83, 0x2E84, 0x2E85)),
        ("Hiragana", "outer_leaf_curve", "curved, sparse outer-leaf silhouettes",
         (0x3057, 0x3064, 0x305D, 0x306E, 0x308B, 0x308C)),
        ("Katakana", "outer_leaf_angle", "angular outer-leaf silhouettes",
         (0x30CE, 0x30D5, 0x30CC, 0x30E1, 0x30E9, 0x30EF)),
        ("Hangul Compatibility Jamo", "outer_leaf_chevron", "chevron and fork leaf outlines",
         (0x3145, 0x3148, 0x314A, 0x314B, 0x314C, 0x314D, 0x314E)),
        ("Arabic", "outer_leaf_calligraphic", "flowing, tapered outer-leaf strokes",
         (0x062C, 0x062D, 0x062E, 0x0633, 0x0634, 0x0635, 0x0636)),
        ("Arabic", "mid_canopy_calligraphic", "linked curved mid-canopy marks",
         (0x0639, 0x063A, 0x0641, 0x0642, 0x0646, 0x0647, 0x0648)),
        ("CJK Radicals", "mid_canopy_branch", "branching mid-canopy marks",
         (0x5DDD, 0x6728, 0x6797, 0x68EE)),
        ("CJK Unified Ideographs", "dense_canopy_mass", "dense interior foliage and occlusion",
         (0x8349, 0x6797, 0x68EE, 0x8449, 0x8449)),
        ("CJK Unified Ideographs", "dense_canopy_crosshatch", "high-stroke-count interior leaf mass",
         (0x8449, 0x8449, 0x85C1, 0x85CD, 0x85EA, 0x8607)),
        ("CJK Radicals", "ground_tuft_and_moss", "grass, moss, and root-base accents",
         (0x5C71, 0x5DDD, 0x8349, 0x6728)),
    )
    families: list[dict] = []
    for block, role, note, cps in candidates:
        members = [c.i(cp) for cp in cps]
        members = [member for member in members if member is not None]
        if len(members) >= 2:
            families.append({
                "mode": "stroke", "members": members, "block": block,
                "size": len(members), "role_hint": role, "note": note,
            })
    return families


def load_distraction_families(c: ga.Corpus, block: str | None,
                              limit: int = 0) -> list[dict]:
    """Every glyph in scope as a one-glyph row, ranked most-distracting first.

    This is a ranking screen, not a similarity family: the point is to see which
    glyphs pull the eye out of the line art before they are admitted to a
    vocabulary. The alphanumeric hard flag is surfaced on every row, because the
    design source treats it as a category difference rather than a degree — see
    glyph_features.distraction_components for the cited tutorial passages.
    """
    allow = ga.block_allow(c, block)
    rows = ga.rank_distraction(c, allow)
    if limit:
        rows = rows[:limit]
    families: list[dict] = []
    for rank, r in enumerate(rows, 1):
        flag = "ALNUM" if r["alnum"] else "-"
        if r["alnum"] and r["whitelisted"]:
            flag = "ALNUM(kept)"
        elif r["alnum"] and r["marginal"]:
            flag = "ALNUM(marginal)"
        families.append({
            "mode": "distract",
            "members": [r["index"]],
            "block": r["block"],
            "size": 1,
            "role_hint": f"#{rank}  weight {r['weight']:.3f}  {flag}",
            "note": (f"ink {r['density']:.3f}  ncomp {r['ncomp']}  "
                     f"family median {r['family_median_density']:.3f}"),
            "distract": r,
        })
    return families


def _combo_bitmap(c: ga.Corpus, cells: list[dict], cols: int, rows: int):
    """Composite ink bitmap for one combination, on the REAL cell grid.

    Each cell's glyph is pasted at its (col, row) offset using the same rasterized
    ``c.raw`` grid the single-glyph pane draws, so a combination is shown in the
    atlas rasterization rather than as a re-drawn approximation. Returns
    (bitmap, missing_codepoints)."""
    import numpy as np
    bm = np.zeros((rows * N, cols * N), np.uint8)
    missing: list[int] = []
    for d in cells:
        i = c.i(int(d["cp"]))
        if i is None:
            missing.append(int(d["cp"]))
            continue
        col, row = int(d["col"]), int(d["row"])
        bm[row * N:(row + 1) * N, col * N:(col + 1) * N] = c.raw[i].reshape(N, N)
    return bm, missing


def _bitmap_rows(bm) -> list[str]:
    """One character per pixel — combinations are several cells wide, so the
    two-character ink used by the single-glyph pane would not fit beside a mirror."""
    return ["".join("█" if v else " " for v in row) for row in bm]


def load_combination_families(c: ga.Corpus, mode: str = "combo") -> list[dict]:
    """Load the authored combination dictionary in file order.

    Each entry carries the composite bitmap of the combination and of its
    horizontal mirror, so the viewer can show the pair side by side. The mirror
    cells are stored in the file (generated from glyph_audit.find_mirror pairs);
    this reader does not re-derive them — scripts/tests owns that check.
    """
    if not COMBINATIONS.exists():
        return []
    try:
        doc = json.loads(COMBINATIONS.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"bad combination dictionary {COMBINATIONS}: {exc}\n")
        return []
    families: list[dict] = []
    for cb in doc.get("combinations", []):
        cells = cb.get("cells") or []
        mcells = (cb.get("mirror") or {}).get("cells") or []
        if not cells:
            continue
        cols, rows = int(cb.get("cols", 1)), int(cb.get("rows", 1))
        bm, missing = _combo_bitmap(c, cells, cols, rows)
        mbm, mmissing = _combo_bitmap(c, mcells, cols, rows) if mcells else (bm, [])
        members = [c.i(int(d["cp"])) for d in cells]
        members = [m for m in members if m is not None]
        families.append({
            "mode": mode,
            "members": members,
            "block": "authored",
            "size": len(cells),
            "role_hint": str(cb.get("id", "")),
            "note": str(cb.get("label", "")),
            "combo": {
                "id": str(cb.get("id", "")),
                "label": str(cb.get("label", "")),
                "note": str(cb.get("note", "")),
                "source": str(cb.get("source", doc.get("source", ""))),
                "chars": "".join(str(d.get("char", "")) for d in cells),
                "mirror_chars": "".join(str(d.get("char", "")) for d in mcells),
                "self_symmetric": bool((cb.get("mirror") or {}).get("self_symmetric")),
                "rows": _bitmap_rows(bm),
                "mirror_rows": _bitmap_rows(mbm),
                "missing": missing + mmissing,
            },
        })
    return families



def _half_block_rows(rows: list[str]) -> list[str]:
    """Pack two raster rows per text row with half blocks, so an 8x16 cell shows
    as 8x8 text cells and the terminal's ~1:2 cell restores the true 1:2 pixel
    aspect. One char per pixel row would stretch every glyph 2x vertically (the
    tilde read as an N)."""
    out = []
    for y in range(0, len(rows), 2):
        top = rows[y]
        bot = rows[y + 1] if y + 1 < len(rows) else "." * len(top)
        out.append("".join(
            "\u2588" if t == "#" and b == "#" else "\u2580" if t == "#" else "\u2584" if b == "#" else " "
            for t, b in zip(top, bot)))
    return out


def _seam_family(c: ga.Corpus, rec: dict, role: str, block: str, note: str, source: str) -> dict:
    """One measured combination as a viewer family.

    The composite rows come from the measured data itself (cells cropped to
    their real 8- or 16-px width), so a beside seam is drawn touching, unlike
    the authored ``combo`` path which pastes 16-px canvases. The label shows the
    glyphs on their lattice in reading order, so a corner reads as two rows."""
    cells, mcells = rec["cells"], rec.get("mirror_cells") or rec["cells"]
    members = [m for m in (c.i(int(d["cp"])) for d in cells) if m is not None]
    lattice = rec.get("lattice") or ["".join(str(d.get("char", "")) for d in cells)]
    mlattice = rec.get("mirror_lattice") or ["".join(str(d.get("char", "")) for d in mcells)]
    chars, mchars = " / ".join(lattice), " / ".join(mlattice)
    rows = _half_block_rows(rec["rows"])
    mrows = _half_block_rows(rec.get("mirror_rows") or rec["rows"])
    return {
        "mode": "combo", "members": members, "block": block, "size": len(cells),
        "role_hint": f"{role}  {chars}", "note": note,
        "combo": {"id": role, "label": note, "note": note, "source": source,
                  "chars": chars, "mirror_chars": mchars, "self_symmetric": chars == mchars,
                  "rows": rows, "mirror_rows": mrows, "missing": []},
    }


def load_seam_families(c: ga.Corpus, limit: int = 0) -> list[dict]:
    """MEASURED candidate combinations, ranked by continuity (lower DSM first).

    Source: .run/glyph_audit/glyph_combo_measured.json from glyph_combo_gallery.py
    (built here when missing; ~7 s). Order: the anti-aliasing family stacked over
    ``|`` (ranked by distance from a continuous bar), then every candidate whose
    seams all have a 0 px gap, then the top rows per lattice shape. Numbers are
    measured on the composite raster; see glyph_cell_pairs.py."""
    if not MEASURED.exists():
        import glyph_combo_gallery as gcg
        sys.stderr.write("measuring combinations (first run)...\n")
        gcg.main([])
    try:
        d = json.loads(MEASURED.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"bad measured data {MEASURED}: {exc}\n")
        return []
    fams: list[dict] = []
    ref = d["study_ref"]
    for n, s in enumerate(d["study"], 1):
        note = (f"gap {s['gap_min']} px   D_SM vs \u2502\u2502 {s['dsm_box']}   vs straight stroke {s['dsm_stroke']}"
                f"   (\u2502 over \u2502: gap {ref['gap_min']} px, D_SM 0; lower = reads more as one stroke)")
        fams.append(_seam_family(c, s, f"study #{n}  {s['char']} over |", "over |", note,
                                 "anti-aliasing family stacked over |, ranked by DSM vs a continuous bar"))
    for n, r in enumerate(d["connected"], 1):
        note = f"CONNECTED  D_SM {r['dsm']}   gaps {r['gaps']}   port {r['port']}   distract {r['distract']}"
        fams.append(_seam_family(c, r, f"connected #{n}  {r['shape']}", "0 px seams", note,
                                 " / ".join(r["names"])))
    for shape, rows in d["shapes"].items():
        for n, r in enumerate(rows, 1):
            if limit and n > limit:
                break
            if r["shape"].startswith("mined_"):
                mem = "  ".join(f"{m['chars']}\u00d7{m['count']}" for m in r.get("members", [])[:4])
                note = (f"USED {r['count']}\u00d7 in the author's plates   {r.get('profile', '')}   "
                        f"orient {r.get('orientation')}   gaps {r.get('gaps')}   D_SM {r.get('dsm')}   [{mem}]")
            elif r["shape"].startswith("runs_"):
                note = (f"{r.get('profile', '')}   rules {'/'.join(r.get('rules', []))}   score {r.get('score')}   "
                        f"gaps {r.get('gaps')}   orient {r.get('orientation')}   D_SM {r.get('dsm')}   "
                        f"x{len(r.get('members', []))}   " + " / ".join(dict.fromkeys(r.get("blocks") or [])))
            else:
                note = (f"D_SM {r['dsm']}   gaps {r['gaps']}   port {r['port']}   orient {r.get('orientation')}   "
                        f"distract {r['distract']}   " + " / ".join(r.get("blocks") or []))
            fams.append(_seam_family(c, r, f"#{n} of {d['counts'][shape]}  {shape}", shape, note,
                                     " / ".join(r["names"])))
    return fams


SJIS_CATEGORY_LABEL = {"idiom": "15.5 idiom", "bigram": "touching pair", "trigram": "touching triple",
                       "stack": "vertical stack", "band": "tone band"}


def load_sjis_corpus_families(c: ga.Corpus, limit: int = 0, mode: str = "sjis",
                              corpus: str = "aa003") -> list[dict]:
    """Corpus-derived proportional Shift_JIS combinations, in category and rank order.

    Rows are pre-rendered in Saitamaar 16 px on the font's advance lattice by
    scripts/sjis_corpus_combos.py, so a combination is drawn at its true pixel
    offsets rather than on the 8/16 px terminal cell grid. Counts are over the
    AAHub training slugs of the pinned archive snapshot named in the file.
    corpus selects the dataset: aa003 (slug pages, default) or aa004 (MLT pages)."""
    path = SJIS_CORPORA[corpus]
    if not path.exists():
        return []
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"bad SJIS corpus data {path}: {exc}\n")
        return []
    units = d.get("unit_labels", {"slug": "slugs", "page": "pages"})
    if "unit_labels" in d:
        source = (f"{d.get('corpus', '')} AAHub train, archive {d['archive_commit'][:7]}, "
                  f"{d['slugs']:,} {units['slug']} / {d['pages']:,} {units['page']}, "
                  f"{d['font']} {d['px']} px")
    else:
        source = (f"AAHub train, archive {d['archive_commit'][:7]}, {d['slugs']} slugs / {d['pages']} pages, "
                  f"{d['font']} {d['px']} px")
    seen: dict[str, int] = {}
    fams: list[dict] = []
    for v in d.get("viewable", []):
        cat = v["category"]
        seen[cat] = seen.get(cat, 0) + 1
        if limit and seen[cat] > limit:
            continue
        chars = " / ".join(v["lattice"])
        mchars = " / ".join(v["mirror_lattice"])
        bits = [f"n={v['count']:,}"]
        if v.get("pooled_n") is not None:
            bits.append(f"with mirror {v['pooled_n']:,}")
        if v.get("pages") is not None:
            bits.append(f"{v['pages']:,} {units['page']} / {v['slugs']} {units['slug']}")
        if v.get("dx_px") is not None:
            bits.append(f"centre offset {v['dx_px']:+d} px")
        if not v.get("mirror_exact", True):
            bits.append("mirror approximate (glyph without a 15.5 partner)")
        bits.append("x px " + ",".join(f"{x:g}" for x in v["offsets_px"]))
        note = f"{SJIS_CATEGORY_LABEL.get(cat, cat).upper()}   " + "   ".join(bits)
        members = [m for m in (c.i(ord(ch)) for ch in "".join(v["lattice"]) if ch not in " \u3000")
                   if m is not None]
        fams.append({
            "mode": mode, "members": members, "block": f"sjis {cat}", "size": len("".join(v["lattice"])),
            "role_hint": f"#{v.get('rank', seen[cat])} {cat}  {chars}", "note": note,
            "combo": {"id": f"sjis_{cat}_{v.get('rank', seen[cat])}", "label": note, "note": note,
                      "source": source, "chars": chars, "mirror_chars": mchars,
                      "self_symmetric": chars == mchars,
                      "rows": _half_block_rows(v["rows"]), "mirror_rows": _half_block_rows(v["mirror_rows"]),
                      "missing": []},
        })
    return fams


def load_context_families(c: ga.Corpus, mode: str = "context") -> list[dict]:
    """Load hand-curated source passages with provenance and interpretation bounds.

    The family size reflects the longest recorded focus form for list filtering;
    it is not a rule that a useful construction must have any fixed glyph count.
    """
    if not CONTEXT_EVIDENCE.exists():
        return []
    try:
        doc = json.loads(CONTEXT_EVIDENCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"bad contextual evidence {CONTEXT_EVIDENCE}: {exc}\n")
        return []
    if doc.get("schema") != "glyph_morphology.contextual_combo_evidence.v1":
        sys.stderr.write(f"unsupported contextual evidence schema: {CONTEXT_EVIDENCE}\n")
        return []
    families: list[dict] = []
    import construction_tool_mapping as tool_mapping
    import operator_reference_sources as reference_sources
    for record in reference_sources.attach(tool_mapping.attach(doc.get("families", []))):
        forms = [str(form) for form in record.get("focus_forms", []) if str(form)]
        focus_chars = "".join(forms)
        members: list[int] = []
        seen: set[int] = set()
        for ch in focus_chars:
            if ch.isspace() or ord(ch) in seen:
                continue
            seen.add(ord(ch))
            idx = c.i(ord(ch))
            if idx is not None:
                members.append(idx)
        families.append({
            "mode": mode,
            "members": members,
            "block": "context evidence",
            "size": max((len(form) for form in forms), default=1),
            "role_hint": str(record.get("id", "")),
            "note": str(record.get("pattern_family", "")),
            "context": record,
        })
    return families


def load_combo_families(c: ga.Corpus, limit: int = 0,
                        corpus: str = "aa003") -> list[dict]:
    """The full combination axis, including curated source-context records."""
    families = load_combination_families(c, mode="combo")
    families.extend(load_seam_families(c, limit))
    families.extend(load_sjis_corpus_families(c, limit, mode="combo", corpus=corpus))
    families.extend(load_context_families(c, mode="combo"))
    families.extend(load_pattern_families(c, mode="combo"))
    families.extend(load_round_families(c, mode="combo"))
    families.extend(load_aaj_families(c, mode="combo"))
    return families


def load_pattern_families(c, mode: str = "patterns", doc: dict | None = None) -> list[dict]:
    """Native comparison groups from the tracked, source-hashed intake snapshot."""
    import saitamaar_pattern_intake as intake
    try:
        doc = doc if doc is not None else intake.load()
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write(f"bad native pattern evidence: {exc}\n")
        return []
    result = []
    for source in doc["families"]:
        record = dict(source, measurement=doc["measurement"],
                      reproduced_rows=len(doc["reported_checks"]))
        chars = list(dict.fromkeys("".join(row for v in record["native_comparisons"]
                                           for row in v["text_rows"])))
        result.append({"mode": mode, "members": [c.i(ord(ch)) for ch in chars if c.i(ord(ch)) is not None],
                       "block": "native pattern comparisons",
                       "size": max(len(row) for v in record["native_comparisons"] for row in v["text_rows"]),
                       "role_hint": record["id"], "note": record["title"], "context": record})
    return result


def load_aaj_families(c, mode: str = "aaj", doc: dict | None = None) -> list[dict]:
    import aaj_template_intake as intake
    doc = doc if doc is not None else intake.load()
    return [{"mode": mode, "members": [c.i(ord(ch)) for ch in dict.fromkeys(r["converter_template"]["text"])
                                        if c.i(ord(ch)) is not None],
             "block": "AA Judgment composite templates", "size": len(r["converter_template"]["text"]),
             "role_hint": r["id"], "note": r["title"], "context": r}
            for r in doc["families"]]


def load_round_families(c, mode: str = "round", doc: dict | None = None) -> list[dict]:
    import operator_construction_crops as crops
    import construction_tool_mapping as tool_mapping
    import operator_reference_sources as reference_sources
    doc = doc if doc is not None else crops.load()
    return [{"mode": mode, "members": [c.i(ord(ch)) for ch in dict.fromkeys("".join(r["focus_forms"]))
                                        if c.i(ord(ch)) is not None],
             "block": "operator construction crops", "size": max(map(len, r["focus_forms"]), default=0),
             "role_hint": r["id"], "note": r["title"], "context": r}
            for r in reference_sources.attach(tool_mapping.attach(doc["families"]))]


def load_default_families(c: ga.Corpus, block: str | None, seam_limit: int) -> list[dict]:
    """The one-command standalone browser surface.

    It keeps the discovered morphology families as the base, then adds the
    curated/review families that a glyph-tooling user expects to reach by
    pressing ``m`` instead of relaunching: foliage strokes, authored combos, and
    measured seam/run candidates, and source-context records. Distraction is
    excluded because it is a complete one-glyph ranking, not a family corpus.
    """
    fams = load_families(c, block)
    if block:
        return fams
    fams.extend(load_foliage_stroke_families(c))
    fams.extend(load_combination_families(c, mode="authored"))
    fams.extend(load_seam_families(c, seam_limit))
    fams.extend(load_sjis_corpus_families(c, seam_limit))
    fams.extend(load_context_families(c, mode="combo"))
    fams.extend(load_context_families(c, mode="context"))
    fams.extend(load_pattern_families(c, mode="combo"))
    fams.extend(load_pattern_families(c, mode="patterns"))
    for mode in ("combo", "context", "round"):
        fams.extend(load_round_families(c, mode=mode))
    for mode in ("combo", "aaj"):
        fams.extend(load_aaj_families(c, mode=mode))
    return fams


def _display_char_width(ch: str) -> int:
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1


def _wrap_display(text: str, width: int) -> list[str]:
    """Wrap Unicode source text by terminal columns, preserving codepoints."""
    width = max(1, width)
    rows: list[str] = []
    current = ""
    columns = 0
    for ch in text:
        ch_width = _display_char_width(ch)
        if current and columns + ch_width > width:
            rows.append(current)
            current = ""
            columns = 0
        current += ch
        columns += ch_width
    if current or not rows:
        rows.append(current)
    return rows


def _context_detail_lines(record: dict, width: int, native: bool = False, x: int = 0) -> list[str]:
    """Human-readable detail pane retaining separate evidence/provenance fields."""
    if record.get("native_comparisons"):
        return _pattern_detail_lines(record, width)
    lines: list[str] = []

    def add(line: str) -> None:
        lines.extend(_wrap_display(line, width))

    provenance = record.get("provenance") or {}
    interpretation = record.get("interpretation") or {}
    add(str(record.get("title", record.get("id", "context record"))))
    if record.get("converter_template"):
        template = record["converter_template"]
        add("RECOVERED COMBINATION: " + template["text"])
        add("codepoints: " + " ".join(template["codepoints"]))
        profile = template["profile"]
        add(f"{profile['font']} {profile['px']}px, {profile['row_pitch_px']}px rows; native advances, whole glyphs.")
        add("COMPARISON RASTER, NOT recovered Windows/MS Gothic output.")
        if len(template["raster_rows"][0]) > width:
            add("RASTER WIDER THAN PANE: clipped, not wrapped or rescaled; widen terminal.")
        lines.extend(_half_block_rows(template["raster_rows"]))
        add(f"total advance: {template['advance_px']:g}px")
        for placement in template["placements"]:
            add(f"{placement['char']} x={placement['x_px']:g}px advance={placement['advance_px']:g}px")
        add(f"internal label: {provenance['internal_label']!r}; builder {provenance['builder_instruction_va']}; string {provenance['text_va']}")
        add("PE SHA256: " + provenance["executable_sha256"])
        add("font SHA256: " + provenance["font_sha256"])
        add(template["limit"])
        return lines
    if record.get("native_reference"):
        import operator_construction_crops as crops
        raster, scale, offset = crops.raster_rows(record, width, native, x)
        shape = record["native_reference"]
        label = "PACKAGED SCREENSHOT" if shape.get("kind") == "operator-screenshot" else "PACKAGED NATIVE PNG"
        add(f"{label} {shape['width']}x{shape['height']}px. [v] overview/source pixels; [h/l] pan; [[]/[]] scroll.")
        if native:
            add(f"NATIVE PIXELS 1:1, x={offset}. No resampling; half blocks pack two source rows per text row.")
        else:
            add(f"OVERVIEW 1:{scale} integer ink pooling; context only, NOT native glyph-fit evidence. Press v for native pixels.")
        lines.extend(_half_block_rows(raster))
        add("--- EXACT SOURCE TEXT / PROVENANCE (text columns are not native font metrics) ---")
    else:
        add("TEXT CONTEXT ONLY: terminal columns do not reproduce Saitamaar advances; inspect the paired native PNG before judging ink fit.")
    add(f"pattern family: {record.get('pattern_family', 'unclassified')}")
    add("focus: " + " / ".join(record.get("focus_forms") or []))
    add("focus length is codepoints in a quoted form, not native width or the extent of this multi-row construction.")
    add(f"record: {record.get('id', '')}   source: {provenance.get('source_id', 'unspecified')}")
    for key in ("source_url", "image_path", "text_path", "raw_text_path", "turntable_gif_path", "frame_records_path",
                "construction_record_path", "catalog_path", "reference_registry_path"):
        if provenance.get(key):
            add(f"{key}: {provenance[key]}")
    for key in ("source_image_sha256", "source_text_sha256_file",
                "source_text_sha256_utf8_rstrip_lf"):
        if provenance.get(key):
            add(f"{key}: {provenance[key]}")
    for key in ("annotation_status", "construction_record_status", "native_image_status",
                "review_state", "context_limit", "frame_review_method", "study_status", "source_binding_status", "decoding", "original_reference_status"):
        if provenance.get(key):
            add(f"{key.replace('_', ' ')}: {provenance[key]}")
    for variant in provenance.get("source_variants") or []:
        add(f"SHARED MOTIF VARIANT aa[{variant['archive_piece_index']}] rows {variant['line_start']}-{variant['line_end']}: {variant['text_path']}")
    if provenance.get("operator_verdict") is not None:
        add(f"operator verdict: {provenance['operator_verdict']}")
        add(f"operator note: {provenance.get('operator_note') or '(empty)'}")
        rects = provenance.get("operator_rects")
        if rects is None and any(p.get("operator_rect_px")
                                 for p in record.get("passages") or []):
            rects = "per passage"
        add(f"operator rectangles: {rects if rects is not None else 'not recorded'}")
    for key in ("observed_visual", "drawn_analogy", "mathematical_family",
                "historical_implementation_limit"):
        add(f"{key.replace('_', ' ')}: {interpretation.get(key, 'not recorded')}")
    if record.get("tool_mapping"):
        import construction_tool_mapping as tool_mapping
        for line in tool_mapping.detail_lines(record["tool_mapping"]):
            add(line)
    for count in provenance.get("corpus_counts") or []:
        add(f"corpus count: {count['corpus']} {count['pattern']} = "
            f"{count['occurrences']:,} occurrences / {count['pages']:,} pages / "
            f"{count['slugs']:,} slugs")
    for passage in record.get("passages") or []:
        if passage.get("frame_index") is not None:
            add(f"--- frame {passage['frame_index']:03} @ {passage.get('angle_deg')}° "
                f"{passage.get('view_path', '')}")
            for row in passage.get("glyph_rows") or []:
                add(f"glyph record: {row}")
            continue
        rows = passage.get("rows") or []
        line_end = int(passage.get("line_start", 1)) + len(rows) - 1
        add(f"--- passage {passage.get('id', '')} lines "
            f"{passage.get('line_start', '?')}-{line_end}")
        if passage.get("operator_region"):
            add(f"operator region {passage['operator_region']}: "
                f"{passage.get('operator_label', '')}")
        elif passage.get("operator_label") is not None:
            add(f"operator label: {passage['operator_label']}")
        if passage.get("operator_rect_px"):
            rect = passage["operator_rect_px"]
            add(f"operator rectangle px: x={rect['x']} y={rect['y']} "
                f"w={rect['w']} h={rect['h']}")
        for row in passage.get("operator_excerpt_rows") or []:
            add(f"operator excerpt: {row}")
        for offset, row in enumerate(rows):
            line_no = int(passage.get("line_start", 1)) + offset
            add(f"{line_no:03}: {row}")
    return lines


def _pattern_detail_lines(record: dict, width: int) -> list[str]:
    """Raster rows stay intact, never wrapped or redrawn using terminal glyphs."""
    lines = []

    def add(text: str) -> None:
        lines.extend(_wrap_display(text, width))

    profile = record["measurement"]
    add(record["title"])
    add(f"Saitamaar {profile['px']}px / {profile['row_pitch_px']}px rows. Native binary ink, not normalized glyphs.")
    for variant in record["native_comparisons"]:
        add("--- " + " / ".join(variant["text_rows"]))
        if len(variant["raster_rows"][0]) > width:
            add("RASTER WIDER THAN PANE: widen terminal; rows are clipped, not wrapped/rescaled.")
        lines.extend(_half_block_rows(variant["raster_rows"]))
        for metric in variant["glyph_metrics"]:
            axes = ",".join("dot" if c["axis_deg"] is None else f"{c['axis_deg']:.0f}"
                            for c in metric["components"])
            add(f"{metric['char']} {metric['codepoint']} advance={metric['advance_px']:g}px "
                f"ink={metric['ink_px']}px density={metric['ink_per_advance_row']:.2f} "
                f"components={len(metric['components'])} axes={axes} bbox={metric['ink_bbox_xyxy_inclusive']}")
    add("8-connected INK COMPONENTS, NOT PEN STROKES. PCA axes do not decompose crossings/hooks.")
    add(record["interpretation"]["observed_visual"])
    add(record["interpretation"]["drawn_analogy"])
    add(profile["angle_convention"])
    add(profile["limits"])
    add(f"{record['reproduced_rows']} supplied measurement rows reproduced, including duplicate observations.")
    add("font SHA256: " + record["provenance"]["source_font_sha256"])
    add(record["interpretation"]["historical_implementation_limit"])
    return lines


def _dump_context_record(record: dict) -> None:
    if record.get("tool_mapping"):
        for line in _context_detail_lines(record, 160):
            print("       " + line)
        return
    if record.get("converter_template"):
        for line in _context_detail_lines(record, 160):
            print("       " + line)
        return
    if record.get("native_reference"):
        for line in _context_detail_lines(record, 100):
            print("       " + line)
        return
    if record.get("native_comparisons"):
        for line in _pattern_detail_lines(record, 240):
            print("       " + line)
        return
    provenance = record.get("provenance") or {}
    interpretation = record.get("interpretation") or {}
    print(f"       context: {record.get('id')} — {record.get('title')}")
    print("       TEXT CONTEXT ONLY: terminal spacing is not a native Saitamaar art preview; use the paired PNG for ink-fit review.")
    print(f"       pattern family: {record.get('pattern_family')}")
    print(f"       source: {provenance.get('source_id', 'unspecified')}")
    for key in ("image_path", "text_path", "turntable_gif_path", "frame_records_path",
                "construction_record_path", "catalog_path"):
        if provenance.get(key):
            print(f"       {key}: {provenance[key]}")
    for key in ("source_image_sha256", "source_text_sha256_file",
                "source_text_sha256_utf8_rstrip_lf", "turntable_gif_sha256",
                "frame_records_sha256", "construction_sha256"):
        if provenance.get(key):
            print(f"       {key}: {provenance[key]}")
    for key in ("annotation_status", "construction_record_status", "native_image_status",
                "review_state", "context_limit", "frame_review_method", "study_status"):
        if provenance.get(key):
            print(f"       {key}: {provenance[key]}")
    if "operator_verdict" in provenance:
        rects = provenance.get("operator_rects")
        if rects is None and any(p.get("operator_rect_px")
                                 for p in record.get("passages") or []):
            rects = "per passage"
        print(f"       operator verdict: {provenance['operator_verdict']}; "
              f"note={provenance.get('operator_note', '')!r}; "
              f"rects={rects if rects is not None else 'not recorded'}")
    for key in ("observed_visual", "drawn_analogy", "mathematical_family",
                "historical_implementation_limit"):
        print(f"       {key}: {interpretation.get(key, 'not recorded')}")
    for count in provenance.get("corpus_counts") or []:
        print(f"       corpus count: {count['corpus']} {count['pattern']} "
              f"{count['occurrences']:,} occurrences; {count['pages']:,} pages; "
              f"{count['slugs']:,} slugs")
    for passage in record.get("passages") or []:
        if passage.get("frame_index") is not None:
            print(f"       frame {passage['frame_index']:03} angle={passage.get('angle_deg')} "
                  f"path={passage.get('view_path', '')}")
            for row in passage.get("glyph_rows") or []:
                print(f"         glyph record: {row}")
            continue
        print(f"       passage {passage.get('id')} starting line {passage.get('line_start', '?')}")
        if passage.get("operator_region"):
            print(f"         operator region {passage['operator_region']}: "
                  f"{passage.get('operator_label', '')}")
        elif passage.get("operator_label") is not None:
            print(f"         operator label: {passage['operator_label']}")
        if passage.get("operator_rect_px"):
            rect = passage["operator_rect_px"]
            print(f"         operator rectangle px: x={rect['x']} y={rect['y']} "
                  f"w={rect['w']} h={rect['h']}")
        for row in passage.get("operator_excerpt_rows") or []:
            print(f"         operator excerpt: {row}")
        for offset, row in enumerate(passage.get("rows") or []):
            line_no = int(passage.get("line_start", 1)) + offset
            print(f"         {line_no:03}: {row}")


def dump_families(c: ga.Corpus, fams: list[dict], mode: str) -> None:
    """Print the groups as text so they can be verified without a TTY.

    The curses screen is the review surface, but every axis must also be readable
    from a pipe: that is what makes a change to dir8/distract/combo/context
    checkable in a test or a report."""
    from collections import Counter
    counts = Counter(f["mode"] for f in fams)
    # Honour the selected axis exactly as the curses list pane does: `--mode dir8
    # --dump` must print the dir8 groups, not the whole catalog.
    shown = fams if mode == "all" else [f for f in fams if f["mode"] == mode]
    print(f"# glyph_families_viewer --dump   mode={mode}   families={len(shown)}"
          f"   (loaded {len(fams)})")
    print("# axes: " + ", ".join(f"{k}:{v}" for k, v in sorted(counts.items())))
    for n, f in enumerate(shown, 1):
        members = " ".join(f"U+{int(c.cps[i]):04X}({chr(int(c.cps[i]))})"
                           for i in f["members"])
        extent = f"focus length={f['size']} codepoints" if f.get('context') else f"size={f['size']:<3}"
        head = (f"#{n:4} [{f['mode']:8}] {extent} [{f['block']}]")
        role = f.get("role_hint", "")
        print(f"{head}  {role}  {members}".rstrip())
        context = f.get("context")
        if context:
            _dump_context_record(context)
        combo = f.get("combo")
        if combo:
            print(f"       {combo['id']}: {combo['chars']}  mirror {combo['mirror_chars']}"
                  + ("  (self-symmetric)" if combo["self_symmetric"] else ""))
            print(f"       source: {combo['source']}")
            if combo["missing"]:
                print("       MISSING from cache: "
                      + " ".join(f"U+{cp:04X}" for cp in combo["missing"]))
            gap = "   "
            for a, b in zip(combo["rows"], combo["mirror_rows"]):
                print(f"       |{a}|{gap}|{b}|")


def init_colors() -> dict[str, int]:
    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass
    spec = ({
        "hud": (252, -1), "dim": (240, -1), "sel": (16, 252), "ink": (231, -1),
        "spin": (213, -1), "dir8": (198, -1), "ramp": (84, -1), "fill": (215, -1),
        "cycle": (81, -1), "mirror": (147, -1), "topo": (208, -1),
        "distract": (203, -1), "combo": (214, -1), "context": (45, -1),
        "authored": (114, -1), "sjis": (177, -1), "patterns": (45, -1), "round": (114, -1),
    } if curses.COLORS >= 256 else {
        "hud": (curses.COLOR_WHITE, -1), "dim": (curses.COLOR_BLUE, -1),
        "sel": (curses.COLOR_BLACK, curses.COLOR_WHITE), "ink": (curses.COLOR_WHITE, -1),
        "spin": (curses.COLOR_MAGENTA, -1), "dir8": (curses.COLOR_MAGENTA, -1),
        "ramp": (curses.COLOR_GREEN, -1),
        "fill": (curses.COLOR_YELLOW, -1), "cycle": (curses.COLOR_CYAN, -1),
        "mirror": (curses.COLOR_BLUE, -1), "topo": (curses.COLOR_RED, -1),
        "distract": (curses.COLOR_RED, -1), "combo": (curses.COLOR_YELLOW, -1),
        "context": (curses.COLOR_CYAN, -1),
        "authored": (curses.COLOR_GREEN, -1), "sjis": (curses.COLOR_MAGENTA, -1),
        "patterns": (curses.COLOR_CYAN, -1),
        "round": (curses.COLOR_GREEN, -1),
    })
    pairs = {}
    for i, (name, (fg, bg)) in enumerate(spec.items(), start=1):
        try:
            curses.init_pair(i, fg, bg)
        except curses.error:
            pass
        pairs[name] = curses.color_pair(i)
    return pairs


def safe(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x >= w or x < 0:
        return
    try:
        win.addstr(y, x, text[:w - x], attr)
    except curses.error:
        pass


def run(stdscr, c: ga.Corpus, fams_all: list[dict], initial_mode: str, saved_only: bool) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    cset = init_colors()
    from collections import Counter
    axis_counts = Counter(f["mode"] for f in fams_all)
    mode_idx = MODES.index(initial_mode)
    sel = 0
    top = 0
    frame = 0
    paused = False
    which = "raw"
    fps = 4.0
    len_filter = 0          # 0 = all lengths; 1-9 = only families of that size
    context_scroll = 0
    reference_native = False
    reference_x = 0
    reference_id = None
    last = time.monotonic()
    stdscr.timeout(60)

    def view():
        m = MODES[mode_idx]
        fs = fams_all if m == "all" else [f for f in fams_all if f["mode"] == m]
        if len_filter:
            fs = [f for f in fs if f["size"] == len_filter]
        if m in ORDERED_MODES:
            # ranking order (distract) and authored file order (combo) ARE the
            # information; a size sort would destroy them.
            return fs
        # sort by size so multiple lengths group together (cycles of 3,4,..16
        # become visible bands); rotation/structure read by length too
        return sorted(fs, key=lambda f: (f["mode"], -f["size"]))

    def legend():
        parts = []
        for i, m in enumerate(MODES):
            cnt = len(fams_all) if m == "all" else axis_counts.get(m, 0)
            tag = f"{AXIS_LABEL[m]} {cnt}"
            parts.append(f"[{tag}]" if i == mode_idx else tag)
        return "  ".join(parts)

    while True:
        fams = view()
        if sel >= len(fams):
            sel = max(0, len(fams) - 1)
        selected_id = fams[sel].get("context", {}).get("id") if fams else None
        if selected_id != reference_id:
            reference_native = False
            reference_x = 0
            context_scroll = 0
            reference_id = selected_id
        h, w = stdscr.getmaxyx()
        list_w = 40
        list_h = h - 4

        if sel < top:
            top = sel
        elif sel >= top + list_h:
            top = sel - list_h + 1

        stdscr.erase()
        scope = "SAVED" if saved_only else ("FOLIAGE STROKES" if all(
            f["mode"] == "stroke" for f in fams_all) else "DISCOVERY+REVIEW")
        if all(f["mode"] == "round" for f in fams_all):
            scope = "OPERATOR CONSTRUCTION CROPS"
        safe(stdscr, 0, 1, f"Glyph Families ({scope}) — axes: " + legend(), cset["hud"] | curses.A_BOLD)
        lf = f"len={len_filter}" if len_filter else "len=all"
        note = ""
        safe(stdscr, 1, 1, f"{len(fams)} shown  {lf}  "
                           f"fps={fps:.0f} {'PAUSED' if paused else 'PLAY'}  render={which}"
                           + note, cset["dim"])

        # list pane
        for row in range(list_h):
            idx = top + row
            if idx >= len(fams):
                break
            f = fams[idx]
            y = 3 + row
            issel = idx == sel
            attr = cset["sel"] if issel else cset["hud"]
            chars = "".join(chr(int(c.cps[i])) for i in f["members"][:6])
            extent = f"cp{f['size']:<2}" if f.get('context') else f"sz{f['size']:<2}"
            line = f"{'>' if issel else ' '}[{f['mode']:5}] {extent} {chars}"
            if f.get("context", {}).get("native_reference"):
                line = f"{'>' if issel else ' '}[{f['mode']:5}] {f['context']['title']}"
            shown = (_wrap_display(line, list_w - 1)[0] if f.get("context", {}).get("native_reference")
                     else line.ljust(list_w))
            safe(stdscr, y, 1, shown, attr)
            if not issel:
                safe(stdscr, y, 2, f"[{f['mode']:5}]", cset.get(f["mode"], cset["hud"]))

        for y in range(3, 3 + list_h):
            safe(stdscr, y, list_w + 1, "│", cset["dim"])

        # detail / animation pane
        if fams:
            f = fams[sel]
            members = f["members"]
            dx = list_w + 3
            avail = max(0, w - dx - 1)
            extent = f"focus length {f['size']} codepoints" if f.get('context') else f"size {f['size']}"
            safe(stdscr, 3, dx, f"{f['mode'].upper()}  {extent}  [{f['block']}]",
                 cset.get(f["mode"], cset["hud"]) | curses.A_BOLD)
            context = f.get("context")
            combo = f.get("combo")
            if context:
                detail = _context_detail_lines(context, avail, reference_native, reference_x)
                visible_count = max(0, h - 6)  # reserve the footer; do not overwrite a source row
                max_scroll = max(0, len(detail) - visible_count)
                context_scroll = min(context_scroll, max_scroll)
                kind = ("round" if context.get("native_reference") else
                        "patterns" if context.get("native_comparisons") else "context")
                safe(stdscr, 4, dx, f"{kind} {context_scroll + 1}-{min(len(detail), context_scroll + visible_count)}"
                     f" / {len(detail)}   [[]/[]] scroll", cset["dim"])
                for line_i, line in enumerate(detail[context_scroll:context_scroll + visible_count]):
                    safe(stdscr, 5 + line_i, dx, line, cset["hud"])
            if not context and combo:
                # A combination is a multi-cell picture, so the pane shows the whole
                # composite next to its horizontal mirror rather than one animating
                # glyph. Side by side when the pane is wide enough, stacked when not.
                safe(stdscr, 4, dx, f"{combo['chars']}   mirror {combo['mirror_chars']}"
                     + ("   (self-symmetric)" if combo["self_symmetric"] else ""),
                     cset["hud"])
                safe(stdscr, 5, dx, combo["note"][:avail], cset["dim"])
                safe(stdscr, 6, dx, f"source: {combo['source']}"[:avail], cset["dim"])
                main_rows, mir_rows = combo["rows"], combo["mirror_rows"]
                cw = len(main_rows[0]) if main_rows else 0
                if cw and cw * 2 + 4 <= avail:
                    safe(stdscr, 7, dx, "ORIGINAL".ljust(cw + 4) + "MIRROR", cset["dim"])
                    for gy, (a, b) in enumerate(zip(main_rows, mir_rows)):
                        safe(stdscr, 8 + gy, dx, a, cset["ink"])
                        safe(stdscr, 8 + gy, dx + cw + 4, b, cset["ink"])
                else:
                    safe(stdscr, 7, dx, "ORIGINAL", cset["dim"])
                    for gy, a in enumerate(main_rows):
                        safe(stdscr, 8 + gy, dx, a, cset["ink"])
                    y0 = 9 + len(main_rows)
                    safe(stdscr, y0 - 1, dx, "MIRROR", cset["dim"])
                    for gy, b in enumerate(mir_rows):
                        safe(stdscr, y0 + gy, dx, b, cset["ink"])
            elif not context and members:
                fr = frame % len(members)
                mi = members[fr]
                cp = int(c.cps[mi])
                safe(stdscr, 4, dx, "frame " + " ".join(
                    (f"[{chr(int(c.cps[i]))}]" if k == fr else f" {chr(int(c.cps[i]))} ")
                    for k, i in enumerate(members[:16])), cset["hud"])
                safe(stdscr, 5, dx, f"U+{cp:04X}  {c.names[mi]}", cset["dim"])
                role_hint = f.get("role_hint", "")
                if role_hint:
                    safe(stdscr, 6, dx, f"role: {role_hint}", cset["dim"])
                note = f.get("note", "")
                if note:
                    safe(stdscr, 7, dx, note[:avail], cset["dim"])
                grid = getattr(c, which)[mi].reshape(N, N)
                for gy, gr in enumerate(grid):
                    safe(stdscr, 8 + gy, dx,
                         "".join("██" if v else "  " for v in gr), cset["ink"])

        safe(stdscr, h - 1, 1,
             "[jk]sel [PgUp/Dn]page [m]axis [1-9]len [0]all "
             "[space]pause [+/-]speed [w]raw/norm [[]/[]]scroll [v]ref pixels [h/l]pan [q]uit",
             cset["dim"])
        stdscr.refresh()

        # advance animation on a timer regardless of key input
        now = time.monotonic()
        if not paused and now - last >= 1.0 / max(0.5, fps):
            frame += 1
            last = now

        ch = stdscr.getch()
        if ch == -1:
            continue
        if ch in (ord("q"), 27):
            return
        elif ch in (curses.KEY_DOWN, ord("j")):
            sel = min(sel + 1, max(0, len(fams) - 1)); frame = 0; context_scroll = 0
            reference_native = False; reference_x = 0
        elif ch in (curses.KEY_UP, ord("k")):
            sel = max(sel - 1, 0); frame = 0; context_scroll = 0
        elif ch == curses.KEY_NPAGE:
            sel = min(sel + list_h, max(0, len(fams) - 1)); frame = 0; context_scroll = 0
        elif ch == curses.KEY_PPAGE:
            sel = max(sel - list_h, 0); frame = 0; context_scroll = 0
        elif ch == ord("m"):
            mode_idx = (mode_idx + 1) % len(MODES); sel = 0; top = 0; frame = 0; context_scroll = 0
        elif ord("1") <= ch <= ord("9"):
            v = ch - ord("0")
            len_filter = 0 if len_filter == v else v; sel = 0; top = 0; frame = 0; context_scroll = 0
        elif ch == ord("0"):
            len_filter = 0; sel = 0; top = 0; frame = 0; context_scroll = 0
        elif ch == ord(" "):
            paused = not paused
        elif ch in (ord("+"), ord("=")):
            fps = min(30.0, fps + 1)
        elif ch == ord("-"):
            fps = max(1.0, fps - 1)
        elif ch == ord("w"):
            which = "norm" if which == "raw" else "raw"
        elif ch == ord("["):
            context_scroll = max(0, context_scroll - 1)
        elif ch == ord("]"):
            context_scroll += 1
        elif ch == ord("v") and fams and fams[sel].get("context", {}).get("native_reference"):
            reference_native = not reference_native
            context_scroll = 0
        elif ch in (ord("h"), ord("l")) and fams and fams[sel].get("context", {}).get("native_reference"):
            if not reference_native:
                context_scroll = 0
            reference_native = True
            max_x = max(0, fams[sel]["context"]["native_reference"]["width"] - max(1, w - list_w - 4))
            reference_x = min(max_x, max(0, reference_x + (16 if ch == ord("l") else -16)))

def main() -> int:
    locale.setlocale(locale.LC_ALL, "")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--block", type=str, default=None, help="scope to a block-name substring")
    ap.add_argument("--saved", action="store_true",
                    help="replay only the tracked operator-reviewed saved_families registry")
    ap.add_argument("--foliage-strokes", action="store_true",
                    help="review actual stroked glyph sets for tree foliage; no atlas or runtime mutation")
    mode_requested = any(arg == "--mode" or arg.startswith("--mode=") for arg in sys.argv[1:])
    mode_choices = MODES + ["seam"]
    ap.add_argument("--mode", choices=mode_choices, default="all",
                    help="open on one animation axis; use 'cycle' for all discovered "
                         "cycles, 'distract' for the DISTRACTION ranking, 'combo' for "
                         "the useful-combination browser (including source context), "
                         "'context' for source-backed multi-row constructions, 'authored' for the nine seed "
                         "combinations, 'sjis' for corpus-derived Shift_JIS AA combinations, "
                         "'patterns' for native Saitamaar bundle/combination comparisons, "
                         "'round' for operator-supplied local construction crops, "
                         "'aaj' for all 40 recovered AA Judgment combinations, "
                         "or legacy 'seam' as an alias for combo")
    ap.add_argument("--dump", action="store_true",
                    help="print the groups as text and exit; no TTY required, so the "
                         "selected axis can be verified from a pipe or a test")
    ap.add_argument("--limit", type=int, default=0,
                    help="distract / combo: keep only the top N rows (per measured shape for combo; 0 = all)")
    ap.add_argument("--corpus", choices=sorted(SJIS_CORPORA), default="aa003",
                    help="SJIS corpus dataset for --mode sjis / combo: aa003 (AAHub slug pages, default) "
                         "or aa004 (AAHub MLT crawl, train keys)")
    args = ap.parse_args()
    if args.mode == "aaj":
        import aaj_template_intake as intake
        try:
            aaj_doc = intake.load()
        except (OSError, ValueError) as exc:
            ap.error(str(exc))
        c = intake.TemplateCorpus(aaj_doc)
    elif args.mode == "round":
        import operator_construction_crops as crops
        try:
            round_doc = crops.load()
        except (OSError, ValueError) as exc:
            ap.error(str(exc))
        c = crops.ConstructionCorpus(round_doc)
    elif args.mode == "context":
        # Text/source-pixel evidence needs a codepoint index, not a private
        # discovery feature cache. No terminal-font raster fit is claimed.
        import operator_construction_crops as crops
        context_doc = json.loads(CONTEXT_EVIDENCE.read_text(encoding="utf-8"))
        crop_doc = crops.load()
        c = crops.ConstructionCorpus({"families": context_doc["families"] + crop_doc["families"]})
    elif args.mode == "patterns":
        import saitamaar_pattern_intake as intake
        try:
            pattern_doc = intake.load()
        except (OSError, ValueError) as exc:
            ap.error(str(exc))
        c = intake.PatternCorpus(pattern_doc)
    else:
        c = ga.Corpus()
    if args.saved and args.foliage_strokes:
        ap.error("--saved and --foliage-strokes select different review sources")
    if (args.saved or args.foliage_strokes) and args.mode in ("distract", "combo", "context",
                                                               "authored", "seam", "sjis", "patterns", "round", "aaj"):
        ap.error(f"--mode {args.mode} replaces the family source; it cannot be "
                 f"combined with --saved / --foliage-strokes")
    if args.foliage_strokes:
        fams = load_foliage_stroke_families(c)
        initial_mode = "stroke"
    elif args.mode == "distract":
        fams = load_distraction_families(c, args.block, args.limit)
        initial_mode = "distract"
    elif args.mode == "authored":
        fams = load_combination_families(c, mode="authored")
        initial_mode = "authored"
    elif args.mode == "patterns":
        fams = load_pattern_families(c, doc=pattern_doc)
        initial_mode = "patterns"
    elif args.mode == "round":
        fams = load_round_families(c, doc=round_doc)
        initial_mode = "round"
    elif args.mode == "aaj":
        fams = load_aaj_families(c, doc=aaj_doc)
        initial_mode = "aaj"
    elif args.mode == "context":
        fams = load_context_families(c) + load_round_families(c, mode="context")
        initial_mode = "context"
    elif args.mode in ("combo", "seam"):
        fams = load_combo_families(c, args.limit, args.corpus)
        initial_mode = "combo"
    elif args.mode == "sjis":
        fams = load_sjis_corpus_families(c, args.limit, corpus=args.corpus)
        initial_mode = "sjis"
    else:
        fams = load_saved_families(c, args.block) if args.saved else load_default_families(c, args.block, args.limit)
        initial_mode = "combo" if not mode_requested and not args.dump and not args.saved else args.mode
    if not fams:
        source = {"distract": "ranked glyphs", "combo": "combinations",
                  "context": "context evidence",
                  "authored": "authored combinations", "seam": "measured combinations",
                  "sjis": "SJIS corpus combinations"}.get(
            args.mode, "saved families" if args.saved else "families")
        print(f"no {source} found.", file=sys.stderr)
        return 1
    if args.dump:
        try:
            dump_families(c, fams, initial_mode)
        except BrokenPipeError:
            try:
                sys.stdout.close()
            except OSError:
                pass
        return 0
    if not sys.stdout.isatty():
        print(f"{len(fams)} families (needs an interactive TTY to view, or --dump).",
              file=sys.stderr)
        return 2
    curses.wrapper(run, c, fams, initial_mode, args.saved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
