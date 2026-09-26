# ascii-art-authoring skill vs. proportional Shift_JIS art (audit, 2026-09-26)

This directory records an audit of the `ascii-art-authoring` agent skill
against the sparse, outline-first Shift_JIS art style. The style exemplar is
the AAHub page 爆発・煙 (explosion and smoke),
<https://aahub.org/mlt/a60392576bd5eefca3ed22d55606b85f>. The page has 180 art
posts (res1–res112 explosions, res114–res181 smoke; res0 and res113 are
section labels). The audit read a private archive snapshot of that page,
rendered as AAHub renders it: Saitamaar at 16 px, which reproduces
MS PGothic advance widths.

This is an audit only. No skill file was edited.

| file | role |
|---|---|
| `README.md` | this audit |
| `aa_slug_stats.py` | measurement script. Takes the post directory, the font, and the source URL as arguments. It never overwrites an existing output with different bytes. |
| `bakuhatsu_kemuri_stats.json` | measured output: glyph frequencies, class shares, space mixing, ink density, fixed-grid tests, idiom probe, and per-post rows keyed by AAHub res id. Posts are identified by SHA-256. No art text is stored. |

All numbers below come from `bakuhatsu_kemuri_stats.json`. Its input set
SHA-256 is `681615b0954a6bce59c6699249702d41b8c6ab3c934158a78d22dd0e25e8ced1`.

## 0. Which skill copy is canonical

There are two copies of the skill:

- **Global copy**, tracked in the `claude-skills-private` repository. It has 998 lines. Its last commit is
  `c8c39d5` (2026-09-21), and the working tree is clean. It adds
  `references/drj-3d-stereogram-guide-1994.md`, section 14 (DRJ3D
  stereograms), and the routing hook to
  `fl4512-rendering-npr-rendering-techniques` (lines 541–544).
- **Project copy** in `asciicker-Y9-2` at `.claude/skills/ascii-art-authoring/SKILL.md`. It has 548
  lines and was last committed in `c5b194825` (2026-09-08).

**Verdict: the global copy is canonical.** The project copy is a stale fork.
The evidence:

1. The first global commit `d1b1f50` (2026-09-08 02:11) imported the project
   copy. Apart from the added routing hook (four lines), the diff is empty.
2. Every later change landed only in the global copy (`6274c77`, `c8c39d5`).
3. The Y9-2 failure log records the DRJ3D precedence decision against those
   global commits: `asciicker-Y9-2` `docs/FAILURE_LOG.md:246411` at `9d145579e`.

The project copy is missing section 14, the `DRJ3D` citation row, and hook 4.
Every finding in sections 1–13 applies to both copies. Line numbers cited as
`SKILL.md:N` refer to the global copy. Because the project copy lacks the
line-19 citation row, its line numbers are one lower after line 18.

## 1. How the 爆発・煙 pieces build form (Q1)

The following posts were read in full, with their whitespace made visible:
res1, res4, res5, res9, res13, res21, res23, res50, res67, res72, res73,
res75, res91, res106, res114, res132, res153, res168, and res177.
The renders of res73 and res168 were also inspected visually.

### 1.1 Inventory and frequencies (whole page)

- The page has 228,771 glyphs, of which 129,919 are not spaces. There are 492 distinct glyphs,
  including 125 kanji and 148 kana.
- The spaces are 72,048 full-width U+3000 (11 px) and 26,804 half-width
  U+0020 (5 px).
- The 25 most frequent non-space glyphs, with their advance in px:
  `:` 36,446 (3) · `.` 18,336 (3) · `;` 9,666 (3) · `'` 6,395 (3) ·
  `,` 6,377 (3) · `|` 5,757 (4) · `i` 4,497 (3) · `l` 2,513 (3) ·
  `_` 2,330 (5) · `/` 2,085 (8) · `-` 1,989 (8) · `"` 1,737 (8) ·
  `／` 1,459 (16) · `ﾞ` 1,288 · `￣` 1,221 (16) · `＿` 1,191 (16) ·
  `､` 1,165 (7) · `⌒` 1,101 (16) · `ヽ` 1,027 (12) · `＼` 1,009 (16) ·
  `!` 963 · `｀` 862 · `´` 808 · `=` 705 · `ｌ` 641.
- The most frequent kanji are used as shapes, not as words: `三` 501, `二` 396, `州` 264 (all in one
  post), `从` 209 (43 posts), `人` 125, `彡` 114 (32 posts), `丶` 93, and `乂` 40.
  `从` and `彡` carry debris and smoke wisps, as at the base of res1 and in res5.
