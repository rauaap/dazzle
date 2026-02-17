from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SlideSource:
    markdown: str
    start_line: int


@dataclass(frozen=True)
class FragmentRef:
    id: str
    order: int


@dataclass(frozen=True)
class Slide:
    index: int
    html: str
    fragments: list[FragmentRef]


@dataclass(frozen=True)
class Deck:
    slides: list[Slide]


_SLIDE_DELIMITER_RE = re.compile(r"^\s*---\s*$")
_FENCE_RE = re.compile(r"^\s*([`~]{3,})")


def split_markdown_into_slides(source: str) -> list[SlideSource]:
    lines = source.splitlines()
    slide_lines: list[str] = []
    slide_start = 1
    slides: list[SlideSource] = []

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
            elif marker_char == fence_char and marker_len >= fence_len:
                fence_char = None
                fence_len = 0

        if fence_char is None and _SLIDE_DELIMITER_RE.match(line):
            slides.append(SlideSource(markdown="\n".join(slide_lines), start_line=slide_start))
            slide_lines = []
            slide_start = idx + 1
            continue

        slide_lines.append(line)

    slides.append(SlideSource(markdown="\n".join(slide_lines), start_line=slide_start))
    return slides

