# Line-art minimalism in AAHub Shift_JIS art: AA-004 TRAIN measurement (2026-09-30)

This directory tests one claim. The minimalist line-art style that the
`ascii-art-authoring` skill describes in section 15 is outline first, with
empty interiors and sparse ink, uses tone only as a declared material, and is
built from stroke idioms. The claim says that many, if not most, AAHub
Shift_JIS pieces are in this style. The claim was first shown on the
爆発・煙 page (`[AAHUB-BK]`, `[SJIS-AUDIT]` in
`../sjis_aa_skill_audit/`).

The measurements cover the AA-004 crawl and use the TRAIN partition only.
No skill file was edited. The proposed skill text is in
`proposed_skill_delta.md`.

Labels used below:

- **measured**: a number that a script in this directory computed.
- **inferred**: a reading or a judgement that the scripts do not compute.

## 1. Headline answer

| reading of the claim | TRAIN share | label |
|---|---|---|
| Sparse ink (ink ≤ 5 % of the bounding box) | **94.1 %** of 806,288 pieces (median 2.89 %) | measured, whole TRAIN |
| Uses at least one skill-15.5 contour idiom | **90.1 %** | measured, whole TRAIN |
| Strict line minimal: empty interiors, tone share < 0.25, ink ≤ 5 % | **30.6 %** (95 % CI 29.7–31.5) | measured, weighted sample |
| Outline first, with tone only as a bounded material (line minimal + line-plus-tone) | **56.9 %** (CI 56.0–57.8) | measured, weighted sample |
| SJIS-AUDIT "outline-dominant" (outline share ≥ 0.6) | **20.3 %** (CI 19.6–21.0) | measured, weighted sample |

**Verdict (inferred from the measured rows above).**

- **"Many" holds.** Each reading of the claim is met by at least about a
  fifth of TRAIN.
- **"Most" holds only under the broad reading.** Under that reading, the
  outline comes first and a bounded tone material is allowed. Under the
  strict reading (empty interiors, little tone), about 31 % of pieces
  qualify, so "most" does not hold.
- **爆発・煙 is a typical page, not an outlier.** On its own 179 pieces:
  - line minimal: 34.6 % (TRAIN: 30.6 %);
  - ink median: 2.35 % (TRAIN: 2.89 %);
  - outline-dominant: 16.2 % (TRAIN: 20.3 %).
- **Confidence is high for the ink and idiom rows.** They are exact counts
  over the whole of TRAIN.
- **Confidence is moderate for the class shares.** The classes come from
  rule thresholds set in this study. No human labels validate them.
  Section 3.3 shows how much the line-minimal share moves when the
  thresholds move: from 13 % to 50 %.

**Sparse ink does not identify line art (measured).** The pieces that the
tone-dominant class fills with `.:.:` or `::::` still have a median ink of
2.95 %. Line-minimal pieces have 2.43 %. The reason is that the tone glyphs
are 3 px dots. On ink share alone, a tone-filled portrait passes the skill's
"keep ink sparse" rule. The measure that separates the styles is
envelope emptiness, which is defined in section 3.1. The medians by class
are 0.71 for line minimal, 0.68 for line-plus-tone, 0.58 for tone-dominant
and 0.54 for dense-filled.

## 2. Inputs

| input | identity |
|---|---|
| Archive | `/Users/r/Projects/ascii-art-archive`. Records are read as Git blobs at commit `f498eb30678c753a2867f0a97ecc22561f54543e`, never from the work tree. |
| Index | `collections/aahub-mlt/index.jsonl` at that commit, sha256 `c7a35081…cd14d01f9` (checked against the split file) |
| Split owner | `/Users/r/Projects/screenshot-of-ascii-art-to-txt-converter/data/aahub_mlt_split.json`, sha256 `983848da35bab64d91b59de02bb0d8c0998edfa0ec942d5588b7a485b6b52347`. Only `train_keys` (10,559 pages) are used. Every script asserts that no key is in `held_out_keys`. |
| Font | `/Users/r/Projects/ascii-art-archive/collections/aahub/Saitamaar.ttf`, sha256 `592bf6be803ed76311841b95a10b20db3df0ec693a15f858757d47420b9b3a28`, 16 px |
| Render | Same as converter `scripts/mlt_pairs.py` `render_aahub`: 8 px pad, 17 px pitch, first baseline y = 22, ink is L < 128 |
| TRAIN text set | `input_set_sha256` `3c59e740…acd5e0` in `results.json`: per page, the sha256 over its pieces' text hashes |

**Piece rule.** A piece is a record entry `aa[i]` whose text has at least
two lines. This rule matches `is_art` in `mlt_pairs.py`. It keeps 806,288
art pieces and skips 98,785 single-line section headers.

**Numeric character references.** AA-004 keeps some glyphs as numeric HTML
character references, for example thin spaces `&#8198;`, block glyphs
`&#9608;` and `&#65374;`. These appear in 20,452 TRAIN pieces (2.5 %,
measured). A browser shows the character, so the scripts decode the numeric
references before measuring. They also treat the Unicode fixed-width spaces
U+2000–U+200A, U+00A0 and U+202F as spacing. These two steps extend
SJIS-AUDIT, whose page contains none of these glyphs. Saitamaar maps
U+2002–U+200A, U+2588 and U+2591, so those characters render with their own
advance. It does not map U+00A0.