- Kana are used as curved strokes: `ヽ` 1,027, `ノ` 455, `ヾ` 384, `ﾉ` 318, `ゝ` 211,
  `ﾍ` 91, and `く` 80. Kana are also used as sound-effect lettering, for example in res50.

### 1.2 Outline versus texture

This split uses heuristic classes; the class sets are in the script.

- Fine texture (`. , ; : ' `` ` `` ､ " ﾞ` and similar dots) is **64.5 %** of
  non-space glyphs. Stroke classes (full-width `＿￣／＼｜⌒―`, ASCII
  `_/\|-()!il`, and kana) total **27.7 %**. Kanji are 1.6 %.
- The 27.7 % is an upper bound for outline. `i`, `l` and `|` are dual-use:
  in res9, runs of `iiii` are vertical hatching, not contour.
- The page is **bimodal, not uniformly sparse**. 30 posts have an outline
  share of at least 0.6. The pure-outline puffs and rings are res4, res23,
  res72–res75, res91, res132, and res153. 32 posts have a texture share of at
  least 0.8. The pure dot-tone flashes are res12, res13, res67, and res177.
  The large smoke masses combine both: an outline of `ヽ ） ﾉ ／ { ＜`
  encloses a `::::` screen-tone field, as in res168.
- Even so, **ink is sparse** because the tone glyphs are 3 px dots. The median
  ink density is 2.4 % of the bounding box (p10 1.3 %, p90 4.4 %, maximum
  8.1 % in res9).

Tone is built as a 1D density ramp at the edges of a mass: `...` → `.:.` →
`:::`. The most frequent touching bigrams are `::` (18,103), `:.`, `.:`, `..`,
`;;`, `;:`, and `:;`.

### 1.3 Stroke idioms

The script counts touching glyphs, so these idioms are exact substrings.

| idiom | count | posts | example posts | reads as |
|---|---|---|---|---|
| `⌒ヽ` | 128 | 39 | res5, res21, res22 | the upper-right lobe of a cumulus puff |
| `(⌒` / `（⌒` | 87 / 14 | 28 / 9 | res17, res27, res57 | the left lobe of a puff |
| `⌒)` / `⌒）` | 47 / 27 | 21 / 18 | res49, res83 | the closing lobe |
| `_ノ` / `＿ノ` | 39 / 19 | 24 / 12 | res11, res19 | the lower-right hook |
| `ヽ_` / `ヽ＿` | 24 / 5 | 18 / 5 | res15, res21 | the lower-left hook |
| `｀ヽ` | 152 | 32 | res11, res21 | a soft shoulder |
| `､_` | 48 | 31 | res24, res25 | a sub-cell step into a horizontal |
| `＼＿` / `＿／` | 37 / 26 | 20 / 16 | res1, res10, res23 | a V floor / a bowl |
| `／￣` / `￣＼` | 25 / 29 | 14 / 15 | res16, res19 | an arch shoulder |
| `-‐` / `‐-` | 99 / 35 | 46 / 21 | res1, res4, res72 | a flattened top or bottom arc (`-―-`, `‐--‐`) |
| `'´` | 92 | 40 | res19, res20 | a shallow rising tip |
| `,,` / `_,` | 1,368 / 393 | 103 / 78 | res1, res2 | flicker and debris at a base |

The classic small smoke puff (res153, lines 1–3; `□` is U+3000 and `·` is
U+0020; source: the AAHub URL above):

```
□□□□□□□□□□·□/⌒)
□□□□□□□□□□·（□□□）
□·□·□□□□□□□□ゝ__ノ
```

The outline-only bomb ring (res72, lines 1–3, same source and notation):

```
□□□□□□□·-―-
□□□□／□□□□□,·⌒ヽ.
□□□/□□□□□□·ヽ.□_,ハ
```

### 1.4 Stroke continuity and proportional spacing

- **Mixed spaces are the positioning mechanism.**
  - 6,459 whitespace runs of length 2 or more mix U+3000 and U+0020.
    2,223 of them alternate (`□·□·□·`).
  - There are **0** half-only runs, **0** adjacent half-space pairs, and
    **0** lines starting with a half space, in 3,214 lines. This is the
    BBS/HTML whitespace-collapse rule. A run of spaces must be written as
    full-width spaces with single half spaces interleaved.
  - With 11 px and 5 px units, most pixel offsets are reachable.
    2,067 of 2,419 indented lines (85 %) start at an x offset that is not a
    multiple of 8 px.
- **Continuity is vertical, and the unit is the pixel.** 133,576 glyph pairs
  on adjacent rows have centres within 3 px of each other. The top vertical
  pairs are `:/:`, `./.`, `|/|`, and `i/i`. Contours are placed at the pixel
  by choosing between glyphs of 3, 4, 5, 8, 11, 12, and 16 px, for example
  `|` (4) against `｜` (16), and `/` (8) against `／` (16).
  In res72 and res73, `/`, `／` and `|` step a circle outline on 5 px and
  11 px increments.
- **Negative space carries the form.** Each puff is only its lobe strokes.
  The inside stays empty (res132, res153), unless the author wants tone
  (res168).

## 2. What the skill teaches, against this style (Q2)

The skill scopes this style out explicitly: *"Do not apply it to
proportional-font text art"* (`SKILL.md:23-24`). DRJ3D likewise demands a
non-proportional font (`SKILL.md:578`, falsifier `SKILL.md:965`). The skill
is therefore not *wrong* about Shift_JIS art. The problem is that it is
silent: an agent asked for "outlined AA like 爆発・煙" has no route, and
applying the skill anyway misfires on the points below.

### 2.1 Where it is right and transfers

- Negative space breaks seams, and empty cells are a tool
  (`SKILL.md:51-55`, `:95`). This matches the empty puff interiors.
- Dithering by alternating two glyphs and lightening by erasing members
  (`SKILL.md:281-283`). This matches `:.:.` / `;:;:` bands and the thinned
  `..·..` rims (res13).
- Rim dots carry curvature (`SKILL.md:284-285`). This matches the `.:.` edges
  of smoke masses (res168).
- Declare a material language and reuse it (`SKILL.md:176-181`). The page
  uses `⌒ヽ`-lobe for smoke, `::::` for smoke body, `从/彡` for debris, and
  `iiii` for a lit wall (res9) consistently.
- The target is a readable abstraction, not a likeness (`SKILL.md:102`).
- Treat alphanumerics as gaze anchors (`SKILL.md:144-148`). This holds for
  Latin letters read as words, but see 2.3.

### 2.2 Fixed-grid assumptions that break on proportional art

| skill text | why it breaks here |
|---|---|
| "confirms the font is monospaced" (`SKILL.md:35`); cell aspect 1:1 / 1:2 / 16:29 (`SKILL.md:38-39`) | There is no cell. Only 14.7 % of non-space glyphs have a Saitamaar advance equal to an 8 px or 16 px cell. No post reaches 90 %; the maximum is res49 at 72.5 %. |
| Cell anisotropy table and "60°–90° impoverished because glyphs are horizontally centred" (`SKILL.md:225-239`) | Horizontal placement resolution is about 1 px, by mixing 5 px and 11 px spaces. Steep lines are cheap: `\|` (4 px) and `/` (8 px) can sit at any offset (res23, res91). |
| Anti-aliasing means inserting empty *cells* (`SKILL.md:185`, `:188`) | Here, anti-aliasing and sub-placement are done with sub-cell *space widths* and glyph-width choice (`\|` against `｜`, `ｰ` 10 px against `―` 16 px). The skill has no concept of space width. |
| "Mirror art by typing the row in reverse" (`SKILL.md:206-207`) | Reversing a row changes pixel offsets unless the spaces are re-balanced. `ヽ` (12 px) and `ノ` (11 px) are not width-symmetric. |
| Box-drawing junctions to connect parts (`SKILL.md:98`) | Proportional box-drawing only aligns in its own runs (res50 buildings). It is not a general joint. |

### 2.3 Glyph vocabulary: the combination patterns do not cover the idioms

- The 29-mark alphabet plus the 12-letter whitelist (`SKILL.md:110-114`)
  covers 74.6 % of non-space glyphs, but almost all of that coverage is
  3 px tone punctuation (`: . ; ' ,`). None of the stroke carriers that make
  the outlines are admitted: `＿ ￣ ／ ＼ ⌒ ヽ ノ ﾉ （ ） ｰ ― ､`.
- "Never use a letter outside the whitelist" (`SKILL.md:152-153`, falsifier
  `:452`) flags 143 of 180 posts. `i` (4,497), `l` (2,513), `r`, `j`, and `Y`
  are used as stroke and hatch shapes, not read as letters. The gaze-anchor
  rationale (`:144`) does not apply to a 3 px `i` inside a hatch.
- The combination table (`SKILL.md:155-164`) has six Stone Story rows. The
  data file it points to (`SKILL.md:545-547`) has nine rows:
  `_.-´`, `` `-._ ``, `.-´`, `` `-. ``, `\|/`, `|||`, `(o)`, `_ / ‾`, and
  `.':¡!·`. **None** of the section 1.3 idioms appear there.
  The stair step `_.-´` does occur in spirit as `_,` / `､_` / `'´`, but
  with different glyphs and sub-cell spacing.
- This repository's `assets/glyphs/authored/glyph_combinations.v1.json`
  (SHA-256 `7f559dbf…`) is a derived copy: it is byte-identical to Y9-2
  `6372a431f`. Y9-2 HEAD differs only in the `owner` field (`33ce9b3fc`,
  where the data became atlas-compiler input). The nine combinations are the
  same, the measurement font is Unifont, and the cell is fixed (`cell_px: 16`).
  Neither copy can represent a proportional idiom, because the schema stores
  integer `col`/`row` cell offsets, not pixel x.

### 2.4 Sparse versus dense guidance

- The skill carries value with ink density (`SKILL.md:264`) and warns
  against a "1D density ramp" as the way to *learn* (`SKILL.md:171`). This
  page uses exactly such ramps (`...`→`.:.`→`:::`) as its tone language, and
  also keeps median ink at 2.4 %.
- The style taxonomy (`SKILL.md:245-252`) has Block, Filled, Line, and Box. It
  has no row for **line plus screen-tone**: an outline enclosing a
  sub-cell-dot tone field, as in res168. That is the dominant large-piece
  mode on this page. "Filled" (dense letterforms, the only depth cue is the
  hole) is a different thing.
- There is no sparsity budget or ink-density falsifier. Nothing tells an
  agent that a pure-outline puff (res153: 3 rows, about 12 glyphs) is a
  complete piece.

### 2.5 Outline-first versus fill

- The still-piece loop (`SKILL.md:48-56`) blocks rough shapes, substitutes
  glyphs, erases, then applies anti-aliasing. It never says **outline first,
  then decide whether tone is needed**.
- On this page, tone always has a defined edge. In mixed posts the edge is a
  stroke contour (res168). In pure-tone posts it is a density edge that the
  tone ramp itself draws: res13's ring is a dense-to-sparse `:;:` → `..·..`
  band, and res177 uses a `::::` core in a `:·:` field. Tone never fades
  without a shape.
- Tone inside an outline is allowed only when it is a distinct material
  (smoke body, a lit wall). This is the material rule of `SKILL.md:176-181`,
  but the skill never connects that rule to fill decisions.

## 3. Do Xu / FL-4512 / unicasso target this style? (Q3)

**Verdict: they match on intent and diverge on medium. The page is a valid
*style* reference, and a valid *raster-level evaluation* set for its
outline-dominant subset under the conditions below. It is not valid as a
text-level or per-cell ground truth.**

Where they match:

- The three projects share the same intent: a structure-first line field with preserved empty space.
  - The Y9-2 FL-4512 structural goal is "sparse skeleton and
    visibility-indicating contour glyph strokes with tonal and filled-field
    glyphs absent" (`asciicker-Y9-2` `docs/FAILURE_LOG.md:183879` at
    `9d145579e`).
  - unicasso is characterised in `asciicker-Y9-2` `docs/FAILURE_LOG.md:183934`
    as "sparse structure-based line fields with coherent cross-cell routing
    and preserved empty space".
  - The Xu pipeline converts vector line art into structure-preserving ASCII.
