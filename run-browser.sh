#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required" >&2
  exit 69
}
python3 -c 'import numpy; import fontTools; from PIL import Image' >/dev/null 2>&1 || {
  echo "NumPy, Pillow, and fonttools are required; install requirements.txt" >&2
  exit 69
}

case " $* " in
  *" --list-blocks "*) ;;
  *)
    if [ ! -t 0 ] || [ ! -t 1 ]; then
      echo "interactive browsing requires a real TTY" >&2
      exit 69
    fi
    ;;
esac

exec python3 "$repo_root/scripts/glyph_morphology_browser.py" "$@"
