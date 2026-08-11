#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cache="$repo_dir/.run/glyph_audit/glyph_features.npz"

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required" >&2
  exit 69
}
python3 -c 'import numpy; import fontTools; from PIL import Image' >/dev/null 2>&1 || {
  echo "NumPy, Pillow, and fonttools are required; install requirements.txt" >&2
  exit 69
}
if [ ! -t 0 ] || [ ! -t 1 ]; then
  echo "interactive family browsing requires a real TTY" >&2
  exit 69
fi

if [ ! -f "$cache" ]; then
  python3 "$repo_dir/scripts/glyph_features.py"
fi
exec python3 "$repo_dir/scripts/glyph_families_viewer.py" "$@"