- These traits match the outline-dominant posts: res4, res23, res72–res75,
  res91, res132, and res153.

Where they diverge, with measurements:

1. **Grid.**
   - Xu's reproduction uses Courier New or Menlo and printable ASCII only
     (`Xu-structured-ascii-art-algorithm-reproduction-experiments`
     `xu/ascii_port.py:27`, `:570`).
   - unicasso solves the font size so that advance equals cell width, and
     rejects glyphs whose advance is not exact (`asciicker-Y9-2`
     `docs/FAILURE_LOG.md:182646`, `docs/research/ascii/articles/FL4512_REPOSITORIES.md:171`).
   - Y9-2 renders on fixed 8×16, 16×32, or 32×32 cells.
   - On this page, only 14.7 % of non-space glyph instances have a
     grid-exact advance, and no post reaches 90 %.
2. **Placement survives neither re-flow nor snapping.**
   - Re-flowing each line on an 8/16 px grid moves glyph centres by a median
     of 202 px (p90 538 px). Only 12.5 % (16,764 of 133,576) of vertically
     aligned pairs stay aligned.
   - Keeping the proportional x and snapping it to 8 px columns preserves
     80 % of the vertical pairs. However, it puts 59 % of glyphs (77,014)
     into a column shared with another glyph, which a one-glyph-per-cell
     grid cannot hold.