The converter's `render_aahub` draws the undecoded reference text. Any
pair it builds from such a piece therefore shows the literal `&#…;`
(inferred from its code; not run here).

## 3. Method

### 3.1 Per-piece metrics (`aa004_style_stats.py`)

| metric | definition | comparable to |
|---|---|---|
| `ink_share` | ink px ÷ (widest line advance px × rows × 17), on the 16 px render | SJIS-AUDIT `ink_density` |
| `ink_est` | the same ratio, computed by summing cached single-glyph ink counts, for every TRAIN piece | equals `ink_share` on all 54,135 rendered pieces (ratio p10 = p50 = p90 = 1.0, measured). The whole-TRAIN ink figures therefore use it. |
| `outline_share`, `texture_share`, outline-dominant (≥ 0.6), texture-dominant (≥ 0.8) | SJIS-AUDIT `glyph_class`, copied unchanged | SJIS-AUDIT §1.2 |
| `tone_share` | share of non-space glyphs inside a tone band. Dot band: at least 4 dot glyphs (`. , : ; ' `` ` `` ､ ･ " ﾞ ﾟ ｀` …), touching or separated by single half spaces. Horizontal hatch: at least 3 of `ﾆ 二 ニ 三 = ≡`. Vertical hatch: at least 4 of `i l | ｌ ｉ I !`. Diagonal hatch: at least 3 repeats of one of `/ ／ \ ＼`. | skill 15.6 and 15.7 (operational) |
| `dot_band_closed` | a dot band with a non-space glyph directly on both of its row ends | row-level proxy for 15.7.3 ("every tone mass has a defined edge") |
| `envelope_blank` | Envelope: for each text row, the span from its first to its last non-space glyph, 17 px tall. Value: the share of envelope pixels with no ink inside a 5×5 px window. This is the interior-emptiness measure. | new |
| `interior_space_share` | the advance px of spaces inside the row spans ÷ the span px (text level) | new |
| `text_share` | share of glyphs in language runs: Japanese runs with at least 2 non-shape hiragana or at least 3 kanji or katakana and at least 3 distinct characters; Latin words of at least 3 distinct letters; full-width alphanumerics | 15.6 (letters as letters) |
| idioms | substring counts of every skill-15.5 idiom. "Contour idioms" means the lobe, lobe-base, shoulder, arch, flat-arc, sub-cell-step and entry groups, without `从 彡 ,,`. | 15.5 |

**Calibration against SJIS-AUDIT (measured).** The pipeline was run on the
爆発・煙 record from AA-004. That record has 179 art pieces; SJIS-AUDIT had
180 posts. The ink figures reproduce SJIS-AUDIT:

| statistic | this pipeline | SJIS-AUDIT |
|---|---|---|
| median | 0.0235 | 0.0236 |
| p10 | 0.0125 | 0.0128 |
| p90 | 0.0439 | 0.0441 |
| outline-dominant posts | 29 of 179 | 30 of 180 |

### 3.2 Sampling

- Rendering every piece would take about 5 CPU-hours. The raster metrics
  (`ink_share`, `envelope_blank`) are therefore computed on a sample.
  Every text metric, and `ink_est`, is computed on all of TRAIN.
- **Stratum:**
  - `汎用AA/<sub>` and `2ch/<sub>` folders: the second-level folder;
  - all other pages: the top-level folder. This covers the kana-row title
    folders, `A・0・記号`, `実在人物パロディ`, `企業・ご当地キャラクター`
    and `原典不明人物`.
  - This gives 38 strata.
- **Selection rule.** A piece (key, i) is rendered when
  `int(sha256("aa004-line-art-style-v1|key|i")[:12], 16) / 16**12 < min(1, 2000 / n_s)`.
  Here `n_s` is the stratum's `pieces` total in `index.jsonl`.
- **Sample size.** 54,127 sampled pieces, from 44 in the smallest stratum to
  1,985 in the largest. The 179 爆発・煙 pieces are also rendered, for
  calibration only.
- **TRAIN-wide shares.** The sampled pieces are weighted by stratum art
  pieces ÷ stratum sampled pieces.
- **Confidence intervals.** A page-cluster bootstrap with 300 resamples
  gives the CIs; the seed is fixed. Each per-stratum Wilson interval in
  `tables.json` is computed per piece and ignores page clustering, so it is
  too narrow.
- **Resources.** The full run took 23.5 min on 2 worker processes, with a
  1.29 GB peak footprint.

### 3.3 Style classes

The class is chosen by the first rule that applies, in this order.
The thresholds are fixed in the script.

1. **text**: `text_share` ≥ 0.3.
2. **tone_dominant**: `tone_share` ≥ 0.6.
3. **dense_filled**: ink > 0.05, or `envelope_blank` < 0.6.
4. **line_plus_tone**: `tone_share` ≥ 0.25.
5. **line_minimal**: everything else.

The thresholds are anchored on the calibration page. Its ink p90 is 0.044
and its `envelope_blank` median is 0.68. The tone cut of 0.25 is the
SJIS-AUDIT "mixed" region.

**Threshold sensitivity (measured; `line_minimal_sensitivity` in
`results.json`).**

- Moving the ink cut between 0.04 and 0.07 changes the line-minimal share by
  at most 2 points.
- Moving the blank cut between 0.5 and 0.7 moves the share from 37 % to
  17 %, with ink ≤ 0.05 and tone < 0.25.
- Moving the tone cut between 0.15 and 0.35 moves the share from 22 % to
  39 %.
- Over the whole 27-point grid the share ranges from 12.8 % to 49.8 %.
  It never reaches 50 %.

## 4. Results

### 4.1 By subject group (TRAIN-weighted; `tables.json`)

Groups:

- **works**: the kana-row title folders and `A・0・記号`. These are
  characters from named works, and they make up 82 % of TRAIN pieces.
- **2ch**: the 2ch character folders.
- **generic**: 汎用AA.
- **other**: real-person parody and company or regional mascots.

| group | art pieces | line minimal | line + tone | tone-dominant | dense/filled | text | outline-dominant | ink ≤ 5 % and blank ≥ 0.6 |
|---|---|---|---|---|---|---|---|---|
| works | 664,050 | 28.7 % | 27.8 % | 16.4 % | 26.9 % | 0.2 % | 18.3 % | 62.6 % |
| 2ch | 81,744 | 41.9 % | 18.7 % | 13.0 % | 25.3 % | 1.0 % | 30.1 % | 65.8 % |
| generic | 48,367 | 35.2 % | 19.0 % | 14.9 % | 30.4 % | 0.5 % | 29.1 % | 61.2 % |
| other | 12,127 | 40.7 % | 22.4 % | 11.0 % | 25.0 % | 0.8 % | 29.9 % | 67.8 % |
| **all TRAIN** | 806,288 | **30.6 %** | **26.3 %** | 15.9 % | 26.9 % | 0.3 % | 20.3 % | 62.9 % |

### 4.2 By stratum (`results.json` `by_stratum`)

Column sources:

- **ink med, tone med, tone any, idiom any:** whole TRAIN.
- **LM, L+T, TD, DF:** the rendered sample, unweighted within the stratum.

| stratum | pieces | ink med | outline-dom | tone any | tone med | 15.5 idiom any | LM | L+T | TD | DF |
|---|---|---|---|---|---|---|---|---|---|---|
| 汎用AA/エフェクト | 2,101 | 1.81 % | 27.5 % | 77 % | 0.16 | 62 % | **51.5 %** | 19.7 % | 13.7 % | 14.3 % |
| 汎用AA/地図 | 881 | 2.03 % | 19.4 % | 58 % | 0.03 | 66 % | 57.9 % | 9.7 % | 10.1 % | 17.9 % |
| 汎用AA/軍事 | 1,956 | 2.77 % | 30.4 % | 94 % | 0.17 | 89 % | 44.0 % | 22.0 % | 4.9 % | 28.9 % |
| 汎用AA/乗り物・メカ | 2,058 | 3.56 % | 35.2 % | 92 % | 0.16 | 82 % | 42.4 % | 18.2 % | 8.1 % | 30.9 % |
| 汎用AA/小道具 | 9,111 | 2.94 % | 40.0 % | 74 % | 0.15 | 63 % | 38.7 % | 15.2 % | 13.3 % | 31.8 % |
| 汎用AA/体 | 13,714 | 2.19 % | 25.3 % | 78 % | 0.22 | 84 % | 38.1 % | 26.5 % | 17.0 % | 18.2 % |
| 汎用AA/伝承・伝説・空想の生物 | 1,287 | 2.68 % | 27.2 % | 84 % | 0.22 | 90 % | 38.6 % | 17.9 % | 16.0 % | 27.4 % |
| 汎用AA/人間・モブ | 3,509 | 2.85 % | 23.6 % | 92 % | 0.29 | 85 % | 28.3 % | 21.9 % | 17.6 % | 31.9 % |
| 汎用AA/動植物 | 1,848 | 2.61 % | 20.6 % | 80 % | 0.25 | 83 % | 28.3 % | 16.9 % | 18.6 % | 35.7 % |
| 汎用AA/背景・風景 | 8,038 | **4.35 %** | 23.2 % | 94 % | 0.37 | 81 % | **20.3 %** | 17.4 % | 21.7 % | **40.4 %** |
| 汎用AA/文字 | 3,665 | 4.44 % | 40.6 % | 17 % | 0.00 | 24 % | 35.0 % | 1.7 % | 2.4 % | **60.7 %** |
| 2ch/無関係シリーズ | 138 | 3.11 % | 64.5 % | 75 % | 0.07 | 100 % | 71.0 % | 11.6 % | 0.7 % | 16.7 % |
| 2ch/なんJ関連AA | 767 | 2.77 % | 48.5 % | 58 % | 0.04 | 71 % | 54.4 % | 10.0 % | 4.0 % | 28.9 % |
| 2ch/ドクオ | 546 | 2.19 % | 44.3 % | 68 % | 0.16 | 87 % | 54.0 % | 16.9 % | 17.4 % | 11.4 % |
| 2ch/元ネタ有り | 13,032 | 2.69 % | 20.6 % | 92 % | 0.18 | 97 % | 47.3 % | 21.2 % | 4.0 % | 26.5 % |
| 2ch/モナー派生 | 4,428 | 3.02 % | 42.4 % | 49 % | 0.00 | 64 % | 44.9 % | 10.4 % | 5.7 % | 37.0 % |
| 2ch/やる夫派生 | 45,373 | 2.73 % | 31.5 % | 80 % | 0.24 | 88 % | 44.4 % | 17.5 % | 16.4 % | 21.3 % |
| 2ch/ダディクール | 1,096 | 2.85 % | 13.4 % | 98 % | 0.26 | 98 % | 40.9 % | 32.0 % | 11.7 % | 15.0 % |
| 2ch/ショボーン派生 | 1,919 | 3.40 % | 26.3 % | 58 % | 0.05 | 66 % | 26.4 % | 8.5 % | 6.2 % | **52.9 %** |
| 2ch/やる夫スレオリジナル | 9,809 | 2.97 % | 22.4 % | 96 % | 0.35 | 86 % | 25.8 % | 25.9 % | 17.6 % | 30.8 % |
| 2ch/VIPRPG | 542 | 2.68 % | 23.8 % | 84 % | 0.39 | 97 % | 26.4 % | 45.6 % | 11.4 % | 16.6 % |
| 企業・ご当地キャラクター | 4,203 | 2.81 % | 38.6 % | 74 % | 0.12 | 88 % | 50.1 % | 17.5 % | 8.8 % | 22.7 % |
| 実在人物パロディ | 7,880 | 2.91 % | 24.5 % | 90 % | 0.25 | 92 % | 35.8 % | 25.0 % | 12.1 % | 26.4 % |
| は行 (works) | 92,734 | 2.75 % | 19.6 % | 92 % | 0.30 | 92 % | 34.7 % | 29.6 % | 14.9 % | 20.7 % |
| や行 (works) | 30,021 | 2.63 % | 26.5 % | 93 % | 0.31 | 93 % | 35.2 % | 33.9 % | 11.7 % | 19.1 % |
| た行 (works) | 86,276 | 2.90 % | 21.2 % | 91 % | 0.30 | 92 % | 29.2 % | 26.5 % | 14.7 % | 29.1 % |
| さ行 (works) | 88,184 | 2.95 % | 19.8 % | 93 % | 0.33 | 90 % | 29.0 % | 25.9 % | 14.3 % | 30.5 % |
| A・0・記号 (works) | 155,477 | 2.96 % | 17.3 % | 94 % | 0.35 | 92 % | 26.2 % | 27.9 % | 17.5 % | 28.3 % |
| か行 (works) | 93,636 | 2.92 % | 17.9 % | 94 % | 0.35 | 92 % | 26.7 % | 27.3 % | 18.6 % | 27.0 % |
| あ行 (works) | 48,642 | 2.95 % | 16.9 % | 94 % | 0.36 | 93 % | 26.4 % | 29.5 % | 19.2 % | 24.8 % |
| わ・を・ん (works) | 1,588 | 3.88 % | 14.4 % | 93 % | 0.36 | 90 % | 19.0 % | 32.7 % | 17.9 % | 30.4 % |

The other strata, and every column for every stratum, are in
`results.json` (`by_stratum`, `by_top_level`, `by_sub_folder`). The
per-page summary rows for all 10,559 TRAIN pages are in `pages`.

### 4.3 Tone and idioms (whole TRAIN, measured)

**Tone is present in 90.9 % of pieces.**

- Dot tone is present in 85.7 % of pieces and hatch in 55.4 %.
- The median tone share is 0.31.
- Of all dot bands, 63.1 % are closed by a glyph at both row ends. On
  爆発・煙 the figure is 37.7 %. Smoke and explosion tone ends in a density
  edge more often than character tone does.

**The tone spellings follow the skill's material contract.** As section 4.5
of the skill requires, each spelling is a small fixed set:

| spelling | bands | share of pieces | label |
|---|---|---|---|
| `::` (`::::`) | 8.07 M | — | measured |
| `.:` (`.:.:`) | 4.11 M | — | measured |
| diagonal `///` | 1.16 M | — | measured |
| `ﾆ` / `ニﾆ` hatch | 0.98 M | — | measured |
| half-space-interleaved `: : :` | — | 33.5 % | measured (`candidate_idioms.json`) |
| `:.:.:` | — | 18.3 % | measured (`candidate_idioms.json`) |

**Skill-15.5 idioms by total count:**

- `,,` 1.56 M
- `_,` 1.28 M
- `'´` 0.72 M
- `｀ヽ` 0.69 M
- `彡` 0.54 M
- `､_` 0.49 M
- `从` 0.37 M
- `＼＿` 0.34 M
- `／￣` 0.31 M
- `_ノ` 0.29 M
- `⌒ヽ` 0.29 M
- `ゝ__ノ` 755

The last one confirms the skill's note that `ゝ__ノ` is rare outside smoke
pages.

**Letters (measured).** 1.16 % of Latin-letter occurrences in TRAIN are in
word runs (348,610 letters). The rest are shape letters. The most frequent
are:

- `i` 13.4 M
- `l` 7.6 M
- `r` 1.7 M
- `V` 1.4 M
- `j` 1.4 M
- `Y` 0.64 M
- `x` 0.44 M
- `f` 0.40 M
- `z` 0.33 M

`r`, `j`, `Y`, `f` and `z` are outside the 4.1 whitelist and are used as
strokes. This supports section 15.6 at corpus scale.

## 5. Conclusions

1. **Sparse ink is close to universal.** 94.1 % of TRAIN pieces have
   ≤ 5 % ink (measured). The exceptions are measured as well:
   - 汎用AA/文字 (block lettering), with 59 % sparse;
   - 背景・風景, with 63 % sparse;
   - 乗り物・メカ, with 77 % sparse;
   - わ・を・ん, with 76 % sparse.

   Ink share does not separate line art from tone fill (section 1).
2. **Stroke idioms are close to universal.** 90.1 % of pieces contain a
   skill-15.5 contour idiom (measured). The idiom table is the corpus
   vocabulary, not a smoke-page vocabulary.
3. **Strict minimalism is a large minority.** About 31 % of TRAIN is strict
   line minimal (measured, threshold-dependent).
4. **Outline first with bounded tone is a narrow majority.** About 57 % of
   TRAIN is outline first with tone as a bounded material (measured,
   threshold-dependent). That pieces "read outline first" is an inference;
   the class rule tests tone share and emptiness, not drawing order.
5. **Strict line art is most common in effects, maps and the classic 2ch
   characters.** For example, モナー派生 44.9 %, ドクオ 54.0 % and
   なんJ 54.4 % (measured).
6. **Work characters are line plus tone material.** These pages hold 82 %
   of TRAIN (measured). On them, tone-filled hair and clothing (`.:.:`,
   `::::`, `///` blush, `ﾆﾆ` shading) make line-plus-tone, tone-dominant
   and dense together about 70 % (measured). That these tones are a
   declared material for hair, cloth and blush is inferred from the
   exemplars; the scripts do not read semantics.
7. **The style does not hold for four kinds of page.**
   - **Backgrounds** (背景・風景): dense 40 %, ink median 4.35 %, hatch in
     73 % of pieces (measured). They are drawn as box-drawing buildings and
     hatch (inferred).
   - **Lettering** (文字): dense 61 % (measured). These are `■`/`□` block
     letters, an instance of the Block/Filled styles of skill section 6
     (inferred from exemplars).
   - **Unicode block art** (`█ ▇ ◢`, for example the `ユニコード` pages) and
     **kanji mosaics** (`鬱櫑嬲` grey ramps). Both are skill-6 Block and
     Filled styles. Their counts are inside dense/text; they are not
     measured separately.
   - **2ch/ショボーン派生**: dense 53 % (measured). The reason is not
     inspected.
8. **Clouds and smoke away from 爆発・煙 use the same lobe language plus
   further spellings.** See sections 6 and 7. The cloud-bearing pages in
   effects and backgrounds (section 6.2) are line art with dot-tone bodies.
   The background pages are denser overall (measured, page rows in
   `results.json`).

## 6. Exemplars (TRAIN only; `exemplars.json`)

**Notation.** `□` is U+3000 and `·` is U+0020, as in SJIS-AUDIT. Excerpts
are 3 consecutive lines. Lines longer than about 60 glyphs are cut with
`…`; the full rows are in `exemplars.json` and in the archive.

**Selection.** The rules are in `exemplars.py`:

- best score per class and per subject group;
- the cloud scan ranks pieces by the count of lobe idioms.

### 6.1 Style classes

| class | key : aa index (page) | why |
|---|---|---|
| line minimal | `0b009c14dbe81b3aff18d7b041ba770f:117` (2ch/モナー派生/ガナー) | ink 1.6 %, blank 0.84, tone 0.05. A contour of `､_ ´｀ヽ '´ ,-､` with nothing inside. |
| line minimal | `a93040c0e2f4eabd9ded91d0af4a1752:91` (ら行/…/渡辺曜01（基本）) | ink 0.9 %, blank 0.92, outline share 0.92. A work-character piece drawn as pure strokes. |
| line + tone | `e3c64501282f3a35c43931c1239fbe34:113` (2ch/ショボーン派生/AF杉浦) | `::::` fills a region closed by `ト､ﾉV( l-―r⌒f` strokes. The tone is a bounded material. |
| tone-dominant | `85cb726da5e416e44ceb4fbbf32c8c89:81` (汎用AA/エフェクト/エフェクト) | tone share 1.0. A `:;:;` core inside a `.....` rim, with no stroke. This is the res13-type flash with a density edge. |
| tone-dominant | `e8a150abd7ef4615bc44216a02a20b09:102` (さ行/…/トゥルーデ02) | Hair and clothing filled with `::::`. Ink is only 2.1 %, but blank is 0.57. |
| dense/filled | `2311c40433d80dddf162116ddc2a3159:354` (汎用AA/文字/熟語01) | ink 52 %. `■` block lettering. |
| dense/filled | `c191f6f16d351e711a8f378034302d27:20` (わ・を・ん/…/黒木智子04（ユニコード）) | ink 67 %. Unicode block art `▂▃▅▆▇█◢◤`. This is the skill-6 Block style. |
| text (false positive) | `bcd3fef536aad52e8c5eba90b03206fb:235` (実在人物パロディ/…) | A kanji-density mosaic (`丶丶…鬱櫑嬲…`). It is the skill-6 Filled style, but the text heuristic labels it text. |

```
line minimal, 0b009c14…:117
□｀ー-,､_□□□□□□□ｌ·_,·-+ﾆ'´￣□□´｀ヽ､＿ヽ_＞-·､_□□/□·_,-､｀ヽ·□·ｌ
□□□□□·￣ﾌi□□·,□r'·＿__｀,＿ｒ'´￣·｀ヽi-='´｀ヽ､-､／ヽ,へ□!□□!´ヽ·ノ
□□□□_,·-'´!｀ヽ,'´□ｌ'´,ｨ□□□ｂ·ヽ-ｨ―-<ｰ□□□／ヽ｀ヽ,·l□·｀ヽ,--,,ﾉ|´

line + tone, e3c64501…:113
□□□|□□□□□□□□□□□□□□□·ト、ﾉV(::::::l-―r⌒f:::::::::::::::::::／_·／
□□□|!·□·□·□·□·□·□·□·j{□□·□·>::::::::::{:::::」·_·/□□□L::::／￣·／／
□□□|!□□□□·□·□·□·□·j{□□·＜::::::::::::::ヽノ□/□/!□「□·」□□□□·／□·／

tone-dominant flash, 85cb726d…:81
□□□□·□·□·□·.....:;:;:;:;:;:;:;:;:;:;:;:;:;:;:;:;:;:.....
□□·□·□·□·.·.:;:;:;:;:;:;:;:;:;:.:;:..;:.:..:;:.:;:;:;:;:;:;:;:;:;:.·.
□□·□·□·,:;:;:;:;:;:;:;:;:.:.:.:.:..·.:.·.:.·.:.·..:.:.:.:.:;:;:;:;:;:;:;:;:.
```

### 6.2 Clouds, smoke and spray outside 爆発・煙

| key : aa index (page) | why |
|---|---|
| `29bbdb9128e7655193cb54559cd127cf:224` (汎用AA/背景・風景/背景) | A cloud bank of lobe chains `⌒'～⌒ヾ⌒`, `〃´⌒ヾ` and `ゝ'⌒ヽ`, with empty interiors and no tone. It is pure line art, inside a background page. |
| `a3d73b4915c673e26474c9d3013d00b3:46` (汎用AA/小道具/娯楽系/煙草) | Cigarette smoke as line-only curls `）ヽ`, `⌒)ﾉ`, `⌒)イ⌒)` rising from the cigarette. The lobe count is 7. |
| `ea2e1523c12ba9428fef4b24f095be79:23` (汎用AA/背景・風景/…/街並み06（燃えている街…）) | Smoke from a burning town: `γ⌒＼`, `γ⌒`, `ゝ·__ノ`, `乂_` lobes with `:·:·:` half-space dot bodies and a `.·.·:·:` density ramp. |
| `1823425068f1993743f2308e797c2c2c:45` (汎用AA/背景・風景/地形/地形（山・鉱山・桟道）) | Clouds around a mountain. Flattened lobe tops `⌒¨¨⌒''～`, `ノ⌒""⌒～-` and `γ⌒¨゛` over a `:·:·:` body. |
| `85cb726da5e416e44ceb4fbbf32c8c89:33` (汎用AA/エフェクト/エフェクト) | Scallop chains `(⌒⌒⌒ヽ`, `～⌒⌒Y⌒` and `/⌒⌒⌒ヽﾉ` at the edge of a smoke field. |
| `095894e54a97eac6d0e9ac467852b1e1:91` (汎用AA/エフェクト/エレメント/エレメントその他) | Spray or splash. Small open shapes `__,ノし`, `八__,ノ(_,/`, `γ⌒ヽ` and `ノ(___` are scattered in a dot field `;·.:·:`. Each splash is a contour fragment, not a closed lobe. |
| `c3b8fbf7b30d912ce6336b379f96d745:165` (汎用AA/エフェクト/攻撃エフェクト/技) | A motion trail: the stamp `⌒ヽ〕iト` repeats diagonally, beside speed lines `Zﾕ=‐'",｡o≦=‐─·‐`. |

```
cloud bank, 29bbdb91…:224 (lines 2-4)
□□□□□□□□□·□·□·,□⌒'～⌒ヾ⌒·∩lｌ冊ll∩·|,·⌒´⌒ヽ
□□□□□□□□□□□·（□□□□□□□·),·⌒ヽ〃´⌒ヾ·□□□□□）｀⌒ヽ
□□□□□□□□□□,□´,ゝ'⌒ヽ,□□□□□□(⌒□□□□□·,□⌒ヾ⌒'～｀⌒ヽ

cigarette smoke, a3d73b49…:46 (lines 0-2)
□□□□□□□□□□□□□□·}·ﾄ､□□□□□□□□□□·r‐ｧ
□□□□□□□□□□□□―く□）ヽ□·＿,□□□□＿ノ·（_
□□□□□□□□□□□□□□·（·□:|□⌒)ﾉ□□□⌒)イ⌒)·□,.ｨ

burning-town smoke, ea2e1523…:23 (excerpt lines 15-17, cut)
ﾆﾑ＿|{□□·＼:::〕iト·γ⌒＼·>__ノ:·:.□⌒ヽ□|□｀丶＿ノ:·:γ⌒□.·.·:·:·:):·:·:·…
ニﾑγ⌒□□□＼:::::::::≧=‐￣｀'＜⌒□□□ノ:·:·:·ノ｀丶､⌒乂_γ⌒□ヽ:·:·:·:·:ノ□…
ﾆﾆﾑ{□□□γ´彡≧=‐□L_:::::::::::::::＞''＾丶､□□·;⌒ヽ□｀丶／⌒ゝ·__ノ:·γ⌒□…

mountain cloud, 18234250…:45 (excerpt lines 7-9, cut)
:·:·;⌒¨¨⌒''～·､、·:·:·:·:·:·:·:·:·.□□□□□·.·:·:·:·:..□□.·.·..:..□·:::::::::…
:·:·ゝ,□□□□□□□)□:□:□:□:·ノ⌒""⌒～-·.:·:·:·:..□□.·.·..:..□·:::::::::.□…
:□:□:´"''～～～'′.□:□.·(⌒·□□·□·□·□·□·.:·:·:·:.□□.·.·.·.:.□·:::::::::.…
```

Page-level figures for these pages are measured and are in `results.json`
`pages`:

| page | outline-dominant | tone median | ink median |
|---|---|---|---|
| 背景 | 40.1 % | 0.24 | 3.6 % |
| 煙草 | 19.6 % | 0.34 | 2.4 % |
| 街並み06 | 12.5 % | 0.38 | 4.5 % |
| 山 | 4.5 % | 0.56 | 3.2 % |
| エフェクト | 24.3 % | 0.22 | 1.8 % |
| 技 | 19.5 % | 0.16 | 1.4 % |

## 7. Style knowledge

### 7.1 Idioms and material bindings not in skill 15.5

All counts are measured over all 806,288 TRAIN pieces
(`candidate_idioms.json`). Every reading is inferred from the exemplars in
section 6. The candidates were read off exemplars before they were counted.

| idiom | pieces | reading (inferred) | where most frequent |
|---|---|---|---|
| `⌒Y` / `Y⌒` (`⌒Y⌒Y⌒`) | 4.3 % / 3.5 % | Scallop chain: lobes joined at a cusp. Used for cloud edges, and also for fur, foliage and hair. | 2ch/VIPRPG 20 %, 汎用AA/体 9 % |
| `⌒'`, `'～`, `～'` (`⌒'～⌒`) | 4.3 %, 3.5 %, 1.3 % | A wisp tick: a lobe that trails into a wave (cloud fringe, smoke tail) | 背景・風景 10 %, 乗り物・メカ 7 % |
| `⌒ヾ` | 3.0 % | A lobe with a doubled tick (cloud bank) | わ・を・ん 9 %, 伝承 6 % |
| `⌒¨` (`⌒¨¨⌒`) | 2.8 % | A flattened lobe: cloud base or bank top | やる夫スレオリジナル 9 %, 背景・風景 5 % |
| `γ⌒` (`γ⌒ヽ`) | 2.4 % | A puff head, opening upward and to the left. Its mirror pair is `⌒ヽ`. | や行 6 %, 軍事 5 %, 背景・風景 5 % |
| `⌒ゝ` | 0.9 % | A lobe turning down into a base | やる夫スレオリジナル 5 % |
| `ノし`, `__,ノし` | 0.2 %, 1.9 % (`__,ノ`) | Splash or flame tongue: an open contour fragment | エフェクト 1.3 % |
| `-=ﾆ` / `ﾆ=-`, `=-` / `-=` | 9.7 % / 10.8 %, 28.4 % / 27.9 % | **Tapered hatch.** Horizontal hatch thins through `=` and `-` into a stroke. A tone band ends on a taper, not on a contour. | ダディクール 53–63 %, やる夫スレオリジナル 24–55 % |
| `///` | 19.0 % | Diagonal-hatch material: blush, cast shadow, gloss | ま行 26 %, ら行 24 % |
| `: : :` (half-space interleave), `:.:.:`, `. . .` | 33.5 %, 18.3 %, 7.0 % | The dominant dot-tone spellings. The interleave is the 15.4 whitespace law applied to tone. `. . .·.·:·;` is a density ramp (街並み06:41). | VIPRPG 67 %, 背景・風景 34 % (`:.:.:`) |
| `i|`, `|i`, `l|`, `i!` | 14.1 %, 12.8 %, 11.2 %, 10.0 % | Vertical-strand tone: hair strands, wood, metal | 背景・風景 27–28 %, 乗り物・メカ 18–27 % |
| `（__人__）`, `（●）` | 1.1 %, 1.2 % | Fixed face idioms: the やる夫 mouth and the ダディクール eye. The art of a 2ch character is a fixed glyph signature. | やる夫派生 17 %, ダディクール 66 % |
| `〕iト` (`⌒ヽ〕iト`) | 2.6 % | A motion-trail stamp in 技:165. Most occurrences are on character pages, where the reading is not inspected. | さ行 4.5 % |

**Not supported.** The `人_` / `_人` "splash" candidates are not a
splash idiom (measured): they occur in 27 % of やる夫派生 pieces, which is
the `（__人__）` mouth. The ground candidates (`､w,`, `wW`) occur in at most
0.07 % of pieces.

### 7.2 How outline-first varies by subject (measured shares, inferred readings)

- **Effects** (`汎用AA/エフェクト`) follow the skill best:
  - line minimal 51.5 %;
  - ink median 1.8 %;
  - tone median 0.16;
  - only 34 % of dot bands are closed.

  Tone in effects is mostly pure-tone with a density edge: flashes, dust
  and spray.
- **Classic 2ch characters** (モナー, ドクオ, なんJ, 無関係) are drawn
  outline-only: line minimal 45–71 %, tone median 0.00–0.16.
- **Work characters** (82 % of TRAIN) draw the outline first and then fill
  named regions (hair, clothing, shadow) with a dot or hatch material:
  - tone median 0.30–0.36;
  - 60–66 % of dot bands closed by strokes.

  This is the skill's line-plus-screen-tone row. Here it applies to
  figures, not to smoke.
- **Backgrounds** are hatch-heavy, with box-like lines:
  - hatch in 73 % of pieces;
  - `||`, `￣|`, `|＿` and `ﾆﾆ` among the top n-grams.

  Clouds inside backgrounds stay line art (section 6.2).
- **Lettering and block art** are outside the line style (sections 5.7
  and 6.1).

### 7.3 What does not fit the skill

1. **"Keep ink sparse" with the median 2.4 % (15.7.4) is not a style
   test.** Tone-dominant and dense pieces satisfy it (section 1). The
   quantity that discriminates is envelope emptiness.
2. **"Every tone mass has a defined edge" (15.7.3)** holds for 63 % of dot
   bands at the row level. The open bands are flashes, ramps and the
   free-floating `: : :` fields.
3. **15.10 says the idiom readings come only from one smoke page.** The
   counts here extend those frequencies to subject strata. The readings in
   7.1 are still inferred.
4. **Skill section 6 Block and Filled styles exist on AAHub** (Unicode
   block art, `■` lettering, kanji mosaics). Section 15 treats AAHub as
   line plus tone only.

## 8. Reproduce

```sh
cd docs/research/ascii/sjis_aa_line_art_style_aa004
A=/Users/r/Projects/ascii-art-archive
S=/Users/r/Projects/screenshot-of-ascii-art-to-txt-converter/data/aahub_mlt_split.json
python3 aa004_style_stats.py --archive $A --split $S --out results.json --sample-out sample_pieces.jsonl.gz --workers 2
python3 candidate_idiom_counts.py --archive $A --split $S --out candidate_idioms.json
python3 exemplars.py --archive $A --split $S --sample sample_pieces.jsonl.gz --out exemplars.json
python3 derive_tables.py --results results.json --sample sample_pieces.jsonl.gz --out tables.json
```

Every script refuses to overwrite an existing output with different bytes.
It needs `fontTools`, `Pillow`, `numpy` and `scipy`; the versions used were
Pillow 12.1.0, numpy 2.5.2 and scipy 1.18.1, on Python 3.14. Outputs of
this run:

| file | sha256 |
|---|---|
| `results.json` | `816d9166fd42cce2d1675cafe242c4ecfdc164de1bf4e63efd0234251028203b` |
| `sample_pieces.jsonl.gz` | content (uncompressed) `d4b0d2f4813a42b85a0e0a96e4e02329213b32fe7141abb1fb834364cc1a4ac2`, 54,135 rows |
| `candidate_idioms.json` | `348958e0f09b90187eb39db83fca43b6a0e7de4d1067104d31d531ab0341c091` |
| `exemplars.json` | `a95af977accef85a7622e57e52ba09404a0d45f1a9067670b9e8c110f41f0f63` |
| `tables.json` | `7a9a54422cefdfba4aa0476c139b65849642f109166afd792fbddd2b6004a1f2` |

The pipeline is deterministic by construction: fixed hash sampling, ordered
`imap` and a seeded bootstrap. The 23-minute main run was executed once and
was not re-run to confirm byte identity.

## 9. Limits

- **The classes are rule thresholds, not human labels.** No piece was
  hand-labelled to measure precision. The sensitivity grid in section 3.3
  is the only robustness check.
- **The tone and text detectors are lexical.**
  - A `::::` run inside a contour line counts as tone.
  - Kanji mosaics count as text (section 6.1).
  - `|l|` pillars shorter than 4 glyphs are not counted as tone.
- **`envelope_blank` is measured on row spans, not on the true
  silhouette.** A concave shape counts its outside bays as interior.
- **Sample metrics carry page clustering.** The bootstrap CI accounts for
  this only TRAIN-wide.
- **The n-gram lists in `results.json` are sums of each page's top 400
  n-grams.** They are lower bounds. The candidate idiom counts are exact.
- **Rendering differs from the browser for unmapped glyphs.** A glyph
  missing from Saitamaar (for example U+00A0, and some symbols) gets zero
  advance in the text metrics. PIL draws it with Saitamaar's fallback
  glyph, where a browser would fall back to another font.
- **The held-out partition was not opened.** The results describe TRAIN
  only (75.5 % of AA-004 pages; 905,073 index pieces including headers).
