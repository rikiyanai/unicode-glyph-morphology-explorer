# Unicode Glyph Morphology Explorer

Private standalone extraction of the Y9-2 terminal tools for browsing Unicode
glyphs by rendered morphology. The browser uses a pinned eight-font chain and
the same 16×16 shape analysis vocabulary as the source catalog tooling.

![Browse, filter, and inspect Unicode morphology](docs/glyph-morphology-explorer.gif)

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

## Browse discovered families

![Animate and filter morphology families](docs/glyph-families-viewer.gif)

```sh
./run-families.sh
```

The first run builds a package-local ignored feature cache under `.run/`; the
viewer itself is read-only. Use `j`/`k` to select, `m` to change the morphology
axis, `1`–`9` to filter by family length, and `q` to exit.

## Boundary

The supported user features are the morphology browser and the read-only family
viewer. Internal audit/feature helpers support those two paths. The repository
includes the selected saved-family registry and exact pinned font chain. It
excludes the engine, compiler outputs, runtime, paper drafts, agent/process
material, caches, and unrelated assets.

The repository is private. The bundled font identities, copyright metadata,
license mapping, and license texts are recorded in
[docs/font-provenance.md](docs/font-provenance.md) and `docs/licenses/`. Exact
source-code identities and the family viewer's deliberate read-only delta are
recorded in [docs/code-provenance.md](docs/code-provenance.md).
