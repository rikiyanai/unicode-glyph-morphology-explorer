# Unicode Glyph Morphology Explorer

A fork of [msokalski/asciicker](https://github.com/msokalski/asciicker), a CP437 3D ASCII engine.

Browse Unicode glyphs by rendered shape instead of only by codepoint or script. The tools use a pinned eight-font chain and 16×16 shape analysis to compare density, orientation, topology, and related visual features.

![Browse, filter, and inspect Unicode morphology](docs/glyph-morphology-explorer.gif)

## Run

```sh
python3 -m pip install -r requirements.txt
./run-browser.sh --block "Geometric Shapes"
```

The interactive browser requires a UTF-8 terminal. List the known Unicode blocks without entering the browser:

```sh
./run-browser.sh --list-blocks
```

Controls are shown in the browser footer. `q` exits without changing tracked files.

## Browse discovered families

![Animate and filter morphology families](docs/glyph-families-viewer.gif)

The recording shows live family animation, selection, morphology-axis switching, length filtering, speed control, and pause/resume; its source is [docs/recordings/glyph-families-viewer.tape](docs/recordings/glyph-families-viewer.tape).

```sh
./run-families.sh
```

The first run builds a local ignored feature cache under `.run/`. The family viewer is read-only. Use `j`/`k` to select, `m` to change the morphology axis, `1`–`9` to filter by family length, and `q` to exit.

## Current family registry

The tracked review registry contains 96 nonblank family records. Fifteen additional records are now carried from the current Y9-2 source artifact: twelve `cycle` records covering Latin-1 Supplement, Arabic, Basic Latin, Latin Extended-B, Greek Extended, Mathematical Operators, and Cherokee, plus three `stroke` records covering CJK Strokes and Katakana.

The `cycle` records use the existing family-discovery vocabulary. The three `stroke` records are preserved as source evidence; `stroke` is not claimed as a current interactive axis in `glyph_families_viewer.py`. The full registry is in [docs/research/ascii/glyph_audit/saved_families.jsonl](docs/research/ascii/glyph_audit/saved_families.jsonl), with the extraction and source-artifact boundary documented in [docs/code-provenance.md](docs/code-provenance.md).

## Included data

The repository includes the morphology browser, the read-only family viewer, the selected saved-family registry, and the exact pinned font chain used for rendering. It does not include the full Asciicker engine or runtime.

Font identities, copyright metadata, license mapping, and license texts are recorded in [docs/font-provenance.md](docs/font-provenance.md) and `docs/licenses/`. Source-code identities are recorded in [docs/code-provenance.md](docs/code-provenance.md).
