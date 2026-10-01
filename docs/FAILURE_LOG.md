# Failure Log

## 2026-09-08 — D42.8 review sync kept standalone combination browser broad

- The Asciicker FL-4512 D42.8 review corrected three claims that matter to this
  standalone viewer: the Stone Story tutorial alphabet is 25 basic marks plus 4
  extended marks, not a 33-glyph set; Asciicker runtime `combo_hits` counts
  candidate transition evaluations, not selected/rendered combination usage; and
  viewer-facing Unicode run review should stay separate from runtime proof
  counters.
- The standalone package already kept `COMBOS` as the full useful-combination
  review surface: authored seeds, mined tutorial-plate runs, measured seam pairs,
  and generated Unicode/Kana/CJK/Arabic run buckets. The sync records that
  contract and adds a regression so `--mode combo --dump` continues to load the
  broad surface instead of only the nine authored rows.
- A follow-up review of the D42.10 Asciicker handoff found no standalone source
  sync required: the six new Asciicker commits changed prototype runtime
  contour-selection code, runtime proof media, and runtime pack-v2 font routing.
  This repository owns visual glyph exploration, so it now commits only the
  missing standalone artifact: `docs/artifacts/glyph_combo_gallery.html`, a
  static snapshot of the generated combo gallery, plus its checksum.
- Highest supported stage remains **Verified** for the standalone viewer:
  `.run/` caches are local rebuild artifacts, the committed gallery is a review
  snapshot, and runtime contour rendering proof remains in the Asciicker
  repository.

## 2026-08-31 — public provenance and family-registry reconciliation

- **Observed mismatch:** After fast-forwarding local `main` to remote `1307328`,
  the contract test still required source/package SHA-256 rows that the
  public-cleanup commit intentionally removed from `docs/code-provenance.md`.
- **Fix:** The test now checks that every packaged owner, the original extraction
  revision, and the read-only hardening statement are documented, without
  reintroducing the removed public hash table.
- **Registry evidence:** The current Y9-2 source checkout at observed revision
  `54f0c8b2c256fd41d6dcb9e1b369d8b41235e31e` contained 15 additional dirty-tree
  rows beyond the standalone's 81 nonblank rows. They were copied into the
  standalone registry with the source-artifact caveat; twelve are `cycle` rows
  and three are retained `stroke` evidence outside the current viewer axes.
- **Verification:** The registry parses as 96 nonblank JSONL rows, its 15-row
  tail matches the observed source artifact, and `python3 -m unittest discover
  -s tests -v` passes all eight tests.

## P0C-02 · 2026-08-11 — standalone extraction created

- The source checkout was treated as read-only.
- Extracted the morphology browser, helper chain, pinned eight-font chain, and
  three contract tests into a private repository.
- Font hashes were preserved, but the license package and headed TUI recording
  remained incomplete. Public visibility stayed blocked.

## P0C-02 · 2026-08-12 — font licenses and real user path added

- Added embedded copyright/license metadata for all eight pinned font files and
  the applicable OFL, Apache, Arphic, and Unifont license texts.
- Added a real terminal recording linked from the README.
- Public visibility remains a separate user approval; private execution and
  attribution packaging are verified.

## P0C-02 · 2026-08-12 — acceptance re-audit retained both TUI recordings

- Intended product: interactive Unicode morphology and discovered-family
  browsing with visible navigation and no tracked save authority.
- Direct execution, source inspection, and frame review agree with that scope.
  Both recordings show the real curses interfaces and visible state changes.
- Highest supported stage remains **Verified, not Accepted**. Riki's personal
  judgment and any visibility decision remain open.

## P0C-02 · 2026-08-12 — all-repository source re-audit found missing code provenance

- The source-identity check compared the packaged implementation with Y9-2
  commit `242ecba44f76ed1120dadf06653fd6de47017b7f`. The morphology browser,
  glyph feature/skeleton helpers, font owner, and saved-family registry remain
  byte-identical to that commit.
