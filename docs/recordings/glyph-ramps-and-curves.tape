Output docs/glyph-ramps-and-curves.gif
Require python3
Set Shell "zsh"
Set FontSize 26
Set Width 1200
Set Height 900
Set Framerate 12
Set TypingSpeed 1ms
Set Theme "Catppuccin Mocha"

# Record the real CLI animator, using raw font-chain rasters throughout.
# Explicit examples, not claims of automatic family discovery or interpolation.
Hide
Type "clear; printf 'INK RAMP | one stem, additional strokes\nOgham U+1686 / 1687 / 1688 / 1689\n22 / 28 / 34 / 40 ink pixels in this profile\nRaw 16x16 font-chain raster; whole glyphs only\n\n'; python3 scripts/glyph_audit.py anim U+1686 U+1687 U+1688 U+1689 --fps 2" Enter
Sleep 500ms
Show
Sleep 4s

Hide
Ctrl+C
Type "clear; printf 'CORNER TO CURVE | sharp / rounded return\nU+2514 / U+2570\nCompare the turn and the paper around it\nRaw 16x16 font-chain raster; no deformation\n\n'; python3 scripts/glyph_audit.py anim U+2514 U+2570 --fps 1" Enter
Sleep 500ms
Show
Sleep 4s

Hide
Ctrl+C
Type "clear; printf 'HOOKS | angled / curved return\nKatakana RE U+30EC / Hiragana SI U+3057\nCompare the lower turn and open bowl\nRaw 16x16 font-chain raster; selected comparison\n\n'; python3 scripts/glyph_audit.py anim U+30EC U+3057 --fps 1" Enter
Sleep 500ms
Show
Sleep 4s
Hide
Ctrl+C
Sleep 300ms
