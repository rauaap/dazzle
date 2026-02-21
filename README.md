# dazzle

Compile Markdown documents into self-contained HTML slide decks.

## Install

```bash
pip install -e .
```

## Usage

```bash
dazzle build slides.md -o deck.html
```

### Build flags

- `-c, --config PATH`: load TOML config. If omitted, dazzle tries `./dazzle.toml`, then `~/.config/dazzle/config.toml`.
- `-x, --extension EXT`: enable extra Python-Markdown extension (repeatable).
- `-s, --stylesheet VALUE`: add CSS by file path or inline CSS text (repeatable).
- `-j, --javascript VALUE`: add JS by file path or inline JS text (repeatable).
- `--no-default-css`: disable built-in `theme.css`.
- `--no-default-js`: disable built-in `runtime.js`.

Config values are applied first, then CLI values are appended.

### Config file (`dazzle.toml`)

```toml
# Repeatable markdown extension names
extension = ["toc", "admonition"]

# Each item can be a file path or inline CSS text
stylesheet = ["./slides.css", "h1 { letter-spacing: 0.04em; }"]

# Each item can be a file path or inline JS text
javascript = ["./slides.js", "window.DEBUG = true;"]

# Optional: disable built-in assets
include_default_css = true
include_default_js = true

# Optional: extension-specific options passed to Python-Markdown
[markdown_extension_configs]
toc = { marker = "Table of contents" }
codehilite = { pygments_style = "friendly", noclasses = true }
```

Example:

```bash
dazzle build slides.md -o deck.html -x sane_lists -s ./extra.css -j "console.log('loaded')"
```

## Markdown features

- Slide separators via `---`
- Fragment blocks (for arbitrary content):

```md
::: fragment
- reveal me later
:::
```

- List fragments:

```md
* Revealed as a fragment
    * Nested fragment revealed later
- Static bullet (not a fragment)
```

`*` bullets are fragment steps (including nested bullets) and reveal in document order.
`-` bullets remain static list items.

- Fenced code blocks with Pygments highlighting
- Local images embedded as base64 data URIs

Remote image URLs (`http://` and `https://`) are rejected in v1.
