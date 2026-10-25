from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import aahub_round_refs as refs
import glyph_families_viewer as viewer


class RoundReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = refs.load()
        cls.corpus = refs.ReferenceCorpus(cls.doc)
        cls.families = viewer.load_round_families(cls.corpus, doc=cls.doc)

    def test_seven_distinct_paired_sources_and_verbatim_text(self):
        self.assertEqual(len(self.families), 7)
        self.assertEqual(len({r["provenance"]["source_id"] for r in self.doc["families"]}), 7)
        for record in self.doc["families"]:
            p = record["provenance"]
            image = ROOT / p["image_path"]
            text = ROOT / p["text_path"]
            self.assertEqual(refs.sha(image.read_bytes()), p["source_image_sha256"])
            self.assertEqual(refs.sha(text.read_bytes()), p["source_text_sha256_file"])
            self.assertEqual(text.read_text().splitlines(), record["passages"][0]["rows"])
            with Image.open(image) as native:
                self.assertEqual(native.size, (record["native_reference"]["width"],
                                               record["native_reference"]["height"]))
            for form in record["focus_forms"]:
                self.assertIn(form, text.read_text(), record["id"])

    def test_packaged_pairs_match_archive_when_available(self):
        for record in self.doc["families"]:
            p = record["provenance"]
            for kind in ("image", "text"):
                source = Path(p[f"origin_{kind}_path"])
                if source.is_file():
                    self.assertEqual(source.read_bytes(), (ROOT / p[f"{kind}_path"]).read_bytes())

    def test_overview_is_bounded_and_honestly_labelled(self):
        for record in self.doc["families"]:
            rows, scale, offset = refs.raster_rows(record, 80)
            self.assertLessEqual(len(rows[0]), 80)
            self.assertLessEqual(len(rows), 48)
            self.assertEqual(offset, 0)
            self.assertGreaterEqual(scale, 1)
            pane = viewer._context_detail_lines(record, 80)
            self.assertIn("OVERVIEW", "\n".join(pane))
            self.assertIn("NOT native glyph-fit evidence", "\n".join(pane))
            for row in viewer._half_block_rows(rows):
                self.assertIn(row, pane)

    def test_native_pan_is_exact_source_pixels_without_resampling(self):
        for record in self.doc["families"]:
            with Image.open(ROOT / record["provenance"]["image_path"]) as image:
                ink = np.asarray(image.convert("L")) < 128
            for requested_x in (0, 32, 100000):
                rows, scale, offset = refs.raster_rows(record, 73, True, requested_x)
                self.assertEqual(scale, 1)
                expected = ["".join("#" if v else "." for v in row[offset:offset + 73]) for row in ink]
                self.assertEqual(rows, expected)
                self.assertEqual(offset, min(requested_x, max(0, ink.shape[1] - 73)))
            pane = viewer._context_detail_lines(record, 80, True, 16)
            self.assertIn("NATIVE PIXELS 1:1", "\n".join(pane))

    def test_standalone_view_needs_no_morphology_cache(self):
        script = ("import sys;sys.path.insert(0,sys.argv[1]);import glyph_families_viewer as v;"
                  "v.ga.Corpus=lambda:(_ for _ in ()).throw(AssertionError('cache load'));"
                  "sys.argv=['viewer','--mode','round','--dump'];raise SystemExit(v.main())")
        result = subprocess.run([sys.executable, "-c", script, str(ROOT / "scripts")],
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        import operator_construction_crops as crops
        self.assertIn("families=8", result.stdout)
        self.assertIn("PACKAGED SCREENSHOT", result.stdout)
        for record in crops.load()["families"]:
            self.assertIn(record["id"], result.stdout)
            self.assertIn(record["provenance"]["source_image_sha256"], result.stdout)

    def test_wrapper_round_dump_skips_cache_builds_and_tty(self):
        result = subprocess.run([str(ROOT / "run-families.sh"), "--mode=round", "--dump"],
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("families=8", result.stdout)
        self.assertNotIn("computing families", result.stderr)

    def test_combo_and_default_axes_include_round_sources(self):
        with patch.object(viewer, "load_combination_families", return_value=[]), \
             patch.object(viewer, "load_seam_families", return_value=[]), \
             patch.object(viewer, "load_sjis_corpus_families", return_value=[]), \
             patch.object(viewer, "load_context_families", return_value=[]), \
             patch.object(viewer, "load_pattern_families", return_value=[]), \
             patch.object(viewer, "load_aaj_families", return_value=[]), \
             patch.object(viewer, "load_families", return_value=[]), \
             patch.object(viewer, "load_foliage_stroke_families", return_value=[]):
            combo = viewer.load_combo_families(self.corpus)
            default = viewer.load_default_families(self.corpus, None, 0)
        import operator_construction_crops as crops
        self.assertEqual(len(combo), 8)
        for mode in ("combo", "context", "round"):
            self.assertEqual({f["context"]["id"] for f in default if f["mode"] == mode},
                             {r["id"] for r in crops.load()["families"]})

    def test_interpretation_does_not_identify_forgotten_kanji(self):
        records = {r["id"]: r for r in self.doc["families"]}
        self.assertIn("not identified", records["round-halo-res373"]["interpretation"]["drawn_analogy"])
        self.assertIn("not operator art approval", records["round-portrait-res91"]["provenance"]["annotation_status"])
        self.assertIsNone(records["round-wheels-resK-01"]["provenance"]["source_url"])


if __name__ == "__main__":
    unittest.main()
