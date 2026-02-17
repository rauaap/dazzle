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