- `glyph_families_viewer.py` is intentionally derived: the standalone deletes
  the source repository's `s` key, append-to-JSON implementation, save status,
  and tracked-save help text. That is the correct read-only product boundary,
  and tests exercise it, but only font provenance was documented. No file
  recorded the original code hash, packaged hash, or exact hardening delta.
- Therefore the TUI remains implemented and tested, but the code-attribution
  trail is incomplete until a code-provenance document records the source
  commit, byte identities, and the one deliberate derived module.

## P0C-02 · 2026-08-12 — code provenance and derived-viewer gate added

- Added a code-provenance table for all eight packaged Python owners and the
  saved-family registry. Seven source files and the registry are byte-identical
  to source commit `242ecba`; the table records their exact hashes.
- Recorded both hashes for the derived family viewer and the complete
  standalone delta: only the tracked-save key, file append, save status, and
  save help are removed. Morphology/family behavior is not reimplemented.
- Added a regression that pins the packaged viewer hash and requires the source
  hash and read-only-hardening rationale in the provenance document.

## P0C-02 · 2026-08-12 — bare-interpreter test invocation lacked declared dependencies

- A re-audit invocation used Homebrew Python 3.11 directly without first
  installing `requirements.txt`. Three of seven tests errored during import
  because `fontTools` was unavailable; that run supplied no morphology-product
  verdict.
- The successor verification uses a clean temporary Python 3.11 environment
  populated from the repository's declared requirements. Only that prepared
  run may support the final test claim.

## P0C-02 · 2026-08-12 — first provenance regression left eight rows documentary-only

- Normal-subagent review confirmed all nine documented source hashes and the
  derived viewer delta, but found that the first regression mechanically pinned
  only `glyph_families_viewer.py`. The other seven scripts and saved-family
  registry could drift while their provenance table remained stale.
- The successor gate hashes all nine packaged owners and requires every source
  identity in the provenance document. The derived viewer still carries its
  distinct packaged hash and explicit read-only-hardening rationale.

## P0C-02 · 2026-08-12 — README front page carried redundant visibility wording

- The README still opened with `Private standalone` and later repeated that the
  repository is private. That metadata is true repository state, but it is not
  useful front-page product copy and distracts from the two real TUI recordings.
- The successor removes that wording from README prose while keeping font
  license, source-code provenance, and exact recording evidence links intact.

## P0C-02 · 2026-09-08 — Godot profile boundary was under-documented

- Review of the D42.10 Asciicker handoff found that this standalone package
  could be read as a direct runtime proof surface, even though its combo/seam
  data is measured on the pinned 8×16 half-width / 16×16 full-width terminal
  profile.
- Current Asciicker Godot native-terminal work targets a taller profile: 16×32
  half-width cells, with full-width glyphs retaining intact 32×32 masks across
  two adjacent tall cells. Orthographic and perspective rendering also remain
  separate runtime proof conditions.
- README and code provenance now state that standalone families, seam gaps,
  D_SM radii, altitude bands, and run offsets are exploration evidence only
  until rebased in cell units for the Godot profile and checked per projection.

## 2026-09-26 — ascii-art-authoring skill has no route for proportional Shift_JIS art

