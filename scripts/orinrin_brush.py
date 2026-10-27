"""Portable audit transcription of Orinrin BrushStringMake, including overshoot.

Derived from ViewKeyButton.cpp:943–1014, Copyright (C) 2011–2013
Orinrin/SikigamiHNQ, commit f5dd6da43198eccbf58fbe2eec71ebe8c7fdb874.
GPL-3.0-or-later; assets/glyphs/contextual/windows-aa/upstream/COPYING.
Widths are supplied by the caller, as the C++ asks its font-width functions.
This does not run the editor or infer a surface direction/density.
"""


def brush_string_make(target_width, pattern, string_width, char_width):
    width = string_width(pattern)
    if width <= 0 or target_width <= 0:
        return None
    count = target_width // width
    remainder = target_width - count * width
    result = pattern * count
    for char in pattern:
        if remainder <= 0:
            break
        result += char
        remainder -= char_width(char)
    return result