3. **Tone.**
   - 66 % of non-space glyphs are tone or texture. The FL-4512 structural
     goal explicitly excludes tonal glyphs.
   - Xu 2010 is line-only.
   - The smoke half of the page (median outline share 0.29) is mostly
     outside their target.
4. **Metric.**
   - Xu's metric is AISS: alignment-insensitive, log-polar shape histograms
     scored per grid cell (see the Xu repository's
     `docs/research/ascii/verification/fl4512/xu-attempt-history/ALIGNMENT_LOG.md`).
     It is not SSIM, and it presupposes a cell lattice.
   - The official-monk gates (exact-cell rate, occupancy, target-glyph rate;
     `xu/reproduction_contracts.json`) are text-cell metrics. They have no
     meaning against proportional art.
5. **Font lineage is a partial bridge only.**
   - The Xu authors' presentation lists MS PGothic beside Courier New and
     MS Mincho (`xu/reproduction_contracts.json:36`). The Xu repository's
     `docs/research/ascii/verification/fl4512/xu-attempt-history/DEFORMATION_FIX_LOG.md:966-972`
     concludes that the paper's ASCII font
     is Courier New.
   - The two known proportional-placement methods are Xu 2017 (dynamic
     programming over flexible stripe boundaries) and Chung 2022 (greedy
     proportional-font placement). The Xu repository names them as
     different synthesis algorithms (`DEFORMATION_FIX_LOG.md:1218-1230`).

