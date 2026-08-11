# Unicode Glyph Morphology Explorer

Private standalone extraction of the Y9-2 terminal tools for browsing Unicode
glyphs by rendered morphology. The browser uses a pinned eight-font chain and
the same 16×16 shape analysis vocabulary as the source catalog tooling.

## Run

```sh
python3 -m pip install -r requirements.txt
./run-browser.sh --block "Geometric Shapes"
```

The interactive browser requires a real UTF-8 terminal. List the known Unicode
blocks without entering curses:

```sh
./run-browser.sh --list-blocks
```

Controls are displayed in the browser footer; `q` exits without writing tracked
files.

## Boundary

This repository includes the morphology browser, family/audit helpers, selected
saved-family registry, and the exact pinned font chain. It excludes the engine,
compiler outputs, runtime, paper drafts, agent/process material, caches, and
unrelated assets.

The repository is private. Font redistribution/publication remains a separate
license gate; see [docs/font-provenance.md](docs/font-provenance.md).
