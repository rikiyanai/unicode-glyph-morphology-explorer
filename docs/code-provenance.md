# Code provenance

The standalone implementation was extracted from private source repository
`rikiyanai/asciicker-Y9-2` at commit
`242ecba44f76ed1120dadf06653fd6de47017b7f`.

| Packaged path | Source SHA-256 | Packaged SHA-256 | Status |
| --- | --- | --- | --- |
| `scripts/compile_glyph_manifest.py` | `6fd8c06dd911b424b3bc256b491c0a027e01c92a9c567cd7dc804f0ff2c3d47e` | same | byte-identical |
| `scripts/fl4482_font_chain.py` | `dddbc999ad36f9bbf973b32cc65ebde304c396d1966675462a9f9eb625df04b0` | same | byte-identical |
| `scripts/generate_glyph_shape_catalog.py` | `b5f0c58ac22cfe31797a9e37951b8deea557dd9bc09612a0e8f9cc759abffff2` | same | byte-identical |
| `scripts/glyph_audit.py` | `2dfd6fc7eabe921ef3dff57b04254b93bdbd0dfa4f2023a01cda176e6ffc6071` | same | byte-identical |
| `scripts/glyph_families_viewer.py` | `0ad3f63736313cd02e2b0f53c03a0b7ed00cca22ae2d8bf057696c9c52b479b0` | `e11f0cf1784c062811abdd3b1bdc1d521a4b391dcfd786fc063ccaa8c8ce73ee` | deliberately derived |
| `scripts/glyph_features.py` | `ed19cc976f140cf4bc6d15c2bad5e1575ea2dd998346441ac7fdd1d08c2462f6` | same | byte-identical |
| `scripts/glyph_morphology_browser.py` | `8eadca1a559952b90cc1935db038238cc1496fd973c6fad0669a3c3fd97e2bdc` | same | byte-identical |
| `scripts/glyph_skeleton.py` | `7e225890f4d24038b84c64dfd67e3a226f82434a6105c4b888fbd0bf16208a86` | same | byte-identical |
| `docs/research/ascii/glyph_audit/saved_families.jsonl` | `d33bb598d122b3b073186b9ca6fc0dc69148d49578a12fb04a4f54e10ef1aa11` | same | byte-identical |

The only code delta is the family viewer's read-only hardening. The source
repository version bound `s` to appending a selected family to the tracked
`saved_families.jsonl` registry. The standalone removes that key handler, file
append, save-status state, and save help text. It does not replace morphology,
family discovery, rendering, navigation, animation, or filtering logic.

Font byte identities and licenses are recorded separately in
[font-provenance.md](font-provenance.md).
