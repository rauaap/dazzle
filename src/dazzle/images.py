from __future__ import annotations

from pathlib import Path
import base64
import mimetypes
import urllib.parse

from dazzle.errors import CompileError
from dazzle.html_parser import PassthroughHTMLParser


def _to_data_uri(asset_path: Path) -> str:
    if not asset_path.exists():
        raise CompileError(f"Image file not found: {asset_path}")
    if not asset_path.is_file():
        raise CompileError(f"Image path is not a file: {asset_path}")

    mime, _ = mimetypes.guess_type(asset_path.name)
    if not mime or not mime.startswith("image/"):
        raise CompileError(f"Unsupported image type for '{asset_path}'.")

    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _rewrite_img_src(src: str, markdown_dir: Path) -> str:
    parsed = urllib.parse.urlparse(src)
    if parsed.scheme in ("http", "https"):
        raise CompileError(f"Remote images are not allowed in v1: {src}")
    if parsed.scheme == "data":
        return src
    if parsed.scheme and parsed.scheme != "file":
        raise CompileError(f"Unsupported image URL scheme '{parsed.scheme}' for '{src}'.")

    decoded_src = urllib.parse.unquote(parsed.path if parsed.scheme == "file" else src)
    img_path = Path(decoded_src)
    if not img_path.is_absolute():
        img_path = (markdown_dir / img_path).resolve()
    return _to_data_uri(img_path)


class ImageEmbeddingHTMLParser(PassthroughHTMLParser):
    """Rewrites only img src attributes to embedded data URIs while passing through all other HTML."""

    def __init__(self, markdown_dir: Path) -> None:
        super().__init__()
        self._markdown_dir = markdown_dir

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "img":
            super().handle_starttag(tag, attrs)
            return
        self._emit_start_tag(tag, self._rewrite_img_attrs(attrs))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "img":
            super().handle_startendtag(tag, attrs)
            return
        self._emit_startend_tag(tag, self._rewrite_img_attrs(attrs))

    def _rewrite_img_attrs(self, attrs: list[tuple[str, str | None]]) -> list[tuple[str, str | None]]:
        rewritten: list[tuple[str, str | None]] = []
        for name, value in attrs:
            if name == "src" and value is not None:
                rewritten.append((name, _rewrite_img_src(value, self._markdown_dir)))
            else:
                rewritten.append((name, value))
        return rewritten


def embed_images_in_html(html: str, markdown_dir: Path) -> str:
    parser = ImageEmbeddingHTMLParser(markdown_dir)
    parser.feed(html)
    parser.close()
    return parser.get_html()
