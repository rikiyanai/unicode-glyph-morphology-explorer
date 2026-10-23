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
- `scripts/sjis_corpus_combos.py`
- `scripts/glyph_seam_index.py`
- `scripts/glyph_cell_features.py`
- `scripts/glyph_cell_pairs.py`
- `scripts/glyph_families_viewer.py`
- `scripts/glyph_features.py`
- `scripts/glyph_morphology_browser.py`
- `scripts/glyph_skeleton.py`
- `assets/glyphs/authored/glyph_combinations.v1.json`
- `assets/glyphs/corpus/aahub_aa003_train.sjis_combos.v1.json`
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

The D42.10 doc-hygiene follow-up also records the measurement boundary between
this repository and the current Godot target. Standalone combo/seam data is
measured on the pinned font-chain terminal profile: 8×16 half-width cells and
16×16 full-width cells. The Godot native terminal now targets 16×32 half-width
cells, with intact 32×32 full-width masks spanning two adjacent tall cells, and
keeps orthographic and perspective election/proof conditions separate. Therefore
standalone families are candidate-discovery evidence only; runtime thresholds,
D_SM radii, altitude bands, and run offsets require a cell-unit rebase before
Godot consumption.

Font identities and licenses are recorded separately in
[font-provenance.md](font-provenance.md).

## Corpus-derived Shift_JIS combinations (2026-09-27)

`scripts/sjis_corpus_combos.py` is new code in this repository, not an import.
It scales `docs/research/ascii/sjis_aa_skill_audit/aa_slug_stats.py` from one
AAHub page to every training slug of the private ascii-art-archive snapshot
`3687cc564d3f542a3aaaea98b351713b360599f4`. The screenshot converter's
`data/aahub_split.json` (sha256 `d61d856f…a8d500`) decides which slugs are
training. `assets/glyphs/corpus/aahub_aa003_train.sjis_combos.v1.json` is its
output. It holds counts, and rows rendered in Saitamaar (font sha256
`8f8c9b6e…35890`); no archive text is copied into it beyond combinations of
at most three glyphs and band samples of at most 12.

## Contextual construction evidence (2026-10-23)

`assets/glyphs/contextual/shallot_native_contexts.v1.json` is a separate curated
evidence owner, not regeneration of the AA-003/AA-004 count files above. It
includes bounded longer/multi-row source excerpts, original row locators,
source hashes, regional operator-label scope and selected ordered turntable
glyph records. Its eight records retain unassigned and text-only candidates
alongside paired PNG/TXT witnesses. Exact local/private source paths document
origin; their availability on another installation is not promised.

The viewer's `context` mode and `combo` integration expose those relationships.
Terminal text preserves source codepoints but does not reproduce proportional
Saitamaar spacing; use paired native art for visual review. Neither record
membership, corpus recurrence, old renderer limits nor a whole-piece verdict
establishes a mathematical curve family, runtime implementation or acceptance.
`scripts/tests/test_contextual_combo_evidence.py` checks provenance and
source-passage consistency when the private source files are available.

## Native pattern intake (2026-10-23)

The operator supplied the stroke-bundle stdout from session
`f84bdfc6-58ab-4abb-bdf3-87932b50e456`. The surviving `bundles.py` and
`glyphcheck2.py` were inspected; their SHA-256 identities and the source-font
identity are retained in `assets/glyphs/contextual/saitamaar_pattern_intake.v1.json`.
All 47 supplied bundle rows reproduce with that pinned Saitamaar font, including
duplicate observations. The original term "strokes" denotes 8-connected ink
components; the viewer corrects that label without altering the raw stdout.
PCA describes a component's major axis, not its constituent pen strokes.

`scripts/saitamaar_pattern_intake.py` supplies a maintained reproduction and
native-advance raster builder. Its declared output is
`assets/glyphs/contextual/saitamaar_pattern_evidence.v1.json`; both input and
generator hashes are checked before viewing. The tracked rasters make the
comparisons viewable without those temporary scripts or an external font.
No font bytes are newly bundled. No claim about another renderer is imported.
Tone/curve combination layouts are explicit comparison proposals derived from
the supplied target spellings, not source-region approvals or motion evidence.

## README recording refresh (2026-10-23)

The two README GIFs were re-recorded from the actual terminal tools using their
maintained VHS tapes in `docs/recordings/`. The morphology browser recording
inspects U+31D6, ノ, 川 and ﾘ in its font-chain raster profile. The family recording
uses the native-pattern axis: parallel and vertical bundles, crossing forms,
curved-return combinations and multi-row tone columns. Startup/exit shell screens
are hidden; these are tool demonstrations, not renderer or artwork acceptance.
Both outputs were decoded and sampled at two-second intervals for visual review.

The operator approved the displayed native-pattern demo; its GIF is retained
unchanged (SHA-256
`66a036f299ae3d25299e61c0e8132739bf0a7f085f1fade1c35b96bb373d9c26`).
A separate `glyph-ramps-and-curves.gif` records the existing `glyph_audit.py anim`
CLI: U+1686–U+1689 (22, 28, 34, 40 ink pixels), U+2514/U+2570, and
U+30EC/U+3057. These are explicitly selected comparisons in the raw 16×16
font-chain profile, not newly discovered clusters, interpolation, native
Saitamaar measurements, or evidence of feature-anchored runtime refinement.
The 11.68-second output was fully decoded, and sampled frames were inspected
for all four ramp steps and both members of each corner/hook comparison.
The two earlier GIF hashes were verified unchanged after recording.
