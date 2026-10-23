# Unicode Glyph Morphology Explorer

Unicode Glyph Morphology Explorer is a terminal browser for finding Unicode
characters by how they look.

It exists because codepoint names and script blocks are the wrong search tool
when you are building ASCII/Unicode visual effects. Sometimes you need “a thin
vertical stroke,” “a dense block,” “a diagonal ramp,” or “a family of related
shapes.” This repo renders glyphs through a pinned eight-font chain and compares
their silhouettes by density, orientation, topology, and related visual
features. The base morphology browser keeps the historical 16×16 raster, while
the combination/seam tools measure as-positioned terminal cells: 8×16 for
half-width glyphs and 16×16 for full-width glyphs.

Use it to browse candidate glyphs, inspect why they group together, and keep a
small reviewed registry of useful morphology families for ASCII-renderer work.

![Inspect a turning CJK stroke, ノ, 川 and ﾘ by their ink shapes](docs/glyph-morphology-explorer.gif)

Single-glyph inspection: turns, curves, parallel stems and hooks in the
browser's 16×16 font-chain profile—not a tour of symbol names.

## Run

```sh
python3 -m pip install -r requirements.txt
./run-browser.sh --block "CJK Strokes"
```

The interactive browser requires a UTF-8 terminal. List the known Unicode blocks without entering the browser:

```sh
./run-browser.sh --list-blocks
```

Controls are shown in the browser footer. `q` exits without changing tracked files.

## Browse discovered families

![Compare native Saitamaar stroke bundles, curved-return runs and multi-row tone bands](docs/glyph-families-viewer.gif)

Native-pattern comparisons: `彡 / ミ / ﾐ`, `川 / 巛 / ﾘ / ﾙ`, crossed forms,
curved-return combinations and multi-row tone columns. These are the packaged
Saitamaar 16 px rasters at native advances, not stretched terminal glyphs.
Replay this view with `./run-families.sh --mode patterns`.

![Animate an Ogham ink ramp, sharp and rounded corners, and angled and curved hooks](docs/glyph-ramps-and-curves.gif)

Ramps and curves: `ᚆ ᚇ ᚈ ᚉ` adds strokes along one stem, `└ / ╰` compares
a sharp and rounded corner, and `レ / し` compares angled and curved returns.
The CLI animator displays complete raw 16×16 font-chain rasters; these selected
comparisons do not stretch glyphs or interpolate between them.

The reproducible recording recipes are
[single-glyph inspection](docs/recordings/glyph-morphology-explorer.tape),
[native-pattern comparisons](docs/recordings/glyph-families-viewer.tape), and
[ramps and curves](docs/recordings/glyph-ramps-and-curves.tape).

The family viewer shows reviewed glyph sequences as animated shape families.
You can switch morphology axes, filter by family length, change speed, pause on
a specific sequence, review distraction ranking, inspect authored multi-cell
seeds beside their mirrors, and browse measured useful-combination candidates
from mined usage, seam pairs, and geometry-discovered Unicode runs.

```sh
./run-families.sh
```

The first run builds local ignored caches under `.run/`: the morphology feature
cache, the discovered-family catalog, the cell-feature cache for the standalone
font-chain repertoire, mined Stone Story tutorial-plate usage, seam-pair
indexes, geometry-discovered run indexes up to length 4, and the measured
combination gallery.
After that, the same command opens the read-only viewer directly. Use `j`/`k`
to select, `m` to change the morphology axis, `1`–`9` to filter by family
length, and `q` to exit.

The direct Python entrypoint uses the same loaded family set. With no arguments
it opens on the `COMBOS` axis first, while `--mode all` starts on the mixed
all-family list:

```sh
python3 scripts/glyph_families_viewer.py
python3 scripts/glyph_families_viewer.py --mode all
```

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

That `combo` mode is the full useful-combination browser. For just the nine
authored seed rows:

```sh
python3 scripts/glyph_families_viewer.py --mode authored --dump
```

For broader review, `scripts/glyph_combo_candidates.py` enumerates every
connected two- and three-cell arrangement over the full Stone Story plate
line-art alphabet: 25 basic marks plus 4 extended marks. It reports 148,016
candidates before any manual art selection:

```sh
python3 scripts/glyph_combo_candidates.py --limit 20
```

`scripts/glyph_combo_mine.py` counts recurring combinations in the packaged
Stone Story tutorial plates. `scripts/glyph_seam_index.py` finds measured
adjacent-cell pairs across the standalone font-chain repertoire.
`scripts/glyph_run_walker.py` then walks those seam relations into
variable-length beside and stacked runs. The one-command defaults build length-4
Unicode/Kana/CJK/Arabic review buckets, so examples such as `_.-´`,
`` `-._ ``, `\|/`, `(‾)`, `/‾\`, `\_/`, `|` over `|`, CJK stroke chains, and
Arabic joining-form runs can be reviewed as run families rather than fixed two-
or three-cell tuples.

The standalone viewer treats those combinations as visual exploration data, not
runtime proof counters. In particular, Asciicker runtime `combo_hits` values are
candidate-transition diagnostics; they are not selected or rendered combination
usage counts.

The measurement profile matters. These standalone combo and seam artifacts are
8×16 half-width / 16×16 full-width exploration data from the pinned font chain.
Current Asciicker Godot native-terminal work uses a tall 16×32 half-width cell;
full-width glyphs retain intact 32×32 masks across two adjacent tall cells.
Before a family, seam threshold, D_SM radius, altitude rule, or run offset is
used by that renderer, it must be rebased in cell units for the Godot profile.
Orthographic and perspective rendering also remain separate proof conditions,
so this repo can identify candidate families but cannot certify either
projection's runtime election.

The one-command family viewer builds and opens the measured combination surface
too. To jump straight to it:

```sh
./run-families.sh --mode combo
```

A committed snapshot of the generated HTML review sheet is available at
[docs/artifacts/glyph_combo_gallery.html](docs/artifacts/glyph_combo_gallery.html).
Regenerate the working copy with `python3 scripts/glyph_combo_gallery.py`.

### Shift_JIS AA combinations from the AAHub corpus

`./run-families.sh --mode sjis` opens combinations counted over the AAHub
training slugs (23,363 pages) and drawn in Saitamaar 16 px at their true pixel
offsets, each beside its mirror. The categories are:

- the stroke idioms from ascii-art-authoring section 15.5;
- touching stroke pairs and triples;
- vertical stacks whose centres lie within 3 px;
- tone bands.

`--mode combo` includes them too. The data file is tracked, so no build step
runs. Regenerating it needs the private archive and the font:

```sh
python3 scripts/sjis_corpus_combos.py ARCHIVE SPLIT.json Saitamaar-Regular.ttf \
    --out assets/glyphs/corpus/aahub_aa003_train.sjis_combos.v1.json