Conditions under which the page is a valid reference or evaluation set:

- **Render the target exactly as published.** Use Saitamaar, or MS PGothic
  if it is licensed, at 16 px with a 17 px line step. Use the exact
  whitespace, and apply no whitespace normalisation. Never re-render the
  art text in a monospace font: that destroys it, as shown in point 2 above.
- **Compare in pixel space, not text space.** Render the candidate (Xu,
  unicasso, or FL-4512 output) in its own monospace font, scale it to the same
  physical size, and score the two rasters. Suitable metrics are
  edge-chamfer or skeleton distance, AISS over a sliding window, or SSIM on
  blurred edges. Exact-cell, occupancy, or glyph-match rates are invalid.
- **Split the set.** Use the outline-dominant subset (outline share ≥ 0.6;
  30 posts, listed in the JSON `per_piece` rows) for structure-only methods.
  Keep the tone-dominant posts (texture share ≥ 0.8; 32 posts) as a
  separate evaluation for any method that claims tone.
- **Restricting to a fixed-width glyph subset is not a valid condition.**
  No post is at least 90 % grid-exact. Dropping the non-grid glyphs removes
  the outlines themselves.
- **Treat the posts as style targets, not as reproduction targets.** Human
  art is not an optimum of any of these objectives. Use it as qualitative
  acceptance evidence for "reads like 爆発・煙", and as a source of idioms
  (section 1.3) to seed a combination dictionary. The dictionary must store
  pixel x when targeting proportional output, or a cell-unit rebase when
  targeting a fixed grid.

## 4. Recommended skill changes (Q4), prioritised, not applied

Target the canonical global copy (`claude-skills-private`), then either
retire the Y9-2 project copy or re-sync it. The first change is most
important.

**P1. Replace the blanket exclusion with a scoped route (`SKILL.md:23-24`).**
Proposed text:

> Apply sections 1–13 to monospaced text art. For proportional-font art
> (Shift_JIS/2ch AA rendered in MS PGothic or Saitamaar), apply section 15
> instead. Sections 2 (still-piece loop), 3 (depth checklist), 4.5
> (material contract), and 8 (dithering) transfer. Sections 1.4–1.6, 4.1,
> 4.3, 4.6, and the cell-anisotropy table do not.

**P2. Add section 15, "Proportional Shift_JIS art (outline-first)".** It
should contain:

