from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class MorphologyContract(unittest.TestCase):
    def test_pinned_font_chain_is_complete(self) -> None:
        from fl4482_font_chain import discover_font_chain

        chain = discover_font_chain()
        self.assertEqual(len(chain), 8)
        self.assertTrue(all(path.is_file() for path in chain))

    def test_block_enumeration_includes_geometric_shapes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "glyph_morphology_browser.py"),
                "--list-blocks",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn("Geometric Shapes", result.stdout)

    def test_browser_scores_a_geometric_shape(self) -> None:
        from glyph_morphology_browser import GlyphScorer

        entry = GlyphScorer().score(0x25A0)
        self.assertEqual(entry.cp, 0x25A0)
        self.assertFalse(entry.blank)
        self.assertTrue(entry.metrics)

    def test_font_license_package_covers_every_pinned_font(self) -> None:
        metadata_path = ROOT / "docs" / "licenses" / "FONT-METADATA.json"
        metadata = json.loads(metadata_path.read_text())
        self.assertEqual(set(metadata), {path.name for path in (ROOT / "assets" / "fonts").iterdir()})
        for name, row in metadata.items():
            font = ROOT / "assets" / "fonts" / name
            self.assertEqual(hashlib.sha256(font.read_bytes()).hexdigest(), row["sha256"])
            self.assertTrue(row["copyright"])
            self.assertTrue(row["license_description"])
        for license_name in (
            "OFL-1.1.txt",
            "APACHE-2.0.txt",
            "ARPHIC-PUBLIC-LICENSE.txt",
            "UNIFONT-LICENSE.txt",
        ):
            self.assertGreater((ROOT / "docs" / "licenses" / license_name).stat().st_size, 500)

    def test_family_viewer_has_no_tracked_save_surface(self) -> None:
        source = (ROOT / "scripts" / "glyph_families_viewer.py").read_text()
        self.assertNotIn('elif ch == ord("s")', source)
        self.assertNotIn("open(saved_path", source)
        self.assertIn("standalone viewer is read-only", source)

    def test_saved_registry_retains_source_observed_family_rows(self) -> None:
        rows = [
            json.loads(line)
            for line in (ROOT / "docs/research/ascii/glyph_audit/saved_families.jsonl")
            .read_text()
            .splitlines()
            if line.strip()
        ]
        self.assertEqual(len(rows), 96)
        additions = rows[-15:]
        self.assertEqual(sum(row["mode"] == "cycle" for row in additions), 12)
        self.assertEqual(sum(row["mode"] == "stroke" for row in additions), 3)
        self.assertEqual(
            {row["block"] for row in additions},
            {
                "Arabic",
                "Basic Latin",
                "CJK Strokes",
                "Cherokee",
                "Greek Extended",
                "Katakana",
                "Latin Extended-B",
                "Latin-1 Supplement",
                "Mathematical Operators",
            },
        )

    def test_packaged_owners_have_code_provenance(self) -> None:
        expected = (
            "scripts/compile_glyph_manifest.py",
            "scripts/fl4482_font_chain.py",
            "scripts/generate_glyph_shape_catalog.py",
            "scripts/glyph_audit.py",
            "scripts/glyph_combo_candidates.py",
            "scripts/glyph_families_viewer.py",
            "scripts/glyph_features.py",
            "scripts/glyph_morphology_browser.py",
            "scripts/glyph_skeleton.py",
            "assets/glyphs/authored/glyph_combinations.v1.json",
            "docs/research/ascii/glyph_audit/saved_families.jsonl",
        )
        provenance = (ROOT / "docs" / "code-provenance.md").read_text()
        for relative in expected:
            self.assertTrue((ROOT / relative).is_file(), relative)
            self.assertIn(relative, provenance, relative)
        self.assertIn("242ecba44f76ed1120dadf06653fd6de47017b7f", provenance)
        self.assertIn("90d2f5edab212a9a1ecb9ec5d7161066047c7810", provenance)
        self.assertIn("read-only hardening", provenance)

    def test_combination_candidate_surface_is_exhaustive_for_two_and_three_cells(self) -> None:
        from glyph_combo_candidates import SHAPES, USEFUL_LINE_GLYPHS, enumerate_candidates

        rows = enumerate_candidates(c=None, max_size=3, max_distraction=1.0)
        n = len(USEFUL_LINE_GLYPHS)
        self.assertEqual(len(rows), len(SHAPES[2]) * n**2 + len(SHAPES[3]) * n**3)
        self.assertEqual(len(rows), 25088)

    def test_family_wrapper_fails_visibly_without_tty(self) -> None:
        result = subprocess.run(
            [str(ROOT / "run-families.sh")],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 69)
        self.assertIn("requires a real TTY", result.stderr)


if __name__ == "__main__":
    unittest.main()
