from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import glyph_families_viewer as viewer  # noqa: E402

DATA = ROOT / "assets/glyphs/contextual/shallot_native_contexts.v1.json"


class ContextEvidenceData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.families = {record["id"]: record for record in cls.doc["families"]}

    def test_schema_and_evidence_categories_are_explicit(self) -> None:
        self.assertEqual(self.doc["schema"], "glyph_morphology.contextual_combo_evidence.v1")
        self.assertEqual(len(self.families), len(self.doc["families"]))
        self.assertGreaterEqual(len(self.families), 8)
        for record in self.doc["families"]:
            self.assertTrue(record["provenance"]["source_id"], record["id"])
            self.assertTrue(record["passages"], record["id"])
            self.assertEqual(set(record["interpretation"]), {
                "observed_visual", "drawn_analogy",
                "mathematical_family", "historical_implementation_limit",
            }, record["id"])
        self.assertTrue(any("current MAIN" in item for item in self.doc["claim_boundaries"]))
        self.assertTrue(any("old-typist 20-glyph" in item for item in self.doc["claim_boundaries"]))

    def test_t7_operator_boxes_and_source_rows_are_not_conflated(self) -> None:
        record = self.families["t7-texture-defined-regions"]
        regions = {p["operator_region"]: p for p in record["passages"]}
        self.assertEqual(set(regions), {"r1", "r2", "r3"})
        self.assertEqual(regions["r2"]["operator_label"],
                         "minimal glyphs showing branches going up into leaf")
        self.assertEqual(regions["r1"]["operator_label"], "root plus patchy grass, good")
        self.assertEqual(regions["r3"]["operator_label"], "falling leaves , good ")
        self.assertEqual(regions["r2"]["operator_rect_px"], {"x": 13, "y": 51, "w": 61, "h": 71})
        self.assertEqual(regions["r3"]["operator_rect_px"], {"x": 127, "y": 61, "w": 158, "h": 64})
        self.assertEqual(regions["r1"]["operator_rect_px"], {"x": 15, "y": 141, "w": 325, "h": 103})
        # The region-note excerpt labels row 7, while its paired full TXT passage
        # begins at row 8. Keep those source identities separate.
        self.assertEqual(regions["r1"]["line_start"], 8)
        self.assertTrue(regions["r1"]["operator_excerpt_rows"][0].startswith("7:"))
        self.assertIn("texture-defined boundary", record["interpretation"]["observed_visual"])
        self.assertEqual(record["pattern_family"], "texture-defined-boundaries")

    def test_c424_whole_piece_yes_does_not_become_region_approval(self) -> None:
        record = self.families["c424-bounded-punctuation-pockets"]
        provenance = record["provenance"]
        passage = record["passages"][0]
        self.assertEqual(provenance["operator_verdict"],
                         "yes for the whole piece (page index424), not the full AAHub page")
        self.assertTrue(record["title"].startswith("S#424"))
        self.assertNotIn("approved figure", record["title"])
        self.assertEqual(provenance["operator_note"], "")
        self.assertEqual(provenance["operator_rects"], [])
        self.assertIsNone(passage["operator_region"])
        self.assertIsNone(passage["operator_label"])
        self.assertIn("dot/colon-like", record["interpretation"]["observed_visual"])

    def test_hand_interior_marks_remain_analogy_not_math_claim(self) -> None:
        record = self.families["hand-open-interiors-across-ordered-views"]
        interpretation = record["interpretation"]
        self.assertIn("drawn analogy only", interpretation["drawn_analogy"])
        self.assertIn("not proven mathematical suggestive contours or ridges",
                      interpretation["mathematical_family"])
        self.assertIn("not normal-speed playback",
                      record["provenance"]["frame_review_method"])
        self.assertEqual(record["provenance"]["frame_count"], 96)
        samples = [p for p in record["passages"] if "frame_index" in p]
        self.assertEqual([p["frame_index"] for p in samples], [0, 24, 48, 72])
        self.assertEqual([p["angle_deg"] for p in samples], [0, 90, 180, 270])
        self.assertEqual(record["provenance"]["protected_voids_from_study"],
                         ["inter-finger webs", "thumb/palm recess"])
        self.assertIn("current MAIN", interpretation["historical_implementation_limit"])

    def test_multirow_joins_caps_and_text_only_candidates_keep_context(self) -> None:
        c126 = self.families["c126-framed-punctuation-and-y-turn"]
        self.assertEqual(c126["focus_forms"], ["∨／:x=ﾐ", "Ｙ＾Ｖ"])
        self.assertIn("not original-pixel identity",
                      c126["provenance"]["construction_record_status"])
        light = next(p for p in c126["passages"] if p["id"] == "c126-light-paper-and-tone-context")
        self.assertEqual(light["line_start"], 16)
        self.assertEqual(len(light["rows"]), 5)
        self.assertIn("not demonstrated principal-highlight", c126["interpretation"]["mathematical_family"])

        c99 = self.families["c99-receding-joined-pairs"]
        self.assertEqual(len(c99["passages"][0]["rows"]), 7)
        self.assertEqual(c99["annotation_status"] if "annotation_status" in c99 else
                         c99["provenance"]["annotation_status"],
                         "agent-observed; parent raw-text validated; not operator approval")
        self.assertEqual(c99["passages"][0]["rows"][1].count("|レi"), 1)
        self.assertIn("row returns", c99["title"])

        c135 = self.families["c135-shared-y-supports-and-cap-variants"]
        self.assertIsNone(c135["provenance"]["paired_native_png"])
        self.assertIn("no paired original native PNG", c135["provenance"]["native_image_status"])
        self.assertIn("Y＾Y＾Y", c135["focus_forms"])
        self.assertTrue(any("f⌒ヽ" in row for row in c135["passages"][0]["rows"]))

        cap = self.families["aahub-rounded-cap-exemplar"]
        self.assertEqual([x["corpus"] for x in cap["provenance"]["corpus_counts"]],
                         ["AA-003", "AA-004"])
        self.assertNotEqual(cap["provenance"]["corpus_counts"][0]["occurrences"],
                            cap["provenance"]["corpus_counts"][1]["occurrences"])
        self.assertIn("/⌒ヽ", cap["focus_forms"])
        for entry in cap["provenance"]["corpus_counts"]:
            corpus_id = "aa003" if entry["corpus"] == "AA-003" else "aa004"
            corpus_doc = json.loads(
                viewer.SJIS_CORPORA[corpus_id].read_text(encoding="utf-8")
            )
            measured = next(
                item for item in corpus_doc["viewable"]
                if item["category"] == "idiom" and item["key"] == entry["pattern"]
            )
            self.assertEqual(entry["occurrences"], measured["count"])
            self.assertEqual(entry["pages"], measured["pages"])
            self.assertEqual(entry["slugs"], measured["slugs"])

        raw = self.families["organic-person-underscore-unassigned"]
        self.assertEqual(raw["focus_forms"], ["人_"])
        self.assertIsNone(raw["provenance"]["paired_native_png"])
        self.assertEqual(raw["provenance"]["visual_evidence"], [])
        self.assertIn("No person", raw["interpretation"]["drawn_analogy"])

    def test_verbatim_passages_match_local_paired_text_when_available(self) -> None:
        checked = 0
        for record in self.doc["families"]:
            provenance = record.get("provenance", {})
            path = Path(provenance.get("text_path", ""))
            if not path.is_file():
                continue
            expected_text_hash = provenance.get("source_text_sha256_file")
            if expected_text_hash:
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 expected_text_hash, record["id"])
            image_path = Path(provenance.get("image_path", ""))
            expected_image_hash = provenance.get("source_image_sha256")
            if image_path.is_file() and expected_image_hash:
                self.assertEqual(hashlib.sha256(image_path.read_bytes()).hexdigest(),
                                 expected_image_hash, record["id"])
            source_rows = path.read_text(encoding="utf-8").splitlines()
            for passage in record.get("passages", []):
                if not passage.get("rows"):
                    continue
                start = int(passage.get("line_start", 1)) - 1
                actual = source_rows[start:start + len(passage["rows"])]
                if actual != passage["rows"]:
                    details = []
                    for offset, (source, stored) in enumerate(zip(actual, passage["rows"])):
                        if source != stored:
                            first_diff = next(
                                (i for i, pair in enumerate(zip(source, stored))
                                 if pair[0] != pair[1]),
                                min(len(source), len(stored)),
                            )
                            details.append({
                                "line": start + offset + 1,
                                "source_len": len(source),
                                "stored_len": len(stored),
                                "first_diff": first_diff,
                                "source_repr": ascii(source),
                                "stored_repr": ascii(stored),
                                "source_window": [
                                    (i, f"U+{ord(ch):04X}") for i, ch in enumerate(
                                        source[max(0, first_diff - 3):first_diff + 8],
                                        max(0, first_diff - 3),
                                    )
                                ],
                                "stored_window": [
                                    (i, f"U+{ord(ch):04X}") for i, ch in enumerate(
                                        stored[max(0, first_diff - 3):first_diff + 8],
                                        max(0, first_diff - 3),
                                    )
                                ],
                            })
                    self.fail(f"{record['id']} / {passage['id']} source-row mismatch: {details}")
                checked += 1
        if not checked:
            self.skipTest("private source-pair paths are not present in this checkout")
        self.assertGreater(checked, 0)

    def test_ordered_hand_glyph_samples_match_frame_records_when_available(self) -> None:
        record = self.families["hand-open-interiors-across-ordered-views"]
        frame_path = Path(record["provenance"]["frame_records_path"])
        if not frame_path.is_file():
            self.skipTest("turntable frame records are not present in this checkout")
        self.assertEqual(hashlib.sha256(frame_path.read_bytes()).hexdigest(),
                         record["provenance"]["frame_records_sha256"])
        frames = json.loads(frame_path.read_text(encoding="utf-8"))
        self.assertEqual(len(frames), record["provenance"]["frame_count"])
        samples = [p for p in record["passages"] if "frame_index" in p]
        for sample in samples:
            frame = frames[sample["frame_index"]]
            self.assertEqual(int(frame["angle"]), sample["angle_deg"])
            grouped: dict[int, list[dict]] = {}
            for glyph in frame["glyphs"]:
                grouped.setdefault(int(glyph["row"]), []).append(glyph)
            start = sample["glyph_row_start"]
            actual = [
                "".join(g["glyph"] for g in sorted(grouped[row], key=lambda g: g["x"]))
                for row in range(start, start + len(sample["glyph_rows"]))
            ]
            self.assertEqual(actual, sample["glyph_rows"], sample["id"])
            self.assertTrue(Path(sample["view_path"]).is_file(), sample["view_path"])
        gif_path = Path(record["provenance"]["turntable_gif_path"])
        if gif_path.is_file():
            self.assertEqual(hashlib.sha256(gif_path.read_bytes()).hexdigest(),
                             record["provenance"]["turntable_gif_sha256"])
        construction_path = Path(record["provenance"]["construction_record_path"])
        if construction_path.is_file():
            self.assertEqual(hashlib.sha256(construction_path.read_bytes()).hexdigest(),
                             record["provenance"]["construction_sha256"])

    def test_t7_region_excerpts_match_local_annotation_when_available(self) -> None:
        record = self.families["t7-texture-defined-regions"]
        note_path = Path(record["provenance"]["annotation_path"])
        if not note_path.is_file():
            self.skipTest("private T#7 annotation note is not present in this checkout")
        note = json.loads(note_path.read_text(encoding="utf-8"))
        by_label = {r["label"]: r for r in note["rects"]}
        for passage in record["passages"]:
            annotation = by_label[passage["operator_label"]]
            self.assertEqual(passage["operator_rect_px"], {
                key: annotation[key] for key in ("x", "y", "w", "h")
            })
            self.assertEqual(passage["operator_excerpt_rows"],
                             annotation["text"].splitlines())


