#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cache="$repo_dir/.run/glyph_audit/glyph_features.npz"
catalog="$repo_dir/.run/glyph_audit/families.jsonl"
cell_cache="$repo_dir/.run/glyph_audit/glyph_cell_features.npz"
combo_json="$repo_dir/.run/glyph_audit/glyph_combo_measured.json"
combo_html="$repo_dir/.run/glyph_audit/glyph_combo_gallery.html"

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required" >&2
  exit 69
}
python3 -c 'import numpy; import fontTools; import scipy; import skimage; from PIL import Image' >/dev/null 2>&1 || {
  echo "NumPy, Pillow, fonttools, scipy, and scikit-image are required; install requirements.txt" >&2
  exit 69
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
if [ ! -f "$cell_cache" ]; then
  python3 "$repo_dir/scripts/glyph_cell_features.py" --build
fi
if [ ! -f "$combo_json" ] || [ ! -f "$combo_html" ]; then
  python3 "$repo_dir/scripts/glyph_combo_gallery.py"
fi
echo "combo gallery: $combo_html" >&2
exec python3 "$repo_dir/scripts/glyph_families_viewer.py" "$@"
