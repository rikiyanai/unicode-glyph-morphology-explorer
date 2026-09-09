from __future__ import annotations

import hashlib
import json
import re
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
            "scripts/glyph_cell_features.py",
            "scripts/glyph_cell_pairs.py",
            "scripts/glyph_combo_candidates.py",
            "scripts/glyph_combo_gallery.py",
            "scripts/glyph_combo_mine.py",
            "scripts/glyph_run_walker.py",
            "scripts/glyph_seam_index.py",
            "scripts/glyph_families_viewer.py",
            "scripts/glyph_features.py",
            "scripts/glyph_morphology_browser.py",
            "scripts/glyph_skeleton.py",
            "assets/glyphs/authored/glyph_combinations.v1.json",
            "assets/glyphs/authored/stone_story_tutorial_plates/01-sacrificial-pit-layers.txt",
            "assets/glyphs/authored/stone_story_tutorial_plates/02-poison-adept-walk-cycle.txt",
            "assets/glyphs/authored/stone_story_tutorial_plates/03-styles-fonts-alphabet.txt",
            "assets/glyphs/authored/stone_story_tutorial_plates/04-lines-materials-antialiasing.txt",
            "assets/glyphs/authored/stone_story_tutorial_plates/05-depth-dithering-shadows.txt",
            "assets/glyphs/authored/stone_story_tutorial_plates/06-animation-subtractive.txt",
            "docs/research/ascii/glyph_audit/saved_families.jsonl",
        )
        provenance = (ROOT / "docs" / "code-provenance.md").read_text()
        for relative in expected:
            self.assertTrue((ROOT / relative).is_file(), relative)
            self.assertIn(relative, provenance, relative)
        self.assertIn("242ecba44f76ed1120dadf06653fd6de47017b7f", provenance)
        self.assertIn("90d2f5edab212a9a1ecb9ec5d7161066047c7810", provenance)
        self.assertIn("7a87dcd0dbfa99520803794e6ab46046a744b2ee", provenance)
        self.assertIn("read-only hardening", provenance)

    def test_packaged_combo_gallery_snapshot_is_current_review_artifact(self) -> None:
        html = ROOT / "docs" / "artifacts" / "glyph_combo_gallery.html"
        checksums = ROOT / "docs" / "artifacts" / "SHA256SUMS"
        index = ROOT / "docs" / "artifacts" / "README.md"
        self.assertTrue(html.is_file())
        self.assertTrue(checksums.is_file())
        self.assertTrue(index.is_file())
        text = html.read_text()
        self.assertIn("<title>Seam Ledger</title>", text)
        self.assertIn('"total": 148016', text)
        self.assertIn('"runs_beside_w16_cjk": 600', text)
        self.assertIn('"runs_stacked_w16_cjk": 600', text)
        self.assertIn('"runs_beside_w8_rtl": 600', text)
        checksum_text = checksums.read_text()
        expected = re.search(r"^([0-9a-f]{64})  glyph_combo_gallery\.html$", checksum_text, re.M)
        self.assertIsNotNone(expected)
        self.assertEqual(hashlib.sha256(html.read_bytes()).hexdigest(), expected.group(1))

    def test_combination_candidate_surface_is_exhaustive_for_two_and_three_cells(self) -> None:
        from glyph_combo_candidates import SHAPES, USEFUL_LINE_GLYPHS, enumerate_candidates

        rows = enumerate_candidates(c=None, max_size=3, max_distraction=1.0)
        n = len(USEFUL_LINE_GLYPHS)
        self.assertEqual(len(rows), len(SHAPES[2]) * n**2 + len(SHAPES[3]) * n**3)
        self.assertEqual(len(rows), 148016)
        self.assertEqual(n, 29)

    def test_combo_mode_remains_the_full_review_surface(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "glyph_families_viewer.py"),
                "--mode",
                "combo",
                "--dump",
                "--limit",
                "80",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn("mode=combo", result.stdout)
        self.assertIn("[authored]", result.stdout)
        self.assertIn("families=", result.stdout)
        first = result.stdout.splitlines()[0]
        count = int(first.split("families=", 1)[1].split()[0])
        self.assertGreater(count, 100)

    def test_documentation_rejects_stale_combo_count_and_runtime_metric_confusion(self) -> None:
        readme = (ROOT / "README.md").read_text()
        provenance = (ROOT / "docs" / "code-provenance.md").read_text()
        failure_log = (ROOT / "docs" / "FAILURE_LOG.md").read_text()
        combined = "\n".join((readme, provenance, failure_log))
        self.assertIn("25 basic marks plus 4 extended marks", combined)
        self.assertIn("candidate-transition diagnostic", combined)
        self.assertNotIn("33 tutorial", combined)

    def test_stone_story_usage_miner_uses_packaged_plates(self) -> None:
        from glyph_combo_mine import PLATE_DIR, mine

        self.assertTrue(str(PLATE_DIR).endswith("assets/glyphs/authored/stone_story_tutorial_plates"))
        result = mine(min_count=3, max_run=6, measure=False)
        self.assertEqual(len(result["plates"]), 6)
        self.assertGreaterEqual(len(result["families"]), 700)

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
