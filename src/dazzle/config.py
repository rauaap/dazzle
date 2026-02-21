from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class BuildConfig:
    extensions: list[str]
    extension_configs: dict[str, dict[str, object]]
    css_chunks: list[str]
    js_chunks: list[str]
    include_default_css: bool = True
    include_default_js: bool = True


@dataclass(frozen=True)
class BuildCliOptions:
    config_path: Path | None
    extensions: list[str]
    stylesheets: list[str]
    javascripts: list[str]
    no_default_css: bool
    no_default_js: bool


def load_build_config(cli: BuildCliOptions, cwd: Path, home: Path | None = None) -> BuildConfig:
    home_dir = home if home is not None else Path.home()

    config_path = cli.config_path.expanduser() if cli.config_path is not None else None
    if config_path is None and (cwd / ".dazzle.toml").is_file():
        config_path = cwd / ".dazzle.toml"
    if config_path is None and (home_dir / ".config" / "dazzle" / "config.toml").is_file():
        config_path = home_dir / ".config" / "dazzle" / "config.toml"

    raw: dict[str, object] = {}
    if config_path is not None:
        with config_path.open("rb") as f:
            raw = tomllib.load(f)

    extensions = [*list(raw.get("extension", [])), *cli.extensions]

    include_default_css = bool(raw.get("include_default_css", True)) and not cli.no_default_css
    include_default_js = bool(raw.get("include_default_js", True)) and not cli.no_default_js
    extension_configs = {str(k): dict(v) for k, v in dict(raw.get("markdown_extension_configs", {})).items()}

    css_chunks: list[str] = []
    js_chunks: list[str] = []

    for value in list(raw.get("stylesheet", [])):
        candidate = Path(os.path.expanduser(value))
        if not candidate.is_absolute():
            candidate = (config_path.parent if config_path is not None else cwd) / candidate
        if candidate.exists() and candidate.is_file():
            css_chunks.append(candidate.read_text(encoding="utf-8"))
        else:
            css_chunks.append(value)

    for value in cli.stylesheets:
        candidate = Path(os.path.expanduser(value))
        if not candidate.is_absolute():
            candidate = cwd / candidate
        if candidate.exists() and candidate.is_file():
            css_chunks.append(candidate.read_text(encoding="utf-8"))
        else:
            css_chunks.append(value)

    for value in list(raw.get("javascript", [])):
        candidate = Path(os.path.expanduser(value))
        if not candidate.is_absolute():
            candidate = (config_path.parent if config_path is not None else cwd) / candidate
        if candidate.exists() and candidate.is_file():
            js_chunks.append(candidate.read_text(encoding="utf-8"))
        else:
            js_chunks.append(value)

    for value in cli.javascripts:
        candidate = Path(os.path.expanduser(value))
        if not candidate.is_absolute():
            candidate = cwd / candidate
        if candidate.exists() and candidate.is_file():
            js_chunks.append(candidate.read_text(encoding="utf-8"))
        else:
            js_chunks.append(value)

    return BuildConfig(
        extensions=extensions,
        extension_configs=extension_configs,
        css_chunks=css_chunks,
        js_chunks=js_chunks,
        include_default_css=include_default_css,
        include_default_js=include_default_js,
    )
