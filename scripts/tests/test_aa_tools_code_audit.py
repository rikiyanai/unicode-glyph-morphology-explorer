from pathlib import Path
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import orinrin_brush as brush
import aa_tools_code_audit as audit


class CodeAndComboAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = audit.load()

    def test_pinned_source_identity_and_decoded_copies(self):
        source = self.doc["orinrin_source"]
        self.assertEqual(source["commit"], "f5dd6da43198eccbf58fbe2eec71ebe8c7fdb874")
        self.assertEqual(source["source_file_count"], 57)
        self.assertEqual(len(source["retained_source_files"]), 9)
        for record in source["retained_source_files"]:
            raw = (ROOT / record["raw_path"]).read_bytes()
            decoded = (ROOT / record["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record["raw_sha256"])
            self.assertEqual(hashlib.sha256(decoded).hexdigest(), record["utf8_sha256"])
            self.assertEqual(raw.decode("cp932").encode("utf-8"), decoded)

    def test_exact_inputs_and_all_38_fragments(self):
        for path, expected in self.doc["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)
        self.assertEqual(sum(len(r["fragments"]) for r in self.doc["records"]), 38)
        self.assertEqual((self.doc["justice_candidate_count"], self.doc["aaj_composite_count"], self.doc["orinrin_palette_group_count"]), (93, 40, 24))

    def test_justice_cannot_directly_emit_each_complete_supplied_construction(self):
        for record in self.doc["records"]:
            self.assertTrue(any(p["justice_missing_characters"] for p in record["fragments"]), record["id"])
        cup = next(r for r in self.doc["records"] if r["id"] == "aramaki-cup-plate-surface-following-tone")
        missing = set(c for p in cup["fragments"] for c in p["justice_missing_characters"])
        self.assertTrue({"彡", "彳", "ジ", "<"}.issubset(missing))

    def test_no_multi_character_fragment_is_a_whole_recovered_preset(self):
        for record in self.doc["records"]:
            for part in record["fragments"]:
                self.assertFalse(part["aaj_equal_composite"])
                if len(part["text"]) > 1:
                    self.assertEqual(part["orinrin_palette_contains_entire_fragment"], [])
        self.assertIn("full pinned alphabet is now audited", " ".join(self.doc["limits"]))

    def test_full_aaj_alphabet_excludes_required_glyphs_in_every_construction(self):
        for record in self.doc["records"]:
            self.assertTrue(any(p["aaj_missing_characters_both_modes"] for p in record["fragments"]), record["id"])
        cup = next(r for r in self.doc["records"] if r["id"] == "aramaki-cup-plate-surface-following-tone")
        missing = {c for p in cup["fragments"] for c in p["aaj_missing_characters_both_modes"]}
        self.assertTrue({"<", "ン", "彡", "彳", "ジ"}.issubset(missing))

    def test_aaj_constants_and_direct_tone_branches_are_retained_exactly(self):
        import struct
        doc = json.loads((ROOT / self.doc["aaj_alphabet"]["path"]).read_text())
        for row in doc["constants"]:
            raw = bytes.fromhex(row["bytes_hex"])
            self.assertEqual(len(raw), row["byte_length"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            self.assertEqual(raw.decode(row["encoding"]), row["text"])
        self.assertEqual(doc["proportional_internal_alphabet"], "".join(r["text"] for r in doc["constants"][:4]) * 2)
        self.assertEqual(doc["reachable_multichar_mapping_count"], 39)
        self.assertEqual([(r["label"], r["text"]) for r in doc["unreachable_builder_mappings"]], [("W", "^^")])
        self.assertEqual([r["text"] for r in doc["direct_tone_or_blank_outputs"]],
                         ["　", "....", ":.:.", ";,;,", ";;;;", "i.i.", "i;i;", "lili", "llll", " ", ".", ":", "i", "C", "X", "Q", "W", "M"])
        self.assertIn("W", doc["monospaced_output_characters_upper_bound"])
        self.assertNotIn("W", doc["monospaced_internal_alphabet"])
        for row in doc["direct_tone_or_blank_outputs"]:
            raw = bytes.fromhex(row["bytes_hex"])
            self.assertEqual(raw.decode("cp932"), row["text"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
        pe_path = audit.WORK / "aaj/aaj.exe"
        if pe_path.exists():
            from windows_aa_intake import PinnedPE
            pe = PinnedPE(pe_path.read_bytes())
            for row in doc["constants"]:
                offset = pe.offset(int(row["va"], 16))
                length = struct.unpack_from("<I", pe.data, offset - 4)[0]
                self.assertEqual(pe.data[offset:offset + length], bytes.fromhex(row["bytes_hex"]))
            self.assertEqual(audit.recover_aaj_alphabet(), doc)

    def test_every_additional_library_hit_has_exact_source_locator_and_kind(self):
        for record in self.doc["records"]:
            for part in record["fragments"]:
                for hit in part["orinrin_other_saved_text_contains_fragment"]:
                    rows = (ROOT / hit["path"]).read_text().splitlines()
                    self.assertEqual(rows[hit["line"] - 1], hit["text"])
                    self.assertIn(part["text"], hit["text"])
                    if hit["path"].endswith("lettering-3.ast"):
                        self.assertIn("not a preset", hit["kind"])

    def test_browser_reports_each_exact_source_and_its_exclusions(self):
        import construction_tool_mapping as mapping
        doc = mapping.load()
        for record in doc["records"]:
            details = "\n".join(mapping.detail_lines({**record, "limit": doc["limit"]}))
            self.assertIn("SOURCE-CODE CAPABILITY AUDIT", details)
            self.assertIn("AAJ cannot directly emit:", details)
            self.assertIn("not just its 40", details)

    def test_brush_preserves_exact_pattern_and_whole_glyph_overshoot(self):
        widths = {"彡": 16, ".": 3, ";": 3, " ": 5}
        char_width = widths.__getitem__
        string_width = lambda s: sum(char_width(c) for c in s)
        result = brush.brush_string_make(17, "彡", string_width, char_width)
        self.assertEqual(result, "彡彡")
        self.assertEqual(string_width(result), 32)
        self.assertEqual(brush.brush_string_make(7, ".;", string_width, char_width), ".;.")
        self.assertEqual(brush.brush_string_make(16, ". ", string_width, char_width), ". . ")
        self.assertIsNone(brush.brush_string_make(0, "彡", string_width, char_width))
        self.assertIsNone(brush.brush_string_make(5, "", string_width, char_width))

    def test_active_brush_entry_and_multirow_materialisation_are_present(self):
        base = ROOT / "assets/glyphs/contextual/windows-aa/code-audit"
        keys = (base / "ViewKeyButton.cpp").read_text()
        handler = keys[keys.index("VOID Evw_OnLButtonUp("):keys.index("HRESULT ViewBrushStyleSetting(")]
        self.assertIn("ViewBrushFilling(  );", handler)
        brush_func = keys[keys.index("LPTSTR BrushStringMake("):]
        self.assertIn("dCnt = dDotLen / dPtnDot", brush_func)
        self.assertIn("wsBuff += ptPattern[i]", brush_func)
        materialise = (base / "ViewCentral.cpp").read_text()
        self.assertIn("LayerBoxVisibalise( ghInst, ptString", materialise)
        self.assertIn("DocInsertString( &gdDocXdot, &gdDocLine, NULL, ptString, D_SQUARE", materialise)


if __name__ == "__main__":
    unittest.main()
