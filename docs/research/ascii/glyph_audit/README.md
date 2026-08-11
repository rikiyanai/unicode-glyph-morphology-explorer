# Glyph Audit Review State

This directory holds durable, human-authored glyph-family review state.

`saved_families.jsonl` is written by `scripts/glyph_families_viewer.py` when the
operator presses `s`. Each JSONL row records one reviewed family:

```json
{"mode":"spin","size":4,"block":"Arrows","cps":[8592,8593,8594,8595],"chars":"<glyph chars>"}
```

Regenerable glyph feature caches stay under `.run/glyph_audit/`. Manual review
choices do not: they are tracked here so cache cleanup cannot erase them.
