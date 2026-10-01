#!/usr/bin/env python3
"""Line-art style measurement over the AA-004 AAHub crawl, TRAIN partition only.

Question: is the minimalist line-art style of the ascii-art-authoring skill
(section 15: outline first, empty interiors, sparse ink, tone only as a
declared material, stroke idioms) the majority style of AAHub Shift_JIS art?

Inputs (all read-only, all verified at start):
  ARCHIVE  ascii-art-archive checkout; records are read as Git blobs at the
           commit the split names (f498eb306...), never from the work tree.
  SPLIT    screenshot-of-ascii-art-to-txt-converter/data/aahub_mlt_split.json
           Only `train_keys` are opened. Held-out records are never read.
  FONT     <ARCHIVE>/collections/aahub/Saitamaar.ttf at 16 px.

Two passes over the same stream:
  1. text pass, every TRAIN art piece (a piece = record aa[i] with >= 2 lines):
     SJIS-AUDIT class shares (glyph_class copied unchanged from
     ../sjis_aa_skill_audit/aa_slug_stats.py), tone bands, text runs, letter use,
     skill 15.5 idiom counts, outline n-grams, and an ink estimate from cached
     single-glyph ink counts.
  2. raster pass, a deterministic stratified sample (see SAMPLING) plus every
     piece of the calibration page 爆発・煙: render exactly as
     converter scripts/mlt_pairs.py render_aahub (Saitamaar 16 px, 8 px pad,
     17 px pitch, first baseline y=22, threshold < 128), then
       ink_share      = ink px / (widest line advance px * rows * 17)  [SJIS-AUDIT]
       envelope_blank = share of the row-span envelope (each text row from its
                        first to last non-space glyph, 17 px tall) with no ink
                        inside a 5x5 px window (Chebyshev radius 2).

SAMPLING: stratum = 汎用AA/<sub>, 2ch/<sub>, otherwise the top-level folder.
A piece (key, i) is rendered when
  int(sha256(f"{SEED}|{key}|{i}")[:12], 16) / 16**12 < min(1, TARGET / n_s)
where n_s is the stratum's TRAIN piece count from index.jsonl `pieces`.

Output: --out results.json (aggregates, exemplar candidates) and
--sample-out sample_pieces.jsonl.gz (one row per rendered piece). Existing
outputs are never replaced with different bytes.

Usage:
  python3 aa004_style_stats.py --archive ~/Projects/ascii-art-archive \
     --split ~/Projects/screenshot-of-ascii-art-to-txt-converter/data/aahub_mlt_split.json \
     --out results.json --sample-out sample_pieces.jsonl.gz --workers 2
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path

SEED = "aa004-line-art-style-v1"
TARGET = 2000
SPLIT_SHA256 = "983848da35bab64d91b59de02bb0d8c0998edfa0ec942d5588b7a485b6b52347"
CALIBRATION_KEY = "a60392576bd5eefca3ed22d55606b85f"  # 汎用AA/エフェクト/爆発・煙
SIZE_PX, PAD_PX, PITCH_PX, FIRST_BASELINE = 16, 8, 17, 22
HALF, FULL = " ", "　"
# Extension over SJIS-AUDIT (whose page has none): Unicode fixed-width spaces
# that AA-004 carries as numeric entities are spacing, not ink.
EXTRA_SPACES = set("             ")
SPACES = frozenset({HALF, FULL} | EXTRA_SPACES)

# ---- SJIS-AUDIT classes, copied unchanged from aa_slug_stats.py --------------
FINE_TEXTURE = set(".,;:'`､｡･・\"ﾞﾟ‘’´¨…‥゛゜")
FW_STROKE = set("＿￣／＼｜⌒―─‐ー－～")
ASCII_STROKE = set("_/\\|-~^=()[]{}<>!il")


def glyph_class(ch: str) -> str:
    cp = ord(ch)
    if ch in (HALF, FULL):
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


OUTLINE_CLASSES = {"fullwidth_stroke", "ascii_stroke", "kana"}
TEXTURE_CLASSES = {"fine_texture", "kanji"}
NGRAM_CLASSES = OUTLINE_CLASSES | {"fullwidth_other", "other_symbol"}
SKILL_ALPHABET = set("`~!^()-_+=;:'\",.\\/|<>[]{}") | set("´‾¡·") | set("oOvVTL7UcCxX")

# ---- skill 15.5 idiom table, grouped as the skill groups it -----------------
IDIOMS_155 = {
    "lobe": ["⌒ヽ", "(⌒", "⌒)", "（⌒", "⌒）"],
    "lobe_base": ["ヽ_", "_ノ", "ゝ__ノ"],
    "shoulder": ["／￣", "￣＼", "＿／", "＼＿"],
    "arch_bowl": ["／￣＼", "＼＿／"],
    "flat_arc": ["-―-", "‐--‐"],
    "sub_cell_step": ["､_", "_,", "'´"],
    "entry": ["｀ヽ"],
    "debris_material": ["从", "彡"],
    "base_flicker": [",,"],
}
CONTOUR_GROUPS = ["lobe", "lobe_base", "shoulder", "arch_bowl", "flat_arc", "sub_cell_step", "entry"]
ALL_155 = {s for v in IDIOMS_155.values() for s in v}

# ---- tone bands (this study's operational definition) ------------------------
DOT = set(".,;:'`､｡･・\"ﾞﾟ‘’´¨…‥゛゜｀")
# a dot band: >= 4 dot glyphs, touching or separated by single half spaces
DOT_BAND = re.compile("[%s](?:[%s]| (?=[%s]))*" % ((re.escape("".join(sorted(DOT))),) * 3))
H_HATCH = set("ﾆ二ニ三=≡")           # horizontal hatch (skill 15.6)
V_HATCH = set("il|ｌｉI!")            # vertical hatch (iiii lit wall, res9)
D_HATCH = set("/／\\＼")              # diagonal hatch (/// blush, speed lines)
HATCH_FAMILIES = {"h": H_HATCH, "v": V_HATCH, "d": D_HATCH}


def hatch_runs(line: str):
    """Yield (family, start, end) for runs of >= 3 touching glyphs of one family.
    Diagonal runs must repeat a single glyph (a mixed / \\ run is a zigzag stroke);
    vertical runs need >= 4 glyphs (`|l|` is usually a pillar, not tone)."""
    for m in HATCH_RE.finditer(line):
        yield m.lastgroup, m.start(), m.end()


HATCH_RE = re.compile("(?P<h>[%s]{3,})|(?P<v>[%s]{4,})|(?P<d>/{3,}|／{3,}|\\\\{3,}|＼{3,})" % (
    re.escape("".join(sorted(H_HATCH))), re.escape("".join(sorted(V_HATCH)))))


# ---- text runs (language, not shape) ----------------------------------------
def is_hira(c): return 0x3041 <= ord(c) <= 0x3096
def is_kata(c): return 0x30A1 <= ord(c) <= 0x30F6
def is_kanji(c): return 0x4E00 <= ord(c) <= 0x9FFF


JP_TEXT = re.compile("[ぁ-ゖァ-ヶ一-鿿ー、。！？…っ]{3,}")
LATIN_WORD = re.compile("[A-Za-z]{3,}")
FW_ALNUM = re.compile("[Ａ-Ｚａ-ｚ０-９]{2,}")
LATIN = re.compile("[A-Za-z]")
SHAPE_HIRA = set("くしつへゝゞ")  # hiragana regularly drawn as strokes


def text_spans(line: str):
    spans = []
    for m in JP_TEXT.finditer(line):
        s = m.group(0)
        hira = sum(1 for c in s if is_hira(c) and c not in SHAPE_HIRA)
        distinct = len(set(s))
        kanji_kata = sum(1 for c in s if is_kanji(c) or is_kata(c))
        if (hira >= 2 or kanji_kata >= 3) and distinct >= 3:
            spans.append(m.span())
    for m in LATIN_WORD.finditer(line):
        if len(set(m.group(0).lower())) >= 3:
            spans.append(m.span())
    for m in FW_ALNUM.finditer(line):
        spans.append(m.span())
    return spans


# ---- rendering ---------------------------------------------------------------
_font = None
_glyph_ink = {}


def font(path):
    global _font
    if _font is None:
        from PIL import ImageFont
        _font = ImageFont.truetype(str(path), SIZE_PX)
    return _font


def glyph_ink(ch, fpath):
    v = _glyph_ink.get(ch)
    if v is None:
        from PIL import Image, ImageDraw
        f = font(fpath)
        im = Image.new("L", (48, 40), 255)
        ImageDraw.Draw(im).text((8, 26), ch, font=f, fill=0, anchor="ls")
        v = sum(1 for b in im.tobytes() if b < 128)
        _glyph_ink[ch] = v
    return v


def render_metrics(lines, adv_lines, fpath):
    import numpy as np
    from PIL import Image, ImageDraw
    from scipy import ndimage
    f = font(fpath)
    width = max(int(math.ceil(f.getlength(l))) for l in lines) + 2 * PAD_PX
    height = len(lines) * PITCH_PX + 2 * PAD_PX
    im = Image.new("L", (width, height), 255)
    dr = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        dr.text((PAD_PX, FIRST_BASELINE + i * PITCH_PX), l, font=f, fill=0, anchor="ls")
    ink = np.asarray(im) < 128
    black = int(ink.sum())
    max_px = max(1.0, max((r[-1][1] if r else 0.0) for r in adv_lines))
    ink_share = black / (max_px * len(lines) * PITCH_PX)
    near = ndimage.maximum_filter(ink, size=5)
    env = blank = 0
    for i, row in enumerate(adv_lines):
        nz = [(a, b) for a, b, c in row if c not in SPACES]
        if not nz:
            continue
        x0 = PAD_PX + int(nz[0][0]); x1 = PAD_PX + int(math.ceil(nz[-1][1]))
        y0 = PAD_PX + i * PITCH_PX; y1 = y0 + PITCH_PX
        sl = near[y0:y1, x0:x1]
        env += sl.size
        blank += int(sl.size - sl.sum())
    return round(ink_share, 5), round(blank / env, 4) if env else None, black


# ---- per piece ----------------------------------------------------------------
_INFO = {}  # ch -> (advance px, SJIS-AUDIT class, single-glyph ink px, n-gram eligible)


def analyse_piece(text, adv, fpath, do_render):
    lines = text.rstrip("\n").split("\n")
    pc = collections.Counter()
    tone_dot = tone_h = tone_v = tone_d = 0
    dot_bands = dot_bands_closed = 0
    text_glyphs = 0
    latin_in_word = latin_shape = latin_shape_whitelist = 0
    shape_letters = collections.Counter()
    word_letters = collections.Counter()
    idioms = collections.Counter()
    ngrams = collections.Counter()
    band_spellings = collections.Counter()
    adv_lines = []
    interior_space_px = span_px = 0.0
    ink_est = 0
    for line in lines:
        x = 0.0
        row = []
        ngmask = []
        for ch in line:
            info = _INFO.get(ch)
            if info is None:
                cls = "space" if ch in EXTRA_SPACES else glyph_class(ch)
                info = _INFO[ch] = (adv(ch), cls, 0 if cls == "space" else glyph_ink(ch, fpath),
                                    cls in NGRAM_CLASSES)
            w = info[0]
            row.append((x, x + w, ch))
            x += w
            pc[info[1]] += 1
            ink_est += info[2]
            ngmask.append(info[3])
        adv_lines.append(row)
        nz = [k for k, (_, _, c) in enumerate(row) if c not in SPACES]
        if nz:
            a, b = nz[0], nz[-1]
            span_px += row[b][1] - row[a][0]
            interior_space_px += sum(row[k][1] - row[k][0] for k in range(a, b + 1) if row[k][2] in SPACES)
        # tone
        in_tone = [False] * len(line)
        for m in DOT_BAND.finditer(line):
            seg = m.group(0)
            ndots = sum(1 for c in seg if c != HALF)
            if ndots >= 4:
                tone_dot += ndots
                s0, e0 = m.span()
                dot_bands += 1
                # row-level 15.7.3 proxy: the band is closed on both sides by a glyph
                # (a stroke), not by a space or the line end
                if s0 > 0 and e0 < len(line) and line[s0 - 1] not in SPACES and line[e0] not in SPACES:
                    dot_bands_closed += 1
                for k in range(*m.span()):
                    in_tone[k] = True
                band_spellings["dot:" + "".join(sorted(set(seg) - {HALF}))] += 1
        for fam, s, e in hatch_runs(line):
            if any(in_tone[s:e]):
                continue
            n = e - s
            if fam == "h":
                tone_h += n
            elif fam == "v":
                tone_v += n
            else:
                tone_d += n
            band_spellings[fam + ":" + "".join(sorted(set(line[s:e])))] += 1
        # text and letters
        tspans = text_spans(line)
        intext = [False] * len(line)
        for s, e in tspans:
            for k in range(s, e):
                intext[k] = True
        text_glyphs += sum(intext)
        for mm in LATIN.finditer(line):
            k, ch = mm.start(), mm.group(0)
            if True:
                if intext[k]:
                    latin_in_word += 1
                    word_letters[ch] += 1
                else:
                    latin_shape += 1
                    shape_letters[ch] += 1
                    if ch in SKILL_ALPHABET:
                        latin_shape_whitelist += 1
        # outline n-grams (SJIS-AUDIT rule: runs of 2-3 touching outline-ish glyphs)
        # (n-gram glyphs are never spaces, so a mask run is a touching run)
        L = len(line)
        for i in range(L - 1):
            if ngmask[i] and ngmask[i + 1]:
                ngrams[line[i:i + 2]] += 1
                if i + 2 < L and ngmask[i + 2]:
                    ngrams[line[i:i + 3]] += 1
    for grp, lst in IDIOMS_155.items():
        for s in lst:
            k = text.count(s)
            if k:
                idioms[s] += k
    nonspace = sum(v for k, v in pc.items() if k != "space")
    if nonspace == 0:
        return None
    max_px = max(1.0, max((r[-1][1] if r else 0.0) for r in adv_lines))
    area = max_px * len(lines) * PITCH_PX
    tone = tone_dot + tone_h + tone_v + tone_d
    rec = {
        "rows": len(lines),
        "nonspace": nonspace,
        "max_px": round(max_px, 1),
        "outline_share": round(sum(pc[k] for k in OUTLINE_CLASSES) / nonspace, 4),
        "texture_share": round(sum(pc[k] for k in TEXTURE_CLASSES) / nonspace, 4),
        "tone_share": round(tone / nonspace, 4),
        "tone_dot": tone_dot, "tone_h": tone_h, "tone_v": tone_v, "tone_d": tone_d,
        "dot_bands": dot_bands, "dot_bands_closed": dot_bands_closed,
        "text_share": round(text_glyphs / nonspace, 4),
        "interior_space_share": round(interior_space_px / span_px, 4) if span_px else None,
        "ink_est": round(ink_est / area, 5),
        "latin_in_word": latin_in_word, "latin_shape": latin_shape,
        "latin_shape_whitelist": latin_shape_whitelist,
        "contour_idioms": sum(idioms[s] for g in CONTOUR_GROUPS for s in IDIOMS_155[g]),
        "idiom_groups": {g: sum(idioms[s] for s in IDIOMS_155[g]) for g in IDIOMS_155
                         if sum(idioms[s] for s in IDIOMS_155[g])},
    }
    if do_render:
        rec["ink_share"], rec["envelope_blank"], _ = render_metrics(lines, adv_lines, fpath)
    return rec, ngrams, band_spellings, shape_letters, word_letters, idioms


# ---- worker ----------------------------------------------------------------------
NUM_ENTITY = re.compile(r"&#(?:[0-9]+|[xX][0-9a-fA-F]+);")


def decode_entities(text):
    """AA-004 records keep some glyphs as numeric HTML character references
    (thin spaces U+2006/U+2009, blocks ░█▓, ～ ...). A browser shows the
    character, so decode them before measuring. Named entities are left alone
    (none were seen in a 300-page TRAIN probe)."""
    import html
    return NUM_ENTITY.sub(lambda m: html.unescape(m.group(0)), text)


def stratum_of(path):
    p = path.split("/")
    if p[0] in ("汎用AA", "2ch") and len(p) > 2:
        return p[0] + "/" + p[1]
    return p[0]


def selected(key, i, rate):
    h = int(hashlib.sha256(f"{SEED}|{key}|{i}".encode()).hexdigest()[:12], 16) / 16 ** 12
    return h < rate


def worker(args):
    archive, commit, fpath, jobs = args
    from fontTools.ttLib import TTFont
    tt = TTFont(str(fpath))
    upm = tt["head"].unitsPerEm
    cmap = tt.getBestCmap()
    hmtx = tt["hmtx"]
    cache = {}

    def adv(ch):
        v = cache.get(ch)
        if v is None:
            g = cmap.get(ord(ch))
            v = hmtx[g][0] * SIZE_PX / upm if g else 0.0
            cache[ch] = v
        return v

    cat = subprocess.Popen(["git", "-C", str(archive), "cat-file", "--batch"],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = []
    for key, stored, stratum, path, rate in jobs:
        cat.stdin.write(f"{commit}:{stored}\n".encode()); cat.stdin.flush()
        header = cat.stdout.readline().split()
        size = int(header[2])
        blob = cat.stdout.read(size); cat.stdout.read(1)
        rec = json.loads(gzip.decompress(blob))
        page = {"key": key, "stratum": stratum, "path": path, "pieces": [],
                "ngrams": collections.Counter(), "bands": collections.Counter(),
                "shape_letters": collections.Counter(), "word_letters": collections.Counter(),
                "idioms": collections.Counter(), "headers": 0, "entity_pieces": 0, "text_sha": hashlib.sha256()}
        for i, entry in enumerate(rec["aa"]):
            text = entry.get("value") or ""
            if text.strip("\n").count("\n") < 1:
                page["headers"] += 1
                continue
            page["text_sha"].update(hashlib.sha256(text.encode()).digest())
            if "&#" in text:
                dec = decode_entities(text)
                if dec != text:
                    page["entity_pieces"] += 1
                    text = dec
            do_r = selected(key, i, rate) or key == CALIBRATION_KEY
            res = analyse_piece(text, adv, fpath, do_r)
            if res is None:
                continue
            r, ng, bs, sl, wl, idm = res
            r["i"] = i
            r["sampled"] = selected(key, i, rate)
            page["pieces"].append(r)
            page["ngrams"].update(ng); page["bands"].update(bs)
            page["shape_letters"].update(sl); page["word_letters"].update(wl); page["idioms"].update(idm)
        page["text_sha"] = page["text_sha"].hexdigest()
        # keep only frequent n-grams per page to bound memory
        page["ngrams"] = collections.Counter(dict(page["ngrams"].most_common(400)))
        out.append(page)
    cat.stdin.close(); cat.wait()
    return out


# ---- aggregation -------------------------------------------------------------------
def q(vals, p):
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    return round(vals[min(len(vals) - 1, int(p * len(vals)))], 4)


def med(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 4) if vals else None


# Composite class rules. Thresholds are fixed in this file, anchored to the
# calibration page as stated in README section 3; sensitivity is reported.
def style_class(r, ink_max=0.05, blank_min=0.6, tone_line=0.25, tone_fill=0.6, text_min=0.3):
    if r["text_share"] >= text_min:
        return "text"
    ink = r.get("ink_share")
    blank = r.get("envelope_blank")
    if r["tone_share"] >= tone_fill:
        return "tone_dominant"
    if ink is not None and (ink > ink_max or (blank is not None and blank < blank_min)):
        return "dense_filled"
    if r["tone_share"] >= tone_line:
        return "line_plus_tone"
    return "line_minimal"


CLASSES = ["line_minimal", "line_plus_tone", "tone_dominant", "dense_filled", "text"]


def summarise(pieces, rendered_only=False, include_unsampled=False):
    P = [p for p in pieces if (not rendered_only or "ink_share" in p)]
    if not P:
        return None
    n = len(P)
    out = {
        "pieces": n,
        "outline_share_median": med([p["outline_share"] for p in P]),
        "outline_dominant_share": round(sum(p["outline_share"] >= 0.6 for p in P) / n, 4),
        "texture_dominant_share": round(sum(p["texture_share"] >= 0.8 for p in P) / n, 4),
        "tone_any_share": round(sum(p["tone_share"] > 0 for p in P) / n, 4),
        "tone_share_median": med([p["tone_share"] for p in P]),
        "tone_share_p90": q([p["tone_share"] for p in P], 0.9),
        "text_dominant_share": round(sum(p["text_share"] >= 0.3 for p in P) / n, 4),
        "interior_space_share_median": med([p["interior_space_share"] for p in P]),
        "ink_est_median": med([p["ink_est"] for p in P]),
        "ink_est_p90": q([p["ink_est"] for p in P], 0.9),
        "sparse_ink_le_0_05_share": round(sum(p["ink_est"] <= 0.05 for p in P) / n, 4),
        "dot_band_closed_share": (lambda a, b: round(a / b, 4) if b else None)(
            sum(p["dot_bands_closed"] for p in P), sum(p["dot_bands"] for p in P)),
        "hatch_any_share": round(sum((p["tone_h"] + p["tone_v"] + p["tone_d"]) > 0 for p in P) / n, 4),
        "dot_tone_any_share": round(sum(p["tone_dot"] > 0 for p in P) / n, 4),
        "contour_idiom_any_share": round(sum(p["contour_idioms"] > 0 for p in P) / n, 4),
        "contour_idioms_per_100_glyphs_median": med([100 * p["contour_idioms"] / p["nonspace"] for p in P]),
        "latin_letters_in_words_share": (lambda a, b: round(a / (a + b), 4) if a + b else None)(
            sum(p["latin_in_word"] for p in P), sum(p["latin_shape"] for p in P)),
        "nonspace_median": med([p["nonspace"] for p in P]),
    }
    R = [p for p in P if "ink_share" in p and (p["sampled"] or include_unsampled)]
    if R:
        out["rendered"] = len(R)
        out["ink_share_median"] = med([p["ink_share"] for p in R])
        out["ink_share_p10"] = q([p["ink_share"] for p in R], 0.1)
        out["ink_share_p90"] = q([p["ink_share"] for p in R], 0.9)
        out["envelope_blank_median"] = med([p["envelope_blank"] for p in R])
        cls = collections.Counter(style_class(p) for p in R)
        out["class_share"] = {c: round(cls[c] / len(R), 4) for c in CLASSES}
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--split", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sample-out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit-pages", type=int, default=0, help="debug: first N TRAIN pages only")
    ap.add_argument("--keys", default="", help="debug: comma-separated TRAIN keys only")
    args = ap.parse_args()
    if args.workers > 2:
        raise SystemExit("at most 2 workers (operator memory bound)")

    split_bytes = args.split.read_bytes()
    if hashlib.sha256(split_bytes).hexdigest() != SPLIT_SHA256:
        raise SystemExit("split sha256 mismatch")
    split = json.loads(split_bytes)
    commit = split["archive_commit"]
    index = subprocess.run(["git", "-C", str(args.archive), "show", f"{commit}:collections/aahub-mlt/index.jsonl"],
                           check=True, capture_output=True).stdout
    if hashlib.sha256(index).hexdigest() != split["index_sha256"]:
        raise SystemExit("index sha256 mismatch")
    rows = {r["key"]: r for r in map(json.loads, index.decode().splitlines()) if r}
    train = list(split["train_keys"])
    held = set(split["held_out_keys"])
    assert not (set(train) & held), "train/held-out overlap"
    if args.limit_pages:
        train = train[:args.limit_pages]
    if args.keys:
        want = args.keys.split(",")
        train = [k for k in want if k in set(split["train_keys"])]
    fpath = args.archive / "collections/aahub/Saitamaar.ttf"
    font_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()

    n_s = collections.Counter()
    for k in split["train_keys"]:  # rates always from the full TRAIN, also in debug runs
        n_s[stratum_of(rows[k]["path"])] += rows[k]["pieces"]
    rate = {s: min(1.0, TARGET / n) for s, n in n_s.items()}

    jobs = [(k, rows[k]["stored"], stratum_of(rows[k]["path"]), rows[k]["path"], rate[stratum_of(rows[k]["path"])])
            for k in train]
    for j in jobs:
        assert j[0] not in held
    chunks = [jobs[i:i + 50] for i in range(0, len(jobs), 50)]
    work = [(args.archive, commit, fpath, c) for c in chunks]

    # ---- streaming aggregation (pages are not retained) ----
    by_stratum = collections.defaultdict(list)
    by_top = collections.defaultdict(list)
    by_sub = collections.defaultdict(list)
    allp = []
    ngr = collections.defaultdict(collections.Counter)  # stratum -> ngrams
    ngr_pages = collections.defaultdict(collections.Counter)
    bands = collections.defaultdict(collections.Counter)
    shape_letters = collections.defaultdict(collections.Counter)
    word_letters = collections.defaultdict(collections.Counter)
    idioms = collections.defaultdict(collections.Counter)
    page_rows = []
    input_hashes = []
    headers = 0
    entity_pieces = 0
    n_pages = 0

    def stream():
        if args.workers == 1:
            for w in work:
                yield from worker(w)
        else:
            import multiprocessing as mp
            with mp.get_context("spawn").Pool(args.workers) as pool:
                for k, res in enumerate(pool.imap(worker, work)):
                    if k % 20 == 0:
                        print(f"chunk {k + 1}/{len(work)}", file=sys.stderr, flush=True)
                    yield from res

    for pg in stream():
        n_pages += 1
        for p in pg["pieces"]:
            if not p["sampled"] and pg["key"] != CALIBRATION_KEY:
                p.pop("idiom_groups", None)
        st = pg["stratum"]
        top = pg["path"].split("/")[0]
        sub = "/".join(pg["path"].split("/")[:2])
        headers += pg["headers"]
        entity_pieces += pg["entity_pieces"]
        input_hashes.append([pg["key"], pg["text_sha"]])
        for p in pg["pieces"]:
            p["key"] = pg["key"]; p["stratum"] = st
        by_stratum[st].extend(pg["pieces"]); by_top[top].extend(pg["pieces"]); by_sub[sub].extend(pg["pieces"])
        allp.extend(pg["pieces"])
        ngr[st].update(pg["ngrams"])
        for g in pg["ngrams"]:
            ngr_pages[st][g] += 1
        bands[st].update(pg["bands"]); shape_letters[st].update(pg["shape_letters"])
        word_letters[st].update(pg["word_letters"]); idioms[st].update(pg["idioms"])
        if pg["pieces"]:
            page_rows.append({"key": pg["key"], "path": pg["path"], "stratum": st, "pieces": len(pg["pieces"]),
                              **{k: v for k, v in summarise(pg["pieces"]).items()
                                 if k in ("outline_dominant_share", "tone_any_share", "tone_share_median",
                                          "text_dominant_share", "ink_est_median", "contour_idiom_any_share",
                                          "interior_space_share_median")}})

    # TRAIN-wide weighted class shares from the sample (weight = n_s / sampled_s)
    sampled = [p for p in allp if p["sampled"]]
    samp_n = collections.Counter(p["stratum"] for p in sampled)
    real_n = collections.Counter(p["stratum"] for p in allp)
    wt = {s: real_n[s] / samp_n[s] for s in samp_n}
    W = sum(wt[p["stratum"]] for p in sampled)

    def wshare(pred):
        return round(sum(wt[p["stratum"]] for p in sampled if pred(p)) / W, 4)

    sens = {}
    for ink_max in (0.04, 0.05, 0.07):
        for blank_min in (0.5, 0.6, 0.7):
            for tone_line in (0.15, 0.25, 0.35):
                key = f"ink<={ink_max},blank>={blank_min},tone<{tone_line}"
                sens[key] = wshare(lambda p: style_class(p, ink_max, blank_min, tone_line) == "line_minimal")
    weighted = {c: wshare(lambda p, c=c: style_class(p) == c) for c in CLASSES}
    weighted["outline_dominant"] = wshare(lambda p: p["outline_share"] >= 0.6)
    weighted["line_minimal_or_line_plus_tone"] = round(weighted["line_minimal"] + weighted["line_plus_tone"], 4)

    # design-effect-free CI per stratum for line_minimal (pieces within a page are clustered;
    # a page-cluster bootstrap is reported for the TRAIN-wide figure)
    import random
    rnd = random.Random(SEED)
    page_groups = collections.defaultdict(list)
    for p in sampled:
        page_groups[(p["stratum"], p["key"])].append(p)
    strata_pages = collections.defaultdict(list)
    for (s, k), lst in page_groups.items():
        strata_pages[s].append(lst)
    boots = {"line_minimal": [], "line_minimal_or_line_plus_tone": [], "outline_dominant": []}
    for _ in range(300):
        num = collections.Counter(); den = 0.0
        for s, groups in strata_pages.items():
            pick = [groups[rnd.randrange(len(groups))] for _ in groups]
            flat = [p for g in pick for p in g]
            if not flat:
                continue
            w = real_n[s] / len(flat)
            den += w * len(flat)
            for p in flat:
                c = style_class(p)
                num["line_minimal"] += w * (c == "line_minimal")
                num["line_minimal_or_line_plus_tone"] += w * (c in ("line_minimal", "line_plus_tone"))
                num["outline_dominant"] += w * (p["outline_share"] >= 0.6)
        for k in boots:
            boots[k].append(num[k] / den)
    boot_ci = {k: [round(sorted(v)[7], 4), round(sorted(v)[292], 4)] for k, v in boots.items()}

    # ink estimate vs render agreement
    pairs = [(p["ink_est"], p["ink_share"]) for p in allp if "ink_share" in p and p["ink_share"] > 0]
    ratios = sorted(a / b for a, b in pairs)

    # n-grams outside skill 15.5, by stratum, with page spread
    new_ngrams = {}
    for st in sorted(ngr):
        rowsn = []
        for g, n in ngr[st].most_common(200):
            if g in ALL_155 or any(g in s or s in g for s in ALL_155):
                continue
            rowsn.append({"g": g, "n": n, "pages": ngr_pages[st][g]})
            if len(rowsn) >= 25:
                break
        new_ngrams[st] = rowsn
    total_ngr = collections.Counter()
    total_ngr_pages = collections.Counter()
    for st in ngr:
        total_ngr.update(ngr[st]); total_ngr_pages.update(ngr_pages[st])

    cal = [p for p in allp if p["key"] == CALIBRATION_KEY]
    doc = {
        "schema": "aa004_line_art_style.v1",
        "inputs": {
            "archive_commit": commit, "index_sha256": split["index_sha256"],
            "split_path": str(args.split), "split_sha256": SPLIT_SHA256,
            "partition": "train_keys only", "train_pages_read": n_pages,
            "font": str(fpath), "font_sha256": font_sha,
            "render": {"size_px": SIZE_PX, "pad_px": PAD_PX, "pitch_px": PITCH_PX,
                       "first_baseline": FIRST_BASELINE, "threshold": "<128 on L"},
            "seed": SEED, "target_per_stratum": TARGET,
            "input_set_sha256": hashlib.sha256(json.dumps(sorted(input_hashes)).encode()).hexdigest(),
        },
        "counts": {"art_pieces": len(allp), "headers_skipped": headers,
                   "pieces_with_numeric_entities_decoded": entity_pieces, "rendered_sampled": len(sampled),
                   "rendered_calibration": len(cal)},
        "sampling": {s: {"stratum_pieces_index": n_s[s], "rate": round(rate[s], 5), "art_pieces": real_n[s],
                         "sampled": samp_n[s]} for s in sorted(n_s)},
        "train_total": summarise(allp),
        "train_weighted_from_sample": {"class_share": weighted, "page_cluster_bootstrap_95ci": boot_ci,
                                       "line_minimal_sensitivity": sens},
        "by_stratum": {s: summarise(v) for s, v in sorted(by_stratum.items())},
        "by_top_level": {s: summarise(v) for s, v in sorted(by_top.items())},
        "by_sub_folder": {s: summarise(v) for s, v in sorted(by_sub.items()) if len(v) >= 300},
        "calibration_bakuhatsu_kemuri": summarise(cal, include_unsampled=True),
        "ink_est_over_render_ratio": {"n": len(ratios), "median": q(ratios, 0.5), "p10": q(ratios, 0.1),
                                      "p90": q(ratios, 0.9)},
        "idioms_155_by_stratum": {s: dict(idioms[s].most_common()) for s in sorted(idioms)},
        "tone_band_spellings_by_stratum": {s: [[g, n] for g, n in bands[s].most_common(15)] for s in sorted(bands)},
        "shape_letters_by_stratum": {s: dict(shape_letters[s].most_common(15)) for s in sorted(shape_letters)},
        "word_letters_total": sum(sum(c.values()) for c in word_letters.values()),
        "outline_ngrams_not_in_155_by_stratum": new_ngrams,
        "outline_ngrams_not_in_155_total": [
            {"g": g, "n": n, "pages": total_ngr_pages[g]} for g, n in total_ngr.most_common(400)
            if not (g in ALL_155 or any(g in s or s in g for s in ALL_155))][:80],
        "pages": page_rows,
    }
    data = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode()
    if args.out.exists() and args.out.read_bytes() != data:
        print(f"refusing to overwrite {args.out} with different bytes", file=sys.stderr)
        return 3
    args.out.write_bytes(data)
    srows = [p for p in allp if "ink_share" in p]
    sdata = "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in
                    sorted(srows, key=lambda p: (p["key"], p["i"]))).encode()
    sgz = gzip.compress(sdata, mtime=0)
    if args.sample_out.exists() and gzip.decompress(args.sample_out.read_bytes()) != sdata:
        print(f"refusing to overwrite {args.sample_out} with different bytes", file=sys.stderr)
        return 3
    args.sample_out.write_bytes(sgz)
    print(f"wrote {args.out} sha256={hashlib.sha256(data).hexdigest()}")
    print(f"wrote {args.sample_out} rows={len(srows)} content_sha256={hashlib.sha256(sdata).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