- **Observed gap:** the `ascii-art-authoring` skill (canonical copy:
  `claude-skills-private` `c8c39d5`) excludes proportional-font art outright
  (`SKILL.md:23-24`). Its fixed-grid rules are cell aspect, cell anisotropy,
  empty-cell anti-aliasing, and the 12-letter whitelist. Its combination data
  is the nine Stone Story rows in
  `assets/glyphs/authored/glyph_combinations.v1.json`. None of these covers
  the outline-first Shift_JIS idioms (`(⌒ ⌒ヽ _ノ ゝ__ノ ／￣ ＼＿ -―-`)
  seen on the AAHub page 爆発・煙
  (<https://aahub.org/mlt/a60392576bd5eefca3ed22d55606b85f>).
- **Measured, 180 posts, Saitamaar 16 px:**
  - Only 14.7 % of non-space glyphs have a grid-exact advance, and no post
    reaches 90 %.
  - 85 % of indents are off the 8 px grid.
  - The page has zero adjacent half-width spaces (the BBS whitespace-collapse
    rule).
  - Re-flowing the text onto an 8/16 px grid keeps 12.5 % of vertically
    aligned pairs. Snapping to 8 px columns stacks 59 % of glyphs into
    shared columns.
  - 64.5 % of non-space glyphs are fine-dot tone, yet median ink is 2.4 %.
  - The page is bimodal: 30 posts are outline-dominant and 32 are
    tone-dominant.
- **Consequences:**
  - The page is a valid *style* reference for Xu, FL-4512, and unicasso.
  - It is a valid *raster-level* evaluation set only for its outline subset,
    rendered in its own font.
  - It is never valid as a text-cell ground truth, and a fixed-width glyph
    subset is not a viable restriction.
- The glyph repository's `glyph_combinations.v1.json` is a derived copy,
  byte-identical to Y9-2 `6372a431f`. Y9-2 HEAD differs only in its `owner`
  field. The Y9-2 project copy of the skill is a stale fork of the canonical
  copy.
- **Durable owner:** `docs/research/ascii/sjis_aa_skill_audit/` holds the
  audit (`README.md`), the measurement script, and its byte-stable JSON
  output. The input set is identified by SHA-256; no art text is
  redistributed beyond two three-line excerpts cited to the AAHub URL.
- **Stage:** audit only. No skill file, combination data, or viewer code was
  changed. The prioritised skill changes (P1–P7) are proposals awaiting an
  owner decision.

### Owner decision · 2026-09-26 — one canonical skill copy

- **User directive:** the ascii-art-authoring skill must exist as a single
  tracked copy in the private Claude skills repository. Every other agent
  harness (Codex, generic agents, project checkouts) reaches it by symlink,
  never by a copied fork.
- **Measured starting state:**
  - The Codex and generic-agent skill roots are already whole-directory
    symlinks to the Claude skills root. They resolve to the canonical copy,
    and a byte comparison found no difference.
  - The only fork is the Y9-2 project copy under `.claude/skills/`. It is a
    tracked, stale `SKILL.md` without `references/`. Because Claude loads
    project skills alongside global ones, it can shadow the canonical copy
    inside Y9-2.
- **Action:** replace the Y9-2 fork with a tracked symlink to the canonical
  skill directory. Y9-2's `.gitignore` re-include must drop its trailing
  slash so that the symlink is tracked rather than ignored. Paths in Y9-2
  documents that cite `.claude/skills/ascii-art-authoring/SKILL.md` still
  resolve, but their historical line numbers refer to the old fork.
- **Falsifier:**
  - after the change, Y9-2's `.claude/skills/ascii-art-authoring` is a
    symlink;
  - `git ls-files -s` records mode 120000 for it;
  - reading its `SKILL.md` gives bytes identical to the canonical copy.
- **P1–P7 remain proposals.** Any accepted edit lands only in the canonical
  copy.

### Operator correction · 2026-09-27 — the audit misframed grid principles as fixed-grid-only

- **Contradiction:** the audit (gap 2) listed cell aspect, cell anisotropy,
  anti-aliasing by empty cells and mirroring as rules that "do not hold" for
  proportional Shift_JIS art. The operator rejected this, and the art
  supports the rejection:
  - Stroke glyphs on that page are still anisotropic marks inside a
    line-height × advance box.
  - Edges are still softened by leaving tone and space rather than filling.
  - Symmetric forms are still mirrored with paired glyphs (`／`/`＼`, `（`/`）`,
    `ヽ`/`ﾉ`).
  - What changes is the placement lattice: per-glyph advances and
    half/full-width space mixes instead of one uniform cell.
- **Error class:** the audit took a medium-specific mechanism (a uniform
  cell grid) for the principle it implements (glyph shape, orientation and
  negative space carrying form). The parent session relayed the claim
  without checking it.
- **Decision:** the skill keeps one set of core authoring principles, stated
  independently of the medium. It gains an addendum for proportional fonts
  and typesetting. The addendum covers:
  - per-glyph advance lattices (e.g. MS PGothic / Saitamaar units);
  - the space-collapse law (no adjacent U+0020, no leading U+0020);
  - half/full-width space mixing for sub-cell placement;
  - line pitch;
  - Shift_JIS stroke idioms (`⌒ヽ`, `_ノ`, `ゝ__ノ`, `／￣`/`￣＼`, `-―-`);
  - using `i`, `l` and `|` as stroke shapes rather than letters.

  The audit's P1 ("scoped route plus new §15") is re-scoped to this
  structure. Nothing in the core sections is removed or restated as
  fixed-grid-only.
- **Cross-repo implication:** the screenshot-to-text converter decodes the
  same medium. Its proportional decoder already enforces the space-collapse
  law and the advance lattice. The idioms above are candidate multi-glyph
  priors, recorded in the converter's failure log.
- **Stage:** decision logged. No skill edit yet; the edit lands only in the
  canonical copy in the private skills repository.

### 2026-09-27 — corpus-wide Shift_JIS combination extraction, viewable as `--mode sjis`

- **Request:** operator asked for combination and pattern extraction from the
  AAHub corpus, guided by ascii-art-authoring section 15, logged here and
  viewable in the glyph viewer. Before this entry the only Shift_JIS
  measurement was the one-page `bakuhatsu_kemuri_stats.json`, and the
  viewer did not load it.
- **Producer:** `scripts/sjis_corpus_combos.py` (new). It reads Git blobs of
  the private ascii-art-archive at `3687cc5` (AA-003). Slugs come from the
  converter split `data/aahub_split.json` (sha256 `d61d856f…a8d500`),
  training partition only, and held-out slugs are never opened. Coverage:
  114 slugs, 23,363 pages, 457,065 lines, 86 s on one core. Rendering uses
  Saitamaar 16 px on a 17 px pitch (font sha256 `8f8c9b6e…35890`).
- **Output (durable):** `assets/glyphs/corpus/aahub_aa003_train.sjis_combos.v1.json`
  (sha256 `61b0537d…58f8258`, 996,272 bytes). It holds:
  - top-300 counts for idioms, bigrams, trigrams and stacks (each also as an
    outline-only list), plus bands and space spellings;
  - per-slug top bigrams and page tags;
  - 435 rendered entries (36 idioms, 120 bigrams, 120 trigrams, 120 stacks,
    39 bands), each with its 15.5 mirror.

  One-glyph repeats (`//`, `＿＿`, `|/|`) stay counted but are not rendered
  as combinations.
- **Viewer:** `glyph_families_viewer.py --mode sjis` (new axis, 435
  families), also included in `--mode combo` (1,718 families). Test:
  `scripts/tests/test_sjis_corpus_combos.py` (6 pass).
- **Findings (measured):**
  - The 15.5 idioms are not specific to smoke pages. `⌒ヽ` appears
    6,788× on 3,904 pages in 112/114 slugs. `／￣` appears 7,222× (112
    slugs), `＼＿` 7,165×, `_ノ` 6,474× (113), `｀ヽ` 14,348× (113), `彡`
    14,752× (112), `从` 5,619× (108), `／￣＼` 676× and `＼＿／` 540×.
    `ゝ__ノ` is rare: 39× in 10 slugs.
  - Whitespace law (15.4): near zero, not zero. There are 147 adjacent
    U+0020 pairs and 78 line-leading U+0020 in 457,065 lines (0.03% /
    0.02%). The skill's "zero violations" is from one page of 3,214 lines.
  - Most common interior space spellings: `F h` 15.5%, `FF` 12.1%,
    `FF h` 7.2%, `FFF` 6.5%, `h F h` 4.5%.
  - Tone dominates raw counts: `::` makes up 2.0 M of the bigrams. The
    outline-only lists and bands separate the two, as 15.7 separates
    outline from declared tone.
  - Page tags: 6,542 outline, 5,728 tone, 11,093 mixed.
  - Top outline stacks with distinct glyphs: `l` over `|`, `i` over `|`,
    `｜` over `|`, and `￣` over `＿` (the 4.2 occlusion complement,
    5,949× at 0 px).
  - `ﾆ` (140k), `二` (103k) and `ニ` are among the most frequent glyphs and
    are used as hatching. They were added to the stroke set (15.6).
- **Proposals, not applied:**
  - (a) Skill 15.4.1 and 15.5 could cite these corpus counts in place of
    the one-page numbers. Edits land only in the canonical skill copy.
  - (b) The converter's bigram/stroke-idiom prior hypothesis (converter
    FL, 2026-09-27 note item 2) can be built from the same training-only
    counts. The converter remains the owner of that prior.
