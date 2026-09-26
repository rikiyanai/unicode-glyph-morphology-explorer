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
