# Code provenance

This standalone implementation was extracted from `rikiyanai/asciicker-Y9-2`
at commit `242ecba44f76ed1120dadf06653fd6de47017b7f`.

The glyph-family tooling was refreshed from `rikiyanai/asciicker-Y9-2` commit
`90d2f5edab212a9a1ecb9ec5d7161066047c7810`, then the standalone viewer's
read-only hardening was re-applied.

The 2026-09-08 seam-analysis refresh imports committed source from
`rikiyanai/asciicker-Y9-2` through `7a87dcd0dbfa99520803794e6ab46046a744b2ee`
plus the same checkout's observed working-tree corrections for the U+00B4
stair-step glyph and cell-feature cache builder. The
standalone wrapper keeps generated caches under `.run/` and does not package the
Asciicker runtime.

## Packaged owners

The extracted package includes these source owners:

- `scripts/compile_glyph_manifest.py`
- `scripts/fl4482_font_chain.py`
- `scripts/generate_glyph_shape_catalog.py`
- `scripts/glyph_audit.py`
- `scripts/glyph_combo_candidates.py`
- `scripts/glyph_combo_gallery.py`
- `scripts/glyph_combo_mine.py`
- `scripts/glyph_run_walker.py`
- `scripts/glyph_seam_index.py`
- `scripts/glyph_cell_features.py`
- `scripts/glyph_cell_pairs.py`
- `scripts/glyph_families_viewer.py`
- `scripts/glyph_features.py`
- `scripts/glyph_morphology_browser.py`
- `scripts/glyph_skeleton.py`
- `assets/glyphs/authored/glyph_combinations.v1.json`
- `assets/glyphs/authored/stone_story_tutorial_plates/01-sacrificial-pit-layers.txt`
- `assets/glyphs/authored/stone_story_tutorial_plates/02-poison-adept-walk-cycle.txt`
- `assets/glyphs/authored/stone_story_tutorial_plates/03-styles-fonts-alphabet.txt`
- `assets/glyphs/authored/stone_story_tutorial_plates/04-lines-materials-antialiasing.txt`
- `assets/glyphs/authored/stone_story_tutorial_plates/05-depth-dithering-shadows.txt`
- `assets/glyphs/authored/stone_story_tutorial_plates/06-animation-subtractive.txt`
- `docs/research/ascii/glyph_audit/saved_families.jsonl`

## Packaged review artifacts

- `docs/artifacts/glyph_combo_gallery.html`
- `docs/artifacts/SHA256SUMS`

These are generated review snapshots, not source owners. The canonical local
working outputs remain ignored under `.run/glyph_audit/`.

The family viewer differs from its source copy through deliberate read-only hardening:
the standalone removes the key that appended a selected family to
the tracked `saved_families.jsonl` registry. Rendering, navigation, animation,
filtering, and family discovery remain available.

## Registry update

The saved-family registry retains its original 81 nonblank extracted rows and
now includes 15 additional rows observed in the Y9-2 source checkout at
revision `54f0c8b2c256fd41d6dcb9e1b369d8b41235e31e` on 2026-08-31. The source
checkout was dirty when observed, so these rows are recorded as source-artifact
evidence rather than attributed to a clean committed source revision.

Twelve additions use the existing `cycle` family vocabulary. Three additions
use `stroke`; they are retained for evidence but are not represented as a
current interactive axis in `glyph_families_viewer.py`.

Public-facing wording and diagnostics may differ from the source extraction so
they describe behavior directly instead of carrying private development labels.
Those wording changes do not change the font identities or the morphology
algorithms.

The 2026-09-08 refresh adds the CJK Strokes dir8 exception, the distraction
metric, the authored combination dictionary, and the exhaustive useful
combination candidate enumerator. These are offline review tools only.

The seam-analysis refresh adds as-positioned cell features, pair/composite seam
measurement, the measured HTML combination gallery, and `glyph_families_viewer`
`--mode seam`. The standalone `./run-families.sh` command builds those caches on
first interactive launch and then opens the read-only viewer.

The run-walker refresh adds the packaged Stone Story tutorial plates, the
`glyph_combo_mine.py` usage counter, the whole-repertoire `glyph_seam_index.py`
pair index, and `glyph_run_walker.py` for variable-length beside and stacked runs. The
2026-09-08 follow-up sync imports the relation-aware stacked-run walker from
`rikiyanai/asciicker-Y9-2` through
`24dc777cf9ab4a99b3020c4438dd228b9cd486d2`, while preserving the standalone
viewer hardening and packaged Stone Story plate paths. A later same-day wrapper
fix keeps each run file as a separate gallery section and rebuilds stale length-3
Unicode/Kana/CJK/Arabic run caches to length 4. These remain offline exploration
tools; no Asciicker runtime source is packaged.

The family-viewer UI now reserves `AUTHORED` for the nine seed combinations and
uses `COMBOS` for the complete useful-combination review surface: authored seeds,
mined tutorial-plate usage, measured seam pairs, and generated Unicode run
buckets. The direct Python entrypoint opens on `COMBOS` first when launched
without arguments.

The 2026-09-08 D42.8 review sync keeps that standalone browser contract intact.
It records the Stone Story tutorial alphabet as 25 basic marks plus 4 extended
marks, and treats runtime `combo_hits` from Asciicker's seam-DP harness as a
candidate-transition diagnostic rather than selected or rendered run usage.
That runtime metric is not packaged as an explorer surface.

The later D42.10 review sync did not import Asciicker runtime Pieta media or the
prototype pack-v2 font routing into this repository. Those artifacts prove the
runtime contour-selection experiment, while this standalone package owns glyph
and combination exploration. The only added artifact here is the static combo
gallery snapshot generated from the standalone explorer data.

Font identities and licenses are recorded separately in
[font-provenance.md](font-provenance.md).
