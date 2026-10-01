#!/usr/bin/env python3
"""Compare two sjis_corpus_combos.v1 files (counts, coverage, rank changes).

Prints Markdown tables for idioms, outline bigrams and outline stacks:
count, rate per 1,000 lines, page and slug coverage (when the file has it),
and rank in each file. Rank changes are listed for entries in the top N of
either file; an entry missing from a file's top-300 list gets rank "-".
Counting only: no style interpretation.

Usage:
    python3 scripts/sjis_corpus_compare.py A.json B.json [--top 15] [--moves 10] [--window 50]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def key_of(cat: str, e: dict) -> str:
    if cat == "stacks_outline":
        return f"{e['upper']} over {e['lower']} {e['dx_px']:+d}px"
    return e["g"]


def md(k: str) -> str:
    """Inline code safe inside a Markdown table cell."""
    return "`" + k.replace("|", "\\|") + "`"


def ranked(d: dict, cat: str) -> dict[str, tuple[int, dict]]:
    rows = d[cat]
    if cat == "idioms":
        rows = sorted(rows, key=lambda e: -e["n"])
    return {key_of(cat, e): (i, e) for i, e in enumerate(rows, 1)}


def cov(e: dict | None, d: dict) -> str:
    if e is None or e.get("pages") is None:
        return "-"
    return f"{e['pages']:,} / {e['slugs']:,}"


def rate(e: dict | None, d: dict) -> str:
    return "-" if e is None else f"{1000 * e['n'] / d['lines']:.2f}"


def table(a: dict, b: dict, cat: str, top: int, la: str, lb: str) -> list[str]:
    ra, rb = ranked(a, cat), ranked(b, cat)
    keys = [k for k, _ in sorted(rb.items(), key=lambda kv: kv[1][0])][:top]
    out = [f"| {lb} rank | combination | {lb} n | {lb} /1k lines | {lb} pages / slugs | "
           f"{la} rank | {la} n | {la} /1k lines | {la} pages / slugs |",
           "|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k in keys:
        ib, eb = rb[k]
        ia, ea = ra.get(k, (None, None))
        out.append(f"| {ib} | {md(k)} | {eb['n']:,} | {rate(eb, b)} | {cov(eb, b)} | "
                   f"{ia if ia else '-'} | {ea['n'] if ea else 0:,} | {rate(ea, a)} | {cov(ea, a)} |")
    return out


def moves(a: dict, b: dict, cat: str, window: int, n: int, la: str, lb: str) -> list[str]:
    ra, rb = ranked(a, cat), ranked(b, cat)
    big = len(a[cat]) + 1
    cand = {k for k, (i, _) in ra.items() if i <= window} | {k for k, (i, _) in rb.items() if i <= window}
    rows = []
    for k in cand:
        ia = ra.get(k, (big, None))[0]
        ib = rb.get(k, (big, None))[0]
        rows.append((ia - ib, k, ia, ib))
    up = sorted(rows, key=lambda r: (-r[0], r[1]))[:n]
    down = sorted(rows, key=lambda r: (r[0], r[1]))[:n]
    fmt = lambda i: "-" if i == big else str(i)
    out = [f"Rose in {lb} (top-{window} of either): " +
           ", ".join(f"{md(k)} {fmt(ia)}→{fmt(ib)}" for d, k, ia, ib in up if d > 0),
           f"Fell in {lb} (top-{window} of either): " +
           ", ".join(f"{md(k)} {fmt(ia)}→{fmt(ib)}" for d, k, ia, ib in down if d < 0)]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--moves", type=int, default=10)
    ap.add_argument("--window", type=int, default=50)
    args = ap.parse_args(argv)
    a = json.loads(args.a.read_text(encoding="utf-8"))
    b = json.loads(args.b.read_text(encoding="utf-8"))
    la, lb = a.get("corpus", "AA-003"), b.get("corpus", "AA-003")
    out = [f"{la}: {a['slugs']:,} slugs, {a['pages']:,} pages, {a['lines']:,} lines. "
           f"{lb}: {b['slugs']:,} slugs, {b['pages']:,} pages, {b['lines']:,} lines.", ""]
    for cat in ("idioms", "bigrams_outline", "stacks_outline"):
        out += [f"#### {cat}", ""] + table(a, b, cat, args.top, la, lb) + [""]
        out += moves(a, b, cat, args.window, args.moves, la, lb) + [""]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