- **Stage:** Implemented and Executed. The dataset and viewer axis are
  Verified by tests and `--dump`. There is no interactive TTY review by
  the operator yet, so not Accepted.

### 2026-09-30 — Shift_JIS combinations over the AA-004 MLT crawl (TRAIN keys), `--corpus aa004`

- **Request:** measure the same section-15 combinations over the AA-004
  AAHub MLT crawl, train partition only, and make the result viewable.
  Comparison is counts only; style analysis belongs to another lane.
- **Producer:** `scripts/sjis_corpus_combos.py --corpus aa004`. The counting
  loop moved into an `Accumulator` class that is fed one page at a time;
  per-slug bigrams are reduced to their top 8 when the slug ends. AA-003
  stays the default mode.
- **Command:**
  `python3 scripts/sjis_corpus_combos.py ~/Projects/ascii-art-archive
  ~/Projects/screenshot-of-ascii-art-to-txt-converter/data/aahub_mlt_split.json
  ~/Projects/screenshot-of-ascii-art-to-txt-converter/fonts/Saitamaar-Regular.ttf
  --corpus aa004 --out assets/glyphs/corpus/aahub_aa004_train.sjis_combos.v1.json`
- **Inputs:**
  - Archive: Git blobs at `f498eb30678c753a2867f0a97ecc22561f54543e`, read
    from `collections/aahub-mlt/index.jsonl` and `<kk>/<key>.json.gz`.
  - `index.jsonl` sha256 `c7a35081…4d01f9`. The script checks this hash
    against the split's `index_sha256` and stops on a mismatch.
  - Split: `aahub_mlt_split.json` sha256 `983848da…b52347`, `train_keys`
    only. The script checks that train and held-out are disjoint, that
    together they make up the whole index, and that the per-key piece
    counts match the index. Held-out keys are never read.
  - Font: the converter's `fonts/Saitamaar-Regular.ttf` (sha256
    `8f8c9b6e…35890`), the same file that rendered the AA-003 dataset. It
    was kept so that the two datasets are comparable and AA-003 stays byte
    for byte reproducible.
    - The archive's `collections/aahub/Saitamaar.ttf` (sha256
      `592bf6be…3a28`, FontForge build) is the font that reproduces AAHub's
      PNGs pixel for pixel. The coordinator verified this.
    - `Saitamaar-Regular.ttf` is a ttfautohint build of the same design. It
      has the same cmap (10,125 code points) and the same advances. 130
      glyphs, all rare accented Latin or Cyrillic, render differently, by at
      most 12 px at 16 px bilevel (coordinator measurement).
    - With the archive font, the AA-003 rerun differs from the tracked file
      in `font_sha256` and in some rendered rows. The run summary was
      identical: pages, lines, page tags and whitespace law. The full diff
      of counts was not checked.
