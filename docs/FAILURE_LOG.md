# Failure Log

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
