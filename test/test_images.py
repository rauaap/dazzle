from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from dazzle.errors import CompileError
from dazzle.html_parser import PassthroughHTMLParser
from dazzle.images import embed_images_in_html


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89\x00\x00\x00\x0dIDATx\x9cc````\x00\x00\x00\x05\x00\x01"
    b"\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class ImageEmbeddingTests(unittest.TestCase):
    def test_embeds_relative_img_src(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_dir = Path(tmpdir)
            (markdown_dir / "pic.png").write_bytes(PNG_1X1)
            html = '<p><img src="pic.png" alt="x"></p>'
            out = embed_images_in_html(html, markdown_dir)
            self.assertIn('<img src="data:image/png;base64,', out)
            self.assertIn('alt="x"', out)

    def test_keeps_data_uri_unchanged(self) -> None:
        html = '<img src="data:image/png;base64,abc123">'
        out = embed_images_in_html(html, Path.cwd())
        self.assertEqual(html, out)

    def test_rejects_remote_images(self) -> None:
        with self.assertRaisesRegex(CompileError, "Remote images are not allowed in v1"):
            embed_images_in_html('<img src="https://example.com/a.png">', Path.cwd())

    def test_rejects_unsupported_scheme(self) -> None:
        with self.assertRaisesRegex(CompileError, "Unsupported image URL scheme"):
            embed_images_in_html('<img src="ftp://example.com/a.png">', Path.cwd())

    def test_supports_file_scheme_with_percent_decoding(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "a b.png"
            file_path.write_bytes(PNG_1X1)
            html = f'<img src="file://{file_path.as_posix().replace(" ", "%20")}">'
            out = embed_images_in_html(html, Path.cwd())
            self.assertIn('src="data:image/png;base64,', out)

    def test_handles_uppercase_single_quote_and_self_closing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_dir = Path(tmpdir)
            (markdown_dir / "pic.png").write_bytes(PNG_1X1)
            out = embed_images_in_html("<IMG SRC='pic.png' />", markdown_dir)
            self.assertIn('<img src="data:image/png;base64,', out)
            self.assertIn("/>", out)

    def test_img_without_src_is_unchanged(self) -> None:
        html = '<img alt="no source">'
        out = embed_images_in_html(html, Path.cwd())
        self.assertEqual(html, out)


class PassthroughParserTests(unittest.TestCase):
    def test_preserves_comment_entity_and_doctype(self) -> None:
        src = "<!DOCTYPE html><!--x--><p>&nbsp;&#160;</p>"
        parser = PassthroughHTMLParser()
        parser.feed(src)
        parser.close()
        self.assertEqual(src, parser.get_html())


if __name__ == "__main__":
    unittest.main()
