from pathlib import Path
import gzip
import html
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import component_library_intake as intake
import glyph_families_viewer as viewer


class ComponentLibraries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = intake.load()
        cls.corpus = intake.ComponentCorpus(cls.doc["families"])

    def test_all_entries_are_accounted_for_without_calling_headings_presets(self):
        self.assertEqual(len(self.doc["libraries"]), 8)
        self.assertEqual(sum(lib["archive_entry_count"] for lib in self.doc["libraries"]), 1886)
        self.assertEqual(sum(len(lib["section_headings"]) for lib in self.doc["libraries"]), 33)
        self.assertEqual(len(self.doc["families"]), 1853)
        for lib in self.doc["libraries"]:
            records = intake.select(self.doc, lib["id"])
            indices = [r["component_library"]["archive_piece_index"] for r in records]
            heads = [h["archive_piece_index"] for h in lib["section_headings"]]
            self.assertEqual(sorted(indices + heads), list(range(lib["archive_entry_count"])))
            self.assertEqual(len(set(indices) & set(heads)), 0)

    def test_complete_original_rows_whitespace_and_glyphs_are_not_mined_away(self):
        for lib in self.doc["libraries"]:
            page = json.loads(gzip.decompress((ROOT / lib["source_path"]).read_bytes()))
            for r in intake.select(self.doc, lib["id"]):
                index = r["component_library"]["archive_piece_index"]
                rows = html.unescape(page["aa"][index]["value"]).splitlines() or [""]
                self.assertEqual(r["passages"][0]["rows"], rows)
                self.assertEqual(r["provenance"]["source_json_pointer"], f"/aa/{index}/value")

    def test_small_eye_role_and_row_height_hierarchy_survives(self):
        records = {r["component_library"]["archive_piece_index"]: r
                   for r in intake.select(self.doc, "faces-small")}
        self.assertEqual(len(records), 437)
        self.assertEqual(records[17]["component_library"]["section_path"], ["【目・瞳：小型】", "【2行】"])
        self.assertEqual(records[68]["component_library"]["section_path"], ["【目・瞳：小型】", "【3行】"])
        self.assertEqual(records[318]["component_library"]["section_path"], ["【口：小型】"])
        self.assertEqual(records[434]["component_library"]["section_path"], ["【顔：小型】"])
        self.assertIn("灯ぅミ", records[17]["passages"][0]["rows"][0])
        self.assertIn("Vリ", records[17]["passages"][0]["rows"][1])

    def test_circles_and_branching_curves_are_queryable_without_fixed_combo_shortlists(self):
        circles = intake.select(self.doc, "shapes", "円形")
        curves = intake.select(self.doc, "shapes", "枝分かれ")
        self.assertEqual(len(circles), 147)
        self.assertEqual(len(curves), 18)
        self.assertEqual(circles[0]["component_library"]["archive_piece_index"], 2)
        self.assertEqual(curves[0]["component_library"]["archive_piece_index"], 326)
        self.assertEqual(intake.select(self.doc, "shapes", "no such section"), [])

    def test_viewer_panes_distinguish_comparison_source_and_inspection_status(self):
        families = viewer.load_component_families(self.corpus, library="faces-small", section="2行")
        self.assertEqual(len(families), 50)
        pane = "\n".join(viewer._context_detail_lines(families[0]["context"], 100))
        for expected in ["NOT ORIGINAL PNG", "LIBRARY: faces-small", "SOURCE SECTION:",
                         "/aa/17/value", "Whole source entry", "complete original entry"]:
            self.assertIn(expected, pane)
        self.assertIn("NOT personally visually reviewed", self.doc["families"][2]["provenance"]["review_state"])

    def test_default_combo_and_context_loaders_include_library_entries(self):
        for mode in ["parts", "combo", "context"]:
            families = viewer.load_component_families(self.corpus, mode=mode)
            self.assertEqual(len(families), 1853)
            self.assertTrue(all(f["mode"] == mode for f in families))
        with patch.object(viewer, "load_combination_families", return_value=[]), \
             patch.object(viewer, "load_seam_families", return_value=[]), \
             patch.object(viewer, "load_sjis_corpus_families", return_value=[]), \
             patch.object(viewer, "load_context_families", return_value=[]), \
             patch.object(viewer, "load_aaj_families", return_value=[]), \
             patch.object(viewer, "load_round_families", return_value=[]), \
             patch.object(viewer, "load_pattern_families", return_value=[]):
            self.assertEqual(len(viewer.load_combo_families(self.corpus)), 1853)

    def test_cache_free_cli_wrapper_and_role_filter(self):
        for cmd in [[sys.executable, "scripts/glyph_families_viewer.py", "--mode", "parts", "--list-libraries"],
                    ["./run-families.sh", "--mode", "parts", "--library", "shapes", "--section", "円形", "--dump"]]:
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            if "--dump" in cmd:
                self.assertIn("families=147", result.stdout.splitlines()[0])
                self.assertIn("component-shapes-002", result.stdout)
                self.assertNotIn("component-shapes-150", result.stdout)
            else:
                for slug, _, _, _ in intake.LIBRARIES:
                    self.assertIn(slug + ":", result.stdout)

    def test_discovery_scope_is_explicit_and_metadata_candidates_are_not_claimed_reviewed(self):
        discovery = self.doc["discovery"]
        self.assertEqual(discovery["index_rows_scanned"], 13981)
        self.assertEqual(len(discovery["candidates"]), 39)
        self.assertEqual(sum(r["intake_status"] == "packaged library" for r in discovery["candidates"]), 8)
        self.assertTrue(all("エロ描写用" not in r["path"] for r in discovery["candidates"]))

    def test_corpus_accepts_mixed_still_and_frame_glyph_records(self):
        corpus = intake.ComponentCorpus([{"focus_forms": ["乂"], "passages": [{"glyph_rows": ["not rows"]}]},
                                         {"focus_forms": [], "passages": [{"rows": ["⌒"]}]}])
        self.assertIsNotNone(corpus.i(ord("乂")))
        self.assertIsNotNone(corpus.i(ord("⌒")))

    def test_members_include_later_rows_and_native_pixels_are_not_rescaled(self):
        import numpy as np
        from PIL import Image
        import operator_construction_crops as crops
        r = intake.select(self.doc, "shapes", "円形")[0]
        family = viewer.load_component_families(self.corpus, doc={"families": [r]})[0]
        self.assertEqual(set(family["members"]), {self.corpus.i(ord(ch)) for p in r["passages"]
                                               for row in p["rows"] for ch in row})
        ink = np.asarray(Image.open(ROOT / r["provenance"]["image_path"]).convert("L")) < 128
        rows, scale, offset = crops.raster_rows(r, 80, True, 32)
        self.assertEqual(scale, 1)
        self.assertEqual(offset, 32)
        self.assertEqual(rows, ["".join("#" if pixel else "." for pixel in row[32:112]) for row in ink])

    def test_missing_font_glyphs_are_disclosed_without_changing_source(self):
        missing = [r for r in self.doc["families"] if r["component_library"]["missing_comparison_font_codepoints"]]
        self.assertEqual(len(missing), 8)
        for r in missing:
            pane = "\n".join(viewer._context_detail_lines(r, 120))
            self.assertIn("COMPARISON FONT MISSING GLYPHS", pane)
            self.assertIn("not native-fit evidence", pane)
            for cp in r["component_library"]["missing_comparison_font_codepoints"]:
                self.assertIn(chr(int(cp[2:], 16)), "\n".join(r["passages"][0]["rows"]))


if __name__ == "__main__":
    unittest.main()
