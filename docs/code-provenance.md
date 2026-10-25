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

## Circular-construction coverage check (2026-10-23, before intake)

The operator asked for actual AAHub circular/rounded constructions involving
more than the previously cited cap and lower-return idioms, specifically
`メ/ﾒ`, `イ/ｲ`, `ノ/ﾉ`, punctuation and an unidentified kanji. Do not identify
that kanji by guesswork or equate a glyph's presence with a circular use.

At `79cff43`, direct inspection of `scripts/sjis_corpus_combos.py` shows that
`is_stroke` rejects `メ` and `ﾒ`. This excludes them from the mined touching
pairs, triples and vertical stacks. The tracked AA-004 `viewable` list contains
zero entries with either glyph; it contains 1 with `イ`, 2 with `ｲ`, 4 with
`ノ` and 5 with `ﾉ` (entries containing the character, not occurrence counts).
Those counts establish packaged availability only, not circular depiction.
The native-pattern axis separately includes `メ/ﾒ` as whole-glyph comparisons;
it does not thereby preserve their source-context combinations. The existing
`aahub-rounded-cap-exemplar` preserves a `/⌒ヽ` passage with PNG/TXT provenance,
not a comprehensive circle-construction collection.

The requested Luna review confirmed a broader rounded-head source,
`ningen-mobu-09/res91`: paired PNG/TXT inspected, with `メ` on row 1's
upper hair contour, `ノノ` on row 2, and `ｲ` on row 8. `彡` and `州` also
occur in the hair mass, but neither identifies the operator's forgotten kanji.
The parent additionally inspected the paired PNG/TXT for these two controls:

| Source in `/Users/r/Projects/ascii-art-archive/collections/aahub/` | Observed construction | Whole passage in the viewer at `79cff43`? |
|---|---|---|
| [ningen-mobu-09/res91.png](/Users/r/Projects/ascii-art-archive/collections/aahub/ningen-mobu-09/res91.png), [TXT](/Users/r/Projects/ascii-art-archive/collections/aahub/ningen-mobu-09/res91.txt), rows 1–8 | Rounded portrait/hair contour involving `メ`, `ノノ`, `ｲ` and neighboring rows; not a universal meaning for those glyphs. | No. The AA-003 slug aggregate is not a packaged res91 source passage. |
| [yasai-kudamono/resK-185.png](/Users/r/Projects/ascii-art-archive/collections/aahub/yasai-kudamono/resK-185.png), [TXT](/Users/r/Projects/ascii-art-archive/collections/aahub/yasai-kudamono/resK-185.txt), rows 1–20 | Round watermelon: punctuation traces much of the rim, stripe constructions include `ｲ` and `州/洲`, and row 20 has `ﾒﾌ` where a stripe reaches the lower rim. Interior striping is not interchangeable with the outer contour. | No. |
| [bakuhatsu-kemuri/resK-72.png](/Users/r/Projects/ascii-art-archive/collections/aahub/bakuhatsu-kemuri/resK-72.png), [TXT](/Users/r/Projects/ascii-art-archive/collections/aahub/bakuhatsu-kemuri/resK-72.txt), rows 1–8 | Open-paper circular ring built across rows from shallow punctuation/horizontal arcs, diagonals, vertical sides and a small cap; not one repeated curve glyph. | No. The existing source-context record is resK-147, not resK-72. |

These checks correct the earlier broad availability claim: the original archive
contains the examples, but the viewer at `79cff43` did not package these full
contextual constructions as directly viewable reference families. No remembered
kanji was identified conclusively. This initial check was documentation-only;
the subsequent intake below supersedes its availability result.

## Portable AAHub round-reference intake (2026-10-23)

**Operator-rejected selection; uncommitted and not pushed.** The operator
rejected these examples after inspection. The selection substituted rounded
subjects and scattered glyph occurrences for the requested local combinations
that construct circular contours. Packaging exact bytes and passing viewer
tests did not validate that selection. Do not cite this batch as confirmed
coverage of the requested circle-construction vocabulary. The unidentified
kanji remains unresolved. The following records retain what was investigated
and built, not a recommendation or approval to ship it.

At the operator's request, seven byte-identical native PNG/TXT pairs are now
packaged under `assets/glyphs/contextual/aahub-round-refs/`. The source definition
and generated index are `aahub_round_refs.sources.v1.json` and
`aahub_round_refs.v1.json` in the parent contextual directory. The maintained
producer `scripts/aahub_round_refs.py --write` copies only those declared pairs
and writes that index. Read-only loading verifies definition and pair SHA-256
identities; viewing needs neither the original archive nor an external font.

The first three sources are the portrait, watermelon and ring recorded above.
The explicitly requested Luna follow-up inspected four additional native pairs:

| Source | Observed relationship and limits |
|---|---|
| `yasai-kudamono/resK-232`, rows 1–15 | Raised stem/calyx, rounded shoulders, sides and lower arc; a tomato-section item per the archive heading, not an artist-intent label. |
| `jitensha/resK-01`, rows 7–20 | Two rounded punctuation-band wheel rims and their hubs/frame. Parent text/image review refined the initial dot/dash-only description; the rims also use colon/period bands and sloped returns. No live URL was established from its manifest. |
| `shingu-butsugu-mingeihin-zou/res373`, rows 1–35 | Tapered oval/teardrop enclosure around the figure, then pedestal. Repeated `非` is inside the enclosure, not the outer contour or an identification of the forgotten kanji. |
| `shingu-butsugu-mingeihin-zou/res424`, rows 2–24 | Nested head, veil and shoulder arcs, including upper-turn `イ`; interior punctuation is distinct from the outer boundary. This exact archive pair is retained separately from the older annotated S#424 artifact. |

The parent inspected all seven native pairs, compared the original three with
their live AAHub passages, and retained the narrower observed roles rather than
promoting glyph co-occurrence to circular meaning. All original PNG and TXT bytes
are preserved; no font bytes were added. Package paths and direct PNG/TXT links
are in the README's round-reference table.

`./run-families.sh --mode round` opens the new **ROUND REFERENCES** axis without
building discovery or seam caches. The same records appear under **CONTEXT
EVIDENCE** and **COMBOS**. Its labelled overview is integer ink pooling, not native
glyph-fit evidence. `v` selects a 1:1 native-pixel viewport, `h/l` pans, and `[/]`
scrolls the image and exact source text/provenance. Native pixels are not
resampled, rotated or respelled in the terminal font. This addition does not
change the skill, renderer or historical AAHub corpus measurements/filter.

### Chrome receipt and verification scope

The original three live pages are open in Chrome: 人間・モブ09, 野菜・果物 and
爆発・煙. Initial historical `#res` fragment navigations returned `undefined`;
using AAHub's live search and selecting the matching page loaded each correctly.
The exact portrait, watermelon and ring text was located and brought into view,
and the resulting screenshots were inspected. Page URLs are retained without
invented post anchors; archived piece IDs and pair hashes identify the drawing
independently of live numbering. A local `file:` navigation was rejected by the
browser policy and was not bypassed.

The new tests check all seven source pairs, exact TXT rows and focus strings,
archive-byte reproduction where available, bounded labelled overviews, pixel-
exact native panning, all discovery surfaces, and cache-free CLI/wrapper dumps.
The real TUI was exercised through a 9.84-second VHS capture under the ignored
`.run/glyph_audit/round-reference-check.*` outputs. All seven overviews plus
native and panned views were sampled and visually inspected; the GIF fully
decoded. This is viewer verification, not artwork or renderer acceptance.
All 197 tests passed across the repository's twelve test modules (31 contextual/
pattern/round-reference tests, 68 cell/combination/export tests, and 98 directed/
distraction/run/corpus tests). The three existing README GIF hashes were checked
unchanged during this intake.

## Original AAHub reference index — operator's eight crops and cup (2026-10-24)

**Current source locator, updated after the parallel Luna search:** all eight
local crop constructions now have matched source references, and the complete
cup has its exact original text. Seven crops have a single full-artwork source;
**crop 04 matches a motif shared by three artwork variants**, so its unique
variant and repeated left/right occurrence are not asserted. Saving a crop alone
was not sufficient; the new bindings follow full-page image search plus parent
inspection of the actual crop and corresponding archived glyph passages.

