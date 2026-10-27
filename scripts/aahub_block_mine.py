"""Mine native-metric glyph block windows from AAHub AA-003 TRAIN pages (Lane A).

Every TRAIN page (collections/aahub/<slug>/res*.txt; TRAIN membership = per_slug keys
of the pinned sjis_combos aggregate, so no held-out slug is ever opened) is laid out
with aahub_native (Saitamaar 16 px, natural advances, 17 px rows). The page is cut
into lattice cells of 1 row x 16 px measured from the pen origin (x = 0 at line
start). A window of size N x M is N rows x m cells (M = 16*m px), N, m in 2..12,
stepped by 1 row and 1 cell.

Keys per window (both 64-bit, 2D polynomial hashes over per-cell codes):
  text key  exact ink-glyph sequence: for each cell, the (char, pen_x - cell_x) of
            every glyph with ink whose pen falls in the cell. Spaces carry no ink
            and are represented by the pen offsets they produce.
  ink key   ink shape: each cell's ink downsampled to a 4 x 4 occupancy grid
            (x blocks of 4 px; y blocks 0-4, 4-8, 8-13, 13-17 px).
A window is counted only when its top row, bottom row, left column and right column
each hold the pen of at least one inked glyph, so it holds content spanning the full
N x M (no blank-margin translates, no windows filled only by a neighbour's overhang).
The ink key still includes overhanging ink from glyphs whose pen lies outside.
A counted window is also ranked in a third, "outline" table when its inked glyphs
outside sjis_corpus_combos.FINE_TEXTURE span at least two different codepoints (a
construction, not a tone field or a single repeated stroke/hatch glyph).

Also counted: per-glyph vertical continuation, i.e. glyph pairs on adjacent rows
whose ink x-extents overlap by >= 1 px, with the overlap and centre offset.

Stages (exact counts with bounded disk; keys are split into P disjoint partitions by
their top bits, so per-partition totals and top-K candidates union exactly):
  cells   once: per-page cell hash arrays + vertical continuation -> cells/<slug>.npz
  mine    per partition p: windows whose key is in p, shard-deduplicated per slug
  merge   per partition p: reduce shards per size -> part-p.json (totals + top-K)
  final   union partitions, re-rank, resolve exact rows from source, write outputs
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aahub_native import PITCH, Native, read_rows  # noqa: E402

# verbatim copy of sjis_corpus_combos.FINE_TEXTURE (importing that module needs fontTools)
FINE_TEXTURE = set(".,;:'`､｡･・\"ﾞﾟ‘’´¨…‥゛゜")

BIG = np.int32(1 << 30)

SIZES_N = range(2, 13)
SIZES_M = range(2, 13)
CELL = 16
YB = (0, 4, 8, 13, 17)
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
P = np.uint64(0x9E3779B97F4A7C15)  # odd -> invertible mod 2^64
Q = np.uint64(0xC2B2AE3D27D4EB4F)


def inv64(a: int) -> int:
    return pow(a, -1, 1 << 64)


PINV, QINV = np.uint64(inv64(int(P))), np.uint64(inv64(int(Q)))


def mix(x: np.ndarray) -> np.ndarray:
    """splitmix64 finaliser, vectorised; 0 stays a valid input (callers mask empties)."""
    with np.errstate(over="ignore"):
        z = x.astype(np.uint64) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return z ^ (z >> np.uint64(31))


def powers(base: np.uint64, n: int) -> np.ndarray:
    out = np.empty(n, np.uint64)
    v = np.uint64(1)
    with np.errstate(over="ignore"):
        for i in range(n):
            out[i] = v
            v = v * base
    return out


def text_cell_hash(items: list[tuple[str, int]]) -> int:
    h = hashlib.blake2b(digest_size=8)
    for ch, dx in items:
        h.update(ch.encode("utf-8"))
        h.update(bytes((dx,)))
    v = int.from_bytes(h.digest(), "little")
    return v or 1


class Page:
    def __init__(self, nat: Native, rows: list[str]):
        self.rows = rows
        self.layout = nat.layout(rows)
        R = len(rows)
        W = max((nat.row_width(r) for r in rows), default=0)
        C = max(1, -(-W // CELL))
        self.R, self.C = R, C
        a = nat.raster(rows, pad=0)
        A = np.zeros((R * PITCH, C * CELL), bool)
        A[:min(a.shape[0], A.shape[0]), :min(a.shape[1], A.shape[1])] = \
            a[:A.shape[0], :A.shape[1]]
        # ink code: 4x4 occupancy per cell
        code = np.zeros((R, C), np.uint64)
        bit = 0
        for yi in range(4):
            band = A.reshape(R, PITCH, C * CELL)[:, YB[yi]:YB[yi + 1], :].any(axis=1)
            band = band.reshape(R, C, 4, 4).any(axis=3)  # (R, C, xblock)
            for xi in range(4):
                code |= band[:, :, xi].astype(np.uint64) << np.uint64(bit)
                bit += 1
        self.ink_code = code
        Ih = mix(code)
        Ih[code == 0] = 0
        # text code
        T = np.zeros((R, C), np.uint64)
        smin = np.full((R, C), BIG, np.int32)
        smax = np.full((R, C), -1, np.int32)
        for r, line in enumerate(self.layout):
            cells = collections.defaultdict(list)
            for ch, x in line:
                if nat.glyph(ch)[3].size:
                    c = x // CELL
                    if c < C:
                        cells[c].append((ch, x - c * CELL))
                        if ch not in FINE_TEXTURE:
                            smin[r, c] = min(smin[r, c], ord(ch))
                            smax[r, c] = max(smax[r, c], ord(ch))
            for c, items in cells.items():
                T[r, c] = text_cell_hash(items)
        self.smin, self.smax = smin, smax
        self.Th, self.Ih = T, Ih
        self.occ = (T != 0)

    def windows(self, pr, qc):
        """Yield (N, m, tkey, ikey, r0, c0, outline) arrays of anchored windows."""
        from numpy.lib.stride_tricks import sliding_window_view as swv
        R, C = self.R, self.C
        pw, qw = pr[:R][:, None], qc[:C][None, :]
        with np.errstate(over="ignore"):
            ST = np.zeros((R + 1, C + 1), np.uint64)
            SI = np.zeros((R + 1, C + 1), np.uint64)
            ST[1:, 1:] = (self.Th * pw * qw).cumsum(0).cumsum(1)
            SI[1:, 1:] = (self.Ih * pw * qw).cumsum(0).cumsum(1)
        occ = self.occ.astype(np.int32)
        SO_row = np.zeros((R, C + 1), np.int32)
        SO_row[:, 1:] = occ.cumsum(1)          # per row, along columns
        SO_col = np.zeros((R + 1, C), np.int32)
        SO_col[1:, :] = occ.cumsum(0)          # per column, along rows
        for N in SIZES_N:
            if N > R:
                break
            for m in SIZES_M:
                if m > C:
                    break
                nr, nc = R - N + 1, C - m + 1
                top = (SO_row[:nr, m:m + nc] - SO_row[:nr, :nc]) > 0
                bot = (SO_row[N - 1:N - 1 + nr, m:m + nc] - SO_row[N - 1:N - 1 + nr, :nc]) > 0
                left = (SO_col[N:N + nr, :nc] - SO_col[:nr, :nc]) > 0
                right = (SO_col[N:N + nr, m - 1:m - 1 + nc] - SO_col[:nr, m - 1:m - 1 + nc]) > 0
                ok = top & bot & left & right
                if not ok.any():
                    continue
                r0, c0 = np.nonzero(ok)
                wmin = swv(self.smin, (N, m)).min(axis=(2, 3))[r0, c0]
                wmax = swv(self.smax, (N, m)).max(axis=(2, 3))[r0, c0]
                outline = (wmax >= 0) & (wmin < wmax)
                with np.errstate(over="ignore"):
                    def rect(S):
                        v = S[r0 + N, c0 + m] - S[r0, c0 + m] - S[r0 + N, c0] + S[r0, c0]
                        return v * PINVP[r0] * QINVP[c0]
                    yield N, m, rect(ST), rect(SI), r0, c0, outline

    def continuation(self, nat: Native, acc: dict):
        ext = []
        for line in self.layout:
            e = []
            for ch, x in line:
                adv, xo, yo, mk = nat.glyph(ch)
                if mk.size:
                    e.append((x + xo, x + xo + mk.shape[1], ch))
            ext.append(e)
        for r in range(len(ext) - 1):
            up, lo = ext[r], ext[r + 1]
            j0 = 0
            for a0, a1, ga in up:
                while j0 < len(lo) and lo[j0][1] <= a0 - 16:
                    j0 += 1
                for b0, b1, gb in lo[j0:]:
                    if b0 >= a1:
                        break
                    ov = min(a1, b1) - max(a0, b0)
                    if ov >= 1:
                        dx = round(((b0 + b1) - (a0 + a1)) / 2)
                        k = (ga, gb)
                        rec = acc.get(k)
                        if rec is None:
                            acc[k] = [1, ov, collections.Counter({dx: 1})]
                        else:
                            rec[0] += 1
                            rec[1] += ov
                            rec[2][dx] += 1


PMAX = 512
PR, QC = powers(P, PMAX), powers(Q, PMAX)
PINVP, QINVP = powers(PINV, PMAX), powers(QINV, PMAX)


def cells_slug(job):
    root, slug, out = job
    t0 = time.time()
    nat = Native()
    files = sorted((Path(root) / slug).glob("res*.txt"))
    cont: dict = {}
    pages, arrs = [], {}
    for pi, f in enumerate(files):
        rows = read_rows(f)
        pages.append(f.name)
        if len(rows) > PMAX or max((nat.row_width(r) for r in rows), default=0) // CELL >= PMAX:
            raise SystemExit(f"page too large for power tables: {f}")
        pg = Page(nat, rows)
        pg.continuation(nat, cont)
        arrs[f"{pi}_t"], arrs[f"{pi}_i"], arrs[f"{pi}_o"] = pg.Th, pg.Ih, pg.occ
        arrs[f"{pi}_smin"], arrs[f"{pi}_smax"] = pg.smin, pg.smax
    np.savez(Path(out) / f"{slug}.npz", **arrs)
    contj = {f"{a}\t{b}": [v[0], v[1], dict(v[2].most_common(5))] for (a, b), v in cont.items()}
    (Path(out) / f"{slug}.meta.json").write_text(json.dumps(
        {"slug": slug, "pages": pages, "frac_glyphs": sorted(nat.frac_glyphs),
         "seconds_cells": round(time.time() - t0, 1), "continuation": contj}, ensure_ascii=False))
    return slug, len(files), time.time() - t0


class CellPage(Page):
    def __init__(self, Th, Ih, occ, smin, smax):
        self.Th, self.Ih, self.occ, self.smin, self.smax = Th, Ih, occ, smin, smax
        self.R, self.C = Th.shape


def part_of(key: np.ndarray, parts: int) -> np.ndarray:
    return (key >> np.uint64(64 - parts.bit_length() + 1)).astype(np.int64) if parts > 1 \
        else np.zeros(len(key), np.int64)


def mine_slug(job):
    cells, slug, out, part, parts = job
    t0 = time.time()
    z = np.load(Path(cells) / f"{slug}.npz")
    npages = len(z.files) // 5
    per = collections.defaultdict(lambda: ([], [], [], [], [], []))
    nwin = collections.Counter()
    for pi in range(npages):
        pg = CellPage(z[f"{pi}_t"], z[f"{pi}_i"], z[f"{pi}_o"], z[f"{pi}_smin"], z[f"{pi}_smax"])
        for N, m, tk, ik, r0, c0, ol in pg.windows(PR, QC):
            nwin[f"{N}x{m}"] += len(tk)
            L = per[(N, m)]
            L[0].append(tk); L[1].append(ik)
            L[2].append(np.full(len(tk), pi, np.int32))
            L[3].append(r0.astype(np.int16)); L[4].append(c0.astype(np.int16))
            L[5].append(ol)
    arrays = {}
    for (N, m), (tk, ik, pg_, r0, c0, ol) in per.items():
        tk, ik, pg_ = np.concatenate(tk), np.concatenate(ik), np.concatenate(pg_)
        r0, c0, ol = np.concatenate(r0), np.concatenate(c0), np.concatenate(ol)
        for name, key in (("t", tk), ("i", ik), ("o", tk)):
            sel = part_of(key, parts) == part
            if name == "o":
                sel &= ol
            k_all, p_all = key[sel], pg_[sel]
            idx = np.nonzero(sel)[0]
            order = np.lexsort((p_all, k_all))
            k, p = k_all[order], p_all[order]
            if not len(k):
                continue
            first = np.ones(len(k), bool)
            first[1:] = k[1:] != k[:-1]
            starts = np.nonzero(first)[0]
            counts = np.diff(np.append(starts, len(k)))
            newpage = first.copy()
            newpage[1:] |= p[1:] != p[:-1]
            npg = np.add.reduceat(newpage.astype(np.int32), starts)
            o = idx[order[starts]]
            pre = f"{N}x{m}_{name}"
            arrays[pre + "_key"] = k[starts]
            arrays[pre + "_n"] = counts.astype(np.int32)
            arrays[pre + "_pages"] = npg.astype(np.int32)
            arrays[pre + "_page"] = pg_[o]
            arrays[pre + "_r0"] = r0[o]
            arrays[pre + "_c0"] = c0[o]
            if name in ("t", "o"):
                arrays[pre + "_ink"] = ik[o]
    np.savez(Path(out) / f"{slug}.npz", **arrays)
    (Path(out) / f"{slug}.done").write_text(json.dumps({"windows": nwin}))
    return slug, npages, sum(nwin.values()), time.time() - t0


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def train_slugs(a):
    return sorted(json.loads(Path(a.combos).read_text())["per_slug"])


def run_pool(fn, jobs, workers, label):
    t0 = time.time()
    with Pool(workers) as pool:
        for i, (slug, n, *rest) in enumerate(pool.imap_unordered(fn, jobs)):
            print(f"[{label} {i + 1}/{len(jobs)}] {slug}: {n} pages {rest} "
                  f"(elapsed {time.time() - t0:.0f}s)", flush=True)


def cmd_cells(a):
    out = Path(a.cells)
    out.mkdir(parents=True, exist_ok=True)
    todo = [s for s in train_slugs(a) if not (out / f"{s}.meta.json").exists()]
    todo.sort(key=lambda s: -sum(f.stat().st_size for f in (Path(a.root) / s).glob("res*.txt")))
    run_pool(cells_slug, [(a.root, s, str(out)) for s in todo], a.workers, "cells")


def cmd_mine(a):
    out = Path(a.shards) / f"part{a.part}"
    out.mkdir(parents=True, exist_ok=True)
    todo = [s for s in train_slugs(a) if not (out / f"{s}.done").exists()]
    todo.sort(key=lambda s: -(Path(a.cells) / f"{s}.npz").stat().st_size)
    run_pool(mine_slug, [(a.cells, s, str(out), a.part, a.parts) for s in todo], a.workers,
             f"mine p{a.part}")


# ---------------------------------------------------------------- merge

def reduce_size(shard_files, size, kind, topk):
    keys, n, pg, rep_slug, rep_page, r0, c0, ink = [], [], [], [], [], [], [], []
    for si, f in enumerate(shard_files):
        z = np.load(f)
        pre = f"{size}_{kind}"
        if pre + "_key" not in z.files:
            continue
        keys.append(z[pre + "_key"]); n.append(z[pre + "_n"]); pg.append(z[pre + "_pages"])
        rep_slug.append(np.full(len(z[pre + "_key"]), si, np.int32))
        rep_page.append(z[pre + "_page"]); r0.append(z[pre + "_r0"]); c0.append(z[pre + "_c0"])
        if kind in ("t", "o"):
            ink.append(z[pre + "_ink"])
    if not keys:
        return None
    keys = np.concatenate(keys); n = np.concatenate(n).astype(np.int64)
    pg = np.concatenate(pg).astype(np.int64); rep_slug = np.concatenate(rep_slug)
    rep_page = np.concatenate(rep_page); r0 = np.concatenate(r0); c0 = np.concatenate(c0)
    ink = np.concatenate(ink) if ink else None
    order = np.argsort(keys, kind="stable")
    k = keys[order]
    first = np.ones(len(k), bool)
    first[1:] = k[1:] != k[:-1]
    starts = np.nonzero(first)[0]
    N = np.add.reduceat(n[order], starts)
    PG = np.add.reduceat(pg[order], starts)
    SL = np.add.reduceat(np.ones(len(k), np.int64), starts)
    o = order[starts]
    total_windows = int(n.sum())
    distinct = len(starts)
    singletons = int((N == 1).sum())
    # rank by distinct pages, then count
    top = np.lexsort((-N, -PG))[:topk]
    res = {"total_windows": total_windows, "distinct_patterns": distinct,
           "singleton_patterns": singletons,
           "patterns_on_ge2_pages": int((PG >= 2).sum()),
           "patterns_on_ge10_pages": int((PG >= 10).sum()),
           "top": []}
    for t in top:
        res["top"].append({"key": f"{int(k[starts[t]]):016x}", "n": int(N[t]), "pages": int(PG[t]),
                           "slugs": int(SL[t]), "_slug": int(rep_slug[o[t]]),
                           "_page": int(rep_page[o[t]]), "r0": int(r0[o[t]]), "c0": int(c0[o[t]]),
                           **({"ink_key": f"{int(ink[o[t]]):016x}"} if ink is not None else {})})
    return res


def resolve(entry, slug, page_name, root, nat, N, m, cache):
    key = (slug, page_name)
    if key not in cache:
        rows = read_rows(Path(root) / slug / page_name)
        cache[key] = (rows, nat.layout(rows))
    rows, layout = cache[key]
    x0, x1 = entry["c0"] * CELL, (entry["c0"] + m) * CELL
    out_rows, glyphs = [], []
    for r in range(entry["r0"], entry["r0"] + N):
        line = layout[r] if r < len(layout) else []
        txt = "".join(ch for ch, x in line if x0 <= x < x1)
        out_rows.append(txt)
        glyphs.append([[ch, x - x0] for ch, x in line if x0 <= x < x1 and nat.glyph(ch)[3].size])
    entry["rows"] = out_rows
    entry["glyphs"] = glyphs
    entry["locator"] = {"slug": slug, "file": f"collections/aahub/{slug}/{page_name}",
                        "row_start": entry["r0"] + 1, "row_end": entry["r0"] + N,
                        "x_px": [x0, x1]}
    return entry


def cmd_merge(a):
    """Reduce one partition's shards per size; keep exact totals and top-K candidates."""
    shards = Path(a.shards) / f"part{a.part}"
    slugs = train_slugs(a)
    missing = [s for s in slugs if not (shards / f"{s}.done").exists()]
    if missing:
        raise SystemExit(f"partition {a.part} incomplete: {len(missing)} slugs missing")
    files = [shards / f"{s}.npz" for s in slugs]
    windows = collections.Counter()
    for s in slugs:
        windows.update(json.loads((shards / f"{s}.done").read_text())["windows"])
    res = {"part": a.part, "parts": a.parts, "windows_all_parts": dict(windows), "sizes": {}}
    t0 = time.time()
    for N in SIZES_N:
        for m in SIZES_M:
            size = f"{N}x{m}"
            d = {}
            for kind, name in (("t", "text"), ("i", "ink"), ("o", "outline")):
                r = reduce_size(files, size, kind, a.topk)
                if r is not None:
                    for e in r["top"]:
                        e["slug"] = slugs[e.pop("_slug")]
                    d[name] = r
            res["sizes"][size] = d
        print(f"merge p{a.part} N={N} {time.time() - t0:.0f}s", flush=True)
    (Path(a.shards) / f"part{a.part}.json").write_text(json.dumps(res))


