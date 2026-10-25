"""Portable transcription of Orinrin's selected spacing routines.

Derived from DocAdjustant.cpp, Copyright (C) 2011–2013 Orinrin/SikigamiHNQ,
commit f5dd6da43198eccbf58fbe2eec71ebe8c7fdb874. GPL-3.0-or-later applies
to this file; license: assets/glyphs/contextual/windows-aa/upstream/COPYING.
It retains that editor's assumed widths, not newly measured font metrics.
"""
from __future__ import annotations

WIDTHS = {"　": 11, " ": 5, "\u200a": 1, "\u2009": 2,
          "\u2006": 3, "\u2005": 4, "\u2002": 8, "\u2007": 10}
REMAINDERS = ("", "\u200a", "\u2009", "\u2006", "\u2005", " ",
              "\u200a ", "\u2009 ", "\u2002", "\u2005 ", "\u2007")


def assumed_width(text):
    return sum(WIDTHS[ch] for ch in text)


def padding_unicode(dots):
    """DocPaddingSpaceUni: 11-dot full spaces plus a remainder-table suffix."""
    if dots <= 0:
        return None
    full, remainder = divmod(dots, 11)
    return "　" * full + REMAINDERS[remainder]


def padding_plain(dots):
    """DocPaddingSpace + SpaceWidthAdjust + SpaceStrAlloc (exact ordering)."""
    if dots <= 0:
        return None
    full, remainder = divmod(dots, 11)
    half = 1 if 1 <= remainder <= 5 else 0
    if 6 <= remainder <= 10:
        full += 1
    while full >= 0 and 11 * full + 5 * half != dots:
        full -= 1
        half += 2
    if full < 0:
        return None
    # Original alloc fills backwards: ASCII space first, then fullwidth space.
    reverse = []
    while full or half:
        if half:
            reverse.append(" ")
            half -= 1
        if full:
            reverse.append("　")
            full -= 1
    return "".join(reversed(reverse))
