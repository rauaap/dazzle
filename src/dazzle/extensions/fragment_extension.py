from __future__ import annotations

import re
from typing import Iterable
from xml.etree.ElementTree import Element

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor

from dazzle.errors import CompileError

_DIRECTIVE_RE = re.compile(r"^\s*:::\s*([A-Za-z0-9_-]+)\s*$")
_DIRECTIVE_CLOSE_RE = re.compile(r"^\s*:::\s*$")
_STAR_BULLET_RE = re.compile(r"^(\s*)\*\s+(.+)$")
_FENCE_RE = re.compile(r"^\s*([`~]{3,})")


class FragmentPreprocessor(Preprocessor):
    def run(self, lines: Iterable[str]) -> list[str]:
        output: list[str] = []
        in_fragment = False
        fragment_start_line = 0
        fence_char: str | None = None
        fence_len = 0

        for idx, line in enumerate(lines, start=1):
            fence_match = _FENCE_RE.match(line)
            if fence_match:
                marker = fence_match.group(1)
                marker_char = marker[0]
                marker_len = len(marker)
                if fence_char is None:
                    fence_char = marker_char
                    fence_len = marker_len
                    output.append(line)
                    continue
                if marker_char == fence_char and marker_len >= fence_len:
                    fence_char = None
                    fence_len = 0
                    output.append(line)
                    continue

            if fence_char is not None:
                output.append(line)
                continue

            if _DIRECTIVE_CLOSE_RE.match(line):
                if in_fragment:
                    in_fragment = False
                    output.append("</div>")
                    continue
                raise CompileError(f"Unexpected directive close at line {idx}.")

            match = _DIRECTIVE_RE.match(line)
            if match:
                directive = match.group(1)
                if directive != "fragment":
                    raise CompileError(f"Unsupported directive ':::{directive}' at line {idx}.")
                if in_fragment:
                    raise CompileError(f"Nested fragment directives are not supported (line {idx}).")
                in_fragment = True
                fragment_start_line = idx
                output.append('<div class="fragment" markdown="block">')
                continue

            if not in_fragment:
                star_match = _STAR_BULLET_RE.match(line)
                if star_match:
                    indent, content = star_match.groups()
                    output.append(f"{indent}- {content}")
                    output.append(f"{indent}    {{: .fragment}}")
                    continue

            output.append(line)

        if in_fragment:
            raise CompileError(f"Unclosed fragment directive starting at line {fragment_start_line}.")

        return output


class FragmentExtension(Extension):
    def extendMarkdown(self, md) -> None:  # noqa: N802 (library API)
        md.preprocessors.register(FragmentPreprocessor(md), "dazzle_fragment_preprocessor", 35)
        md.treeprocessors.register(FragmentTreeprocessor(md), "dazzle_fragment_treeprocessor", 7)


class FragmentTreeprocessor(Treeprocessor):
    def run(self, root: Element) -> Element:
        order = 0

        for element in root.iter():
            classes = element.get("class", "").split()
            if "fragment" not in classes:
                continue

            order += 1
            if "is-hidden" not in classes:
                classes.append("is-hidden")
                element.set("class", " ".join(classes))

            if "data-fragment-order" not in element.attrib:
                element.set("data-fragment-order", str(order))

        self.md.dazzle_fragment_count = order
        return root
