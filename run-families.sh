#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cache="$repo_dir/.run/glyph_audit/glyph_features.npz"
catalog="$repo_dir/.run/glyph_audit/families.jsonl"
cell_cache="$repo_dir/.run/glyph_audit/glyph_cell_features.npz"
cell_meta="$repo_dir/.run/glyph_audit/glyph_cell_features.meta.json"
combo_json="$repo_dir/.run/glyph_audit/glyph_combo_measured.json"
combo_html="$repo_dir/.run/glyph_audit/glyph_combo_gallery.html"
mine_json="$repo_dir/.run/glyph_audit/mined_combos.json"
run_accept="$repo_dir/.run/glyph_audit/runs_beside_w8_accept.json"
run_plate="$repo_dir/.run/glyph_audit/runs_beside_w8_plate.json"
run_lineart="$repo_dir/.run/glyph_audit/runs_beside_w8_lineart.json"
run_rtl="$repo_dir/.run/glyph_audit/runs_beside_w8_rtl.json"
run_cjk="$repo_dir/.run/glyph_audit/runs_beside_w16_cjk.json"
run_stacked_lineart="$repo_dir/.run/glyph_audit/runs_stacked_w8_lineart.json"
run_stacked_cjk="$repo_dir/.run/glyph_audit/runs_stacked_w16_cjk.json"
seam_stacked_w8="$repo_dir/.run/glyph_audit/seam_pairs_stacked_w8.json"
seam_beside_w8="$repo_dir/.run/glyph_audit/seam_pairs_beside_w8.json"
seam_stacked_w16="$repo_dir/.run/glyph_audit/seam_pairs_stacked_w16.json"
seam_beside_w16="$repo_dir/.run/glyph_audit/seam_pairs_beside_w16.json"
rebuild_gallery=0

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required" >&2
  exit 69
}
python3 -c 'import numpy; import fontTools; import scipy; import skimage; from PIL import Image' >/dev/null 2>&1 || {
  echo "NumPy, Pillow, fonttools, scipy, and scikit-image are required; install requirements.txt" >&2
  exit 69
}

run_json_current() {
  python3 - "$1" "$2" "$3" "$4" "$5" <<'PY'
import json
import sys
from pathlib import Path

path, relation, width, tag, min_length = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
try:
    d = json.loads(Path(path).read_text())
except (OSError, json.JSONDecodeError):
    raise SystemExit(1)
args = d.get("args") or {}
rows = d.get("rows") or []
ok = (
    bool(rows)
    and str(args.get("relation", "beside")) == relation
    and int(args.get("width", d.get("width", 0))) == width
    and str(args.get("tag", "")) == tag
    and int(args.get("length", 0)) >= min_length
)
raise SystemExit(0 if ok else 1)
PY
}

if [ ! -t 0 ] || [ ! -t 1 ]; then
  echo "interactive family browsing requires a real TTY" >&2
  exit 69
fi

if [ ! -f "$cache" ]; then
  python3 "$repo_dir/scripts/glyph_features.py"
fi
if [ ! -f "$catalog" ]; then
  python3 "$repo_dir/scripts/glyph_audit.py" families --json >/dev/null
fi
if [ ! -f "$cell_cache" ] || [ ! -f "$cell_meta" ] || ! python3 -c 'import json, sys; meta=json.load(open(sys.argv[1])); raise SystemExit(0 if int(meta.get("schema", 0)) >= 2 else 1)' "$cell_meta"; then
  python3 "$repo_dir/scripts/glyph_cell_features.py" --build
fi
if [ ! -f "$mine_json" ]; then
  python3 "$repo_dir/scripts/glyph_combo_mine.py" --json >/dev/null
  rebuild_gallery=1
fi
if [ ! -f "$seam_stacked_w8" ]; then
  python3 "$repo_dir/scripts/glyph_seam_index.py" --relation stacked --width 8 --stroke-like --exclude-alnum --max-pairs 20000 --keep 300
  rebuild_gallery=1
