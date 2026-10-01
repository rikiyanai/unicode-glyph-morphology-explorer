#!/usr/bin/env python3
"""Derived tables for README.md, computed only from results.json and
sample_pieces.jsonl.gz (no archive access). Output: --out tables.json.

  group_weighted   TRAIN-weighted class shares per subject group
                   (works = kana-row and A・0・記号 title folders, 2ch, generic = 汎用AA,
                   other = 実在人物パロディ, 企業・ご当地キャラクター, 原典不明人物);
                   weight = stratum art pieces / stratum sampled pieces.
  broad            weighted share of sampled pieces with ink_share <= 0.05,
                   envelope_blank >= B and text_share < 0.3, for B in 0.5/0.6
                   (outline-first + sparse, tone not restricted).
  stratum_ci       Wilson 95 % interval for line_minimal per stratum
                   (piece-level; ignores page clustering, so it is narrow).
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aa004_style_stats as M  # noqa: E402
from exemplars import group  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--sample", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    res = json.loads(a.results.read_text(encoding="utf-8"))
    S = [json.loads(l) for l in gzip.open(a.sample, "rt", encoding="utf-8")]
    S = [p for p in S if p["sampled"]]
    real = {s: v["art_pieces"] for s, v in res["sampling"].items()}
    samp = collections.Counter(p["stratum"] for p in S)
    wt = {s: real[s] / samp[s] for s in samp}

    def wshare(P, pred):
        W = sum(wt[p["stratum"]] for p in P)
        return round(sum(wt[p["stratum"]] for p in P if pred(p)) / W, 4) if W else None

    out = {"inputs": {"results_sha256": hashlib.sha256(a.results.read_bytes()).hexdigest(),
                      "sample_content_sha256": hashlib.sha256(gzip.open(a.sample).read()).hexdigest()}}
    groups = collections.defaultdict(list)
    for p in S:
        groups[group(p["stratum"])].append(p)
    groups["ALL"] = S
    gw = {}
    for g, P in sorted(groups.items()):
        row = {c: wshare(P, lambda p, c=c: M.style_class(p) == c) for c in M.CLASSES}
        row["line_minimal_or_line_plus_tone"] = round(row["line_minimal"] + row["line_plus_tone"], 4)
        row["outline_dominant"] = wshare(P, lambda p: p["outline_share"] >= 0.6)
        row["sampled"] = len(P)
        row["art_pieces"] = sum(real[s] for s in {p["stratum"] for p in P})
        for B in (0.5, 0.6):
            row[f"broad_ink<=0.05_blank>={B}"] = wshare(
                P, lambda p, B=B: p["ink_share"] <= 0.05 and p["envelope_blank"] >= B and p["text_share"] < 0.3)
        gw[g] = row
    out["group_weighted"] = gw
    ci = {}
    for s in sorted(samp):
        P = [p for p in S if p["stratum"] == s]
        k = sum(M.style_class(p) == "line_minimal" for p in P)
        ci[s] = {"n": len(P), "line_minimal": round(k / len(P), 4), "wilson95": M.wilson(k, len(P))}
    out["stratum_ci"] = ci
    pc = {}
    for c in M.CLASSES:
        P = [p for p in S if M.style_class(p) == c]
        pc[c] = {"sampled": len(P),
                 "ink_share_median": M.med([p["ink_share"] for p in P]),
                 "envelope_blank_median": M.med([p["envelope_blank"] for p in P]),
                 "tone_share_median": M.med([p["tone_share"] for p in P]),
                 "outline_share_median": M.med([p["outline_share"] for p in P]),
                 "contour_idioms_per_100_median": M.med([100 * p["contour_idioms"] / p["nonspace"] for p in P])}
    out["per_class_unweighted_sample"] = pc
    data = (json.dumps(out, ensure_ascii=False, indent=1) + "\n").encode()
    if a.out.exists() and a.out.read_bytes() != data:
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    a.out.write_bytes(data)
    print(json.dumps(gw, ensure_ascii=False, indent=1))
    print(f"wrote {a.out} sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
