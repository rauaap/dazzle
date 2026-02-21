from __future__ import annotations

import argparse
from pathlib import Path
import sys

from dazzle.compiler import compile_markdown_file_to_html, compile_markdown_source_to_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dazzle", description="Compile Markdown into a slide deck HTML file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a slide deck from markdown.")
    build_parser.add_argument("input", help="Path to markdown input file, or '-' to read from stdin.")
    build_parser.add_argument("-o", "--output", required=True, help="Path to generated HTML output file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        output_path = Path(args.output)
        if args.input == "-":
            source = sys.stdin.read()
            compile_markdown_source_to_html(
                source=source,
                source_name="stdin.md",
                source_dir=Path.cwd(),
                output_path=output_path,
            )
        else:
            input_path = Path(args.input)
            compile_markdown_file_to_html(input_path, output_path)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
