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

Two inputs (--corpus):

  aa003  (default) collections/aahub/<slug>/resNN.txt, split
         data/aahub_split.json. slug = one AAHub page, page = one resNN.txt.
  aa004  collections/aahub-mlt/<kk>/<key>.json.gz (index.jsonl), split
         data/aahub_mlt_split.json, train_keys only. slug = one MLT page
         (index key), page = one aa[] piece. The split's archive_commit and
         index_sha256 are checked against the Git blob before counting.
         Held-out keys are never read.

Usage:
    python3 scripts/sjis_corpus_combos.py ARCHIVE SPLIT.json FONT.ttf --out OUT.json
    python3 scripts/sjis_corpus_combos.py ARCHIVE MLT_SPLIT.json FONT.ttf --corpus aa004 --out OUT.json
"""
from __future__ import annotations

import argparse
import bisect
import collections
import gzip
import hashlib
import html
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


BAND_RE = re.compile(r"[" + re.escape("".join(sorted(FINE_TEXTURE))) + r"]{4,}")
TOKEN_RE = re.compile(r"[^ 　]+")
SPACE_RUN_RE = re.compile(r"[ 　]{2,}")


class Accumulator:
    """All corpus counters. Pages are fed one at a time and a slug's per-slug
    summary is reduced when the slug ends, so memory does not grow with the
    number of pages. coverage=True also counts distinct pages and slugs per
    bigram and per stack key."""

    def __init__(self, m: Metrics, coverage: bool = False):
        self.m = m
        self.coverage = coverage
        C = collections.Counter
        self.glyphs, self.bigrams, self.trigrams = C(), C(), C()
        self.stacks, self.stacks_outline = C(), C()
        self.idioms, self.idiom_pages = C(), C()
        self.idiom_slugs: dict[str, set] = collections.defaultdict(set)
        self.bands = C()
        self.band_examples: dict[str, collections.Counter] = collections.defaultdict(C)
        self.spellings, self.page_tags, self.law = C(), C(), C()
        self.bigram_pages, self.bigram_slugs, self.stack_pages, self.stack_slugs = C(), C(), C(), C()
        self.slugs: list[str] = []
        self.slug_top_bigrams: dict[str, list] = {}
        self.slug_tags: dict[str, collections.Counter] = {}
        self.slug_pages: dict[str, int] = {}
        self.pages = self.lines_total = self.single_line_pages = 0
        self._begin()

    def _begin(self) -> None:
        self._sb, self._st = collections.Counter(), collections.Counter()
        self._sbset: set = set()
        self._ssset: set = set()
        self._n = 0

    def add_page(self, slug: str, text: str) -> None:
        m = self.m
        lines = text.rstrip("\n").split("\n")
        self.pages += 1
        self._n += 1
        self.single_line_pages += len(lines) == 1
        cls = collections.Counter()
        pb: set = set()
        ps: set = set()
        for line in lines:
            self.lines_total += 1
            self.law["adjacent_half_space_pairs"] += line.count("  ")
            self.law["lines_starting_with_half_space"] += line.startswith(HALF)
            for ch in line:
                self.glyphs[ch] += 1
                cls[glyph_class(ch)] += 1
            for tok in TOKEN_RE.findall(line):
                for i in range(len(tok) - 1):
                    g = tok[i:i + 2]
                    if is_stroke(g[0]) and is_stroke(g[1]):
                        self.bigrams[g] += 1
                        self._sb[g] += 1
                        pb.add(g)
                for i in range(len(tok) - 2):
                    g = tok[i:i + 3]
                    if all(is_stroke(c) for c in g):
                        self.trigrams[g] += 1
                for run in BAND_RE.findall(tok):
                    p = period(run)
                    key = p if p else "(aperiodic)"
                    self.bands[key] += 1
                    self.band_examples[key][run[:12]] += 1
            inner = line.strip(" 　")
            for run in SPACE_RUN_RE.findall(inner):
                self.spellings[space_spelling(run)] += 1
        for idiom in IDIOMS:
            k = text.count(idiom)
            if k:
                self.idioms[idiom] += k
                self.idiom_pages[idiom] += 1
                self.idiom_slugs[idiom].add(slug)
        cs = [centres(line, m) for line in lines]
        for r in range(len(lines) - 1):
            lower = cs[r + 1]
            if not lower:
                continue
            lx = [c for c, _ in lower]
            for cx, ch in cs[r]:
                if not is_stroke(ch):
                    continue
                # lower centres are sorted: scan the window around cx
                j = bisect.bisect_left(lx, cx - 3)
                while j < len(lx) and lx[j] <= cx + 3:
                    if is_stroke(lower[j][1]):
                        key = (ch, lower[j][1], int(round(lx[j] - cx)))
                        self.stacks[key] += 1
                        ps.add(key)
                        if ch not in FINE_TEXTURE and lower[j][1] not in FINE_TEXTURE:
                            self.stacks_outline[key] += 1
                    j += 1
        nonspace = sum(v for k, v in cls.items() if k != "space")
        outline = sum(cls[k] for k in ("fullwidth_stroke", "ascii_stroke", "kana"))
        texture = sum(cls[k] for k in ("fine_texture", "kanji"))
        tag = ("empty" if not nonspace else "outline" if outline / nonspace >= 0.6
               else "tone" if texture / nonspace >= 0.6 else "mixed")
        self.page_tags[tag] += 1
        self._st[tag] += 1
        if self.coverage:
            self.bigram_pages.update(pb)
            self.stack_pages.update(ps)
            self._sbset |= pb
            self._ssset |= ps

    def end_slug(self, slug: str) -> None:
        self.slugs.append(slug)
        self.slug_top_bigrams[slug] = self._sb.most_common(8)
        self.slug_tags[slug] = self._st
        self.slug_pages[slug] = self._n
        if self.coverage:
            self.bigram_slugs.update(self._sbset)
            self.stack_slugs.update(self._ssset)
        self._begin()


def aa003_input(archive: Path, split: dict):
    """AA-003: (provenance head, slug count hint, iterator of (slug, [(hash_name, blob_sha, text)]))."""
    commit = split["archive_commit"]
    manifest = git(archive, "show", f"{commit}:MANIFEST.tsv")
    if hashlib.sha256(manifest).hexdigest() != split["manifest_sha256"]:
        raise SystemExit("archive manifest does not match the split")
    prefix = split["collection"] + "/"
    names = git(archive, "ls-tree", "-r", "--name-only", commit, "--", split["collection"]).decode().splitlines()
    held_out = set(split["held_out_slugs"])
    by_slug: dict[str, list[str]] = collections.defaultdict(list)
    for n in names:
        parts = n[len(prefix):].split("/")
        if len(parts) == 2 and parts[1].startswith("res") and parts[1].endswith(".txt"):
            by_slug[parts[0]].append(n)
    train = sorted(s for s in by_slug if s not in held_out)
    if set(train) & held_out:
        raise SystemExit("held-out slug in training set")

    def pages():
        for slug in train:
            paths = sorted(by_slug[slug])
            blobs = read_blobs(archive, [f"{commit}:{p}" for p in paths])
            yield slug, [(p[len(prefix):], hashlib.sha256(b).hexdigest(), b.decode("utf-8"))
                         for p, b in zip(paths, blobs)]

    head = {"archive_commit": commit, "manifest_sha256": split["manifest_sha256"]}
    return head, len(held_out), {}, pages()


MLT_COLLECTION = "collections/aahub-mlt"


def piece_text(value: str) -> str:
    """AA-004 piece text: about 3 % of stored pieces keep numeric HTML character
    references (&#8201; thin space, &#9617; ░, &#x2588; █ ...). AAHub's viewer
    decodes them and AA-003's text holds the decoded characters, so every piece
    is decoded before anything is counted or rendered. Same definition as the
    converter's scripts/mlt_pairs.py piece_text (converter commit 4c194a3)."""
    return html.unescape(value)


def aa004_input(archive: Path, split: dict, chunk: int = 200):
    """AA-004: MLT pages (index keys) of the train partition; each gz record's
    aa[] entries are the pages. Held-out keys are never read."""
    if split.get("schema") != "aahub_mlt_split.v1":
        raise SystemExit(f"not an AA-004 MLT split: {split.get('schema')}")
    commit = split["archive_commit"]
    index_bytes = git(archive, "show", f"{commit}:{MLT_COLLECTION}/index.jsonl")
    index_sha = hashlib.sha256(index_bytes).hexdigest()
    if index_sha != split["index_sha256"]:
        raise SystemExit(f"index.jsonl at {commit} is {index_sha}, split pins {split['index_sha256']}")
    index = {}
    for line in index_bytes.decode("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            index[r["key"]] = r
    train = sorted(split["train_keys"])
    held_out = set(split["held_out_keys"])
    if len(set(train)) != len(train) or set(train) & held_out:
        raise SystemExit("train keys duplicated or overlapping held-out keys")
    if set(train) | held_out != set(index):
        raise SystemExit("split keys do not partition index.jsonl")
    want = split.get("counts", {})
    exp_pieces = sum(index[k]["pieces"] for k in train)
    if want.get("pages", {}).get("train") not in (None, len(train)) or \
            want.get("pieces", {}).get("train") not in (None, exp_pieces):
        raise SystemExit(f"split counts disagree with index: {len(train)} keys / {exp_pieces} pieces")
    prefix = MLT_COLLECTION + "/"

    def pages():
        for s in range(0, len(train), chunk):
            keys = train[s:s + chunk]
            blobs = read_blobs(archive, [f"{commit}:{index[k]['stored']}" for k in keys])
            for k, blob in zip(keys, blobs):
                rec = json.loads(gzip.decompress(blob))
                texts = [piece_text(a["value"]) for a in rec["aa"]]
                if len(texts) != index[k]["pieces"]:
                    raise SystemExit(f"{k}: {len(texts)} pieces, index says {index[k]['pieces']}")
                sha = hashlib.sha256(blob).hexdigest()
                name = index[k]["stored"][len(prefix):]
                yield k, [(name, sha, t) for t in texts]
            del blobs

    head = {"corpus": "AA-004", "collection": MLT_COLLECTION, "archive_commit": commit,
            "index_sha256": index_sha, "split_schema": split["schema"]}
    extra = {"expected_train_pieces": exp_pieces}
    return head, len(held_out), extra, pages()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archive", type=Path)
    ap.add_argument("split", type=Path)
    ap.add_argument("font", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--corpus", choices=("aa003", "aa004"), default="aa003")
    ap.add_argument("--coverage", action="store_true",
                    help="add distinct page/slug counts to bigram and stack entries (always on for aa004)")
    ap.add_argument("--top", type=int, default=300, help="entries kept per counted category")
    ap.add_argument("--render", type=int, default=120, help="entries rendered per viewable category")
    args = ap.parse_args(argv)

    split_bytes = args.split.read_bytes()
    split = json.loads(split_bytes)
    if args.corpus == "aa004":
        head, n_held_out, extra, source = aa004_input(args.archive, split)
    else:
        head, n_held_out, extra, source = aa003_input(args.archive, split)
    coverage = args.coverage or args.corpus == "aa004"

    m = Metrics(args.font)
    acc = Accumulator(m, coverage)
    input_hashes = []
    seen_blobs = set()
    for slug, items in source:
        for name, sha, text in items:
            if args.corpus == "aa003":
                input_hashes.append([name, sha])
            elif name not in seen_blobs:
                seen_blobs.add(name)
                input_hashes.append([name, sha])
            acc.add_page(slug, text)
        acc.end_slug(slug)
        if args.corpus == "aa004" and len(acc.slugs) % 500 == 0:
            print(f"{len(acc.slugs)} slugs, {acc.pages} pages, {acc.lines_total} lines", file=sys.stderr, flush=True)
    if args.corpus == "aa004" and acc.pages != extra["expected_train_pieces"]:
        raise SystemExit(f"counted {acc.pages} pieces, index expects {extra['expected_train_pieces']}")

    train = acc.slugs
    glyphs, bigrams, trigrams = acc.glyphs, acc.bigrams, acc.trigrams
    stacks, stacks_outline = acc.stacks, acc.stacks_outline
    idioms, idiom_pages, idiom_slugs = acc.idioms, acc.idiom_pages, acc.idiom_slugs
    bands, band_examples, spellings = acc.bands, acc.band_examples, acc.spellings
    page_tags, slug_tags, law = acc.page_tags, acc.slug_tags, acc.law
    pages, lines_total = acc.pages, acc.lines_total

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

    def cov(pages_c, slugs_c, key) -> dict:
        return {"pages": pages_c[key], "slugs": slugs_c[key]} if coverage else {}

    def seq_entries(counter, category, render, keep=lambda g: True, cov_c=None):
        pool = pooled(counter)
        out = []
        ranked = [(g, n) for g, n in counter.most_common() if keep(g)][: args.top]
        shown = 0
        for rank, (g, n) in enumerate(ranked, 1):
            mk, exact, pn = pool[g]
            cv = cov(*cov_c, g) if cov_c else {}
            e = {"g": g, "n": n, "mirror": mk, "mirror_exact": exact, "pooled_n": pn,
                 "px": [round(m.adv(c), 2) for c in g], "cp": [f"U+{ord(c):04X}" for c in g], **cv}
            out.append(e)
            # a run of one repeated glyph is a stroke or hatching, not a combination
            if shown < render and len(set(g)) > 1:
                shown += 1
                add_view(category, g, [(0.0, g)], [(0.0, mk)], n,
                         {"mirror_exact": exact, "pooled_n": pn, "rank": rank, **cv})
        return out

    idiom_list = []
    for rank, (g, n) in enumerate(sorted(idioms.items(), key=lambda kv: -kv[1]), 1):
        mk, exact = mirror(g)
        idiom_list.append({"g": g, "n": n, "pages": idiom_pages[g], "slugs": len(idiom_slugs[g]),
                           "mirror": mk, "mirror_exact": exact,
                           "mirror_n": idioms.get(mk, 0) if mk != g else None})
        add_view("idiom", g, [(0.0, g)], [(0.0, mk)], n,
                 {"mirror_exact": exact, "pages": idiom_pages[g], "slugs": len(idiom_slugs[g]), "rank": rank})

    bcov = (acc.bigram_pages, acc.bigram_slugs)
    bigram_list = seq_entries(bigrams, "bigram", 0, cov_c=bcov)
    trigram_list = seq_entries(trigrams, "trigram", 0)
    bigram_outline = seq_entries(bigrams, "bigram", args.render, is_outline, cov_c=bcov)
    trigram_outline = seq_entries(trigrams, "trigram", args.render, is_outline)

    def stack_entries(counter, render):
      out = []
      shown = 0
      for rank, ((up, lo, dx), n) in enumerate(counter.most_common(args.top), 1):
        mu, eu = mirror(up)
        ml, el = mirror(lo)
        mdx = -dx
        pn = n + (counter.get((mu, ml, mdx), 0) if (mu, ml, mdx) != (up, lo, dx) else 0)
        c = cov(acc.stack_pages, acc.stack_slugs, (up, lo, dx))
        out.append({"upper": up, "lower": lo, "dx_px": dx, "n": n, "pooled_n": pn,
                           "mirror": [mu, ml, mdx], "mirror_exact": eu and el, **c})
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
                     {"mirror_exact": eu and el, "pooled_n": pn, "dx_px": dx, "rank": rank, **c})

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
        **head,
        "split_sha256": hashlib.sha256(split_bytes).hexdigest(),
        "partition": "train",
        "held_out_slugs_excluded": n_held_out,
        "font": args.font.name,
        "font_sha256": hashlib.sha256(args.font.read_bytes()).hexdigest(),
        "px": PX, "line_pitch_px": PITCH,
        "slugs": len(train), "pages": pages, "lines": lines_total,
        "input_set_sha256": hashlib.sha256(json.dumps(input_hashes, ensure_ascii=False).encode()).hexdigest(),
        **({"unit_labels": {"slug": "MLT pages", "page": "pieces"},
            "units": "slug = one AAHub MLT page (index.jsonl key, held-out keys excluded); page = one aa[] piece "
                     "of that page, section-header pieces included; input_set_sha256 hashes the gz record blobs",
            "piece_text": "html.unescape(aa[].value): numeric character references are decoded before counting",
            "mlt_pages": len(train), "pieces": pages,
            "single_line_pieces": acc.single_line_pages} if args.corpus == "aa004" else {}),
        **({"coverage": "bigram, bigrams_outline, stacks and stacks_outline entries carry pages / slugs: "
                        "the number of distinct pages and slugs containing that combination"} if coverage else {}),
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
        "per_slug": {s: {"pages": acc.slug_pages[s], "tags": dict(slug_tags[s]),
                         "top_bigrams": [[g, n] for g, n in acc.slug_top_bigrams[s]]}
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
