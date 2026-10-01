#!/usr/bin/env python3
"""Count candidate idioms that are NOT in skill section 15.5 over every TRAIN
art piece of AA-004 (same inputs, decoding and piece rule as
aa004_style_stats.py). Candidates were read off exemplar pieces and the
outline n-gram lists in results.json; this script only counts them.

Output: --out candidate_idioms.json  {idiom: {n, pieces, pages, by_stratum_pieces}}
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aa004_style_stats as M  # noqa: E402

CANDIDATES = {
    # cloud / smoke contour (beyond the 15.5 lobe set)
    "cloud": ["⌒ヾ", "〃´⌒", "⌒⌒", "γ⌒", "⌒¨", "Y⌒", "Ｙ⌒", "⌒Y", "⌒Ｙ", "ノし", "～'", "'～", "⌒'", "ゝつ", "⌒ゝ", "ゝ'⌒"],
    # splash / spray
    "splash": ["人_", "_人", "__,ノ", "ノ(", "）ノ", ")ノ", "(_"],
    # tapered hatch: tone band running out into a line
    "taper": ["-=ﾆ", "ﾆ=-", "-=ニ", "ニ=-", "=-", "-="],
    # dot tone spelled with interleaved half spaces (`:·:·:`)
    "spaced_dot": [": : :", ". . .", "; ; ;", ":.:.:"],
    # face / figure idioms seen in character exemplars
    "face": ["（__人__）", "(__人__)", "（●）", "（○）", "●）", "（●", "ﾟ", "｀ー´", "ー'", "´ー｀"],
    # hair / strand vertical tone
    "strand": ["i!", "|i", "il", "li", "i|", "l|", "|l", "lll", "iii"],
    # diagonal hatch (blush, shadow, speed)
    "diag_hatch": ["///", "／／／", "＼＼＼"],
    # motion trail and speed lines
    "motion": ["〕iト", "≦=‐", "‐=‐", "─=≡", "≡=─"],
    # ground and grass
    "ground": ["､w,", "\"ﾞ", "'''\"\"'''", "ﾞ\"ﾞ", "wW"],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--split", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    sb = args.split.read_bytes()
    if hashlib.sha256(sb).hexdigest() != M.SPLIT_SHA256:
        raise SystemExit("split sha256 mismatch")
    split = json.loads(sb)
    commit = split["archive_commit"]
    index = subprocess.run(["git", "-C", str(args.archive), "show", f"{commit}:collections/aahub-mlt/index.jsonl"],
                           check=True, capture_output=True).stdout
    if hashlib.sha256(index).hexdigest() != split["index_sha256"]:
        raise SystemExit("index sha256 mismatch")
    rows = {r["key"]: r for r in map(json.loads, index.decode().splitlines()) if r}
    held = set(split["held_out_keys"])
    flat = [(g, s) for g, lst in CANDIDATES.items() for s in lst]
    n = collections.Counter(); pieces = collections.Counter(); pages = collections.Counter()
    by_st = collections.defaultdict(collections.Counter)
    st_pieces = collections.Counter()
    total = 0
    cat = subprocess.Popen(["git", "-C", str(args.archive), "cat-file", "--batch"],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for key in split["train_keys"]:
        assert key not in held
        st = M.stratum_of(rows[key]["path"])
        cat.stdin.write(f"{commit}:{rows[key]['stored']}\n".encode()); cat.stdin.flush()
        size = int(cat.stdout.readline().split()[2])
        blob = cat.stdout.read(size); cat.stdout.read(1)
        seen = set()
        for e in json.loads(gzip.decompress(blob))["aa"]:
            t = e.get("value") or ""
            if t.strip("\n").count("\n") < 1:
                continue
            t = M.decode_entities(t)
            total += 1
            st_pieces[st] += 1
            for g, s in flat:
                k = t.count(s)
                if k:
                    n[s] += k; pieces[s] += 1; by_st[s][st] += 1; seen.add(s)
        for s in seen:
            pages[s] += 1
    cat.stdin.close(); cat.wait()
    out = {"inputs": {"archive_commit": commit, "split_sha256": M.SPLIT_SHA256, "partition": "train_keys only",
                      "art_pieces": total},
           "stratum_pieces": dict(st_pieces),
           "candidates": {g: {s: {"n": n[s], "pieces": pieces[s], "piece_share": round(pieces[s] / total, 5),
                                  "pages": pages[s],
                                  "top_strata_by_piece_share": sorted(
                                      ((st, round(c / st_pieces[st], 4)) for st, c in by_st[s].items()
                                       if st_pieces[st] >= 500), key=lambda x: -x[1])[:4]}
                              for s in lst} for g, lst in CANDIDATES.items()}}
    data = (json.dumps(out, ensure_ascii=False, indent=1) + "\n").encode()
    if args.out.exists() and args.out.read_bytes() != data:
        print(f"refusing to overwrite {args.out}", file=sys.stderr)
        return 3
    args.out.write_bytes(data)
    print(f"wrote {args.out} sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
