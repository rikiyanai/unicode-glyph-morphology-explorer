#!/usr/bin/env python3
"""Preserve the real AAJ browser capture; never regenerate rejected demo plates.

--delete-rejected removes only the five explicitly operator-rejected files in
the declared recordings directory. Recovered sources/palettes are untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/glyphs/contextual/windows-aa/recordings"
LUNA = ROOT / ".run/aa_recovery_recordings"
DATA = ROOT / "assets/glyphs/contextual/ascii_justice_recovery.v1.json"
REJECTED = ("uniform-dark-edge.png", "boundary-edge.png", "mask-page-01.png",
            "ascii-justice-edge-vs-area.gif", "ascii-justice-original-masks.gif")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delete-rejected", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "recordings.v1.json"
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    removed = list(old.get("rejected_artifacts", []))
    if args.delete_rejected:
        for name in REJECTED:
            path = OUT / name
            if path.resolve().parent != OUT.resolve():
                raise ValueError(f"Refuse out-of-directory deletion: {name}")
            if path.exists():
                removed = [r for r in removed if r["filename"] != name]
                removed.append({"filename": name, "sha256_before_deletion": digest(path),
                                "status": "operator rejected; deleted; not depictive/construction evidence"})
                path.unlink()
                print("Deleted:", path)
    capture = OUT / "luna-aaj-viewer.gif"
    if not capture.exists():
        capture.write_bytes((LUNA / capture.name).read_bytes())
    with Image.open(capture) as image:
        artifact = {"path": str(capture.relative_to(ROOT)), "sha256": digest(capture),
                    "size": list(image.size), "frames": image.n_frames,
                    "scope": "Real AAJ browser navigation; Saitamaar comparison rasters, not native Windows output or art approval."}
    manifest = {"source": str(DATA.relative_to(ROOT)), "source_sha256": digest(DATA),
                "generator": str(Path(__file__).relative_to(ROOT)), "generator_sha256": digest(__file__),
                "artifacts": [artifact], "rejected_artifacts": removed,
                "status": "Only the real browser capture is retained as an active recording. Demonstration plates were rejected and must not be recreated or recommended."}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
