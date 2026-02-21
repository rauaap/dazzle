from __future__ import annotations

import unittest

from dazzle.html import render_document
from dazzle.slides import Deck, Slide


class RenderDocumentAssetTests(unittest.TestCase):
    def test_appends_extra_assets(self) -> None:
        deck = Deck(slides=[Slide(index=0, html="<p>x</p>", fragments=[])])
        out = render_document(deck, "T", extra_css=[".x { color: red; }"], extra_js=["window.X=1;"])
        self.assertIn(".x { color: red; }", out)
        self.assertIn("window.X=1;", out)

    def test_can_disable_default_assets(self) -> None:
        deck = Deck(slides=[Slide(index=0, html="<p>x</p>", fragments=[])])
        out = render_document(
            deck,
            "T",
            extra_css=[".x { color: red; }"],
            extra_js=["window.X=1;"],
            include_default_css=False,
            include_default_js=False,
        )
        self.assertIn(".x { color: red; }", out)
        self.assertIn("window.X=1;", out)
        self.assertNotIn("font-family", out)
        self.assertNotIn("addEventListener", out)


if __name__ == "__main__":
    unittest.main()
