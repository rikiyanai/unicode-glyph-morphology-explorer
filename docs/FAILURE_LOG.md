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
- Highest supported stage remains **Verified** for the standalone viewer:
  generated `.run/` caches are local review artifacts, while runtime contour
  rendering proof remains in the Asciicker repository.

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
