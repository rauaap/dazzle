from __future__ import annotations

import argparse
from pathlib import Path
import sys

from dazzle.compiler import compile_markdown_file_to_html, compile_markdown_source_to_html
from dazzle.config import BuildCliOptions, load_build_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dazzle", description="Compile Markdown into a slide deck HTML file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a slide deck from markdown.")
    build_parser.add_argument("input", help="Path to markdown input file, or '-' to read from stdin.")
    build_parser.add_argument("-o", "--output", required=True, help="Path to generated HTML output file.")
    build_parser.add_argument("-c", "--config", help="Path to TOML config file.")
    build_parser.add_argument(
        "-x",
        "--extension",
        action="append",
        default=[],
        help="Python-Markdown extension to load (repeatable).",
    )
    build_parser.add_argument(
        "-s",
        "--stylesheet",
        action="append",
        default=[],
        help="Stylesheet path or inline CSS text (repeatable).",
    )
    build_parser.add_argument(
        "-j",
        "--javascript",
        action="append",
        default=[],
        help="JavaScript path or inline JS text (repeatable).",
    )
    build_parser.add_argument(
        "--no-default-css",
        action="store_true",
        help="Do not include built-in theme CSS.",
    )
    build_parser.add_argument(
        "--no-default-js",
        action="store_true",
        help="Do not include built-in runtime JS.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        output_path = Path(args.output)
        cli_options = BuildCliOptions(
            config_path=Path(args.config) if args.config is not None else None,
            extensions=args.extension,
            stylesheets=args.stylesheet,
            javascripts=args.javascript,
            no_default_css=args.no_default_css,
            no_default_js=args.no_default_js,
        )
        build_config = load_build_config(cli_options, cwd=Path.cwd())
        if args.input == "-":
            source = sys.stdin.read()
            compile_markdown_source_to_html(
                source=source,
                source_name="stdin.md",
                source_dir=Path.cwd(),
                output_path=output_path,
                build_config=build_config,
            )
        else:
            input_path = Path(args.input)
            compile_markdown_file_to_html(input_path, output_path, build_config=build_config)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
