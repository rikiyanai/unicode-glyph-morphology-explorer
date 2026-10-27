#!/usr/bin/env python3
"""Package the operator's 2026-10-26 circle My MLT; never publish the draft.

--write --mlt PATH owns contextual/profile-circle-20261026/ and
profile_circle_evidence.v1.json only. Viewing validates packaged artifacts and
needs neither the private account, source archive nor comparison font.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/glyphs/contextual"
OUT = BASE / "profile_circle_evidence.v1.json"
ART = BASE / "profile-circle-20261026"
ARCHIVE = Path("/Users/r/Projects/ascii-art-archive/collections/aahub-mlt")
FONT = Path("/Users/r/Projects/ascii-art-archive/collections/aahub/Saitamaar.ttf")
SCHEMA = "glyph_morphology.profile_circle_evidence.v1"
PROFILE = "https://aahub.org/mlts/6zbpnrsgp96r"
CHURCH = "2f0353dc8e23bde120d1c050746f937c"
# Exact whole-text matches discovered against all 13,981 pinned archive pages.
# Positions are zero-based in the My MLT, not public archive post numbers.
SOURCES = [(CHURCH, i) for i in
           [33, 33, 34, 36, 48, 52, 52, 54, 57, 57, 58, 73, 74, 97,
            98, 120, 126, 130, 133, 134, 134, 135, 147, 151, 160, 162,
            162, 165, 166, 135]] + [
    ("5cb42e8a1adf7fc1d97b8f776debbff4", 93),
    ("f3983b8012cde80d6c7219f390569b84", 76),
    ("f3983b8012cde80d6c7219f390569b84", 84),
    ("f3983b8012cde80d6c7219f390569b84", 315),
    ("af2d0567b491b61bd90183e58b2bb1bf", 65),
    ("d08548555a8be6fa373d54ff8925cd03", 101),
    ("8510df5d530fcc44cb6b6fac937b4c27", 61),
    ("0bd77d32b9d0101dd0eb6a3104ae4e15", 55),
    ("0bd77d32b9d0101dd0eb6a3104ae4e15", 69),
    ("af2d0567b491b61bd90183e58b2bb1bf", 144),
    ("f2c6919c2b6efd385116f35e107987b9", 26),
    ("8510df5d530fcc44cb6b6fac937b4c27", 165),
    ("8510df5d530fcc44cb6b6fac937b4c27", 217),
    *[("ddd5a07a469de526bc78d56073e70b03", i) for i in [115, 117, 219, 220]],
    *[("f452585ab8d54d61a7f6701f85934209", i) for i in [95, 108, 145]],
    ("7a9ec10846347e9f3860befc2d7b0ffc", 18),
]
ALSO = {
    35: [("b685f3a6d5138cc70aced415d448b373", 261)],
    40: [("8510df5d530fcc44cb6b6fac937b4c27", 141)],
}
# (title, one-based original TXT rows, exact fragments, retained relationship).
# Fragments locate evidence; they are NOT normalized or complete circle stencils.
CURATION = {
    0: ("Martorana: nested arch bands and a rounded return", (8, 18), ["/⌒'ﾊ", "弋____ノ"], "Nested arch boundaries, thickness and the opening cooperate across rows."),
    2: ("Santa Maria Maggiore: tower round", (12, 20), ["Ｙ⌒Ｙ", "乂_ノ"], "The tower's compact round has paired shoulders, a return and enclosing architecture."),
    3: ("Assisi: compact cap and return", (7, 8), ["γ⌒ヽ", "乂__ノ"], "Cap and return preserve the enclosed paper; this is one spelling, not the vocabulary."),
    4: ("Notre Dame: round and partially hidden rounds", (7, 18), ["γ⌒ヽ", "弋＿ノ", "乂___,"], "Full and partly occluded rounds coexist with structural columns; do not close hidden ink."),
    5: ("Aachen: dome cap and flat base", (10, 11), ["γ⌒ヽ", "{＿＿}"], "A domed cap terminates on a flat base; not every cap encloses a circle."),
    7: ("St Paul's: nested medallions and ribbed dome", (11, 16), ["Ｙ⌒Ｙ", "乂_ン", "≧=≦"], "Inner rounds, outer frames and dome ribs have different roles and must not merge."),
    8: ("Krakow: three different rounded constructions", (9, 14), ["ｘ=ミ", "λ＿,ﾉ", "γ⌒ヽ", "乂__乂", "(__)", "乂__ソ"], "Tall round, small flattened ovals and shorter round retain different side/return spellings."),
    10: ("Canterbury: receding curved bands", (1, 21), ["｡o--o｡", "γ⌒ＹＹ⌒ヽ"], "Repeated arch bands recede in depth; their crowns, flanks and gaps change together."),
    11: ("Basement: thick turning arch band", (7, 17), ["ｲ二㌃゜", "ｲﾆア゜", "/ﾆｱ", "寸ム", "寸ﾊ", "∨i,", "Ⅵｉ"], "Multi-stroke band changes from shallow crown to steep flanks around open regions and a pillar."),
    12: ("Dominion chapel: framed round and oval ornament", (3, 17), ["｡o≦==≧o｡", "寸ﾐﾑ", "（ ＿||＿ ）", "（ ￣||￣ ）"], "Outer thick band, inner opening and vertically stacked oval ornament are distinct constructions."),
    13: ("Interior: stacked rounded figure and arch", (4, 7), ["(　)", "/⌒Ｙ", "乂__ﾉ"], "Small oval above a larger rounded form; retain its attachment and nearby arch, not an isolated token."),
    14: ("Interior altar: repeated cap/return frieze", (13, 18), ["f⌒Y", "Y⌒Y", "乂乂"], "Repeated rounds share a band rhythm without becoming one continuous filled stripe."),
    15: ("Stained glass: ring of cooperating rounded cells", (3, 34), ["／￣￣＼", "＼＿＿＿,／", "≧=‐-‐=≦"], "Outer dotted rim, inner ring, rounded cells and intervening paper form a nested arrangement."),
    16: ("Ruined church: interrupted arch returns", (10, 18), ["ｘ=ミ", "j{⌒Ｖ", "/⌒ヽ"], "Broken architecture deliberately interrupts curves; missing masonry is not a demand for closure."),
    17: ("Sewu: grouped carved caps and returns", (7, 14), ["γ⌒l__f⌒Y", "弋ﾆﾆｨ⌒弋ﾆf"], "Small adjacent carved lobes attach to a larger mass, with repeated lower transitions."),
    18: ("Hagia Sophia: thick dome and nested arches", (2, 12), ["ﾏﾑ", "寸i,", "∩∩"], "Dome ribs, turning arch bands and small repeated apertures stay distinct."),
    19: ("Hagia Sophia: medallions on a dome interior", (25, 30), ["γ⌒ヽ", "乂__:ノ"], "Rounded medallions and partly hidden neighbors sit on the larger vaulted volume."),
    21: ("Umayyad Mosque: repeated arch bays", (14, 23), ["f⌒Y", "Ｙ⌒YY", "Y⌒YY⌒"], "Adjacent arches use shared supports and changing projected widths; not separate circles pasted over columns."),
    22: ("Crescent: nested curves and bounded tone", (2, 8), ["-= ､‐ ､", "｀ ｰ- ‐ ´"], "Inner concavity, outer round and bounded punctuation describe a crescent, not a closed disk."),
    23: ("Ajanta: carved, layered arch", (5, 12), ["xく⌒＞", "ｲ⌒>", "ﾉ＿＿_乂"], "Crown ornaments, turning thick band and lower supports surround one opening."),
    24: ("Halloween: rounded pumpkin masses", (11, 24), ["／⌒⌒ヽ", "川", "彡′"], "Lobed volumes, faces and directional side/return marks cooperate; not empty-circle outlines."),
    25: ("Necrovalley altar: another compact return", (15, 17), ["γ⌒ヽ", "ゝ._ ノ"], "A different lower return closes the compact round above its support."),
    27: ("Karnak: shallow column-cap arc", (7, 13), ["jI斗-─--ミ", "i{ー彡"], "A shallow crown transitions to steep side and lower surface marks; it is not a complete circle."),
    28: ("Altar: broad perspective ellipse and thick rim", (6, 20), ["｛=-", "⌒≧s｡", "三三三こ=-"], "Nested elliptical rim, changing thickness, surface marks and paper express a tilted plane."),
    30: ("Flowers: overlapping petals, bowls and vessel rims", (5, 22), ["(⌒y'⌒)", "（⌒大⌒)", "ヾ､;.＿＿,;ノ"], "Petal lobes overlap; bowl/plate ellipses and vessel returns have separate depth and tone roles."),
    31: ("Rounded character: chained scallops and shared returns", (1, 7), ["γ⌒Ｙ⌒ﾝ´｀ヽ", "γ⌒ｿ", "乂＿__メ"], "Several lobes form one outline with shared turns, not a row of independent circular stamps."),
    32: ("Postal character: nested eye circles and broad return", (5, 11), ["Ｙ⌒Ｙ", "人__人", "乂__", "ミ=-"], "Small paired rounds sit inside a larger U-like envelope, with distinct shared returns."),
    33: ("Round character: long lost-and-found envelope", (1, 20), ["_,,,　　　,,,_", "｀ ‐---‐ ´", "弋 ノ"], "A large round body uses shallow crown, shoulders, flanks, interrupted spans and lower turns."),
    34: ("Fruit clusters: overlapping small rounded units", (4, 12), ["⌒X⌒", "人__ﾉ", "ゝ_ﾑ-kイ"], "Many rounded units overlap and occlude, with changing exposed caps and lower returns."),
    35: ("Face: concentric and tilted eye rims", (2, 15), ["}_＞-ヾ_-", "',::..__ ノ' /"], "Eye opening, eyelid and surrounding facial turn are nested but nonconcentric in perspective."),
    36: ("Ruins: compact round against masonry", (16, 18), ["γ⌒ヽ", "乂__ノ"], "The same compact vocabulary serves a different setting; surrounding contacts distinguish its use."),
    37: ("Japanese room: vessel rims and paired lower lobes", (18, 24), ["ｉ´.:.:.:｀ｉ", "乂_,,乂", "{｀¨¨¨¨´}", "乂;;;,,　 ノ"], "Elliptical rims and changing side/return tone construct vessels, not a brightness ramp alone."),
    38: ("Japanese room: small vase and rounded return", (17, 23), ["(__)", "γ＾ヽ", "乂_乂"], "Different small vessels preserve rim/neck/body correspondence at different widths."),
    39: ("Cherries: two overlapping shaded rounds", (4, 8), ["ゝ⌒ヽ", "､ ..:::,ノ", "ヽ､_..::::::ノ"], "Two attached rounded fruits share stems, depth order and bounded side shading."),
    40: ("Laboratory ruins: large round opening with depth", (8, 17), ["_,.二二._", "──=彡"], "The rim, shaded interior, wall plane and interrupted lower edge construct an opening with depth."),
    41: ("Cylinder debris: elliptical ends in different orientations", (1, 15), ["_ ,, -- ― -- ,, _", "|¨≧＝==＝≦¨|", "ー　＿ -　\""], "Elliptical end faces and side walls change with cylinder orientation and occlusion."),
    42: ("Wall opening: tilted nested ellipse and runoff", (3, 16), ["／: _", "＞.、＿＿ ,"], "Inner and outer elliptical boundaries enclose a shaded recess; runoff begins below the opening."),
    43: ("Eyes: nested round openings and thick lower bands", (1, 9), ["ヾ:::::::::::ノ", "ﾏ＞...､＿＿＿,...ィﾀ", "＝==＝"], "Pupil/iris openings, outer eye rim, thick band and paper are selected together."),
    44: ("Eye: partial face with nested round and pupil", (10, 17), ["-‐‐=＝＝", "{　 ●　 l", "ゞ__ 　.ﾉ"], "Eyebrow/lid, iris and pupil have different curvature and tone; surrounding face remains visible."),
    45: ("Large eye: broad round with edge-bound tone", (2, 12), ["｀ー::::::::::::::::＿-‐"], "Shallow crown, sides and lower turn cooperate with a nonuniform bounded tone field."),
    46: ("Eye: tiny round highlight inside a large envelope", (1, 12), ["〃⌒Y", "乂__ノ", "弋こﾘ"], "Small highlight, inner dark mark, outer round and eyelid are separate nested features."),
    47: ("Dog: rounded eyes inside textured head", (4, 20), ["γ oヽ", "ゝ .ノ", "乂 .ノ", "__彡´"], "Compact eye rounds sit inside a fur-edged round envelope; texture can carry the contour."),
    48: ("Dog: fur turns and paired mouth returns", (1, 16), ["ﾐ", "シ", "乂＿_乂"], "Texture bundles turn with the head; paired lower returns belong to the mouth, not the fur boundary."),
    49: ("Dog: long curved body and facial return", (1, 24), ["-‐… -ﾐ", "＼_彡'⌒丶", "`ー―― '''\"´`ー---‐''\""], "Long body arcs, ear/neck turns and supporting contacts read together; no closed-circle requirement."),
    50: ("Plant: overlapping round berries with side tone", (1, 8), ["_{x : . 　. :､}", "ヽ._,_._,ソ⌒>", "_,_._,ソ⌒>"], "Individual berries keep cap, side tone, return, attachment and foreground/background order."),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def split_export(data):
    text = data.decode("utf-8-sig").replace("\r\n", "\n")
    stamp, text = text.split("\n", 1)
    if stamp != "2026/10/26 05:03:38":
        raise ValueError("Unexpected export revision; re-inspect before updating curation")
    return [part.strip("\n") for part in text.split("[SPLIT]")]


def render(rows, path):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(FONT), 16)
    width = math.ceil(max(sum(font.getlength(ch) for ch in row) for row in rows)) + 16
    image = Image.new("L", (width, len(rows) * 17 + 16), 255)
    draw = ImageDraw.Draw(image)
    for y, row in enumerate(rows):
        x = 8.0
        for ch in row:
            draw.text((x, 8 + y * 17), ch, font=font, anchor="la", fill=0)
            x += font.getlength(ch)
    image.save(path)
    return image.size


def build(mlt):
    data = Path(mlt).read_bytes()
    entries = split_export(data)
    if len(entries) != 51:
        raise ValueError("The inspected revision has exactly 51 entries")
    ART.mkdir(parents=True, exist_ok=True)
    export = ART / "circle.utf8.mlt"
    export.write_bytes(data)
    hashes = {str(export.relative_to(ROOT)): sha(data)}
    pages, records, by_text = {}, [], {}
    for n, (page_key, index) in enumerate(SOURCES):
        bindings = [(page_key, index), *ALSO.get(n, [])]
        matches = []
        for key, pos in bindings:
            path = ARCHIVE / key[:2] / f"{key}.json.gz"
            if key not in pages:
                pages[key] = json.loads(gzip.decompress(path.read_bytes()))
            raw = pages[key]["aa"][pos]["value"]
            decoded = html.unescape(raw)
            if entries[n].strip() != decoded.strip():
                raise ValueError(f"Export/archive text mismatch at profile entry {n}")
            matches.append({"source_url": f"https://aahub.org/mlt/{key}", "archive_piece_index": pos,
                            "archive_file_sha256": sha(path.read_bytes())})
        key = sha(decoded.strip().encode())
        if key in by_text:
            by_text[key]["provenance"]["profile_entry_indices"].append(n)
            continue
        # Use the first original as canonical text; retain all exact archive matches.
        raw = pages[page_key]["aa"][index]["value"]
        decoded = html.unescape(raw)
        title, (start, end), forms, relation = CURATION[n]
        rows = decoded.splitlines()
        passage = rows[start - 1:end]
        for form in forms:
            if form not in "\n".join(passage):
                raise ValueError(f"Unverified focus form at {n}: {form!r}")
        stem = f"entry-{n:02}"
        raw_path, txt_path, png_path = [ART / (stem + ext) for ext in (".raw.txt", ".txt", ".png")]
        raw_path.write_text(raw, encoding="utf-8")
        txt_path.write_text(decoded, encoding="utf-8")
        width, height = render(rows, png_path)
        for p in (raw_path, txt_path, png_path):
            hashes[str(p.relative_to(ROOT))] = sha(p.read_bytes())
        record = {"id": f"profile-circle-{n:02}", "title": title,
                  "pattern_family": "operator-profile-rounded-construction", "focus_forms": forms,
                  "native_reference": {"width": width, "height": height, "kind": "saitamaar-comparison"},
                  "provenance": {"source_id": f"My MLT circle entry {n}; original aa[{index}]",
                      "source_url": matches[0]["source_url"], "profile_url": PROFILE,
                      "profile_entry_indices": [n], "profile_visibility": "private draft; unchanged",
                      "text_path": str(txt_path.relative_to(ROOT)), "raw_text_path": str(raw_path.relative_to(ROOT)),
                      "image_path": str(png_path.relative_to(ROOT)), "archive_matches": matches,
                      "source_text_sha256_file": hashes[str(txt_path.relative_to(ROOT))],
                      "source_image_sha256": hashes[str(png_path.relative_to(ROOT))],
                      "reference_registry_path": str(OUT.relative_to(ROOT)),
                      "annotation_status": "operator-selected list membership; feature readings are root interpretations, not new operator rectangle labels",
                      "native_image_status": "NEW Saitamaar 16px/17px-row comparison from exact original TXT; NOT a recovered original PNG or browser screenshot",
                      "source_binding_status": "whole original text matched; only outer whitespace ignored for matching; originals preserved unchanged",
                      "context_limit": "Zero-based profile positions and archive aa indices are different namespaces. Still reference only; no temporal or renderer acceptance."},
                  "passages": [{"id": stem + "-rounded-region", "line_start": start, "rows": passage,
                                "operator_label": None}],
                  "interpretation": {"observed_visual": relation,
                      "drawn_analogy": "Compare the complete form, neighboring rows, enclosed paper and purposeful tone; focus fragments are locators, not independent stamps.",
                      "mathematical_family": "Visual rounded construction; no curvature detector is inferred.",
                      "historical_implementation_limit": "Original editor/workflow unverified. No fixed circle alphabet, runtime algorithm, GIF behavior or universal thickness follows."}}
        records.append(record)
        by_text[key] = record
    doc = {"schema": SCHEMA, "profile_url": PROFILE, "inspected_date": "2026-10-26",
           "entry_count": len(entries), "distinct_drawing_count": len(records),
           "font_sha256": sha(FONT.read_bytes()), "image_profile": "Saitamaar 16px, 17px row pitch, whole glyph advances; comparison only",
           "export_path": str(export.relative_to(ROOT)), "artifact_hashes": hashes, "families": records}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def load():
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise ValueError("Unsupported profile circle snapshot")
    for name, expected in doc["artifact_hashes"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ART.resolve()) or sha(path.read_bytes()) != expected:
            raise ValueError(f"Profile circle artifact changed: {name}")
    return doc


def extend(doc):
    return {**doc, "families": [*doc["families"], *load()["families"]]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--mlt", type=Path)
    args = parser.parse_args()
    if args.write and not args.mlt:
        parser.error("--write requires --mlt")
    doc = build(args.mlt) if args.write else load()
    print(f"{doc['entry_count']} profile entries; {doc['distinct_drawing_count']} distinct drawings")
