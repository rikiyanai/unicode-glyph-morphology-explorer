from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
