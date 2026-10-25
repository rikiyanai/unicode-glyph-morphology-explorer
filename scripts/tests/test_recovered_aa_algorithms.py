from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import ascii_justice_kernels as justice
import orinrin_spacing as spacing
import recover_ascii_justice as recovery


class JusticeRecovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(recovery.INDEX.read_text())

    def test_recovered_source_hash_lines_and_decompiler_limits(self):
        doc = self.doc
        raw = (ROOT / doc["raw_source_path"]).read_bytes()
        text = (ROOT / doc["source_path"]).read_bytes()
        self.assertEqual(raw.decode("cp932").encode("utf-8"), text)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), doc["raw_source_sha256"])
        self.assertEqual(hashlib.sha256(text).hexdigest(), doc["source_sha256"])
        self.assertEqual(len(text.splitlines()), 919)
        self.assertEqual(text.decode().count("if var_59 < 0 var_62 var_59 = 0"), 2)
        self.assertIn("not validated", " ".join(doc["limits"]))
        self.assertEqual(doc["tool"]["commit"], recovery.TOOL_COMMIT)

    def test_embedded_payloads_match_original_executable_when_available(self):
        if not recovery.TARGET.exists():
            self.skipTest("optional original binary unavailable")
        binary = recovery.TARGET.read_bytes()
        self.assertEqual(hashlib.sha256(binary).hexdigest(), recovery.TARGET_HASH)
        for record in self.doc["embedded_payloads"]:
            offset = int(record["offset_in_executable"], 16)
            payload = binary[offset:offset + record["size"]]
            self.assertEqual(hashlib.sha256(payload).hexdigest(), record["sha256"])

    def test_first_index_fastest_mask_decode_matches_all_93_density_entries(self):
        masks = struct.unpack("<12288i", (recovery.OUTPUT / "mjdata14.dat").read_bytes())
        density = struct.unpack("<96i", (recovery.OUTPUT / "mjnodo14.dat").read_bytes())
        self.assertEqual(len(self.doc["candidate_characters"]), 93)
        for glyph in self.doc["glyphs"][:93]:
            i = glyph["index"]
            expected = ["".join("#" if masks[i + 96 * x + 768 * y] == 0 else "."
                                for x in range(8)) for y in range(16)]
            self.assertEqual(glyph["raster_rows"], expected)
            self.assertEqual(glyph["ink_px"], density[i])
            self.assertEqual(glyph["density_value"], density[i])
        self.assertTrue(all(r["char"] is None for r in self.doc["glyphs"][93:]))

    def test_exact_four_case_pixel_reward(self):
        self.assertEqual([justice.pixel_reward(s, t) for s, t in
                          [(True, True), (True, False), (False, True), (False, False)]],
                         [18, 3, -18, 6])

    def test_equal_density_opposite_curves_are_distinguished_by_ink_position(self):
        # Original recovered glyph masks, not a new drawing or converter output.
        left = next(g for g in self.doc["glyphs"] if g["char"] == "(")
        right = next(g for g in self.doc["glyphs"] if g["char"] == ")")
        self.assertEqual(left["ink_px"], 15)
        self.assertEqual(right["ink_px"], 15)
        for source, expected, other in ((left, left, right), (right, right, left)):
            scores = justice.outline_scores([[v == "#" for v in row] for row in source["raster_rows"]], "normal")
            self.assertGreater(scores[expected["index"]], scores[other["index"]])

    def test_outline_strict_channel_threshold_and_forward_thickness(self):
        # darkness 2 -> threshold 40; difference 40 is not enough, 41 is.
        rgb = [[(0, 0, 0)] * 8 for _ in range(16)]
        for row in rgb:
            row[3:] = [(40, 0, 0)] * 5
        self.assertFalse(any(any(row) for row in justice.outline_mask(rgb)))
        for row in rgb:
            row[3:] = [(41, 0, 0)] * 5
        for thickness in (1, 2, 3):
            mask = justice.outline_mask(rgb, thickness)
            self.assertEqual(mask, [[2 <= x < 2 + thickness for x in range(8)] for _ in range(16)])

    def test_original_untested_border_pairs_are_not_silently_repaired(self):
        rgb = [[(0, 0, 0)] * 8 for _ in range(16)]
        rgb[15] = [(255, 255, 255)] * 8
        self.assertFalse(any(any(row) for row in justice.outline_mask(rgb)))
        rgb = [[(0, 0, 0)] * 7 + [(255, 255, 255)] for _ in range(16)]
        self.assertFalse(any(any(row) for row in justice.outline_mask(rgb)))

    def test_scores_match_independent_recovered_mask_table_formula(self):
        mask = [[(3 * x + y) % 5 == 0 for x in range(8)] for y in range(16)]
        for quality, count in (("fast", 15), ("normal", 48), ("nice", 48), ("highest", 93)):
            result = justice.outline_scores(mask, quality)
            self.assertEqual(len(result), 285)
            for alignment in range(1 if quality in ("fast", "normal") else 3):
                for index in range(count):
                    score = 0
                    for x in range(8 if quality in ("fast", "normal") else 7):
                        for row in range(8):
                            y = row * 2 + ((x // 2) % 2)
                            src_x = x + (alignment == 1)
                            dst_x = x + (alignment == 2)
                            t = int(self.doc["glyphs"][index]["raster_rows"][y][dst_x] == ".")
                            score += ((6 - t * 5) if mask[y][src_x] else (-6 + t * 8)) * 3
                    self.assertEqual(result[index + 93 * alignment], score)
            self.assertEqual(result[279:], [0] * 6)


class OrinrinSpacing(unittest.TestCase):
    def test_unicode_table_all_remainders_and_widths(self):
        self.assertEqual([spacing.padding_unicode(i) for i in range(1, 12)],
                         ["\u200a", "\u2009", "\u2006", "\u2005", " ", "\u200a ",
                          "\u2009 ", "\u2002", "\u2005 ", "\u2007", "　"])
        for width in range(1, 1001):
            self.assertEqual(spacing.assumed_width(spacing.padding_unicode(width)), width)
        self.assertIsNone(spacing.padding_unicode(0))

    def test_plain_spaces_exhaustively_match_representable_widths(self):
        for width in range(1, 1001):
            text = spacing.padding_plain(width)
            possible = any((width - 11 * full) % 5 == 0 for full in range(width // 11 + 1))
            self.assertEqual(text is not None, possible, width)
            if text is not None:
                self.assertEqual(spacing.assumed_width(text), width)
                self.assertLessEqual(set(text), {" ", "　"})
        self.assertEqual(spacing.padding_plain(16), "　 ")
        self.assertEqual(spacing.padding_plain(21), " 　 ")
        self.assertIsNone(spacing.padding_plain(4))


if __name__ == "__main__":
    unittest.main()
