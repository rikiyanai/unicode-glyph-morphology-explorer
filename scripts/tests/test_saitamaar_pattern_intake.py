from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import glyph_families_viewer as viewer
import saitamaar_pattern_intake as intake


class PatternIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = intake.load()
        cls.corpus = intake.PatternCorpus(cls.doc)
        cls.families = viewer.load_pattern_families(cls.corpus, doc=cls.doc)

    def test_all_supplied_measurement_rows_preserved_and_reproduced(self):
        checks = self.doc["reported_checks"]
        self.assertEqual(len(checks), 47)
        self.assertTrue(all(row["matches"] for row in checks))
        source_rows = self.doc["source"]["reported_stdout"].splitlines()
        self.assertEqual([row["reported_row"] for row in checks], source_rows)
        self.assertEqual(sum(row.startswith("| adv") for row in source_rows), 3)
        self.assertEqual(sum(row.startswith("ｌ adv") for row in source_rows), 2)

    def test_every_reported_glyph_is_viewable_in_a_comparison(self):
        self.assertEqual(len(self.families), 12)
        self.assertEqual(len({f["context"]["id"] for f in self.families}), 12)
        self.assertTrue({row[0] for row in self.doc["source"]["reported_stdout"].splitlines()}
                        <= {chr(cp) for cp in self.corpus.cps})
        records = {f["context"]["id"]: f["context"] for f in self.families}
        self.assertEqual(records["parallel-slant-bundles"]["focus_forms"], ["彡", "ミ", "ﾐ"])
        self.assertIn("乂", records["crossed-ink-shapes"]["focus_forms"])
        self.assertIn("｀ヽ､_", records["curved-crease-returns"]["focus_forms"])
        self.assertIn("‐-､_", records["curved-crease-returns"]["focus_forms"])
        self.assertIn(["|:."] * 3, [v["text_rows"] for v in records["tone-band-combinations"]["native_comparisons"]])

    def test_rasters_keep_native_advance_row_pitch_and_binary_ink(self):
        for record in self.doc["families"]:
            for variant in record["native_comparisons"]:
                grid = variant["raster_rows"]
                self.assertEqual(len(grid), len(variant["text_rows"]) * 17)
                self.assertEqual(len({len(row) for row in grid}), 1)
                self.assertEqual(set("".join(grid)), {"#", "."})
                if len(variant["text_rows"]) == 1 and len(variant["text_rows"][0]) == 1:
                    metric = variant["glyph_metrics"][0]
                    self.assertEqual(sum(row.count("#") for row in grid), metric["ink_px"])
                    self.assertEqual(len(grid[0]), int(metric["advance_px"]) + 8)

    def test_component_axes_not_mislabelled_pen_stroke_counts(self):
        crossing = next(f for f in self.families if f["context"]["id"] == "crossed-ink-shapes")
        variant = next(v for v in crossing["context"]["native_comparisons"] if v["text_rows"] == ["乂"])
        self.assertEqual(len(variant["glyph_metrics"][0]["components"]), 1)
        lines = viewer._context_detail_lines(crossing["context"], 160)
        self.assertIn("NOT PEN STROKES", "\n".join(lines))
        self.assertIn("not universal glyph meanings", "\n".join(lines))

    def test_interactive_and_dump_expose_rasters_metrics_and_limits(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            viewer.dump_families(self.corpus, self.families, "patterns")
        output = stream.getvalue()
        for family in self.families:
            record = family["context"]
            self.assertIn(record["id"], output)
            self.assertIn(record["title"], output)
            lines = viewer._context_detail_lines(record, 160)
            for variant in record["native_comparisons"]:
                for raster in viewer._half_block_rows(variant["raster_rows"]):
                    self.assertIn(raster, lines)
                for metric in variant["glyph_metrics"]:
                    self.assertIn(metric["codepoint"], output)
        self.assertIn(self.doc["source"]["font_sha256"], output)
        self.assertIn("No renderer behavior", output)

    def test_narrow_terminal_does_not_wrap_or_rescale_raster(self):
        record = self.families[0]["context"]
        lines = viewer._context_detail_lines(record, 10)
        self.assertIn("clipped", "".join(lines))
        for raster in viewer._half_block_rows(record["native_comparisons"][0]["raster_rows"]):
            self.assertIn(raster, lines)

    def test_existing_combo_and_default_axes_include_new_groups(self):
        with patch.object(viewer, "load_combination_families", side_effect=lambda *a, **k: []), \
             patch.object(viewer, "load_seam_families", return_value=[]), \
             patch.object(viewer, "load_sjis_corpus_families", return_value=[]), \
             patch.object(viewer, "load_context_families", return_value=[]), \
             patch.object(viewer, "load_round_families", return_value=[]), \
             patch.object(viewer, "load_aaj_families", return_value=[]), \
             patch.object(viewer, "load_component_families", return_value=[]), \
             patch.object(viewer, "load_families", return_value=[]), \
             patch.object(viewer, "load_foliage_stroke_families", return_value=[]):
            combo = viewer.load_combo_families(self.corpus)
            default = viewer.load_default_families(self.corpus, None, 0)
        self.assertEqual(len(combo), 12)
        self.assertEqual({f["context"]["id"] for f in combo},
                         {f["context"]["id"] for f in self.families})
        self.assertEqual(sum(f["mode"] == "patterns" for f in default), 12)
        self.assertEqual(sum(f["mode"] == "combo" for f in default), 12)

    def test_direct_cli_works_without_loading_morphology_cache(self):
        script = ("import sys; sys.path.insert(0, sys.argv[1]); "
                  "import glyph_families_viewer as v; "
                  "v.ga.Corpus=lambda: (_ for _ in ()).throw(AssertionError('cache load')); "
                  "sys.argv=['viewer','--mode','patterns','--dump']; raise SystemExit(v.main())")
        result = subprocess.run([sys.executable, "-c", script, str(SCRIPTS)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("families=12", result.stdout)
        self.assertIn("Tone-band combination proposals", result.stdout)

    def test_snapshot_is_reproducible_when_original_font_available(self):
        font = Path(self.doc["source"]["font_path"])
        if not font.is_file():
            self.skipTest("external source font not installed; tracked snapshot remains viewable")
        self.assertEqual(intake.build(font), self.doc)

    def test_one_command_wrapper_can_dump_patterns_without_tty_or_cache_build(self):
        result = subprocess.run([str(SCRIPTS.parent / "run-families.sh"),
                                 "--mode=patterns", "--dump"],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("families=12", result.stdout)
        self.assertNotIn("computing families", result.stderr)


if __name__ == "__main__":
    unittest.main()
