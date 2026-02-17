from __future__ import annotations

from pathlib import Path
import base64
import mimetypes
import re
import urllib.parse

from dazzle.errors import CompileError

_IMG_SRC_RE = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")')


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


def embed_images_in_html(html: str, markdown_dir: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        src = match.group(2)
        parsed = urllib.parse.urlparse(src)
        if parsed.scheme in ("http", "https"):
            raise CompileError(f"Remote images are not allowed in v1: {src}")
        if parsed.scheme == "data":
            return match.group(0)
        if parsed.scheme and parsed.scheme != "file":
            raise CompileError(f"Unsupported image URL scheme '{parsed.scheme}' for '{src}'.")

        decoded_src = urllib.parse.unquote(parsed.path if parsed.scheme == "file" else src)
        img_path = Path(decoded_src)
        if not img_path.is_absolute():
            img_path = (markdown_dir / img_path).resolve()

        data_uri = _to_data_uri(img_path)
        return f"{match.group(1)}{data_uri}{match.group(3)}"

    return _IMG_SRC_RE.sub(replace, html)