- **Defect found and fixed in this entry (rework 1):**
  - The first AA-004 output (sha256 `93b7379d…6daa`, never committed)
    counted pieces exactly as stored.
  - About 3 % of stored pieces keep numeric HTML character references:
    `&#8201;` thin space, `&#8198;`, `&#8202;`, `&#9617;` ░, `&#x2588;` █,
    `&#65374;` ～, and others. AAHub's viewer decodes these references, and
    AA-003's text contains the decoded characters: there is no literal `&#`
    in any of the 32,950 AA-003 files (coordinator check).
  - As a result, `&#` appeared as outline bigram rank 29 (795,260 times),
    `&` was counted 799,326 times and `#` 850,794 times, and `;` was
    inflated.
  - Fix: the aa004 mode now decodes every piece with
    `piece_text(v) = html.unescape(v)` before any counting or rendering.
    This is the converter's piece definition (`scripts/mlt_pairs.py
    piece_text`, converter `4c194a3`).
  - A new test checks that a piece containing `&#8201;` counts U+2009 and
    never counts `&`, `#` or `;`. A dataset test checks that no idiom or
    bigram contains `&#`.
- **Output (durable):** `assets/glyphs/corpus/aahub_aa004_train.sjis_combos.v1.json`
  - sha256 `58ad158ab82a2c622509e3df3e3e5448eb46c1ce6a8f7e40f907b5ea2c8965c8`,
    5,419,148 bytes.
  - `input_set_sha256` `2b185251…21789` over the 10,559 gz blobs. This value
    is unchanged from the first output: the blobs are the same, and only
    the decoding changed.
  - The output also has a new `piece_text` field.
  - Same schema as AA-003, with these differences:
    - `manifest_sha256` is replaced by `index_sha256`.
    - Added fields: `corpus`, `collection`, `split_schema`, `units`,
      `unit_labels`, `mlt_pages`, `pieces`, `single_line_pieces` and
      `coverage`.
    - Bigram and stack entries carry `pages` and `slugs`: the number of
      distinct pages and slugs that contain the combination.
  - Units: slug = MLT page (index key); page = one `aa[]` piece. Section
    headers are included: 98,757 pieces have one line.
