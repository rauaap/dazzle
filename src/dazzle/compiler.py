from __future__ import annotations

from pathlib import Path
import re

from markdown import Markdown
from markdown.extensions import Extension

from dazzle.config import BuildConfig
from dazzle.extensions.fragment_extension import FragmentExtension
from dazzle.images import embed_images_in_html
from dazzle.html import render_document
from dazzle.slides import Deck, FragmentRef, Slide, split_markdown_into_slides


_TITLE_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


_DEFAULT_MARKDOWN_EXTENSIONS: list[str | Extension] = [
    "fenced_code",
    "codehilite",
    "tables",
    "md_in_html",
    "attr_list",
]
_DEFAULT_MARKDOWN_EXTENSION_CONFIGS: dict[str, dict[str, object]] = {
    "codehilite": {
        "guess_lang": False,
        "use_pygments": True,
        "noclasses": True,
        "pygments_style": "monokai",
    }
}


def build_markdown_engine(build_config: BuildConfig | None = None) -> Markdown:
    cfg = build_config or BuildConfig(extensions=[], extension_configs={}, css_chunks=[], js_chunks=[])
    extension_configs: dict[str, dict[str, object]] = {
        key: dict(value) for key, value in _DEFAULT_MARKDOWN_EXTENSION_CONFIGS.items()
    }

    for key, value in cfg.extension_configs.items():
        merged = dict(extension_configs.get(key, {}))
        merged.update(value)
        extension_configs[key] = merged

    return Markdown(
        extensions=[*_DEFAULT_MARKDOWN_EXTENSIONS, FragmentExtension(), *cfg.extensions],
        extension_configs=extension_configs,
        output_format="html5",
    )


MARKDOWN_ENGINE = build_markdown_engine()


def _infer_title(source: str, source_name: str) -> str:
    match = _TITLE_RE.search(source)
    if match:
        return match.group(1).strip()
    return Path(source_name).stem


def render_markdown(md: Markdown, source: str) -> str:
    md.reset()
    return md.convert(source)


def compile_markdown_source_to_html(
    source: str,
    source_name: str,
    source_dir: Path,
    output_path: Path,
    build_config: BuildConfig | None = None,
) -> None:
    cfg = build_config or BuildConfig(extensions=[], extension_configs={}, css_chunks=[], js_chunks=[])
    markdown_engine = build_markdown_engine(cfg)
    split_sources = split_markdown_into_slides(source)
    slides: list[Slide] = []

    for index, slide_source in enumerate(split_sources):
        slide_html = render_markdown(markdown_engine, slide_source.markdown)
        slide_html = embed_images_in_html(slide_html, source_dir.resolve())

        fragment_count = getattr(markdown_engine, "dazzle_fragment_count", 0)
        fragments = [FragmentRef(id=f"s{index}-f{order}", order=order) for order in range(1, fragment_count + 1)]
        slides.append(Slide(index=index, html=slide_html, fragments=fragments))

    deck = Deck(slides=slides)
    title = _infer_title(source, source_name)
    document = render_document(
        deck,
        title,
        extra_css=cfg.css_chunks,
        extra_js=cfg.js_chunks,
        include_default_css=cfg.include_default_css,
        include_default_js=cfg.include_default_js,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")


def compile_markdown_file_to_html(
    input_path: Path,
    output_path: Path,
    build_config: BuildConfig | None = None,
) -> None:
    source = input_path.read_text(encoding="utf-8")
    compile_markdown_source_to_html(
        source=source,
        source_name=input_path.name,
        source_dir=input_path.parent,
        output_path=output_path,
        build_config=build_config,
    )
