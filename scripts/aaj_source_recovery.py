#!/usr/bin/env python3
"""Retrieve/inspect AAJ distribution data; never run the Windows program.

All download evidence writes are confined to .run/aaj_algorithm_recovery/.
--page parses a supplied vendor/download page; --archive saves a supplied URL.
No guessed URL grid, installer execution or binary patching is performed.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".run/aaj_algorithm_recovery"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src", "action"):
            if attrs.get(key):
                self.items.append((tag, key, attrs[key]))


def retrieve(url, page=False):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(32 * 1024 * 1024 + 1)
        final_url = response.geturl()
        charset = response.headers.get_content_charset()
    if len(data) > 32 * 1024 * 1024:
        raise ValueError("Refuse unexpectedly large distribution/page")
    identity = hashlib.sha256(data).hexdigest()
    WORK.mkdir(parents=True, exist_ok=True)
    filename = ("page-" + identity[:12] + ".html") if page else Path(urllib.parse.urlparse(final_url).path).name
    if not filename or filename in (".", ".."):
        raise ValueError("No safe download filename")
    target = WORK / filename
    target.write_bytes(data)
    receipt = {"requested_url": url, "final_url": final_url, "sha256": identity,
               "bytes": len(data), "saved_path": str(target), "execution": "none; data only"}
    target.with_name(target.name + ".source.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))
    if page:
        parser = Links()
        parser.feed(data.decode(charset or "cp932", errors="replace"))
        for tag, attr, link in parser.items:
            print(tag, attr, urllib.parse.urljoin(final_url, link))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--page")
    g.add_argument("--archive")
    args = p.parse_args()
    retrieve(args.page or args.archive, page=bool(args.page))