- **Counts:** 10,559 MLT pages, 905,073 pieces, 18,743,835 lines,
  1,007,823,607 glyphs (7,950 distinct). Held-out keys excluded: 3,422.
  Page tags: 213,639 outline, 265,579 tone, 425,794 mixed, 61 empty.
  - After decoding, `&` is not in the top 300 glyphs, and `#` is 55,540
    (2.96 per 1,000 lines; AA-003 6.31).
  - Decoded characters that now appear: U+2009 47,926, U+2006 67,280,
    U+200A 37,445, `░` 78,631, `█` 101,415.
  - A scan of the idiom, bigram, trigram and stack lists and of the
    rendered keys found no `&`, `&#` or digit-`;` artifact.
  Whitespace law: 22,151 adjacent U+0020 pairs and 11,321 line-leading
  U+0020. The top space spellings match AA-003 within 0.6 points: `F h`
  15.7 %, `FF` 12.3 %, `FF h` 7.8 %, `FFF` 6.6 %, `h F h` 4.8 %.
- **Runtime:** the corrected run took 3,707 s wall time (3,089 s user) in a
  single process, with peak RSS 523 MB. The first run took 4,383 s.
- **Checks:**
  - AA-003 is byte-identical after the refactor and after the rework. The
    command was rerun into a scratch path with the pinned font; the result
    had sha256 `61b0537d…58f8258` and `cmp` reported no difference from the
    tracked file.
  - The run reported 905,073 pieces, which equals the split's train piece
    count.
  - `python3 -m pytest scripts/tests/test_sjis_corpus_combos.py -q`:
    16 passed. The new tests cover the AA-004 identities and counts, the
    AA-003 key superset, coverage bounds, the absence of undecoded
    references, `piece_text` decoding, the viewer `--corpus aa004` dump,
    the compare script, and Accumulator coverage with a font-free stub.
  - `--mode sjis --corpus aa004 --dump` gave 435 families.
    `--mode combo --corpus aa004 --dump` gave 1,718.
