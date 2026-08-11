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

    def test_packaged_owners_have_exact_code_provenance(self) -> None:
        expected = {
            "scripts/compile_glyph_manifest.py": (
                "6fd8c06dd911b424b3bc256b491c0a027e01c92a9c567cd7dc804f0ff2c3d47e",
                "6fd8c06dd911b424b3bc256b491c0a027e01c92a9c567cd7dc804f0ff2c3d47e",
            ),
            "scripts/fl4482_font_chain.py": (
                "dddbc999ad36f9bbf973b32cc65ebde304c396d1966675462a9f9eb625df04b0",
                "dddbc999ad36f9bbf973b32cc65ebde304c396d1966675462a9f9eb625df04b0",
            ),
            "scripts/generate_glyph_shape_catalog.py": (
                "b5f0c58ac22cfe31797a9e37951b8deea557dd9bc09612a0e8f9cc759abffff2",
                "b5f0c58ac22cfe31797a9e37951b8deea557dd9bc09612a0e8f9cc759abffff2",
            ),
            "scripts/glyph_audit.py": (
                "2dfd6fc7eabe921ef3dff57b04254b93bdbd0dfa4f2023a01cda176e6ffc6071",
                "2dfd6fc7eabe921ef3dff57b04254b93bdbd0dfa4f2023a01cda176e6ffc6071",
            ),
            "scripts/glyph_families_viewer.py": (
                "0ad3f63736313cd02e2b0f53c03a0b7ed00cca22ae2d8bf057696c9c52b479b0",
                "e11f0cf1784c062811abdd3b1bdc1d521a4b391dcfd786fc063ccaa8c8ce73ee",
            ),
            "scripts/glyph_features.py": (
                "ed19cc976f140cf4bc6d15c2bad5e1575ea2dd998346441ac7fdd1d08c2462f6",
                "ed19cc976f140cf4bc6d15c2bad5e1575ea2dd998346441ac7fdd1d08c2462f6",
            ),
            "scripts/glyph_morphology_browser.py": (
                "8eadca1a559952b90cc1935db038238cc1496fd973c6fad0669a3c3fd97e2bdc",
                "8eadca1a559952b90cc1935db038238cc1496fd973c6fad0669a3c3fd97e2bdc",
            ),
            "scripts/glyph_skeleton.py": (
                "7e225890f4d24038b84c64dfd67e3a226f82434a6105c4b888fbd0bf16208a86",
                "7e225890f4d24038b84c64dfd67e3a226f82434a6105c4b888fbd0bf16208a86",
            ),
            "docs/research/ascii/glyph_audit/saved_families.jsonl": (
                "d33bb598d122b3b073186b9ca6fc0dc69148d49578a12fb04a4f54e10ef1aa11",
                "d33bb598d122b3b073186b9ca6fc0dc69148d49578a12fb04a4f54e10ef1aa11",
            ),
        }
        provenance = (ROOT / "docs" / "code-provenance.md").read_text()
        for relative, (source_sha, packaged_sha) in expected.items():
            actual_sha = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual_sha, packaged_sha, relative)
            self.assertIn(source_sha, provenance, relative)
            if source_sha != packaged_sha:
                self.assertIn(packaged_sha, provenance, relative)
        self.assertIn("read-only hardening", provenance)

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
