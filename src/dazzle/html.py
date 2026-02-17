from __future__ import annotations

from importlib import resources
import html

from dazzle.slides import Deck

def _load_asset(name: str) -> str:
    return resources.files("dazzle").joinpath(name).read_text(encoding="utf-8")


def render_document(deck: Deck, title: str) -> str:
    css = _load_asset("theme.css")
    js = _load_asset("runtime.js")
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
{css}
  </style>
</head>
<body>
  <main id="deck" tabindex="0" aria-label="Slide deck">
{joined_slides}
  </main>
  <script>
{js}
  </script>
</body>
</html>
"""
