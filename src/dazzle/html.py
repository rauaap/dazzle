from __future__ import annotations

from importlib import resources
import html

from dazzle.slides import Deck

def _load_asset(name: str) -> str:
    return resources.files("dazzle").joinpath(name).read_text(encoding="utf-8")


def render_document(
    deck: Deck,
    title: str,
    *,
    extra_css: list[str] | None = None,
    extra_js: list[str] | None = None,
    include_default_css: bool = True,
    include_default_js: bool = True,
) -> str:
    css_chunks: list[str] = []
    js_chunks: list[str] = []
    if include_default_css:
        css_chunks.append(_load_asset("theme.css"))
    if include_default_js:
        js_chunks.append(_load_asset("runtime.js"))
    css_chunks.extend(extra_css or [])
    js_chunks.extend(extra_js or [])
    slides_markup: list[str] = []

    for slide in deck.slides:
        slide_html = slide.html if slide.html.strip() else "<p></p>"
        slides_markup.append(
            (
                f'<section class="slide" data-slide-index="{slide.index}"'
                f' data-fragment-count="{len(slide.fragments)}">'
                f"{slide_html}"
                "</section>"
            )
        )

    joined_slides = "\n".join(slides_markup)
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title}</title>
  <style>
{"\n\n".join(css_chunks)}
  </style>
</head>
<body>
  <main id="deck" tabindex="0" aria-label="Slide deck">
{joined_slides}
  </main>
  <script>
{"\n\n".join(js_chunks)}
  </script>
</body>
</html>
"""
