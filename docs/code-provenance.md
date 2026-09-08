# Code provenance

This standalone implementation was extracted from `rikiyanai/asciicker-Y9-2`
at commit `242ecba44f76ed1120dadf06653fd6de47017b7f`.

The glyph-family tooling was refreshed from `rikiyanai/asciicker-Y9-2` commit
`90d2f5edab212a9a1ecb9ec5d7161066047c7810`, then the standalone viewer's
read-only hardening was re-applied.

## Packaged owners

The extracted package includes these source owners:

- `scripts/compile_glyph_manifest.py`
- `scripts/fl4482_font_chain.py`
- `scripts/generate_glyph_shape_catalog.py`
- `scripts/glyph_audit.py`
- `scripts/glyph_combo_candidates.py`
- `scripts/glyph_families_viewer.py`
- `scripts/glyph_features.py`
- `scripts/glyph_morphology_browser.py`
- `scripts/glyph_skeleton.py`
- `assets/glyphs/authored/glyph_combinations.v1.json`
- `docs/research/ascii/glyph_audit/saved_families.jsonl`

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

Font identities and licenses are recorded separately in
[font-provenance.md](font-provenance.md).