fi
if [ ! -f "$seam_beside_w8" ]; then
  python3 "$repo_dir/scripts/glyph_seam_index.py" --relation beside --width 8 --stroke-like --exclude-alnum --max-pairs 20000 --keep 300
  rebuild_gallery=1
fi
if [ ! -f "$seam_stacked_w16" ]; then
  python3 "$repo_dir/scripts/glyph_seam_index.py" --relation stacked --width 16 --stroke-like --max-pairs 20000 --keep 300
  rebuild_gallery=1
fi
if [ ! -f "$seam_beside_w16" ]; then
  python3 "$repo_dir/scripts/glyph_seam_index.py" --relation beside --width 16 --stroke-like --max-pairs 20000 --keep 300
  rebuild_gallery=1
fi
if ! run_json_current "$run_accept" beside 8 accept 4; then
  python3 "$repo_dir/scripts/glyph_run_walker.py" --chars '_.-´`\|/(o)‾' --length 4 --per-start 0 --no-dsm --max-score 100000 --keep 100000 --json --tag accept --limit 0
  rebuild_gallery=1
fi
if ! run_json_current "$run_plate" beside 8 plate 4; then
  python3 "$repo_dir/scripts/glyph_run_walker.py" --width 8 --plate --length 4 --per-start 400 --budget 3000000 --max-score 40000 --keep 20000 --json --tag plate --limit 0
  rebuild_gallery=1
fi
if ! run_json_current "$run_lineart" beside 8 lineart 4; then
  python3 "$repo_dir/scripts/glyph_run_walker.py" --width 8 --line-like --exclude-alnum --length 4 --per-node 8 --per-start 8 --budget 3000 --max-score 30000 --keep 600 --json --tag lineart --limit 25
  rebuild_gallery=1
fi
if ! run_json_current "$run_rtl" beside 8 rtl 4; then
  python3 "$repo_dir/scripts/glyph_run_walker.py" --width 8 --blocks "Arabic,Hebrew,Syriac,Thaana" --length 4 --per-node 12 --per-start 12 --budget 5000 --max-score 30000 --keep 600 --json --tag rtl --limit 25
  rebuild_gallery=1
fi
if ! run_json_current "$run_cjk" beside 16 cjk 4; then
  python3 "$repo_dir/scripts/glyph_run_walker.py" --width 16 --blocks "CJK Strokes,Box Drawing,Hiragana,Katakana,Kangxi Radicals" --exclude-alnum --length 4 --per-node 12 --per-start 12 --budget 5000 --max-score 30000 --keep 600 --json --tag cjk --limit 25
  rebuild_gallery=1
fi
if ! run_json_current "$run_stacked_lineart" stacked 8 lineart 4; then
  python3 "$repo_dir/scripts/glyph_run_walker.py" --relation stacked --width 8 --line-like --exclude-alnum --length 4 --per-node 8 --per-start 8 --budget 3000 --max-score 30000 --keep 600 --json --tag lineart --limit 25
  rebuild_gallery=1
fi
if ! run_json_current "$run_stacked_cjk" stacked 16 cjk 4; then
  python3 "$repo_dir/scripts/glyph_run_walker.py" --relation stacked --width 16 --blocks "CJK Strokes,Box Drawing,Hiragana,Katakana,Kangxi Radicals" --exclude-alnum --length 4 --per-node 12 --per-start 12 --budget 5000 --max-score 30000 --keep 600 --json --tag cjk --limit 25
  rebuild_gallery=1
fi
if [ ! -f "$combo_json" ] || [ ! -f "$combo_html" ] || [ "$rebuild_gallery" -eq 1 ]; then
  python3 "$repo_dir/scripts/glyph_combo_gallery.py"
fi
echo "combo gallery: $combo_html" >&2
exec python3 "$repo_dir/scripts/glyph_families_viewer.py" "$@"
