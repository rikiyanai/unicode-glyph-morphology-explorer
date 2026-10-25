from pathlib import Path
import gzip
import html
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import operator_reference_sources as sources
import operator_construction_crops as crops
import glyph_families_viewer as viewer


class OperatorReferenceSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = sources.load()
        cls.records = {r["id"]: r for r in cls.doc["records"]}

    def test_all_eight_crops_and_exact_cup_have_individual_entries(self):
        self.assertEqual(len(self.records), 9)
        self.assertEqual(set(self.records), {f"operator-curve-crop-{n:02}" for n in range(1, 9)} | {"aramaki-cup-plate-surface-following-tone"})

    def test_bound_sources_are_original_full_text_not_just_excerpts(self):
        for number, piece in ((1, 161), (2, 165), (3, 36), (5, 97), (6, 73), (7, 57), (8, 57)):
            record = self.records[f"operator-curve-crop-{number:02}"]
            self.assertEqual(record["archive_piece_index"], piece)
            self.assertEqual(record["source_url"], "https://aahub.org/mlt/2f0353dc8e23bde120d1c050746f937c")
            decoded = (ROOT / record["original_full_text_path"]).read_text()
            raw = (ROOT / record["original_raw_text_path"]).read_text()
            self.assertEqual(decoded, html.unescape(raw))
            archive = Path(record["archive_path"])
            if archive.is_file():
                self.assertEqual(json.loads(gzip.decompress(archive.read_bytes()))["aa"][piece]["value"], raw)
            self.assertGreater(len(decoded.splitlines()), record["regions"][0]["line_end"] - record["regions"][0]["line_start"] + 1)

    def test_shared_crop_does_not_receive_fake_unique_original(self):
        record = self.records["operator-curve-crop-04"]
        self.assertIn("unique full-artwork variant unresolved", record["status"])
        for key in ("original_full_text_path", "original_raw_text_path", "archive_piece_index"):
            self.assertIsNone(record[key])
        self.assertEqual([v["archive_piece_index"] for v in record["source_variants"]], [105, 106, 107])
        self.assertEqual(record["source_url"], "https://aahub.org/mlt/2f0353dc8e23bde120d1c050746f937c")
        for variant in record["source_variants"]:
            self.assertTrue((ROOT / variant["text_path"]).is_file())
        self.assertTrue((ROOT / record["crop_path"]).is_file())

    def test_cup_is_exact_original_with_the_reclining_character_not_rice(self):
        record = self.records["aramaki-cup-plate-surface-following-tone"]
        self.assertEqual(record["archive_piece_index"], 176)
        self.assertEqual(record["source_url"], "https://aahub.org/mlt/e8e2f681204d649ea2033d2f62399a04")
        path = ROOT / record["original_full_text_path"]
        self.assertEqual(sources.sha(path), record["original_full_text_sha256"])
        self.assertIn("l　　 ⊃　　⌒_つ", path.read_text())
        self.assertIn("different plate contents", record["not_a_substitute"])
        self.assertIsNone(record["original_full_native_image_path"])
        archive = Path(record["archive_path"])
        if archive.is_file():
            self.assertEqual(json.loads(gzip.decompress(archive.read_bytes()))["aa"][176]["value"].rstrip("\n"), path.read_text().rstrip("\n"))

    def test_every_crop_hash_matches_unchanged_image(self):
        for record in self.records.values():
            if record.get("crop_path"):
                self.assertEqual(sources.sha(ROOT / record["crop_path"]), record["crop_sha256"])

    def test_viewer_points_to_registry_and_explicit_original_status(self):
        doc = crops.load()
        corpus = crops.ConstructionCorpus(doc)
        records = [r["context"] for r in viewer.load_round_families(corpus, doc=doc)]
        for record in records:
            text = "\n".join(viewer._context_detail_lines(record, 100))
            self.assertIn("operator_reference_sources.v1.json", text)
            self.assertIn("original reference status:", text)


if __name__ == "__main__":
    unittest.main()
