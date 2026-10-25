from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import windows_aa_intake as intake
import glyph_families_viewer as viewer


class WindowsAAIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = intake.load()

    def test_all_forty_motifs_and_builder_output_agree(self):
        converter = self.doc["converter"]
        builder, output = converter["builder_mappings"], converter["output_mappings"]
        pairs = lambda rows: [(r["label"], r["text"]) for r in rows]
        self.assertEqual(len(builder), 41)
        self.assertEqual(pairs(builder), pairs(output[:41]))
        self.assertEqual(pairs(output[41:]), [(" ", "_")])
        motifs = converter["multichar_templates"]
        self.assertEqual(len(motifs), 40)
        self.assertEqual(len({r["text"] for r in motifs}), 40)
        self.assertEqual([r["text"] for r in builder if len(r["text"]) == 1], ["　"])
        for item in motifs:
            self.assertEqual(item["codepoints"], [f"U+{ord(ch):04X}" for ch in item["text"]])
        self.assertTrue({"li,", ",il", ".／", ".＼", "ﾞ:､", "ﾟl", "lﾟ"}.issubset({r["text"] for r in motifs}))

    def test_direct_pe_recovery_when_original_available(self):
        path = intake.SAVED / "aaj/aaj.exe"
        if not path.exists():
            self.skipTest("optional original saved PE unavailable")
        self.assertEqual(intake.recover(path.read_bytes()), self.doc["converter"])

    def test_other_build_is_rejected_before_pe_parsing(self):
        with self.assertRaisesRegex(ValueError, "Unrecognized executable"):
            intake.recover(b"not a trusted build")

    def test_raw_cp932_bytes_and_spaces_are_preserved(self):
        for record in self.doc["files"]:
            raw = (ROOT / record["raw_path"]).read_bytes()
            decoded = (ROOT / record["text_path"]).read_bytes()
            self.assertEqual(raw.decode("cp932").encode("utf-8"), decoded)
            self.assertEqual(record["rows"], decoded.decode("utf-8").splitlines())
        brush = next(r for r in self.doc["files"] if r["text_path"].endswith("/aabrush.txt"))
        self.assertIn(". ", brush["rows"])
        self.assertIn("| ", brush["rows"])
        self.assertEqual([row for row in brush["rows"] if row.startswith("[ListName=")],
                         ["[ListName=.,:;]", "[ListName=l|]", "[ListName=ニ三]"])

    def test_documentation_is_not_counted_as_lettering_library(self):
        libraries = [r for r in self.doc["files"] if "/lettering-" in r["text_path"]]
        manual = [r for r in libraries if "manual" in r["kind"]]
        self.assertEqual(len(manual), 1)
        self.assertEqual(manual[0]["template_tags"], 36)
        self.assertEqual(sorted(r["template_tags"] for r in libraries if r not in manual), [10, 85, 91])

    def test_palette_contains_all_named_groups_and_real_combination_samples(self):
        groups = self.doc["palette_groups"]
        self.assertEqual(len(groups), 24)
        palette = next(r for r in self.doc["files"] if r["text_path"].endswith("/aalist.txt"))
        self.assertEqual(intake.palette_groups(palette["rows"]), groups)
        for group in groups:
            self.assertEqual(palette["rows"][group["line_start"] - 1:group["line_end"]], group["rows"])
        impact = groups[21]
        self.assertIn("衝撃", impact["name"])
        self.assertIn("ゞ乂ノ", impact["rows"])
        self.assertIn("/〉", groups[22]["rows"])
        mouth = "\n".join(groups[23]["rows"])
        self.assertIn("　 ／⌒ヽ\n　.i　　　　i\n　 ヽ ＿ ノ", mouth)
        doc = json.loads(intake.CONTEXT.read_text())
        found = {r["id"]: r for r in doc["families"] if r["id"] in intake.PALETTE_IDS}
        self.assertEqual(set(found), intake.PALETTE_IDS)
        for record in found.values():
            self.assertIn("NOT evidence of an atomic multi-row macro", record["provenance"]["context_limit"])

    def test_pinned_upstream_source_and_license_are_preserved(self):
        doc = json.loads(intake.SOURCE_INDEX.read_text())
        self.assertEqual(doc["commit"], intake.UPSTREAM_COMMIT)
        self.assertEqual(len(doc["files"]), 4)
        for record in doc["files"]:
            raw = (ROOT / record["raw_path"]).read_bytes()
            text = (ROOT / record["text_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record["raw_sha256"])
            self.assertEqual(hashlib.sha256(text).hexdigest(), record["text_sha256"])
            self.assertEqual(raw.decode("cp932").encode("utf-8"), text)
            self.assertIn(intake.UPSTREAM_COMMIT, record["url"])
        self.assertEqual(hashlib.sha256((ROOT / doc["license_path"]).read_bytes()).hexdigest(), doc["license_sha256"])

    def test_templates_are_context_viewable_without_artwork_attribution(self):
        import operator_construction_crops as crops
        doc = json.loads(intake.CONTEXT.read_text())
        c = crops.ConstructionCorpus(doc)
        families = viewer.load_context_families(c)
        found = {r["context"]["id"]: r["context"] for r in families if r["context"]["id"] in intake.IDS}
        self.assertEqual(set(found), intake.IDS)
        for record in found.values():
            self.assertIsNone(record["provenance"]["paired_native_png"])
            self.assertIn("No evidence these tools made", record["interpretation"]["historical_implementation_limit"])
        self.assertEqual(len(found["aa-judgment-composite-matching-templates"]["passages"][0]["rows"]), 40)

    def test_context_mode_does_not_require_discovery_cache(self):
        with mock.patch.object(sys, "argv", ["viewer", "--mode", "context", "--dump"]), \
             mock.patch.object(viewer.ga, "Corpus", side_effect=AssertionError("private cache requested")), \
             mock.patch.object(viewer, "dump_families") as dump:
            self.assertEqual(viewer.main(), 0)
            ids = {f["context"]["id"] for f in dump.call_args.args[1]}
            self.assertTrue(intake.IDS.issubset(ids))
        result = subprocess.run([str(ROOT / "run-families.sh"), "--mode", "context", "--dump"],
                                capture_output=True, text=True, check=True)
        for id in intake.IDS:
            self.assertIn(id, result.stdout)


if __name__ == "__main__":
    unittest.main()