The machine-readable owner is
[operator_reference_sources.v1.json](../assets/glyphs/contextual/operator_reference_sources.v1.json).
Its producer `scripts/operator_reference_sources.py --write` rechecks the church
source bindings and all three shared-motif variants against the original compressed archive, and rechecks
the **complete cup drawing** against its own AAHub archive. It retains original
page URLs, zero-based archive indices, source/crop paths and SHA-256 identities.
The viewer's source panes expose `reference registry path` and `original
reference status`; screenshots and full original text are separate fields.

| Operator example | Preserved exact supplied crop/text | Original AAHub artwork and source binding |
|---|---|---|
| **Cup, steam, plate and reclining character** | [Complete exact drawing](../assets/glyphs/contextual/aramaki-cup-plate-176.txt), all 21 rows | **Matched**: [荒巻スカルチノフ](https://aahub.org/mlt/e8e2f681204d649ea2033d2f62399a04), archived `aa[176].value`. Rim/side/return rows 5–14; plate/context rows 15–21. No exact original native PNG packaged. |
| Crop 01 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-01.png) | **Matched**: [church page](https://aahub.org/mlt/2f0353dc8e23bde120d1c050746f937c), archived `aa[161]`, MTG Godless Shrine / `ＭＴＧ 神なき祭壇`; [complete original text](../assets/glyphs/contextual/operator-constructions/church-161.txt), [raw text](../assets/glyphs/contextual/operator-constructions/church-161.raw.txt), rows 11–13: `ｧ宀v`, `弋__人`, `∧`. |
| Crop 02 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-02.png) | **Matched**: [church page](https://aahub.org/mlt/2f0353dc8e23bde120d1c050746f937c), archived `aa[165]`, Karnak; [complete original text](../assets/glyphs/contextual/operator-constructions/church-165.txt), [raw archived text](../assets/glyphs/contextual/operator-constructions/church-165.raw.txt). Crop passage rows 7–10. |
| Crop 03 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-03.png) | **Matched**: [church page](https://aahub.org/mlt/2f0353dc8e23bde120d1c050746f937c), archived `aa[36]`, Assisi; [complete original text](../assets/glyphs/contextual/operator-constructions/church-036.txt), [raw archived text](../assets/glyphs/contextual/operator-constructions/church-036.raw.txt). Crop passage rows 7–8. |
| Crop 04 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-04.png) | **Shared motif matched, not a unique variant**: same church page, rows 6–7, `（(⌒Y⌒)）` / `)Ｉi(`, in [aa[105] wedding](../assets/glyphs/contextual/operator-constructions/church-105.txt), [aa[106] wedding without people](../assets/glyphs/contextual/operator-constructions/church-106.txt), and [aa[107] ordinary-church variant](../assets/glyphs/contextual/operator-constructions/church-107.txt). Each repeats the motif twice. All three full original texts and raw counterparts are packaged; none is claimed to be uniquely identified by this crop. |
| Crop 05 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-05.png) | **Matched**: same church page, archived `aa[97]`; [complete original text](../assets/glyphs/contextual/operator-constructions/church-097.txt), [raw text](../assets/glyphs/contextual/operator-constructions/church-097.raw.txt), rows 4–7: `(　)`, `/⌒Ｙ`, `乂__ﾉ`, `しく__`. |
| Crop 06 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-06.png) | **Matched**: [church page](https://aahub.org/mlt/2f0353dc8e23bde120d1c050746f937c), archived `aa[73]`, church basement; [complete original text](../assets/glyphs/contextual/operator-constructions/church-073.txt), [raw archived text](../assets/glyphs/contextual/operator-constructions/church-073.raw.txt). Crop passage rows 7–17. |
| Crop 07 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-07.png) | **Matched**: same church page, archived `aa[57]`, Poland / Kraków St Mary's Church; [complete original text](../assets/glyphs/contextual/operator-constructions/church-057.txt), [raw text](../assets/glyphs/contextual/operator-constructions/church-057.raw.txt), rows 12–14: `(__)`, `γ⌒ヽ`, `乂__ソ`. |
| Crop 08 | [Exact screenshot](../assets/glyphs/contextual/operator-constructions/crop-08.png) | **Matched**: same full original `aa[57]` as crop 07; [complete text](../assets/glyphs/contextual/operator-constructions/church-057.txt), rows 9–14, including upper `γ⌒ヽ` / `{　　　}` / `乂__乂` and the lower neighboring round. |

Archive indices above are **zero-based local `aa` array positions**, not verified
current live post IDs. No guessed `#post` anchors were added. The additional
[complete Milan church text](../assets/glyphs/contextual/operator-constructions/church-027.txt)
is preserved, but is not falsely assigned to an unresolved crop.

**Cup provenance:**
`/Users/r/Projects/ascii-art-archive/collections/aahub-mlt/e8/e8e2f681204d649ea2033d2f62399a04.json.gz`,
`aa[176].value`; packaged full drawing SHA-256
`8a9030fade504f4033854e98d677830aecdf5b884cbd2df5f48e8b4c7e745808`.
The contextual record remains `aramaki-cup-plate-surface-following-tone` in
`assets/glyphs/contextual/shallot_native_contexts.v1.json`, with the operator's
positive explanation verbatim. The related food-page cup with **rice** is a
different drawing and is **not** substituted for this reference.

Verification after source matching: **37 focused tests passed**, covering the nine individual source
entries, original archive equality, complete cup identity, unchanged crop hashes,
explicit unresolved statuses and viewer links. `git diff --check` passed. This
is archive-source verification, not a new native-image or visual-quality claim.
The public cup page returned the JavaScript-required shell to the web reader;
the available Chrome binding could not be used for new live-page confirmation.
The exact source match is therefore grounded in the inspected saved archive.
Source-discovery candidates, if any, are not admitted by image-match score alone.

## Operator-supplied cup/plate tone example (2026-10-23)

The operator supplied the complete cup, steam, plate and reclining-character
drawing and explicitly called it a positive example of sparse dots **together
with directional multi-stroke glyphs that hug/bend with the surface**. The exact
text is preserved in `assets/glyphs/contextual/aramaki-cup-plate-176.txt`; the
source-context owner is `aramaki-cup-plate-surface-following-tone` in
`shallot_native_contexts.v1.json`. This is separate from the rejected seven
round-reference candidates and must not be used to rehabilitate that selection.

An exact text match was found at `aa[176].value` in the local AAHub
`e8e2f681204d649ea2033d2f62399a04` (荒巻スカルチノフ) archive. The stored file
SHA-256 is `8a9030fade504f4033854e98d677830aecdf5b884cbd2df5f48e8b4c7e745808`;
the LF-trimmed source-text SHA-256 is
`2e97412f21e7dece93d4019afc548c6df9d749f3450920a95a9e0580dee08b28`.
The index is a zero-based archived array index, not an asserted live post ID.
The original operator explanation is retained verbatim in the context record.

The important combination is not "dots make tone." Rows 5–14 tie the upper rim,
sparse-to-denser punctuation, directional `彡` side marks, and changed `彳`/`ジ`
lower returns to the same form. Rows 15–21 retain the plate ellipse, paper and
shadow as neighboring context. These are observed relationships, not a universal
brightness-to-glyph rule or evidence of a renderer implementing them.

The related `tabemono-01/resK-182` native PNG was inspected, but it depicts a rice
mound on the plate rather than this reclining character. It is not the exact
paired image and is not attached as one. The new record is therefore honestly
text-only until the exact variant's native image is preserved. The statue and
church/architecture pages requested by the operator are open in Chrome under
their verified page titles; no new circle-example approval is claimed.
The 14 contextual-evidence tests pass, including exact archived-text identity,
the distinct plate variant, the operator explanation and the stored row spans.

## Operator-supplied local construction crops (2026-10-23)

The operator supplied eight screenshot crops and three full architectural text
passages after rejecting the rounded-object selection. All eight original PNG
byte streams are now retained in `assets/glyphs/contextual/operator-constructions/`.
These are screenshot witnesses with their actual pixel dimensions and hashes;
no font size, advance lattice or original source-pixel crop coordinates are
invented. The canonical definition/index are
`operator_construction_crops.sources.v1.json` and
`operator_construction_crops.v1.json` in the contextual data directory. Producer
`scripts/operator_construction_crops.py --write` owns only those declared outputs.

The three supplied architectural passages match church-page archived entries
27 (Milan), 36 (Assisi) and 165 (Karnak). Crop 06 additionally identifies archived
entry 73, the Fate/stay night church-basement drawing. All four complete source
texts are packaged, preserving raw `aa[index].value` and HTML-decoded display
text separately; for example, Assisi's raw `&#8561;` must not be silently treated
as literal drawn ampersand text or as byte-identical to the pasted decoded form.
The index pins the archive file SHA-256 and hashes every preserved artifact.

Source correspondences verified by neighboring glyph passages, not inferred
from a rounded subject label:

- Crop 02: entry 165, rows 7–10, column-cap `jI斗-─--ミ`.
- Crop 03: entry 36, rows 7–8, `γ⌒ヽ` above `乂__ノ`.
- Crop 06: entry 73, rows 7–17. The left band changes through `ｲﾆア゜` and
  `/ﾆｱ`; the right changes through `寸ム`, `寸ﾊ`, `∨i,` and `Ⅵｉ` as the arch
  becomes steeper. The kanji **寸** is directly identified in this source, not
  guessed from memory. The central column interrupts the visible arch; the
  cropped drawing does not assert that every stroke belongs to one isolated path.

The exact crop-to-row bindings for 01, 04, 05, 07 and 08 remain unresolved. Their
original images remain viewable, with no guessed Unicode transcription or false
source-page attachment. The supplied Milan text remains available for further
binding rather than being assigned to a crop without evidence.

**This supersedes the rejected selection in the active TUI.** `--mode round`
now opens **CONSTRUCTION CROPS**, loading only these eight supplied witnesses.
They also appear in CONTEXT EVIDENCE and COMBOS; none of the seven rejected
rounded-object candidates is returned by that loader. Overview pooling and
unscaled source-pixel view are labelled separately. The source screenshot is
not retyped in the terminal font; exact source rows remain separate text evidence.
This intake changes neither the skill nor any renderer or historical corpus counts.
The 31 focused crop/context/pattern tests pass. The real TUI was captured under
the ignored `.run/glyph_audit/operator-crop-check.*` outputs and the GIF fully
decoded. Sampled views for crops 01, 03, 06 and 08 plus a panned 1:1 crop-06
viewport were visually inspected. This verifies the viewing path, not unresolved
source bindings or renderer behavior. These changes remain uncommitted.

## Circular construction synthesis and saved Windows tools (2026-10-24)

### What was unresolved, and what the supplied examples actually show

"Unresolved" meant **five exact screenshot-to-source-row bindings**, not an
absence of observable construction. The requested Luna follow-up compared crops
01/04/05/07/08 with the four retained church passages and the suggested statue
archive; it returned no confident additional binding. Keep those five screenshots
viewable without guessing their Unicode. Crops 02/03/06 remain source-matched.
The earlier rounded-object examples were a selection failure, not an explanation
of the operator's requested local constructions.

The following is an observational synthesis, not knowledge of the artists'
unseen workflow or a claim about all AAHub art:

1. **Construct an opening and its turns across rows.** A circle is often made
   from shallow crown/bottom marks, changing shoulders, steeper sides and returns,
   rather than repeated parentheses or a large `O`. The enclosed paper and where
   strokes approach/meet are part of the construction.
2. **Change articulation as the tangent changes.** Crop 06's broad arch uses
   the complete `x≪ニ二ﾆ`/`／二-＞''~` shoulder region, then `ｲﾆア゜` and `/ﾆｱ`
   on the left; the right descends through `寸ム`, `寸ﾊ`, `∨i,`, `Ⅵｉ` toward an
   upright. These are differently shaped whole-glyph combinations cooperating
   along a curved band, not a fixed diagonal repeated down a staircase. Exact
   witness: [church-073 rows 7–17](../assets/glyphs/contextual/operator-constructions/church-073.txt)
   and [crop 06](../assets/glyphs/contextual/operator-constructions/crop-06.png).
   **寸** is identified there; this does not prove it is the operator's formerly
   remembered kanji.
3. **Fit adjacent ink and spaces, not character names.** Crop 03's `γ⌒ヽ`
   above `乂__ノ` builds the small round opening from cap/shoulder and lower-return
   relationships. The cross-strokes are part of the intact glyphs, not disposable
   noise. The source's proportional spacing must be retained; terminal columns
   are not a substitute for its native positioning. Witness:
   [church-036 rows 7–8](../assets/glyphs/contextual/operator-constructions/church-036.txt),
   [crop 03](../assets/glyphs/contextual/operator-constructions/crop-03.png).
4. **A curved band is more than one thin contour.** In crop 06, multiple strokes
   establish band thickness/inner and outer turns; the central pillar interrupts
   its visibility. Treating every character as a single isolated centerline loses
   that cooperation. The other supplied crops also show paired lobes, narrowed
   meetings and stacked rounded openings; their exact text remains unassigned.
5. **Surface-following tone uses both sparse and directional marks.** The
   operator's cup example combines dot/colon/semicolon fields with `彡`, then
   changed `彳`/`ジ` lower returns, next to the rim and protected paper. Density
   alone cannot describe the orientation or surface turn. This is the separately
   preserved [cup/plate witness](../assets/glyphs/contextual/aramaki-cup-plate-176.txt),
   not an exact paired raster or a universal dithering rule.

### Recovered saved patterns, not newly invented presets

The packages were already saved in `/Users/r/Desktop/shift_jis_research/` and
extracted in `inspection-20261015/`. Shallot's existing evidence owner had already
recorded the static inspection and 40 motifs. This turn directly rechecked the
saved files and made portable text evidence available here instead of repeating
that earlier report as a new discovery. No PE/installer was executed.

`scripts/windows_aa_intake.py` pins AA Judgment's executable SHA-256 to
`891dc66d0fe134e0002c7cfb1e296dec407ccb0afb0253418d77741b33756fb5`.
It reads the PE section table, recognizes the bounded Delphi compare/assign
instruction chains and decodes their referenced AnsiStrings. **All 41 builder
mappings agree with the first 41 output mappings**: 40 multi-character candidates
plus a separate ideographic space. A 42nd output-only substitution maps ASCII
space to underscore; it is not counted as a matching-template motif. The retained
JSON contains literal strings, codepoints and instruction/string addresses.
This is a build-pinned extractor, not a general decompiler or a full port.

All 40 recovered strings:

| | | | |
|---|---|---|---|
| `__` | `,-^` | `^-,` | `..` |
| `.;` | `;;` | `ll` | `lll` |
| `^)` | `(^` | `ﾟl` | `lﾟ` |
| `...` | `^^^` | `^^` | `.-` |
| `-.` | `--` | `-^` | `^-` |
| `.l` | `l.` | `./` | `.ヽ` |
| `:l` | `l:` | `,,` | `..l` |
| `l..` | `.／` | `.＼` | `li,` |
| `ﾞ､` | `｀､` | `-､` | `ﾟ｡` |
| `ﾞ:､` | `.｡` | `｡.` | `,il` |

Lowercase `l`, ASCII `i`, halfwidth punctuation and fullwidth slants are distinct.
These are small local mask candidates, **not the artist's circular/architectural
dictionary**. The saved Orinrin brush groups are `.,:;`, `l|`, and `ニ三`, including
variants with trailing spaces and `彡`/`ミ`. Its broad insertion palette and three
multiline user items are preserved too. The bundled lettering sets have 10
numeral, 85 hiragana/punctuation and 91 katakana/punctuation entries. The fourth
top-level AST (packaged as `lettering-3.ast` for deterministic inventory order)
is an **illustrated manual with 36 tags, not another lettering preset set**.
Raw CP932 bytes and strict UTF-8 decodes are both retained, with separate hashes.
No template appearance in its intended Windows font was certified.

### Tracing: recovered mechanism and limits

**AA Judgment — automatic local image matching.** Directly inspected pinned
native disassembly at the builder, source-sampling, scoring and output ranges:

- `0x45065b–0x450ad7`: substitute short combinations before rasterization.
- `0x450ad7–0x450c2a`: measure/draw the native text candidate and sample its
  black pixels into 192-byte slots, 16 pixels high and at most 12 sampled columns.
- `0x451a2d–0x451b08`: sample 12 columns × 16 rows at the current image position;
  integer grayscale `(3R + 6G + B)/10`, then compare with the black-level threshold.
- `0x451ec0–0x452307`: compare candidate and source masks. Dark/dark and white/white
  matches earn rewards; missing source ink and added ink incur separate penalties.
  Density/width, mode and sharpness affect weights/normalization. This is not
  average-brightness-only matching. A complete scorer-equivalent port has **not**
  been implemented or tested here.
- `0x452805–0x45291e`: append the selected text, measure the accumulated row's
  native width, and continue from that horizontal position; row pitch is 17 pixels
  proportional or 16 monospaced. Blank/tone shortcuts also exist. The inspected
  handler is sequential local fitting, not evidence of cross-row opening/junction
  preservation or feature-anchored animation.

**Orinrin — actual source found and retrieved.** Its saved readme explicitly
points to GitHub; the author's [upstream repository](https://github.com/SikigamiHNQ/OrinrinEditor)
was located. Four original source files were retrieved at commit
`f5dd6da43198eccbf58fbe2eec71ebe8c7fdb874` (Ver0.341), as raw CP932 and decoded
UTF-8, with GPL text and a hash manifest. They were not compiled. Source/binary
reproducibility is not established merely by their matching version label.

- `TraceCtrl.cpp:930–953` adjusts contrast, gamma, gray mix and rotation;
  `:997–1030` positions, scales, optionally mirrors/flips and blits the image into
  the view. It does **not** choose glyphs in these routines. Its tracing mechanism
  is a manipulable underlay for manual construction, not automatic vectorization.
- `LineTemplate.cpp:838–943` reads `[ListName=...]` groups and passes each intact
  line to the template callback; `BrushTemplate.cpp:584–605` selects a brush item
  and calls `ViewBrushStyleSetting`. This establishes reusable textual insertions,
  not a hidden curve synthesizer.
- `DocAdjustant.cpp:172–195` exchanges one 11-dot fullwidth space for two 5-dot
  ASCII spaces to reduce a gap by one dot. `:244–295` uses remainder tables and
  Unicode spaces for additional widths. These are that editor's metric assumptions,
  not measurements of Saitamaar or a universal license to alter glyph ink.

**Historical checkpoint, superseded by the bytecode recovery below:** at this
earlier inspection ASCII Justice had manual evidence only. Its saved CP932 manual, rows 103–113,
distinguishes tonal gradation from outline extraction (three line thicknesses)
and quality/speed modes. Its exact scorer had not yet been recovered; do not
assign AA Judgment's algorithm to it because the author is the same.

**Useful transfer:** evaluate intact short combinations in their actual font,
preserve their advances/spacing, and distinguish manual construction over a guide
from local automatic image fitting. The AAHub examples additionally require
multi-row turns, band thickness, openings and meetings—none is supplied merely
by discovering these 40 candidates. No renderer or skill changes were made.

The portable pattern/mapping index and decoded source files are linked in the
README. Three new records are discoverable in CONTEXT EVIDENCE and COMBOS.
Context-only viewing now uses its own codepoint index, so it does not depend on
a private glyph-discovery cache. That fixes a directly observed cache-missing
CLI failure without claiming any new font rasterization.

Verification: **39 focused tests passed** across Windows intake, contextual
evidence, operator crops and native-pattern intake. Checks include direct PE
recovery when the saved original is present, builder/output agreement, exact
CP932/UTF-8 identity and trailing spaces, pinned upstream source/license hashes,
and cache-free context discovery. The wrapper dump returns 20 context records
(12 textual records plus eight operator crops). A real TUI capture exercised
the three new records; its selected brush-pane screenshot was directly inspected.
That verifies textual accessibility, not native Windows rendering or artistic
quality. `git diff --check` passed. No commit or push was performed in this turn.

## AA Judgment browser completeness and further algorithm recovery (2026-10-24)

### All 40 combinations are individually viewable

The previous intake exposed all 40 AA Judgment strings inside one textual
context record. That was not a dedicated per-template morphology view. It is
now supplemented, not replaced, by the **AA JUDGMENT** axis (`--mode aaj`):
40 independently selectable records in builder order, also included in COMBOS
and the default browser. The axis and wrapper bypass discovery-cache creation.

`scripts/aaj_template_intake.py --write` produces only
`assets/glyphs/contextual/aaj_templates.native.v1.json`. It takes the complete
40-entry recovered mapping—not a manually selected subset—and checks the pinned
Saitamaar font hash `592bf6be…b9b3a28`. Each record retains the original string,
codepoints, internal label, executable/string addresses, actual per-character
advances/positions, and a 16px-font / 17px-row thresholded raster. Whole glyphs
are drawn without shape normalization, deformation or replacement. The tracked
pixels make viewing independent of the original font/downloads. Narrow panes
clip the raster with a warning rather than wrapping or stretching it.

**Font boundary:** these are explicitly labelled **Saitamaar comparison rasters**,
not a recovery of AA Judgment's original Windows/MS Gothic bitmap atlas.
Template-text completeness does not establish original-font pixel equivalence
or that these motifs construct the operator's AAHub examples.

### Orinrin: the recovered algorithm is spacing and manual tracing assistance

The pinned `TraceCtrl.cpp` routines inspectably manipulate and display an image
underlay; they do not automatically generate glyph contours. Contrast/gamma/gray
operations are delegated to `imgctl` DLL functions. This task does not claim to
have recovered that DLL's internal filter formulas, or a nonexistent glyph chooser
from the blitting routines. The template parser/brush selector retain intact
textual insertions; the artist remains responsible for their construction.

The reusable algorithm in `DocAdjustant.cpp` has now been transcribed into
`scripts/orinrin_spacing.py`, with the original copyright, source commit and
GPL-3.0-or-later notice retained for that derived file:

- `DocPaddingSpace` / `SpaceWidthAdjust`: start with 11-dot fullwidth and 5-dot
  ASCII spaces; replace one fullwidth space by two ASCII spaces to shrink the
  gap by one dot until an exact representation is found or fullwidth spaces run
  out. `SpaceStrAlloc` fills backward, alternating half/full spaces where possible.
- `DocPaddingSpaceUni`: divide the requested width by 11, emit that many fullwidth
  spaces, then use the exact source remainder table for widths 1–10. Examples:
  U+200A=1, U+2009=2, U+2006=3, U+2005=4, ASCII space=5, U+2002=8,
  U+2007=10; widths 6/7/9 pair a thin space with an ASCII space.
- Both routines reject nonpositive widths. The port preserves that behavior and
  the exact returned text ordering, rather than merely finding any equal-width sum.

Exhaustive checks over widths 1–1000 verify representability/assumed width.
They do not measure those codepoints in Saitamaar or the user's terminal. The
result is an inspectable spacing precedent, not permission to stretch glyphs or
to assume one font's spacing constants in another renderer.

### ASCII Justice: static bytecode recovery succeeded

This supersedes the earlier **manual-only** status. The saved executable hash
remains `e640f35c4ff70506e2db76d2c6bcf83e8670277fd53ad3319f4f50b9a5dc4ac7`.
It contains an unencrypted DPM archive with `start.ax` HSP2 bytecode,
`mjdata14.dat`, `mjnodo14.dat` and help text. Every recovered payload was checked
byte-for-byte against its offset in that pinned executable. The JSON manifest
retains sizes, offsets and SHA-256 identities. No Windows PE/DLL was executed.

The source of [deHSP](https://github.com/xsyetopz/deHSP) was downloaded at commit
`491d12d935758a7563b6588b934247536f185b44`, inspected and built as a native .NET CLI
in the ignored `.run/aa_algorithm_recovery/` workspace. SDK 10's new CA2263 lint
initially failed its warnings-as-errors gate; setting `AnalysisLevel=8.0` rebuilt
the **unchanged** upstream source successfully. Runtime roll-forward used the
installed .NET runtime. The target executable was passed strictly as file data
from an input copy inside that declared workspace. No Wine, target execution,
target installer or LFS operation was used.

The resulting **919-line HSP2 decompilation** is preserved as original CP932 bytes
and a strict UTF-8 decode under `assets/glyphs/contextual/windows-aa/ascii-justice/`.
`ascii_justice_recovery.v1.json` owns the source hashes, label/line ranges, tool
provenance and decoded glyph table. This is recovered decompiler output, not the
author's original source: variable/label names are reconstructed. In particular,
the negative-darkness clamp statements at lines **409 and 515** are malformed.
They remain visibly unchanged; the listing was not silently repaired or executed.

The two original `.dat` files are also retained. They encode 96 slots of 8×16
32-bit masks and 96 density integers. The recovered candidate string maps the
first **93 slots** to ASCII characters; three trailing slots are not mapped.
Reading the first HSP array index fastest and interpreting **0=ink, 1=paper**
gives a decisive check: all 93 mapped masks' black-pixel counts equal their
corresponding density entries. These are original table pixels, not newly
rendered approximations or claims about a Japanese proportional alphabet.

### What ASCII Justice actually computes

The following mechanisms are visible in the recovered listing. They are not
borrowed from AA Judgment:

| Stage | Listing witness | Recovered mechanism |
|---|---|---|
| Layout and vocabulary | lines 20–58, 235–244, 345–350 | Fixed 8×16 cell traversal and a 93-character ASCII candidate map. This is not AA Judgment's proportional multi-character candidate library. |
| Tonal preparation | `label_10/11/12/13` | Weighted RGB thresholding, nearly blank/dense shortcuts, quality-dependent sampling, plus accumulated darkness for later density selection. Fast examines 15 candidates; normal 48; nice 93; highest uses three alignment blocks built from the first 48 candidates. |
| Edge extraction | `label_14`, lines 837–890 | Compare each RGB channel separately between adjacent vertical/horizontal samples; an edge exists if **any squared channel difference > (12×darkness_setting+16)²**. Not Sobel, luminance-only gradient or RGB-vector-length thresholding. |
| Edge thickness | `label_73/76`, lines 891–912 | Mark the comparison's starting pixel, then optionally the next one/two pixels in the positive comparison direction. This is directional thickening to 1/2/3 pixels, not centered morphological dilation. |
| Mask matching | `label_16/17/18/19`, lines 651–836 | Sample the recovered binary glyph masks and accumulate distinct match/mismatch rewards, using staggered rows and quality-dependent horizontal alignments. |
| Final selection | lines 299–344 | Sort accumulated scores with HSPDA, then walk ranked candidates looking for a density-compatible result. Normalize candidate indices modulo 93. If none passes, fall back to the leading match, with a special `M` fallback considering the first five ranks. |

The pixel reward table is directly transcribed from repeated scoring expressions:

| Source sample | Template ink | Template paper |
|---|---:|---:|
| Dark | +18 | +3 |
| White | −18 | +6 |

Thus unwanted ink is explicitly penalized; equal average brightness alone is
not the scorer. In outline mode fast/normal score 15/48 candidates at 64 staggered
positions. Nice/highest score 48/93 candidates in each of three horizontal
alignment blocks, at 56 positions per block. Block starts are 0/93/186 within a
285-slot zero-initialized score array; unfilled slots remain zero. These details
are preserved, not replaced with a newly designed optimizer.

Density selection rescales a glyph's table ink count by `11/3`, compares it with
the accumulated/remapped darkness, and accepts a squared discrepancy below
`(gradation_internal+2)²×60`. This accounts for a tone preference separate from
shape-match ranking. HSP2 evaluates unparenthesized expressions left-to-right;
for example, the RGB divisor initialization means `(15+27+3)/3 = 15`, not the
result of Python/C precedence. The vendor's
[migration guide](https://www.onionsoft.net/hsp/v34/doclib/update.htm#FROM2_CALC)
documents that HSP3 changed this behavior. Do not execute the recovered listing
under a modern expression evaluator and call it equivalent.

**Portable, tested subset:** `scripts/ascii_justice_kernels.py` transcribes the
edge mask and outline matching score kernels, with readable names. It preserves
the original omitted border comparisons (vertical pair origins y=0..13;
horizontal origins x=0..5), staggered sample positions, alignment blocks,
unfilled score slots and reward table. The tests check threshold equality versus
strict excess, directional thickness, original border omissions and independent
scalar scoring against the extracted table. No invented border repair is hidden
in a claimed recovery.

**Still not certified:** the complete RGB/gradation path, the malformed clamps,
HSPDA tie ordering, whole-converter equivalence, Windows display-font fidelity or
the quality of produced drawings. The kernels are runnable research code, not
a replacement for MAIN and not a demonstrated circle-construction grammar.

### Reproduction and verification scope

The pinned saved target remains outside the repository. To repeat the optional
static recovery with an installed .NET SDK, use:

```sh
python3 scripts/recover_ascii_justice.py --fetch-tool
python3 scripts/recover_ascii_justice.py --decompile --intake
python3 scripts/aaj_template_intake.py --write
./run-families.sh --mode aaj
```

Only regenerating AAJ pixels requires the pinned external font; browsing does
not. The original `.exe`, extracted `.ax`, downloaded decompiler and compiled
native tooling stay in the ignored recovery workspace, not the portable intake.

**Executed checks:** 62 focused tests pass across AAJ previews, recovered
algorithms, Windows intake and existing context/crop/pattern/round-reference
modules. These include all 40 template-to-record bindings, font-snapshot
reproduction, cache-free CLI/wrapper discovery, COMBOS/default-axis inclusion,
all 93 mask/density correspondences, threshold and score arithmetic, and
Orinrin's assumed-width spacing. A real TUI capture selected the first, tenth
and fortieth entries; the tenth-entry screenshot was directly inspected. Its GIF
fully decodes. This is browser verification, not Windows-output equivalence or
artwork approval. The existing three README GIFs were not regenerated.

Broader tests: cell/combination/export modules returned **57 passed, 11 skipped**.
Directed/distraction/run/corpus modules returned **84 passed, 12 skipped, 2 failed**.
Both failures are the old SJIS CLI paths exiting with `no feature cache`; the
inspected committed viewer also routes SJIS through `ga.Corpus()`. The missing
private cache was not rebuilt, and this unrelated path was not rewritten for
this task. Do not report a fully passing repository suite. No skill or renderer
changes, commit or push were made.

## Recording delivery, recovery-status correction and overlooked presets (2026-10-24)

**Recording-delivery section superseded by operator rejection below.** The mask
and synthetic edge plates described in this historical checkpoint were rejected
as irrelevant to the requested AA constructions, then deleted. They are not
current deliverables or evidence of request satisfaction. The actual recovered
source/palette evidence remains separate and preserved.

**Current status, replacing the quoted manual-only table:** ASCII Justice's
HSP2 listing, original mask/density tables and selected algorithms **have been
recovered**. The 919-line listing is decompiler output, not the original authored
source; two malformed clamp statements and lack of whole-converter Windows
parity remain explicit. The old manual-only paragraph is now labelled a
superseded historical checkpoint. Do not answer the operator with that old row.

The operator explicitly requested a Luna subagent to record GIFs. Luna returned
a real AAJ TUI capture, an exact-table mask gallery and a synthetic edge-kernel
demonstration. Parent inspection of the generated source found that the initial
gallery used nonsquare display pixels/overflowing labels and the initial edge
plate clipped the candidate's lower rows. Those two plates were **not** published
as accepted outputs. The maintained producer `scripts/aa_recovery_recordings.py`
regenerates readable plates with uniform square pixel magnification, bounded
labels and all 16 mask rows visible. Luna's real TUI GIF is preserved byte-for-byte.

Durable files, separate from the three previously approved README demos:

| Recording | What it establishes / does not establish |
|---|---|
| `windows-aa/recordings/luna-aaj-viewer.gif` | Actual browser navigation among the recovered templates. The rasters are labelled Saitamaar comparisons, not original AAJ Windows/MS Gothic output. |
| `windows-aa/recordings/ascii-justice-original-masks.gif` | Six pages covering all 93 mapped original 8×16 mask entries and their exact density counts, with uniform integer magnification. Labels use a UI font; the mask shapes come directly from the recovered table. |
| `windows-aa/recordings/ascii-justice-edge-vs-area.gif` | Synthetic uniform-dark and boundary examples, three outline thicknesses, and raw-score candidate masks computed by the recovered Python kernels. This is not full tonal conversion, final density selection or original application playback. |

Paths above are relative to `assets/glyphs/contextual/`. The producer and
`recordings.v1.json` preserve hashes, dimensions, frame counts and correction
scope. Original Luna generation/capture recipes are archived for provenance;
their original `.run/aa_recovery_recordings/` location is recorded. Run the
maintained `scripts/aa_recovery_recordings.py` for the corrected plates, not an
archived recipe as if its old relative paths had changed. The parent directly
inspected the published first mask page and boundary-demo frame. All three GIFs
fully decoded with ffmpeg; no Windows PE/DLL was launched.

### Contour versus tone, without a false either/or

In **this converter**, "outline/contour mode" means detecting contrast changes
in image pixels before matching glyph masks. It is not a mathematical silhouette
or suggestive-contour detector. A uniformly dark tile produces no edge marks;
only its boundary can trigger them. **Tonal mode** instead retains area-darkness
information and uses glyph ink/density to depict it. The recovered converter's
tonal path still uses shape matching; tone does not mean average-brightness-only
matching or random dots. The two notions describe what information is being
represented, not disjoint glyph alphabets or a ban on mixed constructions.

The operator's cup example combines both: rim/returns and sparse punctuation
**plus directional multi-stroke bands** describe the surface together. The
surface-following orientation and boundaries of those bands are not explained
by an ink-density number alone. The new demo deliberately shows the difference
between a dark region and an edge mask; it does not pretend to reproduce the
still-unvalidated full tonal converter.

### Concrete preset evidence the earlier account missed

The saved `aalist.txt` was inaccurately summarized as a single-character palette.
"One-line template" is the editor's insertion format, **not a guarantee that each
entry has one character**. Direct inspection now confirms all 24 named groups,
including 16 "frequently used strings", 17 expressions, 18 injuries, 19 tears,
20/21 upper/lower eye forms, 22 impact, 23 fingers and 24 angry mouths.
They contain multi-character entries and blank-separated adjacent-row construction
samples. Concrete, source-backed examples include:

- Impact group 22: `ゞ从ﾚ`, `ゞ火ノ`, `ゞ乂ノ`, `ノし／`, `⌒ヾて`.
- Fingers group 23: `f^!`, `γ）`, `/〉`, `／入`, `Yﾌ`, `Y７`.
- Mouth group 24 has the exact three-row rounded construction:

```text
　 ／⌒ヽ
　.i　　　　i
　 ヽ ＿ ノ
```

These are **already bundled reusable patterns**, not newly invented examples.
They are not labelled architectural motifs or proof that these programs created
the supplied church drawings. `LineTemplate.cpp` still parses individual nonempty
rows; preserving a multi-row source sample is not evidence that it is inserted
atomically as one macro.

`windows_aa_intake.py` now preserves every named group, exact row ranges, blank
rows and untrimmed source text in the pattern index, and exposes all 24 separately
as `orinrin-palette-01` through `orinrin-palette-24` in CONTEXT EVIDENCE and COMBOS.
The context surface consequently has 44 records (36 textual records plus the
eight supplied crops), not the previous checkpoint's 20. The AAJ preview snapshot
was regenerated after the index changed. No historical corpus measurements were
silently recomputed.

The operator's larger inference is justified at the **pattern** level: repeated
turns, junctions, openings and directional bands are reusable constructions, not
merely incidental occurrences of similar-looking characters. The inspection
failed by prioritizing character membership/rounded subjects and generic fitting
over complete neighboring-row passages and their geometric role, and then by
failing to inspect the saved palette deeply enough. A lack of identified source
rows did not justify overlooking the visual relationships.

Attribution remains a separate question. A practitioner explicitly documents
choosing/placing glyphs over a tracing image, establishing a manual tracing
workflow alongside reusable techniques
([AA construction walkthrough](https://ccblassty.blog.fc2.com/blog-entry-6.html)).
The inspected source establishes both editor presets and automatic local matchers.
Neither proves which one, or what mixture of tools and manual work, produced
each AAHub source. In particular, this recovered ASCII Justice build emits only
its 93 mapped ASCII characters, so its unmodified output cannot directly supply
the kana/kanji in the operator's arch/cup passages. Later hand editing remains
possible; no author/tool provenance was invented.

Verification after palette intake: **63 focused tests passed**, including exact
24-group reproduction, the bundled rounded sample, intact source spans, all
40 individually viewable AAJ templates and the previously recovered kernels.
With the recording checks included, **66 focused tests pass**. The added tests
decode every GIF frame and verify every displayed original glyph-mask pixel and
all displayed edge/candidate pixels against their sources, including the bottom
rows. `git diff --check` passes. No renderer or skill changes, commit or push
occurred in this recording/palette clarification task.

## Operator rejection: delete the five demonstration assets (2026-10-24)

The operator rejected the demonstration assets as showing none of the requested
AA drawing/construction behavior and explicitly instructed deletion plus an
independent Luna verification. The failure was delivery relevance, not a need
for more pixel-copying tests. The previous 66-pass result did not establish
that those demonstrations answered the operator's request.

Deleted only these five explicitly named files under
`assets/glyphs/contextual/windows-aa/recordings/`:

- `uniform-dark-edge.png`
- `boundary-edge.png`
- `mask-page-01.png`
- `ascii-justice-edge-vs-area.gif`
- `ascii-justice-original-masks.gif`

Their pre-deletion hashes and rejection state are recorded in the existing
recording manifest, not as active image links. README recommendations were
removed. The maintained producer no longer contains any mask-gallery or toy-edge
generation code; it retains only the real AAJ browser capture. Tests now guard
against reintroducing the rejected files/links, rather than certifying them as
successful delivery. Recovered bytecode/source, original numeric tables, the
24-group Orinrin palette and the real AAJ browser capture were not deleted.

Opening receipt from the interrupted preceding task: the practitioner article
was opened in Chrome at its exact URL and verified by its Japanese article title.
`open -R` was executed for the exact local `aalist.txt` path. Finder showed the
containing `windows-aa` folder, but its state initially selected `upstream`;
the corrective selection/Chrome-focus action was interrupted by the operator.
Do not report that final file selection or both foreground views as completed.

The first requested Luna audit completed against the pre-deletion snapshot and
correctly reported files still present and stale recommendations. That result
was not counted as verification of the later changes. A fresh Luna final-state
audit ran after deletion and returned **PASS**, read-only:

- All five rejected assets absent; no filename mentions or links in README.
- Recording manifest has five rejected records and only one active artifact,
  `luna-aaj-viewer.gif`; source/producer/active-recording hashes match.
- Maintained producer contains no demo-plate generation. Earlier delivery text
  is explicitly superseded, rather than presented as current approval.
- The retained palette CP932 file is byte-identical to the available external
  saved original: 9,587 bytes, SHA-256 `07eecc6e…6e141286`. All nine indexed
  source/text pairs exist, with all 24 palette groups retained.
- ASCII Justice's 919-line listing and 49,152/384-byte numeric tables remain.
  All 40 individually selectable AAJ template records remain intact.
- Luna executed **17 passing targeted tests** across recording retention,
  Windows intake and AAJ template intake. These checks establish source/artifact
  integrity, not artistic quality, native Windows playback or converter parity.

The first audit also independently confirmed that the linked artist walkthrough
describes manually placing/revising glyphs over a tracing image, not an automatic
construction algorithm or attribution of any particular archived drawing. No
new visual result was substituted for the rejected demonstrations. No commit or
push occurred in this deletion/verification task.

## Requested palette reveal and tracing walkthrough opened (2026-10-24)

Completed the operator's renewed opening request, superseding the interrupted
opening receipt above:

- Executed `open -R /Users/r/Projects/unicode-glyph-morphology-explorer/assets/glyphs/contextual/windows-aa/aalist.txt`
  successfully. Finder's current accessibility state explicitly selected
  `aalist.txt` at that exact path in the `windows-aa` folder.
- Opened Finder Quick Look for the selected file. Its title was `aalist.txt`,
  and the displayed text contained all 24 named groups, including expressions
  (17), impact constructions (22), fingers (23) and mouths (24). These are the
  saved preset source, not the rejected edge/mask demonstrations. The existing
  CONTEXT EVIDENCE / COMBOS intake remains unchanged.
- Reused the existing Chrome tab for the explicitly requested
  [artist walkthrough](https://ccblassty.blog.fc2.com/blog-entry-6.html), checked
  its exact URL, Japanese article title and tracing instructions, and marked it
  to remain open. The article describes manually placing text over an image
  underlay; this is not evidence of automatic glyph selection or attribution
  of particular AAHub drawings to Orinrin. A supplementary browser screenshot
  timed out; the opening check is based on the returned page accessibility
  state, not a claimed screenshot receipt.

Only this canonical log was edited in this opening task. No new demonstrations,
renderer/skill changes, commit or push.

## Local construction-to-tool mapping clarification (2026-10-24)

The operator asked what the deleted diagnostics actually represented and how
the supplied circle/arch/tone constructions map to recovered Windows tools.
Rechecked the retained manifest, archived generation recipe, recovered kernel,
all 40 AAJ strings, original Orinrin brush/palette rows and the exact source
passages. No rejected image was regenerated.

- `mask-page-01.png` and `ascii-justice-original-masks.gif` were newly laid-out
  galleries of genuine recovered **individual 8×16 glyph masks**, not original
  application screenshots/output or AAHub combination drawings. The surrounding
  labels/layout were authored for the diagnostic.
- `uniform-dark-edge.png`, `boundary-edge.png` and
  `ascii-justice-edge-vs-area.gif` were synthetic input/edge/scoring illustrations
  made with the Python subset. They tested contrast-change extraction and raw
  candidate scores; they did not run the Windows converter or its complete final
  tone/density selection. A constant-dark input can have no interior edges while
  still requiring tonal depiction. This distinction does not explain away the
  missing multi-row construction mapping.
- **Exact preset witness, analogous role:** Orinrin palette 24 contains the
  three source-adjacent rows `　 ／⌒ヽ`, `　.i　　　　i`, `　 ヽ ＿ ノ`.
  This is an actual rounded opening under a mouth heading, not proof of the
  supplied church's source or an automatic circle routine. Palette 22 contains
  `γ⌒` and `⌒ヽ{`; these share turn fragments with church-036's `γ⌒ヽ`,
  but the full two-row `γ⌒ヽ` / `乂__ノ` construction was not identified as
  an exact bundled preset. AAJ contains `__` only as a tiny local candidate;
  that substring is not a recovered circle grammar.
- **No complete recovered template match:** church-073's thick arch changes
  articulation from `x≪ニ二ﾆ` / `／二-＞''~` to `ｲﾆア゜` / `/ﾆｱ`, and
  from `寸ム` to `寸ﾊ`, `∨i,`, `Ⅵｉ` on the opposite side. Those complete
  passages are not among the 40 AAJ candidates. The inspected Orinrin presets
  have not supplied an exact whole-arch match. ASCII Justice's recovered
  93-character ASCII output map cannot directly emit these kana/kanji strings.
- **Shared brush vocabulary, not recovered arrangement:** the cup's punctuation
  and `彡` overlap Orinrin's actual `.,:;` and `ニ三` brushes (`彡`/`ミ` included).
  The rim, directed side bands and changing `彳`/`ジ` lower returns are not thereby
  established as a bundled cup construction or automatic surface-following rule.

Supported interpretation: the examples assemble locally fitting, intact glyphs
and spacing across rows into shallow caps, changing shoulders, steep sides,
returns, thick curved bands and enclosed paper. Tools offer reusable fragments,
manual underlay/spacing assistance, or local automatic image matching; recovered
local scoring is not evidence of a multi-row circle/arch grammar. The
[practitioner walkthrough](https://ccblassty.blog.fc2.com/blog-entry-6.html)
independently demonstrates manual placement and revision over an underlay, not
provenance of these particular AAHub drawings. Five supplied crop-to-text
bindings remain unresolved; no inferred kana/kanji transcription was invented.

This is a source comparison and explanation, not new converter parity, drawing
quality or author/tool attribution verification. Only this canonical log changed.

### Why the recovery does not yet explain the complete constructions

The operator challenged the phrase “we have not recovered an algorithm that
recognizes and preserves complete multi-row circles or arches.” That phrasing
conflated three separate gaps:

- **Implementation recovery:** AAJ's complete scorer-equivalent port and ASCII
  Justice's whole-converter parity remain unfinished. Extracted tables and tested
  kernels do not close those gaps.
- **Construction mapping:** the saved preset fragments and supplied AAHub rows
  have only partial mappings. A complete font-positioned, neighboring-row account
  of each supplied construction has not been delivered. Diagnostic mask galleries
  were not a substitute for that requested comparison.
- **Attribution:** there is no identified tool/session record for these particular
  artworks. Manual tracing is documented elsewhere, not established as their
  exclusive production method.

A dedicated semantic circle recognizer is **not a prerequisite** for an image
matcher to produce a circle-like result: local matches can collectively follow
the source boundary. That is a possible mechanism, not a demonstrated explanation
of these references. Likewise, a manually assembled or pasted construction can
reuse a vocabulary without a circle generator. The proper unresolved question is
which recovered mechanisms reproduce the supplied passages and their relationships,
not whether a routine happens to be named or structured as a circle recognizer.
No source inspection here establishes that such a routine is impossible or absent
from every AA tool. No new converter execution or visual equivalence is claimed.

## Continued construction comparison: what recurs and how (2026-10-24)

The operator asked to continue answering what produces the recurring
combinations. Added `scripts/construction_tool_mapping.py`, its portable
`assets/glyphs/contextual/construction_tool_mapping.v1.json`, and viewer detail
integration. The source rows, operator screenshots, original Windows templates,
skills and renderer were not changed. No rejected diagnostic image was restored.

### Directly checked, bounded findings

- Compared **23 exact fragments**: two from Assisi's opening, fourteen around
  the church-basement arch, one Karnak capital passage, and six cup passages.
  Every fragment has an unambiguous row/codepoint span, complete native-advance
  glyph placements under the pinned Saitamaar 16px comparison profile, and exact
  substring/brush matches against the recovered tool vocabulary. Source and
  template hashes bind the snapshot. Saitamaar positions are not inferred
  measurements of the supplied screenshots' font.
- Re-inspected crop 03 and crop 06 via the image guard's supplied previews.
  The arch's transitions are visible as a continuous band, not isolated slashes;
  those previews do not establish pixel-exact font equivalence.
- Assisi's `γ⌒ヽ` shares exact `γ⌒` with palette 22, row 972, and `⌒ヽ`
  with several saved cap constructions. The lower `乂__ノ` additionally shares
  **`__ノ`** with palette 24 row 1410, not just the previously reported `__`.
  These are partial overlaps, not a matching whole two-row preset. Under the
  comparison font, the cap occupies advance interval x=345–389 and the lower
  fragment x=349–386 on the following 17px-pitch row. That documents an aligned
  two-row construction; advance intervals are not contour/ink bounding boxes.
- The arch's shallow bands share `ニ二`, `二ﾆ` and other fragments with the
  palette. Its source-exact `ｲﾆア゜`, `/ﾆｱ`, `寸ム`, `寸ﾊ`, and `Ⅵｉ`
  have **no shared substring of two or more codepoints** with the inspected
  palette rows or the forty AAJ combinations. This bounded result does not mean
  those characters are unavailable to an editor, absent from every preset
  library, or unavailable among AAJ's other candidate characters.
- The cup directly overlaps saved punctuation brushes plus `彡`. AAJ's
  `..`, `...` and `;;` cover pieces of its punctuation, not its complete
  surface-following bands. ASCII Justice availability is checked against the
  actual recovered 93-character map, not assumed from a character's name.

### Mechanism supported versus still untested

The drawings exhibit **composition by changing local articulation**: shallow
caps, fuller shoulders, steep sides and returns cooperate across rows, with
spacing preserving an opening and multiple strokes supplying band thickness.
The cup couples sparse dots to fuller directed marks rather than treating tone
as uniform fill. These are observations/interpretations of the supplied source
construction, not recovered author instructions.

Saved palette fragments demonstrate that parts of this vocabulary were reusable.
The inspected Orinrin code supplies selection, insertion, spacing and an image
underlay; the inspected automatic matchers supply source/template ink comparison.
Local fitting could generate related fragments without semantic circle recognition,
but reproducing these exact passages through those matchers is **not yet tested**.
The common vocabulary therefore has concrete source/preset overlaps; attributing
the entire arrangement to one recovered algorithm remains unsupported.

The former external AAJ input path
`/Users/r/Desktop/shift_jis_research/inspection-20261015/aaj/aaj.exe` is not
currently present. The recovered tables, addresses and comparison data remain
packaged; this turn did not re-disassemble that executable or complete its port.
No claim of whole-converter parity, exhaustive reference coverage, or visual
approval follows from the new comparison.

### Verification

`python3 -m unittest scripts.tests.test_construction_tool_mapping
scripts.tests.test_operator_construction_crops
scripts.tests.test_contextual_combo_evidence`: **29 tests passed**. Checks bind
exact fragment/template locators, preserve full/halfwidth distinctions, verify
native advances, expose mappings in round/cup context panes, and exercise loading
without a local font. The real cache-free `--mode round --dump` contains the new
comparison sections for the three bound crops. No UI capture or drawing-quality
acceptance is claimed. `git diff --check` passed. No commit/push performed.

Expanded regression run added `test_aaj_template_intake`,
`test_recovered_aa_algorithms` and `test_aa_recovery_recordings`: **46 tests run,
45 passed, 1 skipped**. This does not supersede the stated converter-parity or
visual-review limits.

## What produces the recurring combinations — mechanism answer (2026-10-24)

**The recurring unit is a font-specific construction assembled from intact
glyph ink, horizontal placement, neighboring rows and deliberate paper.** It
is not merely a round character, nor does its recurrence require a hidden
whole-circle preset. In the supplied sources, different local articulations
cooperate to construct a consistent bend, band, opening or surface-tone passage.
That is an observational account of the construction; it does not identify the
original artist's editor or editing history.

### Directly documented authoring operations

The practitioner's [first tutorial](https://ccblassty.blog.fc2.com/blog-entry-5.html)
documents **ずらし** (dot-level placement shifts), **抜き** (leaving gaps so
continuation is implied), and patterned tone. It explains matching line height,
width and spacing rather than treating full/halfwidth forms as interchangeable;
changing the shift between rows changes the apparent line. Tone can clarify a
boundary whose outline is partly omitted. Brushes and copying are both available.
Its font/row-pitch examples are that author's profile, not universal metrics.

The [second tutorial](https://ccblassty.blog.fc2.com/blog-entry-6.html) shows
manual glyph placement over an image underlay, establishing important features
first, combining symbols at different heights for difficult angles, correcting
the overall shape, and deliberately standardizing repeated details instead of
reproducing every source-image variation. Its named editor, established by the
first tutorial, is **（´д｀）Edit**; this is not proof of an Orinrin session or
of the tools used for the supplied AAHub drawings.

Together these explain a documented route to recurring vocabulary: useful
constructions are chosen, adjusted and repeated. Similar local geometry and the
same font make similar solutions useful; that latter causal explanation is an
inference supported by the constraints and examples, not a corpus-wide author
survey. Presets are evidence that such vocabulary is reusable, not proof that
every occurrence was inserted from one preset.

### The supplied examples, not substitute rounded subjects

| Supplied source | How its local construction works |
|---|---|
| [Assisi, complete source](../assets/glyphs/contextual/operator-constructions/church-036.txt), rows 7–8; [crop 03](../assets/glyphs/contextual/operator-constructions/crop-03.png) | `γ⌒ヽ` supplies upper cap/shoulders, while the positioned next-row `乂__ノ` supplies the lower return. Their relationship encloses paper. Matching an isolated cap is not matching this entire opening. |
| [Church-basement source](../assets/glyphs/contextual/operator-constructions/church-073.txt), rows 8–16; [crop 06](../assets/glyphs/contextual/operator-constructions/crop-06.png) | Shallow multi-stroke bands change through `ｲ二㌃゜`, `ｲﾆア゜`, `/ﾆｱ` on one shoulder and `くﾆ心、`, `寸ム`, `寸ﾊ`, `∨i,`, `Ⅵｉ` on the other. Articulation and row position change together; the result is a turning thick band, interrupted by a foreground pillar—not one diagonal repeated around a circle. |
| [Karnak source](../assets/glyphs/contextual/operator-constructions/church-165.txt), row 9; [crop 02](../assets/glyphs/contextual/operator-constructions/crop-02.png) | `jI斗-─--ミ` combines a shallow run and fuller end constructions across the capital. Whole-glyph ink and the surrounding rows matter, not only the central horizontal strokes. |
| [Godless Shrine source](../assets/glyphs/contextual/operator-constructions/church-161.txt), rows 11–13; [crop 01](../assets/glyphs/contextual/operator-constructions/crop-01.png) | `ｧ宀v` caps the opening, `弋__人` makes the lower turn/meeting, and `∧` continues below. This is a distinct compound cap/return vocabulary, not another isolated `⌒` example. |
| [Church variants 105](../assets/glyphs/contextual/operator-constructions/church-105.txt), [106](../assets/glyphs/contextual/operator-constructions/church-106.txt), [107](../assets/glyphs/contextual/operator-constructions/church-107.txt), rows 6–7; [crop 04](../assets/glyphs/contextual/operator-constructions/crop-04.png) | `（(⌒Y⌒)）` forms paired lobes and a central meeting; the next-row `)Ｉi(` continues its stem/returns. Multiple curved glyphs build the compound shape and thickness. The identical local motif repeats twice in each of the three full-artwork variants; the crop cannot choose one variant or one occurrence. |
| [Entry 97 source](../assets/glyphs/contextual/operator-constructions/church-097.txt), rows 4–7; [crop 05](../assets/glyphs/contextual/operator-constructions/crop-05.png) | `(　)` above `/⌒Ｙ`, `乂__ﾉ`, `しく__` makes stacked rounded parts with supporting returns; the adjacent punctuation and framing strokes remain part of the context. |
| [Kraków St Mary's source](../assets/glyphs/contextual/operator-constructions/church-057.txt), rows 9–14; [crops 07](../assets/glyphs/contextual/operator-constructions/crop-07.png) and [08](../assets/glyphs/contextual/operator-constructions/crop-08.png) | The same cap `γ⌒ヽ` participates in different constructions: one has the intervening side row `{　　　}` and lower `乂__乂`; another has upper `(__)` and lower `乂__ソ`. Cap, optional side rows and selected return cooperate; a cap dictionary alone loses these relationships. |
| [Exact cup, steam, plate and reclining-character drawing](../assets/glyphs/contextual/aramaki-cup-plate-176.txt), rows 5–14 | Rim constructions `ヾ<:;_` and `_,.ン`, sparse dot/colon/semicolon fields, fuller `彡` side marks, and changing `彳`/`ジ` lower returns cooperate. Density, direction and the form turn are coupled. Calling this merely a dot-density ramp discards the operator's central observation. |

The repeated text in variants 105–107 is **direct evidence of reuse at the
artwork-text level**, not merely coincidentally equal isolated characters. It
does not establish whether each occurrence was pasted, inserted from a palette,
or typed again. Likewise, differing side/return combinations in the actual
source show why recurring vocabulary can admit variations rather than one
immutable whole-circle string.

### What the Windows tools contribute, specifically

- **Orinrin presets/brushes:** literal reusable insertions. The inspected
  `LineTemplate.cpp:904–943` parser supplies individual nonempty lines; source
  adjacency in the palette does not prove an atomic multi-row insertion macro.
  The saved cap fragments and mouth constructions demonstrate reusable shape
  vocabulary. `TraceCtrl.cpp:997–1030` positions/transforms the **image underlay**,
  not the glyphs. `DocAdjustant.cpp:172–195` adjusts spaces: under its 11/5-dot
  assumptions, exchanging one fullwidth space for two halfwidth spaces reduces
  a gap by one dot without deforming glyph ink.
- **AAJ automatic fitting:** the inspected handler rasterizes native candidate
  glyphs/short combinations, compares source and candidate ink, chooses a result,
  appends it, and advances by measured proportional text width. Similar source
  patches can therefore favor similar local candidates. Crucially, **the forty
  recovered composite candidates are not the complete output alphabet or a list
  of every longer sequence the program could emit**. Lack of an entire arch in
  that list does not show that successive selections could not assemble it.
  Its full character availability and exact reproduction of these drawings are
  not established by the forty-string comparison.
- **ASCII Justice:** recovered edge extraction finds local RGB contrast changes;
  its mask scorer compares stored candidate ink and its density gate contributes
  tonal selection. This is not semantic recognition of a rim or fold. Its mapped
  93 ASCII candidates exclude the supplied kana/kanji themselves, so this build
  cannot directly emit those exact passages. Recovering its mechanism is not
  attribution of AAHub's Japanese construction vocabulary to it.

One concrete check of the recovered Justice scorer separates **shape** from
average tone: its original `(` and `)` masks both contain 15 ink pixels. With
either original mask as source, the normal-quality raw scorer prefers that
mask over the opposite curve. The new regression checks both directions.
The four-case sample rewards are +18 dark/dark, +3 dark/paper, -18 paper/ink,
+6 paper/paper. Relative to a paper template, template ink therefore contributes
+15 at a dark source sample and -24 at a white one. Ink position can distinguish
equal-density candidates. This is a kernel/table check, **not** full conversion,
an AAHub reproduction, or proof that density gating would leave every ranking
unchanged. It does not supply the Japanese glyphs absent from that program.

**Conclusion:** recurrence is explained by reusable geometric/tonal drawing
vocabulary and repeatable placement practices; automated image matching is a
separate documented way to choose local ink approximations. Reconstructing a
specific artist's production chain requires more evidence, but that attribution
gap is not a reason to leave the visible construction method unexplained.
No renderer/skill change, whole-converter equivalence or visual approval is
claimed here.

### Recovery and search execution boundary

At the operator's explicit request, Luna agents were assigned parallel original-
source searches for the five unbound crops. Candidate-only results do not alter
the source registry. Static AAJ reacquisition was attempted through the original
Vector detail URL: it redirected to `maintenance_php_2026.html`; the raw response
and SHA-256 receipt are retained under ignored `.run/aaj_algorithm_recovery/` by
`scripts/aaj_source_recovery.py`. No Windows program was executed, and this
failed retrieval does not establish absence of an algorithm or of another copy.

### Parallel search result and admission

Initial Luna passes over the statue collection (367 native PNGs) and church
text patterns produced no trustworthy bindings; low-score statue leads were
not admitted. The deeper `luna_church_image_match` pass searched all 167 entries
of the known church archive with multiple source font/row-pitch/zoom hypotheses,
checked known crops as calibration controls, and rechecked leading candidates
at full resolution. Its analysis script is retained in ignored
`.run/operator-source-search-church/search.py`. Numeric correlation was used
only for discovery; it was not treated as pixel-exact font equivalence or
artwork acceptance.

The parent then directly read the complete relevant source passages and
inspected the supplied crops 01/04/05/07/08 through their image-guard previews.
Those arrangements corroborate `161:11–13`, `97:4–7`, `57:12–14`, and `57:9–14`.
Crop04's paired motif is present in rows6–7 of all105/106/107, with two identical
occurrences per row; that ambiguity is preserved, not resolved by choosing the
first result. All ten full church source texts/raw counterparts are packaged,
and the source registry/verbatim checks were regenerated.

The TUI now exposes **38 source-positioned fragments across all eight crops
plus the cup**. Repeated text positions are retained; displayed placement for
crop04 is explicitly representative, not a unique left/right identification.
The updated registry is authoritative over earlier historical five-unmatched
checkpoints in this log. No source crop, existing GIF, renderer or skill was
changed by this matching work; no new diagnostic image was published.

Final focused regression: **64 tests run, 62 passed, 2 skipped** across the
construction mapping, original-source registry, operator crops, contextual
evidence, recovered kernels, AAJ templates, Windows intake and retained-recording
tests. The skips concern unavailable optional original inputs; no converter
parity is inferred. Cache-free `--mode round --dump` exposes all eight records,
new source bindings, all three crop04 variant paths, and the new constructions.
`git diff --check` passed. No commit or push was requested/performed this turn.