def cmd_final(a):
    shards, cells, out = Path(a.shards), Path(a.cells), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    parts = [json.loads((shards / f"part{p}.json").read_text()) for p in range(a.parts)]
    slugs = train_slugs(a)
    meta = {s: json.loads((cells / f"{s}.meta.json").read_text()) for s in slugs}
    windows = parts[0]["windows_all_parts"]
    nat = Native()
    cache: dict = {}
    summary, examples = {}, {}
    for N in SIZES_N:
        for m in SIZES_M:
            size = f"{N}x{m}"
            if not windows.get(size):
                continue
            doc = {"size": {"rows": N, "cells": m, "px_wide": m * CELL, "px_tall": N * PITCH},
                   "anchored_windows": windows[size]}
            for name in ("text", "ink", "outline"):
                agg = {"total_windows": 0, "distinct_patterns": 0, "singleton_patterns": 0,
                       "patterns_on_ge2_pages": 0, "patterns_on_ge10_pages": 0}
                top = []
                for P_ in parts:
                    r = P_["sizes"].get(size, {}).get(name)
                    if not r:
                        continue
                    for k in agg:
                        agg[k] += r[k]
                    top += r["top"]
                top.sort(key=lambda e: (-e["pages"], -e["n"], e["key"]))
                top = top[:a.topk]
                for e in top:
                    page = meta[e["slug"]]["pages"][e.pop("_page")]
                    resolve(e, e.pop("slug"), page, a.root, nat, N, m, cache)
                    e.pop("r0"); e.pop("c0")
                agg["top"] = top
                doc[name] = agg
            assert doc["text"]["total_windows"] == windows[size] == doc["ink"]["total_windows"], size
            p = out / f"blocks_{size}.json.gz"
            with gzip.open(p, "wt", encoding="utf-8", compresslevel=9) as fh:
                json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
            summary[size] = {"anchored_windows": windows[size],
                             "distinct_text": doc["text"]["distinct_patterns"],
                             "distinct_ink": doc["ink"]["distinct_patterns"],
                             "text_on_ge2_pages": doc["text"]["patterns_on_ge2_pages"],
                             "text_on_ge10_pages": doc["text"]["patterns_on_ge10_pages"],
                             "ink_on_ge2_pages": doc["ink"]["patterns_on_ge2_pages"],
                             "outline_windows": doc["outline"]["total_windows"],
                             "distinct_outline": doc["outline"]["distinct_patterns"],
                             "outline_on_ge2_pages": doc["outline"]["patterns_on_ge2_pages"],
                             "file": p.name, "bytes": p.stat().st_size}
            examples[size] = {name: [{k: e[k] for k in ("n", "pages", "slugs", "rows", "locator")}
                                     for e in doc[name]["top"][:10]] for name in ("text", "outline")}
            if len(cache) > 4000:
                cache.clear()
        print("final N", N, flush=True)
    # vertical continuation
    cont = collections.defaultdict(lambda: [0, 0, collections.Counter()])
    for s in slugs:
        for k, (c, ov, dx) in meta[s]["continuation"].items():
            rec = cont[k]
            rec[0] += c; rec[1] += ov; rec[2].update({int(d): v for d, v in dx.items()})
    by_upper, by_lower = collections.defaultdict(list), collections.defaultdict(list)
    glyph_tot = collections.Counter()
    for k, (c, ov, dx) in cont.items():
        u, l = k.split("\t")
        glyph_tot[u] += c
        glyph_tot[l] += c
        if c >= a.cont_min:
            by_upper[u].append((c, l, ov, dx))
            by_lower[l].append((c, u, ov, dx))

    def pack(lst, other):
        lst.sort(key=lambda t: (-t[0], t[1]))
        return [{other: g, "n": c, "mean_overlap_px": round(ov / c, 2),
                 "dx_px_top": [[d, v] for d, v in dx.most_common(3)]} for c, g, ov, dx in lst[:a.cont_topk]]
    glyphs = sorted(set(by_upper) | set(by_lower), key=lambda g: (-glyph_tot[g], g))
    contdoc = {"definition": "glyph pairs on adjacent rows whose ink x-extents overlap by >= 1 px; "
                             "dx_px = lower ink centre - upper ink centre (from the 5 most common per shard)",
               "pairs_total": int(sum(v[0] for v in cont.values())), "distinct_pairs": len(cont),
               "min_pair_count_listed": a.cont_min, "per_glyph_topk": a.cont_topk,
               "glyphs": {g: {"n_pairs": glyph_tot[g], "below": pack(by_upper.get(g, []), "lower"),
                              "above": pack(by_lower.get(g, []), "upper")} for g in glyphs}}
    with gzip.open(out / "vertical_continuation.json.gz", "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(contdoc, fh, ensure_ascii=False, separators=(",", ":"))
    combos_p = Path(a.combos)
    combos = json.loads(combos_p.read_text())
    inputs = []
    for s in slugs:
        for pg in meta[s]["pages"]:
            inputs.append(f"collections/aahub/{s}/{pg}\t{sha256(Path(a.root) / s / pg)}")
    archive_commit = subprocess.run(["git", "-C", a.root, "rev-parse", "HEAD"], capture_output=True,
                                    text=True).stdout.strip()
    manifest = {
        "schema": "aahub_blocks.v1",
        "schema_file": "schema.json",
        "producer": "scripts/aahub_block_mine.py (cells, mine/merge x parts, final) + scripts/aahub_native.py",
        "corpus": "AA-003 ascii-art-archive collections/aahub",
        "archive_commit": archive_commit,
        "partition": "train",
        "train_membership_source": f"per_slug keys of assets/glyphs/corpus/{combos_p.name} "
                                   f"(split_sha256 {combos['split_sha256']}); held-out slugs never opened",
        "held_out_slugs_excluded": combos["held_out_slugs_excluded"],
        "split_file_verified": False,
        "split_file_note": "data/aahub_split.json (screenshot-of-ascii-art-to-txt-converter) was not available in "
                           "this environment; TRAIN = the aggregate's 114 per_slug keys, which the skill names as "
                           "TRAIN membership. TXT count equals the aggregate's 23,363 pages.",
        "slugs": len(slugs), "pages": sum(len(meta[s]["pages"]) for s in slugs),
        "input_set_sha256": hashlib.sha256("\n".join(sorted(inputs)).encode()).hexdigest(),
        "input_set_definition": "sha256 of sorted lines '<archive path>\\t<sha256 of file bytes>'",
        "font": "Saitamaar.ttf from trueff-shallot assets/font (byte-identical to archive collections/aahub/Saitamaar.ttf)",
        "font_sha256": nat.font_sha256,
        "px": 16, "line_pitch_px": PITCH, "cell_px": CELL,
        "render_check": "aahub_native.py reproduced the archive resNN.png pixel-exactly on 540/600 random TRAIN "
                        "pages; the other 60 differ only where the archive PNG nudged a row by -1 px or dropped a "
                        "row of low-ink glyphs (e.g. a row of only ＿). Row placement here is a fixed 17 px baseline.",
        "fractional_advance_glyphs": sorted({g for s in slugs for g in meta[s]["frac_glyphs"]}),
        "fractional_advance_note": "pen kept as float and rounded per glyph; affects 19 TRAIN pages",
        "window_definition": "N rows x m cells of 16 px, N,m in 2..12, stride 1 row / 1 cell from pen x=0; "
                             "counted only when its top row, bottom row, left column and right column each hold "
                             "the pen of an inked glyph",
        "key_partitions": a.parts,
        "ranking": "top-K per size by distinct pages, then occurrences, then key",
        "outline_definition": "subset of counted windows whose inked glyphs outside sjis_corpus_combos.FINE_TEXTURE "
                              "span >= 2 different codepoints; text-keyed",
        "topk": a.topk,
        "sizes": summary,
        "vertical_continuation": "vertical_continuation.json.gz",
        "seconds_cells_total": round(sum(meta[s]["seconds_cells"] for s in slugs), 1),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    (Path(a.shards) / "examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("cells", "mine", "merge", "final"):
        p = sub.add_parser(name)
        p.add_argument("--root", default="/home/user/ascii-art-archive/collections/aahub")
        p.add_argument("--combos", default=str(Path(__file__).resolve().parent.parent /
                                               "assets/glyphs/corpus/aahub_aa003_train.sjis_combos.v1.json"))
        p.add_argument("--cells", required=True)
        p.add_argument("--shards", default="")
        p.add_argument("--workers", type=int, default=os.cpu_count())
        p.add_argument("--part", type=int, default=0)
        p.add_argument("--parts", type=int, default=8)
        p.add_argument("--topk", type=int, default=200)
        p.add_argument("--out", default="")
        p.add_argument("--cont-min", type=int, default=20)
        p.add_argument("--cont-topk", type=int, default=12)
    a = ap.parse_args()
    if a.parts & (a.parts - 1):
        raise SystemExit("--parts must be a power of two")
    {"cells": cmd_cells, "mine": cmd_mine, "merge": cmd_merge, "final": cmd_final}[a.cmd](a)


if __name__ == "__main__":
    main()
