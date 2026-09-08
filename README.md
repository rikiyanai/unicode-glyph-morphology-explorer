# Unicode Glyph Morphology Explorer

Unicode Glyph Morphology Explorer is a terminal browser for finding Unicode
characters by how they look.

It exists because codepoint names and script blocks are the wrong search tool
when you are building ASCII/Unicode visual effects. Sometimes you need “a thin
vertical stroke,” “a dense block,” “a diagonal ramp,” or “a family of related
shapes.” This repo renders glyphs through a pinned eight-font chain and compares
their 16×16 silhouettes by density, orientation, topology, and related visual
features.

Use it to browse candidate glyphs, inspect why they group together, and keep a
small reviewed registry of useful morphology families for ASCII-renderer work.

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

The family viewer shows reviewed glyph sequences as animated shape families.
You can switch morphology axes, filter by family length, change speed, pause on
a specific sequence, review distraction ranking, and inspect authored
multi-cell combinations beside their mirrors.

```sh
./run-families.sh
```

The first run builds a local ignored feature cache under `.run/`. The family viewer is read-only. Use `j`/`k` to select, `m` to change the morphology axis, `1`–`9` to filter by family length, and `q` to exit.

## Current family registry

The tracked review registry contains 96 nonblank family records. Fifteen records
come from the current Y9-2 source artifact: twelve `cycle` records covering
Latin-1 Supplement, Arabic, Basic Latin, Latin Extended-B, Greek Extended,
Mathematical Operators, and Cherokee, plus three `stroke` records covering CJK
Strokes and Katakana.

The `cycle` records use the viewer's existing family vocabulary. The three
`stroke` records are also visible through the viewer's stroke review surface.
The full registry is in
[docs/research/ascii/glyph_audit/saved_families.jsonl](docs/research/ascii/glyph_audit/saved_families.jsonl),
with source boundaries documented in [docs/code-provenance.md](docs/code-provenance.md).

## Glyph combinations

The package includes the authored Stone Story combination seed dictionary at
`assets/glyphs/authored/glyph_combinations.v1.json`. The viewer can render those
seeds with:

```sh
python3 scripts/glyph_families_viewer.py --mode combo --dump
```

For broader review, `scripts/glyph_combo_candidates.py` enumerates every
connected two- and three-cell arrangement over the source-named useful
non-alphanumeric line-art alphabet. It reports 25,088 candidates before any
manual art selection:

```sh
python3 scripts/glyph_combo_candidates.py --limit 20
```

## Included data

The repository includes the morphology browser, the read-only family viewer, the
selected saved-family registry, the glyph combination review data, the candidate
enumerator, and the pinned font chain used for rendering. It does not include
the full Asciicker engine or runtime.

Font identities, copyright metadata, license mapping, and license texts are recorded in [docs/font-provenance.md](docs/font-provenance.md) and `docs/licenses/`. Source-code identities are recorded in [docs/code-provenance.md](docs/code-provenance.md).