```

### Browse combinations in source context

The standalone viewer also has a curated source-context axis. It keeps exact
multi-row source passages, paired-artifact provenance, annotation scope, and
interpretation limits beside the combination vocabulary:

```sh
python3 scripts/glyph_families_viewer.py --mode context --dump
./run-families.sh --mode context
```

`--mode combo` includes these context records alongside authored seeds,
measured candidates, and the selected AAHub corpus. Use `[` / `]` in the
interactive viewer to scroll a selected context record; `--dump` prints all
source rows and provenance without opening a TTY.

The terminal pane is **textual context, not a native Saitamaar rendering**:
terminal column widths do not preserve its proportional advances. Use the
record's paired native PNG together with these exact rows before judging glyph
fit, joins or negative shapes. Text-only candidates remain text-only.

The tracked records are source evidence, not universal glyph meanings or
runtime proof. T#7 keeps its three separately boxed operator regions (branch
marks, falling marks, and root/patchy-ground marks) distinct. S#424 (the statue
page, not church C) preserves
the whole-piece `yes` verdict while stating that there are no region rectangles;
its local punctuation reading is not a region-level approval. C#126 and C#99
retain source rows and reconstruction/observation status. C#135 is explicitly
text-only because no paired native PNG was located; the repeated `人_` record
is also raw-text-only and its subject meaning remains unassigned.

Hand evidence preserves open spaces and ordered turntable frame records. Its
interior fold/joint comparison is a drawn analogy only, not a proven
mathematical suggestive-contour or ridge family. The frame review is a static
ordered construction-study frame inspection, not playback of the original AAHub
drawing or current MAIN. Contextual `focus length` counts codepoints in a quoted
form, not its pixel width or the full multi-row construction's extent. The historical old-typist
20-glyph / 38-degree limitation is not presented as current MAIN behavior.
Likewise, AA-003 and AA-004 counts for `/⌒ヽ` are kept separate from the
bounded source example and are not semantic labels.

### Native stroke-bundle and combination comparisons

The supplied Saitamaar comparisons are now a dedicated **NATIVE PATTERNS** axis
and are included in `COMBOS`. Open it directly without rebuilding the full
morphology cache:

```sh
python3 scripts/glyph_families_viewer.py --mode patterns
python3 scripts/glyph_families_viewer.py --mode patterns --dump
./run-families.sh --mode patterns
```

Twelve groups compare parallel/dotted/crossed bundles, narrow and fullwidth
stems, horizontal bands, slope variants, and the quoted tone-band/curved-return
combinations. Use `j`/`k` to select and `[`/`]` to scroll through complete
thresholded Saitamaar rasters, advances, ink coverage, bounding boxes and
component axes. Rasters retain native advances at 16 px with 17 px row pitch;
they are not redrawn with the terminal's font or normalized to square cells.
Widen the terminal when a raster is marked clipped.

The original temporary `bundles.py` and `glyphcheck2.py` were inspected; the
47 supplied bundle-table rows reproduce, including duplicate observations.
**Their "strokes" are 8-connected ink components, not pen strokes.** A component's
PCA axis can conceal a crossing or hook; match the full glyph construction, not
the component count or angle alone. Multi-row tone/curve layouts are comparison
proposals, not approved source passages, renderer fixes or lighting rules.

The input, raw reported stdout, script/font hashes and limits are retained in
`assets/glyphs/contextual/saitamaar_pattern_intake.v1.json`. Its generated,
self-contained raster/measurement snapshot is
`assets/glyphs/contextual/saitamaar_pattern_evidence.v1.json`. Viewing needs no
private font or temporary scripts. Explicit regeneration needs the hash-pinned font:

```sh
python3 scripts/saitamaar_pattern_intake.py --font /path/to/Saitamaar.ttf --write
```

## Included data

The repository includes the morphology browser, the read-only family viewer, the
selected saved-family registry, glyph-combination and contextual-source review
data, the candidate enumerator, a committed combination-gallery snapshot, and
the pinned font chain used for rendering. It does not include the full Asciicker
engine or runtime.

Font identities, copyright metadata, license mapping, and license texts are recorded in [docs/font-provenance.md](docs/font-provenance.md) and `docs/licenses/`. Source-code identities are recorded in [docs/code-provenance.md](docs/code-provenance.md).
