# Unicode Glyph Morphology Explorer

A fork of [msokalski/asciicker](https://github.com/msokalski/asciicker), a CP437 3D ASCII engine.

Browse Unicode glyphs by rendered shape instead of only by codepoint or script. The tools use a pinned eight-font chain and 16×16 shape analysis to compare density, orientation, topology, and related visual features.

![Browse, filter, and inspect Unicode morphology](docs/glyph-morphology-explorer.gif)

## Run

```sh
python3 -m pip install -r requirements.txt
./run-browser.sh --block "Geometric Shapes"
```

The interactive browser requires a UTF-8 terminal. List the known Unicode blocks without entering the browser:

```sh
./run-browser.sh --list-blocks
```

Controls are shown in the browser footer. `q` exits without changing tracked files.

## Browse discovered families

![Animate and filter morphology families](docs/glyph-families-viewer.gif)

```sh
./run-families.sh
```

The first run builds a local ignored feature cache under `.run/`. The family viewer is read-only. Use `j`/`k` to select, `m` to change the morphology axis, `1`–`9` to filter by family length, and `q` to exit.

## Included data

The repository includes the morphology browser, the read-only family viewer, the selected saved-family registry, and the exact pinned font chain used for rendering. It does not include the full Asciicker engine or runtime.

Font identities, copyright metadata, license mapping, and license texts are recorded in [docs/font-provenance.md](docs/font-provenance.md) and `docs/licenses/`. Source-code identities are recorded in [docs/code-provenance.md](docs/code-provenance.md).
