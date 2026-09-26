#!/usr/bin/env python3
"""Glyph statistics for one AAHub slug of proportional Shift_JIS art.

Input: a directory holding one UTF-8 text file per AAHub post (exact
whitespace; the post number is the first digit run in the file name), an
optional same-stem 1-bit PNG render of each post, and the Saitamaar font
(MS PGothic 16 px metrics). None of these is packaged here; pass their
locations on the command line. Output: one JSON document with glyph
frequencies, class shares, space mixing, ink density, and a fixed-grid
re-layout test. The output is written to ``--out`` and an existing output is
never replaced by different bytes.

Usage:
    python3 aa_slug_stats.py SLUG_DIR FONT.ttf --out stats.json \
        --source-url https://aahub.org/mlt/<id>
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont

PX = 16  # AAHub renders Saitamaar at 16 px
HALF_SPACE = " "
FULL_SPACE = "　"

# Heuristic role classes. Kana/kanji are assigned by block below.
FINE_TEXTURE = set(".,;:'`､｡･・\"ﾞﾟ‘’´¨…‥゛゜")
FW_STROKE = set("＿￣／＼｜⌒―─‐ー－～")
ASCII_STROKE = set("_/\\|-~^=()[]{}<>!il")


def glyph_class(ch: str) -> str:
    cp = ord(ch)
    if ch in (HALF_SPACE, FULL_SPACE):
        return "space"
    if ch in FINE_TEXTURE:
        return "fine_texture"
    if ch in FW_STROKE:
        return "fullwidth_stroke"
    if ch in ASCII_STROKE:
        return "ascii_stroke"
    if 0x3040 <= cp <= 0x30FF or 0xFF66 <= cp <= 0xFF9F or 0x31F0 <= cp <= 0x31FF:
        return "kana"
    if 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF:
        return "kanji"
    if 0xFF01 <= cp <= 0xFF5E:
        return "fullwidth_other"
    if cp < 0x80:
        return "ascii_other"
    return "other_symbol"


# Named Shift_JIS stroke idioms probed verbatim (substring counts, touching glyphs).
IDIOMS = ["／￣", "￣＼", "＿／", "＼＿", "／￣＼", "＼＿／", "⌒ヽ", "(⌒", "（⌒", "⌒)", "⌒）",
          "ヽ_", "_ノ", "ヽ＿", "＿ノ", "､_", "_,", ",,", "､､", ";;", "::", ".:", ":.",
          "ﾉ(", ")ヽ", "从", "彡", "‐-", "-‐", "ーニ", "ニ‐", "´`", "'´", "｀ヽ", "ヽ､", "(_", "_)"]

OUTLINE_CLASSES = {"fullwidth_stroke", "ascii_stroke", "kana"}
TEXTURE_CLASSES = {"fine_texture", "kanji"}

# Skill ascii-art-authoring section 4.1: 25 basic + 4 extended + 12 whitelisted.
SKILL_ALPHABET = set("`~!^()-_+=;:'\",.\\/|<>[]{}") | set("´‾¡·") | set("oOvVTL7UcCxX")


def fixed_width(ch: str) -> int:
    """Cell width on a monospace grid: 16 for W/F/A (Shift_JIS double-byte), 8 otherwise."""
    return 16 if unicodedata.east_asian_width(ch) in ("W", "F", "A") else 8


def load_advances(font_path: Path):
    font = TTFont(str(font_path))
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    def adv(ch: str) -> float:
        g = cmap.get(ord(ch))
        return hmtx[g][0] * PX / upm if g else float("nan")

    return adv


def layout(line: str, width_of):
    """Return [(x0, x1, ch)] for every glyph in a line."""
    x = 0.0
    out = []
    for ch in line:
        w = width_of(ch)
        out.append((x, x + w, ch))
        x += w
    return out


def centers(row):
    return [((a + b) / 2, ch) for a, b, ch in row if ch not in (HALF_SPACE, FULL_SPACE)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug_dir", type=Path)
    ap.add_argument("font", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-url", required=True)
    ap.add_argument("--top", type=int, default=60)
    args = ap.parse_args()

    adv = load_advances(args.font)
    pieces = sorted((p for p in args.slug_dir.glob("*.txt") if re.search(r"\d", p.stem)),
                    key=lambda p: int(re.findall(r"\d+", p.stem)[0]))
    if not pieces:
        print("no numbered .txt posts found", file=sys.stderr)
        return 2

    glyphs = collections.Counter()
    glyph_px = collections.Counter()
    hbigrams = collections.Counter()
    outline_ngrams = collections.Counter()
    letters_out = collections.Counter()
    pieces_with_letters_out = 0
    idiom_n = collections.Counter()
    idiom_where = collections.defaultdict(list)
    vpairs = collections.Counter()
    per_piece = []
    input_hashes = []
    drift_all = []
    vpair_total = vpair_kept = vpair_snap_kept = 0
    snap_glyphs = snap_collide = 0
    lead_total = lead_off_grid = 0
    line_count = adjacent_half = lead_half = 0
    mixed_space_runs = pure_half_runs = pure_full_runs = 0
    alternating_runs = 0

    try:
        from PIL import Image
    except ImportError:  # density is optional
        Image = None

    for path in pieces:
        text = path.read_text(encoding="utf-8")
        lines = text.rstrip("\n").split("\n")
        rid = "res" + re.findall(r"\d+", path.stem)[0].lstrip("0")
        input_hashes.append([rid, hashlib.sha256(text.encode("utf-8")).hexdigest()])
        pc = collections.Counter()
        prop_rows, mono_rows = [], []
        max_px = 0.0
        piece_letters_out = False
        for line in lines:
            line_count += 1
            adjacent_half += line.count("  ")
            lead_half += line.startswith(HALF_SPACE)
            for ch in line:
                if ch.isascii() and ch.isalnum() and ch not in SKILL_ALPHABET:
                    letters_out[ch] += 1
                    piece_letters_out = True
            # stroke idioms: runs of 2-3 touching outline-class glyphs
            for m in re.finditer(r"[^ \u3000]+", line):
                tok = m.group(0)
                for n in (2, 3):
                    for i in range(len(tok) - n + 1):
                        g = tok[i:i + n]
                        if all(glyph_class(c) in OUTLINE_CLASSES | {"fullwidth_other", "other_symbol"} for c in g):
                            outline_ngrams[g] += 1
            for ch in line:
                glyphs[ch] += 1
                glyph_px[ch] += adv(ch)
                pc[glyph_class(ch)] += 1
            stripped = [c for c in line if c not in (HALF_SPACE, FULL_SPACE)]
            # horizontal bigrams between glyphs that touch (no space between them)
            for a, b in zip(line, line[1:]):
                if a not in (HALF_SPACE, FULL_SPACE) and b not in (HALF_SPACE, FULL_SPACE):
                    hbigrams[a + b] += 1
            # whitespace runs
            for run in re.findall(r"[ 　]+", line):
                if len(run) < 2:
                    continue
                has_h, has_f = HALF_SPACE in run, FULL_SPACE in run
                if has_h and has_f:
                    mixed_space_runs += 1
                    if re.search(r"(　 ){2,}|( 　){2,}", run):
                        alternating_runs += 1
                elif has_h:
                    pure_half_runs += 1
                else:
                    pure_full_runs += 1
            lead = re.match(r"[ 　]*", line).group(0)
            if lead and stripped:
                lead_total += 1
                lead_px = sum(adv(c) for c in lead)
                if abs(lead_px / 8 - round(lead_px / 8)) > 1e-6:
                    lead_off_grid += 1
            prow = layout(line, adv)
            mrow = layout(line, fixed_width)
            prop_rows.append(prow)
            mono_rows.append(mrow)
            if prow:
                max_px = max(max_px, prow[-1][1])
            # snap test: keep proportional x, quantise each glyph centre to an 8 px column
            cols = collections.Counter(int(((a + b) / 2) // 8) for a, b, c in prow
                                       if c not in (HALF_SPACE, FULL_SPACE))
            snap_glyphs += sum(cols.values())
            snap_collide += sum(n for n in cols.values() if n > 1)
            for (pa, pb, ch), (ma, mb, _) in zip(prow, mrow):
                if ch not in (HALF_SPACE, FULL_SPACE):
                    drift_all.append(abs((pa + pb) / 2 - (ma + mb) / 2))
        # vertical pairs: glyph centres within 3 px on adjacent rows (proportional layout)
        for r in range(len(prop_rows) - 1):
            upper_p, lower_p = centers(prop_rows[r]), centers(prop_rows[r + 1])
            upper_m, lower_m = centers(mono_rows[r]), centers(mono_rows[r + 1])
            for i, (cx, ch) in enumerate(upper_p):
                for j, (dx, dh) in enumerate(lower_p):
                    if abs(cx - dx) <= 3:
                        vpairs[ch + "/" + dh] += 1
                        vpair_total += 1
                        if abs(upper_m[i][0] - lower_m[j][0]) <= 3:
                            vpair_kept += 1
                        if int(cx // 8) == int(dx // 8):
                            vpair_snap_kept += 1
        pieces_with_letters_out += piece_letters_out
        for idiom in IDIOMS:
            k = text.count(idiom)
            if k:
                idiom_n[idiom] += k
                idiom_where[idiom].append(rid)
        ink = None
        png = path.with_suffix(".png")
        if Image is not None and png.exists():
            im = Image.open(png).convert("1")
            w, h = im.size
            black = sum(
                1 for b in im.convert("L").tobytes() if b < 128)
            area = max(1.0, max_px) * (len(lines) * 17)
            ink = round(black / area, 4)
        nonspace = sum(v for k, v in pc.items() if k != "space")
        outline = sum(pc[k] for k in OUTLINE_CLASSES)
        texture = sum(pc[k] for k in TEXTURE_CLASSES)
        exact = sum(1 for line in lines for c in line
                    if c not in (HALF_SPACE, FULL_SPACE) and adv(c) == fixed_width(c))
        allowed = sum(1 for line in lines for c in line
                      if c not in (HALF_SPACE, FULL_SPACE) and c in SKILL_ALPHABET)
        per_piece.append({
            "res": rid,
            "rows": len(lines),
            "max_px": round(max_px, 1),
            "nonspace": nonspace,
            "space_share": round(pc["space"] / max(1, sum(pc.values())), 3),
            "outline_share": round(outline / max(1, nonspace), 3),
            "texture_share": round(texture / max(1, nonspace), 3),
            "kanji": pc["kanji"],
            "skill_alphabet_share": round(allowed / max(1, nonspace), 3),
            "grid_exact_advance_share": round(exact / max(1, nonspace), 3),
            "ink_density": ink,
        })

    total = sum(glyphs.values())
    nonspace_total = total - glyphs[HALF_SPACE] - glyphs[FULL_SPACE]
    classes = collections.Counter()
    for ch, n in glyphs.items():
        classes[glyph_class(ch)] += n
    in_alpha = sum(n for ch, n in glyphs.items() if ch in SKILL_ALPHABET)
    grid_exact = sum(n for ch, n in glyphs.items()
                     if ch not in (HALF_SPACE, FULL_SPACE) and adv(ch) == fixed_width(ch))

    def top(counter, k):
        return [{"g": g, "n": n, "cp": " ".join(f"U+{ord(c):04X}" for c in g if c != "/"),
                 "px": round(adv(g), 1) if len(g) == 1 else None}
                for g, n in counter.most_common(k)]

    inks = [p["ink_density"] for p in per_piece if p["ink_density"] is not None]
    doc = {
        "schema": "sjis_aa_slug_stats.v1",
        "source_url": args.source_url,
        "font": "Saitamaar (MS PGothic metrics), 16 px",
        "pieces": len(pieces),
        "input_set_sha256": hashlib.sha256(json.dumps(input_hashes).encode()).hexdigest(),
        "glyph_total": total,
        "nonspace_total": nonspace_total,
        "distinct_glyphs": len(glyphs),
        "space": {
            "half_U+0020": glyphs[HALF_SPACE],
            "full_U+3000": glyphs[FULL_SPACE],
            "half_px": adv(HALF_SPACE),
            "full_px": adv(FULL_SPACE),
            "runs_len2plus_mixed": mixed_space_runs,
            "runs_len2plus_mixed_alternating": alternating_runs,
            "runs_len2plus_half_only": pure_half_runs,
            "runs_len2plus_full_only": pure_full_runs,
            "lines": line_count,
            "adjacent_half_space_pairs": adjacent_half,
            "lines_starting_with_half_space": lead_half,
            "leading_indents": lead_total,
            "leading_indents_not_multiple_of_8px": lead_off_grid,
        },
        "class_share_of_nonspace": {k: round(v / nonspace_total, 4)
                                    for k, v in sorted(classes.items()) if k != "space"},
        "outline_share_of_nonspace": round(sum(classes[k] for k in OUTLINE_CLASSES) / nonspace_total, 4),
        "texture_share_of_nonspace": round(sum(classes[k] for k in TEXTURE_CLASSES) / nonspace_total, 4),
        "skill_alphabet_share_of_nonspace": round(in_alpha / nonspace_total, 4),
        "nonspace_with_saitamaar_advance_equal_to_fixed_cell": round(grid_exact / nonspace_total, 4),
        "pieces_with_grid_exact_advance_share_ge_0_9": sum(
            1 for p in per_piece if p["grid_exact_advance_share"] >= 0.9),
        "fixed_grid_relayout": {
            "note": "Each line re-laid on an 8 px half / 16 px full cell grid (East Asian Width W/F/A = full).",
            "glyph_center_drift_px_median": round(statistics.median(drift_all), 1),
            "glyph_center_drift_px_p90": round(sorted(drift_all)[int(0.9 * len(drift_all))], 1),
            "vertical_pairs_within_3px": vpair_total,
            "vertical_pairs_still_within_3px_after_relayout": vpair_kept,
        },
        "fixed_grid_snap": {
            "note": "Proportional x kept; each glyph centre quantised to an 8 px column.",
            "nonspace_glyphs": snap_glyphs,
            "glyphs_sharing_a_column_with_another": snap_collide,
            "vertical_pairs_landing_in_same_column": vpair_snap_kept,
        },
        "ink_density": {
            "note": "black px / (widest line px x rows x 17 px) on the 1-bit 16 px render",
            "median": round(statistics.median(inks), 4) if inks else None,
            "p10": round(sorted(inks)[int(0.1 * len(inks))], 4) if inks else None,
            "p90": round(sorted(inks)[int(0.9 * len(inks))], 4) if inks else None,
        },
        "top_glyphs": top(glyphs, args.top),
        "top_touching_bigrams": top(hbigrams, 40),
        "top_outline_stroke_ngrams": top(outline_ngrams, 60),
        "idiom_probe": {i: {"n": idiom_n[i], "pieces": len(idiom_where[i]),
                            "examples": idiom_where[i][:6]} for i in IDIOMS},
        "ascii_alnum_outside_skill_whitelist": {
            "pieces": pieces_with_letters_out,
            "counts": dict(letters_out.most_common()),
        },
        "top_vertical_pairs": top(vpairs, 30),
        "per_piece": per_piece,
        "input_posts_sha256": input_hashes,
    }
    data = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    if args.out.exists() and args.out.read_bytes() != data:
        print(f"refusing to overwrite {args.out} with different bytes", file=sys.stderr)
        return 3
    args.out.write_bytes(data)
    print(f"wrote {args.out} sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
