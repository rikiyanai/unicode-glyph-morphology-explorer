from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import construction_tool_mapping as mapping
import glyph_families_viewer as viewer
import operator_construction_crops as crops


class ConstructionToolMapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = mapping.load()
        cls.records = {r["id"]: r for r in cls.doc["records"]}

    def test_exact_fragments_and_codepoint_locations(self):
        self.assertEqual(sum(len(r["fragments"]) for r in self.records.values()), 38)
        for record in self.records.values():
            rows = (ROOT / record["source_path"]).read_text().splitlines()
            for part in record["fragments"]:
                start = part["source_codepoint_start"]
                self.assertEqual(rows[part["line"] - 1][start:start + len(part["text"])], part["text"])
                self.assertEqual("".join(p["char"] for p in part["placements"]), part["text"])
                for i, placement in enumerate(part["placements"]):
                    self.assertEqual(placement["source_codepoint"], start + i)
                    if i:
                        prev = part["placements"][i - 1]
                        self.assertEqual(placement["x_px"], prev["x_px"] + prev["advance_px"])

    def test_all_overlap_locators_are_exact_not_normalized(self):
        for record in self.records.values():
            for part in record["fragments"]:
                for key in ("palette_overlaps", "aaj_overlaps"):
                    for match in part[key]:
                        shared = match["shared_text"]
                        for pos in match["fragment_offsets"]:
                            self.assertEqual(part["text"][pos:pos + len(shared)], shared)
                        for pos in match["candidate_offsets"]:
                            self.assertEqual(match["text"][pos:pos + len(shared)], shared)
                        if "line" in match:
                            self.assertEqual((ROOT / match["path"]).read_text().splitlines()[match["line"] - 1], match["text"])
        self.assertEqual(mapping.overlaps("ﾆア", [{"text": "ニア"}]), [])

    def test_small_circle_matches_fragments_not_whole_template(self):
        cap, sides = self.records["operator-curve-crop-03"]["fragments"]
        self.assertEqual({m["shared_text"] for m in cap["palette_overlaps"]}, {"γ⌒", "⌒ヽ", "'´"})
        self.assertTrue(all(not m["covers_entire_fragment"] for m in cap["palette_overlaps"]))
        self.assertTrue(all(not m["covers_entire_fragment"] for m in sides["palette_overlaps"]))
        self.assertEqual(sides["aaj_overlaps"], [])

    def test_forty_composites_are_not_claimed_to_be_full_output_vocabulary(self):
        self.assertIn("NOT its complete character vocabulary", self.doc["limit"])
        self.assertIn("does not rule out assembly by successive selections", self.doc["limit"])

    def test_newly_matched_lobes_retain_all_repeat_positions(self):
        record = self.records["operator-curve-crop-04"]
        self.assertIn("not unique attribution", record["reading"])
        for part in record["fragments"]:
            self.assertEqual(len(part["source_codepoint_starts"]), 2)
            self.assertIn("represent first occurrence only", part["placement_status"])

    def test_specific_arch_shoulders_not_in_saved_multichar_presets(self):
        parts = {p["text"]: p for p in self.records["operator-curve-crop-06"]["fragments"]}
        for text in ("ｲﾆア゜", "/ﾆｱ", "寸ム", "寸ﾊ", "Ⅵｉ"):
            self.assertEqual(parts[text]["palette_overlaps"], [])
            self.assertEqual(parts[text]["aaj_overlaps"], [])
            self.assertTrue(parts[text]["ascii_justice_unavailable_characters"])

    def test_native_comparison_positions_reproduce(self):
        # Optional font is needed only to verify/rebuild, never to browse.
        if not mapping.FONT.is_file():
            self.skipTest("Pinned local comparison font unavailable")
        from PIL import ImageFont
        font = ImageFont.truetype(str(mapping.FONT), 16)
        self.assertEqual(mapping.digest(mapping.FONT), mapping.FONT_HASH)
        for record in self.records.values():
            rows = (ROOT / record["source_path"]).read_text().splitlines()
            for part in record["fragments"]:
                row = rows[part["line"] - 1]
                for p in part["placements"]:
                    self.assertEqual(p["x_px"], sum(font.getlength(c) for c in row[:p["source_codepoint"]]))
                    self.assertEqual(p["advance_px"], font.getlength(p["char"]))

    def test_cup_brush_overlap_does_not_claim_automatic_surface_rule(self):
        record = self.records["aramaki-cup-plate-surface-following-tone"]
        band = next(p for p in record["fragments"] if p["line"] == 9)
        self.assertIn("彡", [m["text"] for m in band["brush_items_inside_fragment"]])
        text = "\n".join(mapping.detail_lines({**record, "limit": self.doc["limit"]}))
        self.assertIn("not an arrangement rule", text)

    def test_round_and_cup_context_panes_expose_mapping(self):
        doc = crops.load()
        corpus = crops.ConstructionCorpus(doc)
        families = viewer.load_round_families(corpus, doc=doc)
        self.assertEqual(len(families), 8)
        for family in families:
            record = family["context"]
            self.assertEqual("tool_mapping" in record, record["id"] in self.records)
        arch = next(f["context"] for f in families if f["context"]["id"] == "operator-curve-crop-06")
        self.assertIn("CONSTRUCTION / TOOL COMPARISON", "\n".join(viewer._context_detail_lines(arch, 100)))
        cup = next(f["context"] for f in viewer.load_context_families(corpus)
                   if f["context"]["id"] == "aramaki-cup-plate-surface-following-tone")
        self.assertIn("tool_mapping", cup)

    def test_cli_browsing_needs_no_font(self):
        code = "import sys;sys.path.insert(0,sys.argv[1]);import construction_tool_mapping as m;m.FONT=m.Path('/no/font');print(len(m.load()['records']))"
        result = subprocess.run([sys.executable, "-c", code, str(ROOT / "scripts")], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "9")


if __name__ == "__main__":
    unittest.main()
