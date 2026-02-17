from __future__ import annotations

import unittest

from dazzle.compiler import MARKDOWN_ENGINE, render_markdown


class FragmentAnnotationInExtensionTests(unittest.TestCase):
    def test_directive_fragments_are_annotated_with_order(self) -> None:
        md = MARKDOWN_ENGINE
        html = render_markdown(md, "::: fragment\n- one\n:::\n\n::: fragment\n- two\n:::")
        self.assertIn('class="fragment is-hidden"', html)
        self.assertIn('data-fragment-order="1"', html)
        self.assertIn('data-fragment-order="2"', html)
        self.assertEqual(2, md.dazzle_fragment_count)

    def test_star_list_fragments_get_ordered_in_list_html_order(self) -> None:
        md = MARKDOWN_ENGINE
        html = render_markdown(md, "* One\n    * Two\n- Static")
        self.assertIn('<li class="fragment is-hidden" data-fragment-order="1">One', html)
        self.assertIn('<li class="fragment is-hidden" data-fragment-order="2">Two', html)
        self.assertNotIn('data-fragment-order="3"', html)
        self.assertEqual(2, md.dazzle_fragment_count)

    def test_existing_fragment_order_is_preserved(self) -> None:
        md = MARKDOWN_ENGINE
        html = render_markdown(md, "x\n{: .fragment data-fragment-order=\"9\"}")
        self.assertIn('data-fragment-order="9"', html)
        self.assertNotIn('data-fragment-order="1"', html)
        self.assertEqual(1, md.dazzle_fragment_count)

    def test_non_fragment_class_is_ignored(self) -> None:
        md = MARKDOWN_ENGINE
        html = render_markdown(md, '<div class="fragmented">x</div>')
        self.assertEqual('<div class="fragmented">x</div>', html)
        self.assertEqual(0, md.dazzle_fragment_count)


if __name__ == "__main__":
    unittest.main()
