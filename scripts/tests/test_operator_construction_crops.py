from pathlib import Path
import hashlib
import html
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import operator_construction_crops as crops
import glyph_families_viewer as viewer


class OperatorConstructionCrops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = crops.load()
        cls.corpus = crops.ConstructionCorpus(cls.doc)

    def test_all_eight_exact_operator_images_are_packaged(self):
        self.assertEqual(len(self.doc["families"]), 8)
        for n, record in enumerate(self.doc["families"], 1):
            self.assertEqual(record["id"], f"operator-curve-crop-{n:02}")
            p = record["provenance"]
            data = (ROOT / p["image_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), p["source_image_sha256"])
            original = Path(p["origin_image_path"])
            if original.is_file():
                self.assertEqual(data, original.read_bytes())
            with Image.open(ROOT / p["image_path"]) as image:
                self.assertEqual(image.size, (record["native_reference"]["width"], record["native_reference"]["height"]))

    def test_raw_and_display_text_are_distinct_and_reproducible(self):
        self.assertEqual({s["archive_piece_index"] for s in self.doc["sources"]}, {27, 36, 57, 73, 97, 105, 106, 107, 121, 161, 165})
        for source in self.doc["sources"]:
            raw = (ROOT / source["raw_text_path"]).read_text()
            decoded = (ROOT / source["text_path"]).read_text()
            self.assertEqual(decoded, html.unescape(raw))
            self.assertEqual(decoded.splitlines(), source["decoded_rows"])

    def test_all_eight_local_bindings_are_verbatim_with_variant_ambiguity_explicit(self):
        bound = []
        for record in self.doc["families"]:
            p = record["provenance"]
            if not record["passages"]:
                self.assertEqual(record["focus_forms"], [])
                self.assertIn("unresolved", p["source_binding_status"])
                self.assertIsNone(p["source_url"])
                continue
            bound.append(record["id"])
            source_rows = (ROOT / p["text_path"]).read_text().splitlines()
            for passage in record["passages"]:
                start = passage["line_start"] - 1
                self.assertEqual(source_rows[start:start + len(passage["rows"])], passage["rows"])
                for form in record["focus_forms"]:
                    self.assertIn(form, "\n".join(passage["rows"]))
        self.assertEqual(bound, [f"operator-curve-crop-{n:02}" for n in range(1, 9)])
        ambiguous = self.doc["families"][3]
        self.assertIn("unique full-artwork variant unresolved", ambiguous["provenance"]["source_binding_status"])
        variants = ambiguous["provenance"]["source_variants"]
        self.assertEqual([v["archive_piece_index"] for v in variants], [105, 106, 107])
        for variant in variants:
            text = (ROOT / variant["text_path"]).read_text().splitlines()
            rows = text[variant["line_start"] - 1:variant["line_end"]]
            for form in ambiguous["focus_forms"]:
                self.assertIn(form, "\n".join(rows))

    def test_arch_record_identifies_actual_slope_change_and_kanji(self):
        r = self.doc["families"][5]
        self.assertEqual(r["provenance"]["archive_piece_index"], 73)
        for form in ("ｲﾆア゜", "/ﾆｱ", "寸ム", "寸ﾊ", "Ⅵｉ"):
            self.assertIn(form, r["focus_forms"])

    def test_native_view_is_exact_pixel_data_and_overview_is_labelled(self):
        for record in self.doc["families"]:
            with Image.open(ROOT / record["provenance"]["image_path"]) as image:
                ink = np.asarray(image.convert("L")) < 128
            rows, scale, x = crops.raster_rows(record, 60, True, 16)
            self.assertEqual(scale, 1)
            self.assertEqual(rows, ["".join("#" if v else "." for v in row[x:x + 60]) for row in ink])
            pane = "\n".join(viewer._context_detail_lines(record, 80))
            self.assertIn("PACKAGED SCREENSHOT", pane)
            self.assertIn("OVERVIEW", pane)
            self.assertIn("NOT native glyph-fit evidence", pane)

    def test_round_axis_uses_operator_crops_not_rejected_candidates(self):
        families = viewer.load_round_families(self.corpus)
        self.assertEqual(len(families), 53)
        self.assertEqual([f["context"]["id"] for f in families[:8]],
                         [f"operator-curve-crop-{n:02}" for n in range(1, 9)])
        self.assertTrue(all(f["context"]["id"].startswith("profile-circle-") for f in families[8:]))
        with patch.object(viewer, "load_combination_families", return_value=[]), \
             patch.object(viewer, "load_seam_families", return_value=[]), \
             patch.object(viewer, "load_sjis_corpus_families", return_value=[]), \
             patch.object(viewer, "load_context_families", return_value=[]), \
             patch.object(viewer, "load_aaj_families", return_value=[]), \
             patch.object(viewer, "load_component_families", return_value=[]), \
             patch.object(viewer, "load_pattern_families", return_value=[]):
            self.assertEqual({f["context"]["id"] for f in viewer.load_combo_families(self.corpus)},
                             {f["context"]["id"] for f in families})

    def test_cli_is_portable_without_cache_or_temporary_screenshots(self):
        script = ("import sys;sys.path.insert(0,sys.argv[1]);import glyph_families_viewer as v;"
                  "v.ga.Corpus=lambda:(_ for _ in ()).throw(AssertionError('cache load'));"
                  "sys.argv=['viewer','--mode','round','--dump'];raise SystemExit(v.main())")
        result = subprocess.run([sys.executable, "-c", script, str(ROOT / "scripts")],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("families=53", result.stdout.splitlines()[0])
        self.assertIn("operator-curve-crop-06", result.stdout)
        self.assertIn("unique full-artwork variant unresolved", result.stdout)
        self.assertIn("church-161.txt", result.stdout)
        self.assertIn("church-057.txt", result.stdout)


if __name__ == "__main__":
    unittest.main()
