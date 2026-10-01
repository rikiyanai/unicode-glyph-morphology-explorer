#!/usr/bin/env python3
"""Exemplar selection for the AA-004 line-art style study (TRAIN only).

Reads the per-piece rows written by aa004_style_stats.py (sample_pieces.jsonl.gz)
and picks exemplars by fixed rules; it also runs the cloud/smoke lobe scan over
named TRAIN pages. Excerpts are read from the archive Git blobs at the split's
commit. Output: --out exemplars.json (never overwritten with different bytes).

Rules
  per style class (aa004_style_stats.style_class): candidates are sampled
  pieces with 8..40 rows and 150..2500 non-space glyphs (and text_share
  <= 0.05 outside the text class); score =
    line_minimal    envelope_blank + 0.02 * contour idioms per 100 glyphs
    line_plus_tone  dot_band_closed / dot_bands (closed tone) + envelope_blank
    tone_dominant   tone_share
    dense_filled    ink_share
    text            text_share
  take the best piece per stratum group (works / 2ch / generic / other),
  ties broken by sha256(SEED|key|i).
  cloud scan: for each page in CLOUD_PAGES, rank art pieces by the number of
  LOBE substrings; keep the top 3 per page.
  excerpt: the 3 consecutive lines with the most outline-class glyphs (cloud
  scan: the most LOBE substrings);
  U+3000 is written as □ and U+0020 as · (SJIS-AUDIT notation).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aa004_style_stats as M  # noqa: E402

LOBE = ["⌒ヽ", "(⌒", "⌒)", "（⌒", "⌒）", "ヽ_", "_ノ", "ゝ__ノ", "⌒Y", "Y⌒", "⌒ヾ", "⌒丶", "γ⌒", "⌒¨", "ノし"]
CLOUD_PAGES = {  # TRAIN pages outside 爆発・煙 whose subject includes cloud, smoke or steam
    "85cb726da5e416e44ceb4fbbf32c8c89": "汎用AA/エフェクト/エフェクト",
    "095894e54a97eac6d0e9ac467852b1e1": "汎用AA/エフェクト/エレメント/エレメントその他",
    "ea2e1523c12ba9428fef4b24f095be79": "汎用AA/背景・風景/街・村・一次産業/街並み06（燃えている街・破壊される街）",
    "a3d73b4915c673e26474c9d3013d00b3": "汎用AA/小道具/娯楽系/煙草",
    "1823425068f1993743f2308e797c2c2c": "汎用AA/背景・風景/地形/地形（山・鉱山・桟道）",
    "29bbdb9128e7655193cb54559cd127cf": "汎用AA/背景・風景/背景",
    "dcd1e5ea629209861c16c400953d0bae": "汎用AA/背景・風景/街・村・一次産業/遠景01（街・村のみ）",
    "c3b8fbf7b30d912ce6336b379f96d745": "汎用AA/エフェクト/攻撃エフェクト/技",
}


def group(stratum):
    if stratum.startswith("汎用AA"):
        return "generic"
    if stratum.startswith("2ch"):
        return "2ch"
    if stratum in ("実在人物パロディ", "企業・ご当地キャラクター", "原典不明人物"):
        return "other"
    return "works"


def tiebreak(key, i):
    return hashlib.sha256(f"{M.SEED}|{key}|{i}".encode()).hexdigest()


def excerpt(text, lobes=False):
    lines = text.rstrip("\n").split("\n")
    best, at = -1, 0
    for s in range(max(1, len(lines) - 2)):
        if lobes:
            n = sum(l.count(x) for l in lines[s:s + 3] for x in LOBE)
        else:
            n = sum(1 for l in lines[s:s + 3] for c in l if M.glyph_class(c) in M.OUTLINE_CLASSES)
        if n > best:
            best, at = n, s
    return at, [l.replace("　", "□").replace(" ", "·") for l in lines[at:at + 3]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--split", type=Path, required=True)
    ap.add_argument("--sample", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    sb = args.split.read_bytes()
    if hashlib.sha256(sb).hexdigest() != M.SPLIT_SHA256:
        raise SystemExit("split sha256 mismatch")
    split = json.loads(sb)
    train = set(split["train_keys"])
    commit = split["archive_commit"]
    index = subprocess.run(["git", "-C", str(args.archive), "show", f"{commit}:collections/aahub-mlt/index.jsonl"],
                           check=True, capture_output=True).stdout
    rows = {r["key"]: r for r in map(json.loads, index.decode().splitlines()) if r}
    cache = {}

    def record(key):
        assert key in train, "held-out key requested"
        if key not in cache:
            b = subprocess.run(["git", "-C", str(args.archive), "show", f"{commit}:{rows[key]['stored']}"],
                               check=True, capture_output=True).stdout
            cache[key] = json.loads(gzip.decompress(b))["aa"]
        return cache[key]

    sample = [json.loads(l) for l in gzip.open(args.sample, "rt", encoding="utf-8")]
    sample = [p for p in sample if p["sampled"] and 8 <= p["rows"] <= 40 and 150 <= p["nonspace"] <= 2500]
    score = {
        "line_minimal": lambda p: p["envelope_blank"] + 0.02 * 100 * p["contour_idioms"] / p["nonspace"],
        "line_plus_tone": lambda p: (p["dot_bands_closed"] / p["dot_bands"] if p["dot_bands"] else 0) + p["envelope_blank"],
        "tone_dominant": lambda p: p["tone_share"],
        "dense_filled": lambda p: p["ink_share"],
        "text": lambda p: p["text_share"],
    }
    out = {"rules": __doc__, "by_class": {}, "cloud_scan": {}}
    for cls in M.CLASSES:
        picks = {}
        for p in sample:
            if M.style_class(p) != cls or (cls != "text" and p["text_share"] > 0.05):
                continue
            g = group(p["stratum"])
            s = (score[cls](p), tiebreak(p["key"], p["i"]))
            if g not in picks or s > picks[g][0]:
                picks[g] = (s, p)
        rowsout = []
        for g, (s, p) in sorted(picks.items()):
            text = M.decode_entities(record(p["key"])[p["i"]]["value"])
            at, ex = excerpt(text)
            rowsout.append({"group": g, "key": p["key"], "aa_index": p["i"], "path": rows[p["key"]]["path"],
                            "score": round(s[0], 4),
                            "metrics": {k: p.get(k) for k in ("ink_share", "envelope_blank", "outline_share",
                                                              "tone_share", "text_share", "contour_idioms",
                                                              "nonspace", "rows")},
                            "excerpt_first_line": at, "excerpt": ex})
        out["by_class"][cls] = rowsout
    for key, path in CLOUD_PAGES.items():
        assert rows[key]["path"] == path
        ranked = []
        for i, e in enumerate(record(key)):
            t = M.decode_entities(e.get("value") or "")
            if t.strip("\n").count("\n") < 1:
                continue
            ranked.append((sum(t.count(s) for s in LOBE), tiebreak(key, i), i, t))
        ranked.sort(reverse=True)
        lst = []
        for n, _, i, t in ranked[:3]:
            at, ex = excerpt(t, lobes=True)
            lst.append({"aa_index": i, "lobe_count": n, "excerpt_first_line": at, "excerpt": ex})
        out["cloud_scan"][key] = {"path": path, "top": lst}
    data = (json.dumps(out, ensure_ascii=False, indent=1) + "\n").encode()
    if args.out.exists() and args.out.read_bytes() != data:
        print(f"refusing to overwrite {args.out}", file=sys.stderr)
        return 3
    args.out.write_bytes(data)
    print(f"wrote {args.out} sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