1. **Metric model.** Width is measured in pixels, not cells. At 16 px:
   half space 5, full space 11, `.,:;'il` 3, `|` 4, `_` 5, `/ - ﾉ` 8,
   `ヽ ゝ` 12, `＿ ￣ ／ ＼ ⌒ ―` 16. Place strokes by pixel offset, choosing
   both glyph width and space mix.
2. **Whitespace law.** Never write two adjacent U+0020, and never start a
   line with U+0020. Build offsets from U+3000 with single interleaved
   U+0020 (`□·□·`). The page has zero violations in 3,214 lines.
3. **Outline first.** Draw the contour with stroke idioms, leave the inside
   empty, and decide on tone only after the outline reads.
4. **Idiom table.** Give each idiom a role and example posts:
   - `(⌒ ⌒ヽ ⌒) _ノ ヽ_ ゝ__ノ` for puffs;
   - `／￣ ￣＼ ＿／ ＼＿` for arches and bowls;
   - `-―-` and `‐--‐` for flat arcs;
   - `､_`, `_,`, and `'´` for sub-cell steps;
   - `从` and `彡` for debris and wisps;
   - `,,` for base flicker.
5. **Tone rule.** Tone is a bounded material fill: a `.`→`.:.`→`:::` ramp at
   the rim, with `iiii` or `|||` for vertical hatching. Every tone mass has a
   defined edge: a stroke contour (res168), or, in a pure-tone piece, a
   deliberate density edge (res13, res177).
6. **Letters.** Latin letters used as 3–4 px strokes (`i l j r Y V`) are
   shape glyphs, not gaze anchors. The whitelist falsifier applies only to
   letters that read as letters.
7. **Mirroring.** Mirror with a width-aware swap table, such as `ヽ`↔`ノ`,
   `(`↔`)`, `／`↔`＼`, and `｀`↔`´`. Re-balance the spaces afterwards.
8. **Falsifiers.**
   - A double half space, or a leading half space, appears.
   - A tone mass has no defined edge, neither a contour nor a density edge.
   - A monospace font was used to preview or judge proportional art.
   - A puff interior is filled where the reference leaves it empty.
   - Mixed full-width and half-width strokes misalign by more than 3 px
     between rows where continuity was intended.

**P3. Scope the fixed-grid statements.** Prefix `SKILL.md:35`, `:38-39`,
`:185-188`, `:206-207`, and `:225-239` with "On a monospace grid". State
that on proportional art, horizontal resolution is set by space widths.

**P4. Add a style-taxonomy row (`SKILL.md:245-252`).** Proposed row:
"Line + screen-tone | contour strokes enclosing a fine-dot or hatch tone
field; ink stays sparse (median about 2.4 % on 爆発・煙) | smoke, explosions,
lit surfaces". Also add a sparsity note: a complete piece may be only its
contour (res153).

**P5. Extend the combination data and its hook (`SKILL.md:545-547`).** Add
a v2 schema that allows `x_px` alongside `col`, or a separate
`proportional_idioms` file, seeded from section 1.3 with source posts cited.
State that the v1 file is Stone Story monospace-only, and that its
`glyph_combinations.v1.json` copies are not a Shift_JIS vocabulary.

**P6. Add evaluation guidance cross-linked to FL-4512.** Proportional art is
evaluated as rasters rendered in its original font. Use the conditions in
section 3. Never judge proportional art by exact-cell text match.

**P7. Resolve the two copies.** Mark the Y9-2 project copy as a pointer to
the canonical copy, or re-sync it. As things stand it lacks section 14 and
hook 4, and a Y9-2 session silently loads the older text.

## 5. Reproduce

```sh
python3 docs/research/ascii/sjis_aa_skill_audit/aa_slug_stats.py \
  <post-dir> <Saitamaar.ttf> --out <new-output>.json \
  --source-url https://aahub.org/mlt/a60392576bd5eefca3ed22d55606b85f
```

The script needs `fontTools`, which is already in `requirements.txt`, and
`Pillow` for the optional ink density. The post texts are not
redistributed; compare them by the per-post SHA-256 values in the JSON.

## 6. Limits

- The class shares depend on hand-chosen glyph sets. In particular,
  `i`/`l`/`|` are counted as strokes although some are hatching.
- The vertical-continuity test is a 3 px centre proximity proxy, not a
  contour trace.
- Ink density uses the widest-line bounding box, so ragged posts read lower.
- One page (one topic: explosions and smoke) is not the whole of Shift_JIS
  art. Character art and faces use different idioms.
