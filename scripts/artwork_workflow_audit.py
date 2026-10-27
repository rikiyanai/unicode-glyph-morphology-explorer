#!/usr/bin/env python3
"""Read-only web discovery for exact artwork production provenance.

Fetches own .run/artwork_workflow_audit/ evidence cache only. Raw HTML is a
source capture, never a generated report. Findings belong in code-provenance.md.
No artist/tool attribution is inferred from a reused drawing or a username.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".run/artwork_workflow_audit"


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.ignore = 0
        self.links = []
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.anchor = [dict(attrs).get("href", ""), []]
        if tag in {"script", "style"}:
            self.ignore += 1
        if tag in {"br", "p", "div", "dt", "dd", "pre", "article", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor is not None:
            self.links.append((self.anchor[0], "".join(self.anchor[1])))
            self.anchor = None
        if tag in {"script", "style"}:
            self.ignore = max(0, self.ignore - 1)
        if tag in {"p", "div", "dt", "dd", "pre", "article", "li"}:
            self.parts.append("\n")

    def handle_data(self, text):
        if self.anchor is not None:
            self.anchor[1].append(text)
        if not self.ignore:
            self.parts.append(text)


def fetch(spec):
    label, url = spec.split("=", 1)
    if not re.fullmatch(r"[a-z0-9_-]+", label) or not url.startswith(("https://", "http://")):
        raise ValueError("Use a safe label=http(s)://URL")
    WORK.mkdir(parents=True, exist_ok=True)
    receipt = {"url": url, "fetched_utc": datetime.now(timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "AA-source-provenance-audit/1.0"})
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise ValueError("Source exceeds bounded 8MiB intake")
            charset = response.headers.get_content_charset()
            receipt.update(final_url=response.url, status=response.status, content_type=response.headers.get("Content-Type"))
        if not charset:
            match = re.search(br'charset\s*=\s*["\']?([\w-]+)', raw[:20000], re.I)
            charset = match[1].decode("ascii") if match else None
        charset = {"shift_jis": "cp932", "Shift_JIS": "cp932", "x-sjis": "cp932"}.get(charset, charset)
        decoded = None
        for encoding in dict.fromkeys([charset, "utf-8", "cp932", "euc_jp"]):
            if encoding:
                try:
                    decoded = raw.decode(encoding)
                    charset = encoding
                    break
                except (UnicodeDecodeError, LookupError):
                    pass
        if decoded is None:
            raise ValueError("Could not strictly decode source")
        if "html" in receipt["content_type"].lower():
            parser = Text()
            parser.feed(decoded)
            text = "".join(parser.parts)
        else:
            text = decoded  # MLT and JSON must never pass through an HTML parser.
        (WORK / f"{label}.raw").write_bytes(raw)
        (WORK / f"{label}.txt").write_text(text)
        receipt.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), encoding=charset,
                       text_lines=len(text.splitlines()), raw_path=str((WORK / f"{label}.raw").relative_to(ROOT)))
    except Exception as exc:
        receipt["error"] = str(exc)
    (WORK / f"{label}.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(label, json.dumps(receipt, ensure_ascii=False))


def inspect(label, terms, source, links=False):
    if links:
        receipt = json.loads((WORK / f"{label}.json").read_text())
        parser = Text()
        parser.feed((WORK / f"{label}.raw").read_bytes().decode(receipt["encoding"]))
        for href, title in parser.links:
            if not terms or any(term in href or term in title for term in terms):
                print(title.strip()[:100], urljoin(receipt["final_url"], href))
        return
    rows = (WORK / f"{label}.txt").read_text().splitlines()
    hits = [i for i, row in enumerate(rows) if any(term in row for term in terms)]
    if source:
        # Whitespace-only normalization is DISCOVERY, not verbatim equivalence.
        compact = lambda s: "".join(c for c in s if not c.isspace())
        needles = [compact(row) for row in source.read_text().splitlines() if len(compact(row)) >= 20]
        source_hits = [(i, row) for i, row in enumerate(rows) if any(n in compact(row) for n in needles)]
        print("Whitespace-normalized source-row discovery hits:", len(source_hits), "of", len(needles), "needles")
        hits.extend(i for i, row in source_hits)
    shown = set()
    for i in sorted(set(hits))[:20]:
        for j in range(max(0, i - 3), min(len(rows), i + 4)):
            if j not in shown:
                print(f"{j+1}: {rows[j][:350]}")
                shown.add(j)
    print("Total matching lines:", len(set(hits)))


def json_find(label, terms):
    doc = json.loads((WORK / f"{label}.raw").read_bytes())
    def visit(node):
        if isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            fields = {k: v for k, v in node.items() if isinstance(v, (str, int, bool))}
            if any(term in str(v) for term in terms for v in fields.values()):
                print(json.dumps(fields, ensure_ascii=False)[:1500])
            for value in node.values():
                if isinstance(value, (dict, list)):
                    visit(value)
    visit(doc)


def decode_plain(label):
    receipt = json.loads((WORK / f"{label}.json").read_text())
    text = (WORK / f"{label}.raw").read_bytes().decode(receipt["encoding"])
    (WORK / f"{label}.txt").write_text(text)
    print(label, "strict plain-text decode", receipt["encoding"], len(text.splitlines()), "rows")


def verify_upstream():
    """Check actual upstream MLT blocks, not artist attribution by filename."""
    registry = json.loads((ROOT / "assets/glyphs/contextual/operator_reference_sources.v1.json").read_text())
    reports = []
    for record in registry["records"]:
        label = "aamz-cup-original" if "aramaki-cup" in record["id"] else "aamz-church-original"
        receipt = json.loads((WORK / f"{label}.json").read_text())
        raw = (WORK / f"{label}.raw").read_bytes()
        if hashlib.sha256(raw).hexdigest() != receipt["sha256"]:
            raise ValueError("Changed upstream capture")
        text = raw.decode(receipt["encoding"]).replace("\r\n", "\n")
        variants = record.get("source_variants") or [{"text_path": record["original_full_text_path"]}]
        results = []
        for variant in variants:
            source_path = variant.get("raw_text_path") or record.get("original_raw_text_path") or variant["text_path"]
            source = (ROOT / source_path).read_text().strip("\n")
            starts = [m.start() for m in re.finditer(re.escape(source), text)]
            if not starts:
                raise ValueError(f"No exact upstream MLT match: {variant['text_path']}")
            results.append({"source_path": source_path,
                            "full_text_sha256": hashlib.sha256((ROOT / source_path).read_bytes()).hexdigest(),
                            "upstream_lines": [text.count("\n", 0, at) + 1 for at in starts],
                            "rows": len(source.splitlines())})
        report = {"id": record["id"], "upstream": receipt, "matches": results,
                  "creation_workflow": None, "creator": None,
                  "limit": "Exact collection-text match, not an original creation record or workflow attribution."}
        reports.append(report)
        print(record["id"], json.dumps(results, ensure_ascii=False))
    (WORK / "upstream-verification.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="append", default=[])
    parser.add_argument("--inspect")
    parser.add_argument("--find", action="append", default=[])
    parser.add_argument("--source", type=Path)
    parser.add_argument("--links", action="store_true")
    parser.add_argument("--json-find")
    parser.add_argument("--decode-plain")
    parser.add_argument("--verify-upstream", action="store_true")
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fetch, args.fetch))
    if args.inspect:
        inspect(args.inspect, args.find, args.source, args.links)
    if args.json_find:
        json_find(args.json_find, args.find)
    if args.decode_plain:
        decode_plain(args.decode_plain)
    if args.verify_upstream:
        verify_upstream()
