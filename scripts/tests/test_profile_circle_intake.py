from pathlib import Path
import html
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import profile_circle_intake as intake
import operator_construction_crops as crops
import glyph_families_viewer as viewer


class ProfileCircleIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = intake.load()

    def test_all_profile_positions_and_duplicate_saves_are_retained(self):
        self.assertEqual(self.doc["entry_count"], 51)
        self.assertEqual(len(self.doc["families"]), 45)
        positions = [n for r in self.doc["families"] for n in r["provenance"]["profile_entry_indices"]]
        self.assertEqual(sorted(positions), list(range(51)))
        repeated = [r["provenance"]["profile_entry_indices"] for r in self.doc["families"]
                    if len(r["provenance"]["profile_entry_indices"]) > 1]
        self.assertEqual(repeated, [[0, 1], [5, 6], [8, 9], [19, 20], [21, 29], [25, 26]])

    def test_export_originals_and_focused_regions_agree_without_interior_normalization(self):
        entries = intake.split_export((ROOT / self.doc["export_path"]).read_bytes())
        for r in self.doc["families"]:
            p = r["provenance"]
            text = (ROOT / p["text_path"]).read_text()
            self.assertEqual(html.unescape((ROOT / p["raw_text_path"]).read_text()), text)
            for n in p["profile_entry_indices"]:
                self.assertEqual(entries[n].strip(), text.strip())
            for passage in r["passages"]:
                start = passage["line_start"] - 1
                self.assertEqual(passage["rows"], text.splitlines()[start:start + len(passage["rows"])] )
            for form in r["focus_forms"]:
                self.assertIn(form, "\n".join(r["passages"][0]["rows"]))

    def test_distinct_returns_and_non_circle_constructions_are_not_collapsed(self):
        records = {r["id"]: r for r in self.doc["families"]}
        self.assertIn("乂__ノ", records["profile-circle-03"]["focus_forms"])
        self.assertIn("乂__ﾉ", records["profile-circle-13"]["focus_forms"])
        self.assertIn("乂__ソ", records["profile-circle-08"]["focus_forms"])
        self.assertIn("ゝ._ ノ", records["profile-circle-25"]["focus_forms"])
        for n in [15, 22, 28, 31, 34, 41, 43, 48, 50]:
            self.assertIn(f"profile-circle-{n:02}", records)

    def test_new_rasters_are_not_labelled_originals_and_sources_remain_ambiguous_where_required(self):
        records = {r["id"]: r for r in self.doc["families"]}
        for r in records.values():
            self.assertEqual(r["native_reference"]["kind"], "saitamaar-comparison")
            self.assertIn("NOT a recovered original PNG", r["provenance"]["native_image_status"])
            self.assertEqual(r["provenance"]["profile_visibility"], "private draft; unchanged")
            pane = "\n".join(viewer._context_detail_lines(r, 100))
            self.assertIn("NOT ORIGINAL PNG", pane)
            self.assertIn("ORIGINAL MATCH:", pane)
            self.assertIn("My MLT:", pane)
        self.assertEqual(len(records["profile-circle-35"]["provenance"]["archive_matches"]), 2)
        self.assertEqual(len(records["profile-circle-40"]["provenance"]["archive_matches"]), 2)

    def test_round_combo_and_context_discovery_include_the_new_records(self):
        doc = intake.extend(crops.load())
        corpus = crops.ConstructionCorpus(doc)
        families = viewer.load_round_families(corpus)
        self.assertEqual(len(families), 53)
        self.assertTrue(all(f["members"] for f in families))
        with patch.object(viewer, "load_combination_families", return_value=[]), \
             patch.object(viewer, "load_seam_families", return_value=[]), \
             patch.object(viewer, "load_sjis_corpus_families", return_value=[]), \
             patch.object(viewer, "load_context_families", return_value=[]), \
             patch.object(viewer, "load_aaj_families", return_value=[]), \
             patch.object(viewer, "load_component_families", return_value=[]), \
             patch.object(viewer, "load_pattern_families", return_value=[]):
            self.assertEqual(len(viewer.load_combo_families(corpus)), 53)
        # The context UI uses this same source loader with mode=context.
        self.assertEqual(len(viewer.load_round_families(corpus, mode="context")), 53)

    def test_cache_free_round_cli_exposes_the_last_profile_entry(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/glyph_families_viewer.py"),
                                 "--mode", "round", "--dump"], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("profile-circle-50", result.stdout)
        self.assertIn("operator-curve-crop-08", result.stdout)


if __name__ == "__main__":
    unittest.main()
