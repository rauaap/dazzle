from __future__ import annotations

from html.parser import HTMLParser
import html as html_lib


class PassthroughHTMLParser(HTMLParser):
    """Re-emits parsed HTML tokens to preserve document content during selective transformations."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._out: list[str] = []

    def get_html(self) -> str:
        return "".join(self._out)

    def _format_attrs(self, attrs: list[tuple[str, str | None]]) -> str:
        if not attrs:
            return ""

        formatted: list[str] = []
        for name, value in attrs:
            if value is None:
                formatted.append(name)
            else:
                escaped = html_lib.escape(value, quote=True)
                formatted.append(f'{name}="{escaped}"')
        return " " + " ".join(formatted)

    def _emit_start_tag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._out.append(f"<{tag}{self._format_attrs(attrs)}>")

    def _emit_startend_tag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._out.append(f"<{tag}{self._format_attrs(attrs)} />")

    def _emit_end_tag(self, tag: str) -> None:
        self._out.append(f"</{tag}>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._emit_start_tag(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._emit_startend_tag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        self._emit_end_tag(tag)

    def handle_data(self, data: str) -> None:
        self._out.append(data)

    def handle_comment(self, data: str) -> None:
        self._out.append(f"<!--{data}-->")

    def handle_entityref(self, name: str) -> None:
        self._out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._out.append(f"&#{name};")

    def handle_decl(self, decl: str) -> None:
        self._out.append(f"<!{decl}>")

    def unknown_decl(self, data: str) -> None:
        self._out.append(f"<![{data}]>")

    def handle_pi(self, data: str) -> None:
        self._out.append(f"<?{data}>")
