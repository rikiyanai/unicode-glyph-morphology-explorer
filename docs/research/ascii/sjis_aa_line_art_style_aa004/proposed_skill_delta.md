# Proposed delta to `ascii-art-authoring` section 15 (text only, not applied)

This file proposes text only. The skill files were not edited. Every number
comes from this directory: `results.json`, `tables.json` and
`candidate_idioms.json`. The source is the AA-004 TRAIN partition at archive
commit `f498eb306`, with split sha256 `983848da…b52347`. The proposed
citation id is `AA004-STYLE`, and it would cite
`unicode-glyph-morphology-explorer/docs/research/ascii/sjis_aa_line_art_style_aa004/`.

## D1. Provenance table: add one row

| citation id | source |
|---|---|
| `AA004-STYLE` | unicode-glyph-morphology-explorer `docs/research/ascii/sjis_aa_line_art_style_aa004/` (README, `aa004_style_stats.py`, `results.json`, `candidate_idioms.json`). It covers the AA-004 AAHub crawl, TRAIN `train_keys` only (10,559 pages, 806,288 art pieces), archive `f498eb306`, Saitamaar 16 px, 2026-09-30. |

## D2. 15.1, after the `[SJIS-CORPUS]` paragraph

> `[AA004-STYLE]` measures the style itself over 806,288 AA-004 TRAIN
> pieces. 爆発・煙 is a typical page, not an outlier:
>
> - its line-minimal share is 34.6 % against 30.6 % for TRAIN;
> - its ink median is 2.35 % against 2.89 %.
>
> Treat the section 15 method as the AAHub norm for effects, maps, classic
> 2ch characters and line-drawn props. Treat it as one of two norms for
> work characters. Section 15.7.5 gives the second norm.

## D3. 15.5, add rows after the existing idioms

Counts are pieces containing the idiom, as a share of the 806,288 TRAIN
pieces `[AA004-STYLE]`. The readings come from cited exemplar pieces
(`key:aa index`) and are not measured.

| idiom | reads as | TRAIN pieces | exemplar |
|---|---|---|---|
| `⌒Y⌒` (`⌒Y`, `Y⌒`) | Scallop chain: lobes joined at a cusp. Use it for a cloud edge or a bushy contour. | 4.3 %, 3.5 % | `85cb726d…:33` |
| `γ⌒ヽ` (`γ⌒`) | Puff head opening upward and to the left. It pairs with `⌒ヽ`. | 2.4 % | `ea2e1523…:23` |
| `⌒¨¨⌒` (`⌒¨`) | Flattened lobe: a cloud base or bank top | 2.8 % | `18234250…:45` |
| `⌒'～⌒`, `'～` | Wisp tick: a lobe trailing into a wave (cloud fringe, smoke tail) | 4.3 % (`⌒'`), 3.5 % | `29bbdb91…:224` |
| `⌒ヾ`, `〃´⌒ヾ` | A lobe with a doubled tick | 3.0 %, 0.02 % | `29bbdb91…:224` |
| `）ヽ`, `⌒)ﾉ`, `⌒)イ⌒)` | A rising smoke curl, line only | not counted | `a3d73b49…:46` |
| `__,ノし`, `ノ(___` | Splash or flame tongue: an open contour fragment in a dot field | 1.9 % (`__,ノ`), 0.2 % (`ノし`) | `095894e5…:91` |
| `⌒ヽ〕iト` repeated on a diagonal | A motion-trail stamp | 2.6 % (`〕iト`; most occurrences are on character pages, reading not inspected) | `c3b8fbf7…:165` |

Mirror-table additions: `γ⌒`↔`⌒ヽ`, `⌒Y`↔`Y⌒`. Re-check the widths after
each swap.

## D4. 15.6, extend the shape-glyph sentence

> The corpus confirms this at scale `[AA004-STYLE]`. Only 1.16 % of
> Latin-letter occurrences in TRAIN are inside word runs. `r` (1.7 M),
> `j` (1.4 M), `Y` (0.64 M), `f` (0.40 M) and `z` (0.33 M) are outside the
> 4.1 whitelist, and they are stroke glyphs as often as `i` and `l` are.

## D5. 15.7, new numbered points after point 4

