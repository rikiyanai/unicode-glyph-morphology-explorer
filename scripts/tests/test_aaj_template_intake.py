from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import aaj_template_intake as intake
import windows_aa_intake as windows
import glyph_families_viewer as viewer


class AAJNativeTemplates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = intake.load()
        cls.corpus = intake.TemplateCorpus(cls.doc)
        cls.families = viewer.load_aaj_families(cls.corpus, doc=cls.doc)

    def test_all_forty_are_individually_selectable_in_original_order(self):
        motifs = windows.load()["converter"]["multichar_templates"]
        self.assertEqual(len(self.families), 40)
        self.assertEqual(len({f["role_hint"] for f in self.families}), 40)
        for number, (family, motif) in enumerate(zip(self.families, motifs), 1):
            record = family["context"]
            self.assertEqual(record["id"], f"aaj-template-{number:02}")
            self.assertEqual(record["converter_template"]["text"], motif["text"])
            self.assertEqual(record["converter_template"]["codepoints"], motif["codepoints"])
            self.assertEqual(record["provenance"]["internal_label"], motif["label"])

    def test_native_whole_glyph_advances_and_binary_rasters(self):
        for record in self.doc["families"]:
            template = record["converter_template"]
            raster = template["raster_rows"]
            self.assertEqual(len(raster), 17)
            self.assertEqual(set("".join(raster)), {"#", "."})
            self.assertEqual(len({len(row) for row in raster}), 1)
            self.assertEqual(len(raster[0]), int(template["advance_px"]) + 8)
            x = 0
            for item in template["placements"]:
                self.assertEqual(item["x_px"], x)
                x += item["advance_px"]
            self.assertEqual(x, template["advance_px"])
            self.assertEqual("".join(p["char"] for p in template["placements"]), template["text"])

    def test_snapshot_reproduces_with_pinned_font_when_available(self):
        if not intake.FONT.exists():
            self.skipTest("optional source font unavailable")
        # Build to a temporary declared repository output, not the tracked asset.
        import tempfile
        with tempfile.TemporaryDirectory(dir=ROOT / ".run") as directory:
            with patch.object(intake, "OUTPUT", Path(directory) / "snapshot.json"):
                self.assertEqual(intake.build(), self.doc)

    def test_detail_labels_actual_font_and_does_not_rescale(self):
        for family in self.families:
            record = family["context"]
            detail = viewer._context_detail_lines(record, width=10)
            wide = "\n".join(viewer._context_detail_lines(record, width=160))
            self.assertIn("COMPARISON RASTER, NOT recovered Windows/MS Gothic output.", wide)
            self.assertIn("Saitamaar", wide)
            for row in viewer._half_block_rows(record["converter_template"]["raster_rows"]):
                self.assertIn(row, detail)

    def test_axis_and_wrapper_are_cache_free(self):
        with patch.object(sys, "argv", ["viewer", "--mode", "aaj", "--dump"]), \
             patch.object(viewer.ga, "Corpus", side_effect=AssertionError("cache load")), \
             patch.object(viewer, "dump_families") as dump:
            self.assertEqual(viewer.main(), 0)
            self.assertEqual(len(dump.call_args.args[1]), 40)
        result = subprocess.run([str(ROOT / "run-families.sh"), "--mode=aaj", "--dump"],
                                capture_output=True, text=True, check=True)
        self.assertIn("families=40", result.stdout)
        for number in range(1, 41):
            self.assertIn(f"aaj-template-{number:02}", result.stdout)

    def test_combo_and_default_browser_include_every_template(self):
        c = SimpleNamespace(i=lambda cp: None)
        with patch.object(viewer, "load_combination_families", return_value=[]), \
             patch.object(viewer, "load_seam_families", return_value=[]), \
             patch.object(viewer, "load_sjis_corpus_families", return_value=[]), \
             patch.object(viewer, "load_context_families", return_value=[]), \
             patch.object(viewer, "load_round_families", return_value=[]), \
             patch.object(viewer, "load_pattern_families", return_value=[]), \
             patch.object(viewer, "load_families", return_value=[]), \
             patch.object(viewer, "load_foliage_stroke_families", return_value=[]):
            combo = viewer.load_combo_families(c)
            default = viewer.load_default_families(c, None, 0)
        expected = {r["id"] for r in self.doc["families"]}
        self.assertEqual({f["context"]["id"] for f in combo}, expected)
        self.assertEqual({f["context"]["id"] for f in default if f["mode"] == "aaj"}, expected)


if __name__ == "__main__":
    unittest.main()
