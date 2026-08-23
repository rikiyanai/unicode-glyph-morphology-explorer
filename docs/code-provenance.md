# Code provenance

This standalone implementation was extracted from `rikiyanai/asciicker-Y9-2` at commit `242ecba44f76ed1120dadf06653fd6de47017b7f`.

The repository packages the Unicode morphology browser, feature and family discovery tools, topology helpers, manifest/catalog utilities, and the selected saved-family registry used by the standalone viewers.

The family viewer differs from its source copy in one intentional behavior: this repository removes the key that appended a selected family to the tracked `saved_families.jsonl` registry. The standalone viewer therefore remains read-only. Rendering, navigation, animation, filtering, and family discovery remain available.

Public-facing wording and diagnostics may also differ from the source extraction so they describe behavior directly instead of carrying private development labels. Those wording changes do not change the font identities or the morphology algorithms.

Font identities and licenses are recorded separately in [font-provenance.md](font-provenance.md).
