#!/usr/bin/env python3
"""Corpus-wide Shift_JIS AA combination and pattern extraction (AAHub, training slugs only).

Scales docs/research/ascii/sjis_aa_skill_audit/aa_slug_stats.py from one page to
every training slug of a pinned ascii-art-archive snapshot. The categories follow
ascii-art-authoring section 15:

  idioms     15.5 stroke-idiom table, counted verbatim
  bigrams    touching glyph pairs (no space between), stroke glyphs only
  trigrams   touching glyph triples, stroke glyphs only
  stacks     vertical pairs on adjacent rows whose centres lie within 3 px
             (15.4.4), keyed by the signed centre offset in px
  bands      tone bands (section 8, 15.7): runs of fine-texture glyphs reduced
             to their shortest repeating period
  spaces     whitespace spellings (15.4), with law violations counted
  pages      outline / tone / mixed tag per page (15.7.4)

Mirrors use the 15.5 swap table. A pooled count adds a combination's count
to its mirror's count.

Inputs are read from Git objects at the split's archive commit, never from
the archive worktree. The split file (screenshot converter
data/aahub_split.json) decides which slugs are training. Held-out slugs are
never opened. The top combinations are rendered in the given font at 16 px
on its advance lattice, and the viewer draws those rows without the font.
An existing output is never replaced by different bytes.

Usage:
    python3 scripts/sjis_corpus_combos.py ARCHIVE SPLIT.json FONT.ttf --out OUT.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

PX = 16
PITCH = 17  # AAHub line pitch at 16 px (skill 15.3.3)
HALF, FULL = " ", "　"
SPACES = (HALF, FULL)

FINE_TEXTURE = set(".,;:'`､｡･・\"ﾞﾟ‘’´¨…‥゛゜")
FW_STROKE = set("＿￣／＼｜⌒―─‐ー－～")
ASCII_STROKE = set("_/\\|-~^=()[]{}<>!il")
# Kana that the 15.5 idioms use as strokes, not as text.
KANA_STROKES = set("ヽヾノﾉゝゞへヘﾍくイｲソｿツﾂシｼミﾐトﾞﾟｰﾆニ")
# 从/彡 are the 15.5 debris material. 二 (103k) and the rest are hatching and
# stroke kanji: 二 is the 10th most frequent non-space glyph in the training set.
MATERIAL_KANJI = set("从彡二丶丿乂厂冂")

IDIOMS = ["⌒ヽ", "(⌒", "⌒)", "（⌒", "⌒）", "ヽ_", "_ノ", "ゝ__ノ", "／￣", "￣＼", "＿／", "＼＿",
          "／￣＼", "＼＿／", "-―-", "‐--‐", "､_", "_,", "'´", "从", "彡", ",,",
          "ヽ＿", "＿ノ", "､､", ";;", "::", ".:", ":.", "ﾉ(", ")ヽ", "´`", "｀ヽ", "ヽ､", "(_", "_)"]

MIRROR = {"ヽ": "ノ", "ノ": "ヽ", "ﾉ": "ヽ", "(": ")", ")": "(", "（": "）", "）": "（",
          "／": "＼", "＼": "／", "/": "\\", "\\": "/", "｀": "´", "´": "｀",
          "<": ">", ">": "<", "[": "]", "]": "[", "{": "}", "}": "{", "「": "」", "」": "「"}
# Glyphs the 15.5 table treats as horizontally symmetric.
SYMMETRIC = set("⌒＿￣｜|_-―─‐ー－=:;.,'!iil从彡ｌ^~～\"*+#oO0VvTxXAHIMUWY人亠丶")


def glyph_class(ch: str) -> str:
    cp = ord(ch)
    if ch in SPACES:
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


def is_stroke(ch: str) -> bool:
    """A glyph used as line art. Text kana, kanji and alphanumerics are excluded, so
    captions do not dominate the combination counts. i and l stay in (skill 15.6)."""
    k = glyph_class(ch)
    if k in ("fine_texture", "fullwidth_stroke", "ascii_stroke", "other_symbol"):
        return True
    if k == "fullwidth_other":
        return not ch.isalnum()
    if k == "ascii_other":
        return not ch.isalnum()
    return ch in KANA_STROKES or ch in MATERIAL_KANJI


def is_outline(g: str) -> bool:
    """A combination with at least one stroke that is not fine texture. All-texture
    combinations are tone and are reported as bands (section 8, 15.7)."""
    return any(c not in FINE_TEXTURE for c in g)


def mirror(combo: str) -> tuple[str, bool]:
    """Reverse and swap (skill 4.7.7 / 15.5). exact=False when a glyph has no known
    partner and is not known to be symmetric."""
    out, exact = [], True
    for ch in reversed(combo):
        if ch in MIRROR:
            out.append(MIRROR[ch])
        else:
            out.append(ch)
            if ch not in SYMMETRIC and ch not in SPACES:
                exact = False
    return "".join(out), exact


def period(run: str) -> str:
    for p in range(1, 4):
        unit = run[:p]
        if (unit * (len(run) // p + 1))[: len(run)] == run:
            return unit
    return ""


def git(archive: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(archive), *args], check=True, capture_output=True).stdout


def read_blobs(archive: Path, specs: list[str]) -> list[bytes]:
    """git cat-file --batch over commit:path specs, in order."""
    proc = subprocess.run(["git", "-C", str(archive), "cat-file", "--batch"],
                          input=("\n".join(specs) + "\n").encode("utf-8"),
                          capture_output=True, check=True)
    data, out, i = proc.stdout, [], 0
    for spec in specs:
        nl = data.index(b"\n", i)
        header = data[i:nl].split()
        if header[-1] == b"missing":
            raise SystemExit(f"missing blob: {spec}")
        size = int(header[2])
        out.append(data[nl + 1: nl + 1 + size])
        i = nl + 1 + size + 1
    return out


class Metrics:
    def __init__(self, font_path: Path):
        tt = TTFont(str(font_path))
        self.upm = tt["head"].unitsPerEm
        self.cmap = tt.getBestCmap()
        self.hmtx = tt["hmtx"]
        self.pil = ImageFont.truetype(str(font_path), PX)

    def adv(self, ch: str) -> float:
        g = self.cmap.get(ord(ch))
        return self.hmtx[g][0] * PX / self.upm if g else float(PX)

    def width(self, s: str) -> float:
        return sum(self.adv(c) for c in s)

    def render(self, rows: list[tuple[float, str]]) -> list[str]:
        """rows: [(x_offset_px, text)] one per line, drawn at 16 px on a 17 px pitch.
        Returns '#'/'.' strings, one per pixel row, cropped to the ink columns."""
        width = int(math.ceil(max(x + self.width(t) for x, t in rows))) + 2
        img = Image.new("L", (max(width, 1), PITCH * len(rows) + 2), 0)
        d = ImageDraw.Draw(img)
        for r, (x, text) in enumerate(rows):
            pen = x
            for ch in text:
                d.text((pen, r * PITCH), ch, font=self.pil, fill=255)
                pen += self.adv(ch)
        w, h = img.size
        px = img.load()
        grid = [["#" if px[xx, yy] > 127 else "." for xx in range(w)] for yy in range(h)]
        cols = [xx for xx in range(w) if any(grid[yy][xx] == "#" for yy in range(h))]
        if not cols:
            return ["." * w for _ in range(h)]
        lo, hi = max(0, cols[0] - 1), min(w, cols[-1] + 2)
        return ["".join(row[lo:hi]) for row in grid]


def centres(line: str, m: Metrics) -> list[tuple[float, str]]:
    x, out = 0.0, []
    for ch in line:
        a = m.adv(ch)
        if ch not in SPACES:
            out.append((x + a / 2, ch))
        x += a
    return out


def space_spelling(run: str) -> str:
    return run.replace(FULL, "F").replace(HALF, "h")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archive", type=Path)
    ap.add_argument("split", type=Path)
    ap.add_argument("font", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--top", type=int, default=300, help="entries kept per counted category")
    ap.add_argument("--render", type=int, default=120, help="entries rendered per viewable category")
    args = ap.parse_args(argv)

    split_bytes = args.split.read_bytes()
    split = json.loads(split_bytes)
    commit = split["archive_commit"]
    manifest = git(args.archive, "show", f"{commit}:MANIFEST.tsv")
    if hashlib.sha256(manifest).hexdigest() != split["manifest_sha256"]:
        raise SystemExit("archive manifest does not match the split")
    prefix = split["collection"] + "/"
    names = git(args.archive, "ls-tree", "-r", "--name-only", commit, "--", split["collection"]).decode().splitlines()
    held_out = set(split["held_out_slugs"])
    by_slug: dict[str, list[str]] = collections.defaultdict(list)
    for n in names:
        parts = n[len(prefix):].split("/")
        if len(parts) == 2 and parts[1].startswith("res") and parts[1].endswith(".txt"):
            by_slug[parts[0]].append(n)
    train = sorted(s for s in by_slug if s not in held_out)
    if set(train) & held_out:
        raise SystemExit("held-out slug in training set")

    m = Metrics(args.font)
    glyphs = collections.Counter()
    bigrams = collections.Counter()
    trigrams = collections.Counter()
    stacks_outline = collections.Counter()
    idioms = collections.Counter()
    idiom_pages = collections.Counter()
    idiom_slugs: dict[str, set] = collections.defaultdict(set)
    stacks = collections.Counter()
    bands = collections.Counter()
    band_examples: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    spellings = collections.Counter()
    slug_bigrams: dict[str, collections.Counter] = {}
    page_tags = collections.Counter()
    slug_tags: dict[str, collections.Counter] = {}
    law = collections.Counter()
    input_hashes = []
    pages = lines_total = 0

    for slug in train:
        paths = sorted(by_slug[slug])
        blobs = read_blobs(args.archive, [f"{commit}:{p}" for p in paths])
        sb = collections.Counter()
        st = collections.Counter()
        for path, blob in zip(paths, blobs):
            input_hashes.append([path[len(prefix):], hashlib.sha256(blob).hexdigest()])
            text = blob.decode("utf-8")
            lines = text.rstrip("\n").split("\n")
            pages += 1
            cls = collections.Counter()
            for line in lines:
                lines_total += 1
                law["adjacent_half_space_pairs"] += line.count("  ")
                law["lines_starting_with_half_space"] += line.startswith(HALF)
                for ch in line:
                    glyphs[ch] += 1
                    cls[glyph_class(ch)] += 1
                for tok in re.findall(r"[^ 　]+", line):
                    for i in range(len(tok) - 1):
                        g = tok[i:i + 2]
                        if is_stroke(g[0]) and is_stroke(g[1]):
                            bigrams[g] += 1
                            sb[g] += 1
                    for i in range(len(tok) - 2):
                        g = tok[i:i + 3]
                        if all(is_stroke(c) for c in g):
                            trigrams[g] += 1
                    for run in re.findall(r"[" + re.escape("".join(sorted(FINE_TEXTURE))) + r"]{4,}", tok):
                        p = period(run)
                        key = p if p else "(aperiodic)"
                        bands[key] += 1
                        band_examples[key][run[:12]] += 1
                inner = line.strip(" 　")
                for run in re.findall(r"[ 　]{2,}", inner):
                    spellings[space_spelling(run)] += 1
            for idiom in IDIOMS:
                k = text.count(idiom)
                if k:
                    idioms[idiom] += k
                    idiom_pages[idiom] += 1
                    idiom_slugs[idiom].add(slug)
            for r in range(len(lines) - 1):
                lower = centres(lines[r + 1], m)
                if not lower:
                    continue
                lx = [c for c, _ in lower]
                for cx, ch in centres(lines[r], m):
                    if not is_stroke(ch):
                        continue
                    # lower centres are sorted: scan the window around cx
                    lo = 0
                    while lo < len(lx) and lx[lo] < cx - 3:
                        lo += 1
                    j = lo
                    while j < len(lx) and lx[j] <= cx + 3:
                        if is_stroke(lower[j][1]):
                            key = (ch, lower[j][1], int(round(lx[j] - cx)))
                            stacks[key] += 1
                            if ch not in FINE_TEXTURE and lower[j][1] not in FINE_TEXTURE:
                                stacks_outline[key] += 1
                        j += 1
            nonspace = sum(v for k, v in cls.items() if k != "space")
            outline = sum(cls[k] for k in ("fullwidth_stroke", "ascii_stroke", "kana"))
            texture = sum(cls[k] for k in ("fine_texture", "kanji"))
            tag = ("empty" if not nonspace else "outline" if outline / nonspace >= 0.6
                   else "tone" if texture / nonspace >= 0.6 else "mixed")
            page_tags[tag] += 1
            st[tag] += 1
        slug_bigrams[slug] = sb
        slug_tags[slug] = st

    def pooled(counter, key_fn=lambda k: k):
        out = {}
        for k, n in counter.items():
            mk, exact = mirror(key_fn(k))
            out[k] = (mk, exact, n + (counter.get(mk, 0) if mk != key_fn(k) else 0))
        return out

    viewable = []

    def add_view(category: str, key: str, rows: list[tuple[float, str]], mrows: list[tuple[float, str]],
                 count: int, extra: dict) -> None:
        viewable.append({
            "category": category, "key": key, "count": count,
            "lattice": [t for _, t in rows], "mirror_lattice": [t for _, t in mrows],
            "offsets_px": [round(x, 2) for x, _ in rows],
            "rows": m.render(rows), "mirror_rows": m.render(mrows), **extra,
        })

    def seq_entries(counter, category, render, keep=lambda g: True):
        pool = pooled(counter)
        out = []
        ranked = [(g, n) for g, n in counter.most_common() if keep(g)][: args.top]
        shown = 0
        for rank, (g, n) in enumerate(ranked, 1):
            mk, exact, pn = pool[g]
            e = {"g": g, "n": n, "mirror": mk, "mirror_exact": exact, "pooled_n": pn,
                 "px": [round(m.adv(c), 2) for c in g], "cp": [f"U+{ord(c):04X}" for c in g]}
            out.append(e)
            # a run of one repeated glyph is a stroke or hatching, not a combination
            if shown < render and len(set(g)) > 1:
                shown += 1
                add_view(category, g, [(0.0, g)], [(0.0, mk)], n,
                         {"mirror_exact": exact, "pooled_n": pn, "rank": rank})
        return out

    idiom_list = []
    for rank, (g, n) in enumerate(sorted(idioms.items(), key=lambda kv: -kv[1]), 1):
        mk, exact = mirror(g)
        idiom_list.append({"g": g, "n": n, "pages": idiom_pages[g], "slugs": len(idiom_slugs[g]),
                           "mirror": mk, "mirror_exact": exact,
                           "mirror_n": idioms.get(mk, 0) if mk != g else None})
        add_view("idiom", g, [(0.0, g)], [(0.0, mk)], n,
                 {"mirror_exact": exact, "pages": idiom_pages[g], "slugs": len(idiom_slugs[g]), "rank": rank})

    bigram_list = seq_entries(bigrams, "bigram", 0)
    trigram_list = seq_entries(trigrams, "trigram", 0)
    bigram_outline = seq_entries(bigrams, "bigram", args.render, is_outline)
    trigram_outline = seq_entries(trigrams, "trigram", args.render, is_outline)

    def stack_entries(counter, render):
      out = []
      shown = 0
      for rank, ((up, lo, dx), n) in enumerate(counter.most_common(args.top), 1):
        mu, eu = mirror(up)
        ml, el = mirror(lo)
        mdx = -dx
        pn = n + (counter.get((mu, ml, mdx), 0) if (mu, ml, mdx) != (up, lo, dx) else 0)
        out.append({"upper": up, "lower": lo, "dx_px": dx, "n": n, "pooled_n": pn,
                           "mirror": [mu, ml, mdx], "mirror_exact": eu and el})
        if shown < render and up != lo:
            shown += 1
            au, al = m.adv(up), m.adv(lo)
            # place so that lower centre - upper centre == dx; keep both x >= 0
            xu, xl = 0.0, au / 2 + dx - al / 2
            shift = -min(xu, xl)
            rows = [(xu + shift, up), (xl + shift, lo)]
            amu, aml = m.adv(mu), m.adv(ml)
            mxu, mxl = 0.0, amu / 2 + mdx - aml / 2
            mshift = -min(mxu, mxl)
            add_view("stack", f"{up} over {lo} dx{dx:+d}", rows, [(mxu + mshift, mu), (mxl + mshift, ml)], n,
                     {"mirror_exact": eu and el, "pooled_n": pn, "dx_px": dx, "rank": rank})

      return out

    stack_list = stack_entries(stacks, 0)
    stack_outline = stack_entries(stacks_outline, args.render)

    band_list = []
    for rank, (p, n) in enumerate(bands.most_common(60), 1):
        ex = [r for r, _ in band_examples[p].most_common(3)]
        band_list.append({"period": p, "n": n, "examples": ex})
        if p != "(aperiodic)" and rank <= 40:
            sample = (p * 8)[:8]
            mk, exact = mirror(sample)
            add_view("band", p, [(0.0, sample)], [(0.0, mk)], n, {"mirror_exact": exact, "rank": rank})

    spell_total = sum(spellings.values())
    doc = {
        "schema": "sjis_corpus_combos.v1",
        "producer": "scripts/sjis_corpus_combos.py",
        "skill_basis": "ascii-art-authoring section 15 (15.3 metrics, 15.4 whitespace, 15.5 idioms/mirror table, 15.7 tone)",
        "archive_commit": commit,
        "manifest_sha256": split["manifest_sha256"],
        "split_sha256": hashlib.sha256(split_bytes).hexdigest(),
        "partition": "train",
        "held_out_slugs_excluded": len(held_out),
        "font": args.font.name,
        "font_sha256": hashlib.sha256(args.font.read_bytes()).hexdigest(),
        "px": PX, "line_pitch_px": PITCH,
        "slugs": len(train), "pages": pages, "lines": lines_total,
        "input_set_sha256": hashlib.sha256(json.dumps(input_hashes, ensure_ascii=False).encode()).hexdigest(),
        "glyph_total": sum(glyphs.values()), "distinct_glyphs": len(glyphs),
        "whitespace_law": dict(law),
        "page_tags": dict(page_tags),
        "notes": {
            "stroke_filter": "bigrams/trigrams/stacks keep only line-art glyphs: strokes, fine texture, symbols, "
                             "the 15.5 stroke kana and 从/彡. Text kana, kanji and alphanumerics other than i/l are excluded.",
            "outline": "*_outline lists keep combinations with at least one non-fine-texture glyph (stacks: both); "
                       "the unfiltered lists include tone, which bands summarise. Only *_outline, idioms and bands are rendered; "
                       "rendered bigrams/trigrams/stacks skip one-glyph repeats (hatching, long strokes), which stay counted.",
            "stack": "adjacent-row glyph pair whose centres differ by <= 3 px (15.4.4); dx_px = lower - upper centre",
            "pooled_n": "count + count of the 15.5-mirrored combination (mirror_exact=false: a glyph has no known partner)",
            "band": "maximal run (len >= 4) of fine-texture glyphs reduced to its shortest period (<= 3)",
            "spaces": "interior whitespace runs of length >= 2; F = U+3000 (11 px), h = U+0020 (5 px)",
        },
        "top_glyphs": [{"g": g, "n": n, "px": round(m.adv(g), 2), "class": glyph_class(g)}
                       for g, n in glyphs.most_common(args.top)],
        "idioms": idiom_list,
        "bigrams": bigram_list,
        "trigrams": trigram_list,
        "stacks": stack_list,
        "bigrams_outline": bigram_outline,
        "trigrams_outline": trigram_outline,
        "stacks_outline": stack_outline,
        "bands": band_list,
        "space_spellings": [{"spelling": s, "n": n, "share": round(n / max(spell_total, 1), 4),
                             "px": round(s.count("F") * m.adv(FULL) + s.count("h") * m.adv(HALF), 1)}
                            for s, n in spellings.most_common(60)],
        "per_slug": {s: {"pages": len(by_slug[s]), "tags": dict(slug_tags[s]),
                         "top_bigrams": [[g, n] for g, n in slug_bigrams[s].most_common(8)]}
                     for s in train},
        "viewable": viewable,
    }
    data = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    if args.out.exists() and args.out.read_bytes() != data:
        print(f"refusing to overwrite {args.out} with different bytes", file=sys.stderr)
        return 3
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(json.dumps({"out": str(args.out), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                      "slugs": len(train), "pages": pages, "lines": lines_total,
                      "viewable": len(viewable), "page_tags": dict(page_tags), "law": dict(law)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