> 5. **Two norms, by subject.** Choose the norm from the subject, not from
>    the medium. `[AA004-STYLE]`, TRAIN-weighted:
>
>    | subject | line minimal | line + bounded tone | evidence |
>    |---|---|---|---|
>    | effects | 51 % | 20 % | — |
>    | maps | 58 % | 10 % | — |
>    | classic 2ch characters (モナー, ドクオ, なんJ) | 45–54 % | 10–17 % | — |
>    | work characters (82 % of TRAIN) | 29 % | 28 % | tone-dominant 16 %, filled 27 % |
>
>    - **Effects, maps and classic 2ch characters: line minimal.** Use
>      contour only, with an empty interior.
>    - **Work characters: line plus a regional tone material.** Draw the
>      contour first. Then fill the named regions (hair, cloth, shadow,
>      blush) with one declared material each: `.:.:`, `::::`, `///` or
>      `ﾆﾆ`.
>    - **Backgrounds:** strokes plus hatch. Hatch appears in 73 % of
>      background pieces.
> 6. **Ink share does not test the style.** A tone-filled piece is still
>    sparse, because tone glyphs are 3 px dots. On the AA-004 sample the
>    ink medians are:
>
>    | class | ink median |
>    |---|---|
>    | line minimal | 2.43 % |
>    | tone-dominant | 2.95 % |
>
>    Judge "empty interior" with envelope emptiness instead:
>
>    - **Envelope:** each text row from its first to its last glyph,
>      17 px tall.
>    - **Measure:** the share of envelope pixels with no ink inside a
>      5×5 px window.
>    - **Medians:** line minimal 0.71, line plus tone 0.68, tone-dominant
>      0.58, filled 0.54.
>    - **Rule:** an envelope emptiness below 0.6 means the interior is
>      filled.
> 7. **Tone ends in one of three ways.**
>    - **On a contour.** This is a closed band: 63 % of dot bands in TRAIN,
>      and 38 % on 爆発・煙.
>    - **On a density ramp:** `. . .·.·:·;`.
>    - **On a taper:** horizontal hatch thinning through `=` and `-` into a
>      stroke. The tapers `ﾆ=-` and `-=ﾆ` appear in 10.8 % and 9.7 % of
>      pieces, and `=-` in 28 %.
>
>    Each of the three is a defined edge under point 3.
> 8. **Spell dot tone with the whitespace law.** The commonest dot-tone
>    spelling interleaves single half spaces, `: : :`, and appears in
>    33.5 % of pieces. Next is `:.:.:`, in 18.3 %. Build tone fields with
>    the same full-space and half-space rules as offsets (15.4).

## D6. 15.7.4, append one sentence

> Some AA-004 records encode glyphs as numeric HTML character references:
> 2.5 % of TRAIN pieces, for example thin spaces `&#8198;` and blocks
> `&#9608;`. Decode the numeric references, and treat U+2000–U+200A as
> spacing, before you render or measure. Otherwise the reference text is
> measured as ink.

## D7. 15.8, falsifiers: add rows

| observation | verdict | rule |
|---|---|---|
| A piece is called line art because its ink share is low, but its envelope emptiness is below 0.6. | invalid judgement | 15.7.6 |
| A work-character piece fills a region with two different tone spellings, for example `.:.:` and `::::` on the same hair. | violation | 4.5, 15.7.5 |
| A tone band ends in open space with no contour, no ramp and no taper. | violation | 15.7.3, 15.7.7 |

## D8. 15.10, replace the first bullet and add two

> - The idioms are now counted across 38 subject strata `[AA004-STYLE]`.
>   Their readings outside smoke and cloud pages are still inferred from a
>   few cited exemplars. Examples are `⌒Y⌒` on hair and fur, and `〕iト`
>   on character pages.
> - AAHub also carries skill-6 Block and Filled styles that section 15
>   does not cover. Examples are Unicode block art (`█ ▇ ◢`), `■` block
>   lettering on the 汎用AA/文字 pages (61 % filled) and kanji-density
>   mosaics. Section 15 does not apply to them. Use section 6.
> - `[AA004-STYLE]` classes are rule thresholds, not human labels. The
>   line-minimal share moves between 13 % and 50 % across the stated
>   threshold grid.

## D9. Section 6 taxonomy row "Line + screen tone": amend the subject-fit cell

> smoke, explosions, lit surfaces; on AAHub also the hair, cloth and shadow
> regions of character art (`[AA004-STYLE]`: 28 % of work-character pieces
> are line plus bounded tone)