- **Viewer:** `./run-families.sh --mode sjis --corpus aa004`. `--corpus`
  also applies to `--mode combo`. The default is `aa003`, and the default
  output is unchanged.
- **Comparison:** `scripts/sjis_corpus_compare.py A.json B.json` (new) prints
  count, rate per 1,000 lines, pages/slugs and rank per file.
  - AA-003 has no bigram or stack coverage in its tracked file. For this
    comparison, AA-003 was rerun with `--coverage` into a scratch file
    (sha256 `a5d285ae…70c34`). Its counts are identical to the tracked
    file.
  - In the tables, AA-003 "slugs" are its 114 slugs and AA-004 "slugs" are
    its 10,559 MLT pages.
  - Rows show n (rate per 1,000 lines; pages / slugs).
  - **Idioms (top 8 by AA-004 rank; rank in brackets).**

    | idiom | AA-004 | AA-003 |
    |---|---|---|
    | `::` [1/1] | 53,211,301 (2,838.9; 549,634 / 9,884) | 1,095,013 (2,395.8; 12,076 / 113) |
    | `:.` [2/2] | 18,521,357 (988.1; 422,692 / 9,515) | 359,111 (785.7; 8,772 / 113) |
    | `.:` [3/3] | 17,708,768 (944.8; 395,763 / 9,422) | 351,710 (769.5; 8,323 / 113) |
    | `;;` [4/4] | 3,987,537 (212.7; 140,976 / 7,824) | 119,323 (261.1; 4,307 / 113) |
    | `,,` [5/5] | 1,557,356 (83.1; 301,378 / 9,005) | 57,030 (124.8; 8,819 / 113) |
    | `_,` [6/6] | 1,282,616 (68.4; 427,142 / 9,782) | 34,116 (74.6; 10,479 / 113) |
    | `'´` [7/7] | 724,745 (38.7; 271,472 / 8,972) | 16,445 (36.0; 6,055 / 113) |
    | `｀ヽ` [8/9] | 689,829 (36.8; 303,001 / 9,140) | 14,348 (31.4; 6,578 / 113) |

    Outline idioms in AA-004:
    - `⌒ヽ`: 289,610 (181,747 pieces / 8,556 pages)
    - `／￣`: 309,005 (8,492 pages)
    - `＼＿`: 343,140 (8,430 pages)
    - `_ノ`: 294,110 (8,723 pages)
    - `／￣＼`: 26,787 (4,627 pages)
    - `＼＿／`: 21,076 (4,376 pages)
    - `ゝ__ノ`: 755 (471 pages)

    Largest idiom rank move (AA-003→AA-004): `从` 17→11. All other 35
    idioms move by at most 2 ranks, for example `⌒ヽ` 14→16 and `／￣`
    12→14.
  - **Outline bigrams (top 8 by AA-004 rank).**

    | bigram | AA-004 | AA-003 |
    |---|---|---|
    | `//` [1/1] | 8,428,910 (449.7; 393,770 / 9,649) | 176,126 (385.3; 8,327 / 113) |
    | `i:` [2/5] | 6,931,536 (369.8; 274,487 / 8,751) | 106,623 (233.3; 4,963 / 112) |
    | `:i` [3/6] | 6,727,185 (358.9; 276,437 / 8,787) | 103,251 (225.9; 4,893 / 112) |
    | `ﾆﾆ` [4/9] | 4,470,125 (238.5; 196,151 / 7,956) | 69,928 (153.0; 4,422 / 112) |
    | `__` [5/4] | 4,008,881 (213.9; 619,124 / 10,225) | 110,194 (241.1; 15,683 / 113) |
    | `ニニ` [6/13] | 3,856,325 (205.7; 130,583 / 7,317) | 54,753 (119.8; 2,888 / 109) |
    | `\|:` [7/8] | 3,632,581 (193.8; 406,921 / 9,472) | 77,190 (168.9; 7,807 / 113) |
    | `/:` [8/14] | 3,358,722 (179.2; 468,700 / 9,596) | 52,935 (115.8; 8,317 / 112) |

    `＿＿` falls from 2 to 11 and `￣￣` from 3 to 12. Their rates fall from
    267.4 and 249.6 to 135.4 and 131.5 per 1,000 lines.

    The top 8 outline bigrams are unchanged by decoding.

    Largest moves within the top 50 of either list:
    - Rose: `ニﾆ` 83→37, `:{` 68→46, `{:` 53→34, `}:` 58→39, `/|` 67→50,
      `:!` 64→49.
    - Fell: `|＿` 37→119, `_|` 35→83, `|_` 39→84, `――` 23→42, `-'` 50→68,
      `──` 18→35.
  - **Outline stacks (top 8 by AA-004 rank).**

    | stack | AA-004 | AA-003 |
    |---|---|---|
    | `\|` over `\|` +0 [1/1] | 7,578,106 (404.3; 555,707 / 10,072) | 314,066 (687.1; 13,994 / 114) |
    | `/` over `/` +0 [2/2] | 2,200,912 (117.4; 210,087 / 8,777) | 52,788 (115.5; 4,544 / 113) |
    | `i` over `i` +0 [3/3] | 1,756,323 (93.7; 147,943 / 7,939) | 39,877 (87.3; 3,210 / 112) |
    | `\|` over `\|` +1 [4/5] | 955,477 (51.0; 270,602 / 9,064) | 24,976 (54.6; 6,108 / 113) |
    | `/` over `/` +1 [5/7] | 941,424 (50.2; 169,369 / 8,456) | 18,638 (40.8; 3,435 / 111) |
    | `l` over `l` +0 [6/4] | 930,832 (49.7; 169,572 / 8,304) | 29,379 (64.3; 3,861 / 113) |
    | `/` over `/` −1 [7/8] | 853,038 (45.5; 138,703 / 8,274) | 16,684 (36.5; 2,807 / 112) |
    | `i` over `i` +1 [8/13] | 847,744 (45.2; 107,269 / 7,518) | 13,603 (29.8; 2,046 / 111) |

    These stack counts are 0.2–0.6 % higher than in the first, undecoded
    output. The cause was not measured.

    Largest moves within the top 50 of either list:
    - Rose: `ニ` over `ニ` −1 px 106→47 and +1 px 88→48; `ﾆ` over `ﾆ`
      +2 px 50→27, −3 px 61→40, −1 px 58→38, +3 px 54→36.
    - Fell: `□` over `□` 46→280, `￣` over `＿` +0 44→164, `＿` over `＿`
      45→144, `┃` over `┃` 47→141, `│` over `│` 26→84, `=` over `=` 42→77.
  - The full tables can be reproduced by running
    `python3 scripts/sjis_corpus_compare.py <aa003 --coverage output>
    assets/glyphs/corpus/aahub_aa004_train.sjis_combos.v1.json --top 8 --moves 6`.
    The output sha256 is `88e6e7a1…ee06`.
- **Stage:** Implemented and Executed. The dataset, the viewer selection and
  the comparison are Verified by tests and `--dump`. The operator has not
  reviewed them in an interactive TTY, so not Accepted. The Y9-2 compiler
  still pins only the AA-003 file.