class ContextViewerDiscovery(unittest.TestCase):
    def test_context_dump_is_discoverable_without_tty(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/glyph_families_viewer.py"),
             "--mode", "context", "--dump"],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("mode=context", result.stdout)
        self.assertIn("TEXT CONTEXT ONLY", result.stdout)
        self.assertIn("focus length=", result.stdout)
        self.assertIn("families=8", result.stdout)
        for family_id in (
            "t7-texture-defined-regions",
            "c424-bounded-punctuation-pockets",
            "hand-open-interiors-across-ordered-views",
            "organic-person-underscore-unassigned",
        ):
            self.assertIn(family_id, result.stdout)
        self.assertIn("rects=per passage", result.stdout)
        self.assertIn("mathematical_family", result.stdout)

    def test_combo_loader_includes_context_without_rebuilding_measured_data(self) -> None:
        fake_corpus = SimpleNamespace(i=lambda _cp: None)
        with (
            mock.patch.object(viewer, "load_combination_families", return_value=[]),
            mock.patch.object(viewer, "load_seam_families", return_value=[]),
            mock.patch.object(viewer, "load_sjis_corpus_families", return_value=[]),
            mock.patch.object(viewer, "load_pattern_families", return_value=[]),
        ):
            families = viewer.load_combo_families(fake_corpus, limit=1, corpus="aa004")
        self.assertTrue(families)
        self.assertEqual({f["mode"] for f in families}, {"combo"})
        ids = {f["context"]["id"] for f in families if f.get("context")}
        self.assertEqual(ids, set(json.loads(DATA.read_text())["families"][i]["id"]
                                  for i in range(8)))
        self.assertTrue(all(f["context"] for f in families))

    def test_interactive_detail_lines_keep_provenance_and_source_context(self) -> None:
        record = json.loads(DATA.read_text())["families"][0]
        lines = viewer._context_detail_lines(record, width=160)
        self.assertTrue(any("annotation status:" in line for line in lines))
        self.assertTrue(any("operator rectangles: per passage" in line for line in lines))
        self.assertTrue(any("operator region r2:" in line for line in lines))
        self.assertTrue(any("003: ヾ" in line for line in lines))
        self.assertTrue(any("mathematical family:" in line for line in lines))
        self.assertTrue(any("not native width" in line for line in lines))

    def test_default_browser_exposes_context_axis_as_well_as_combo(self) -> None:
        fake_corpus = SimpleNamespace(i=lambda _cp: None)
        with (
            mock.patch.object(viewer, "load_families", return_value=[]),
            mock.patch.object(viewer, "load_foliage_stroke_families", return_value=[]),
            mock.patch.object(viewer, "load_combination_families", return_value=[]),
            mock.patch.object(viewer, "load_seam_families", return_value=[]),
            mock.patch.object(viewer, "load_sjis_corpus_families", return_value=[]),
            mock.patch.object(viewer, "load_pattern_families", return_value=[]),
        ):
            families = viewer.load_default_families(fake_corpus, block=None, seam_limit=1)
        expected = {f['id'] for f in json.loads(DATA.read_text())['families']}
        for mode in ('context', 'combo'):
            self.assertEqual({f['context']['id'] for f in families if f['mode'] == mode}, expected)

    def test_interactive_details_do_not_hide_reconstruction_or_motion_sources(self) -> None:
        records = {r['id']: r for r in json.loads(DATA.read_text())['families']}
        c126 = '\n'.join(viewer._context_detail_lines(records['c126-framed-punctuation-and-y-turn'], 500))
        self.assertIn('construction record status:', c126)
        self.assertIn('not original-pixel identity', c126)
        hand = '\n'.join(viewer._context_detail_lines(records['hand-open-interiors-across-ordered-views'], 500))
        self.assertIn('turntable_gif_path:', hand)
        self.assertIn('frame_records_path:', hand)
        self.assertIn('not normal-speed playback', hand)


if __name__ == "__main__":
    unittest.main()
