from __future__ import annotations

import unittest

from dazzle.cli import build_parser


class CliParserTests(unittest.TestCase):
    def test_build_parser_accepts_new_flags(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "build",
                "slides.md",
                "-o",
                "deck.html",
                "-c",
                "cfg.toml",
                "-x",
                "toc",
                "-x",
                "admonition",
                "-s",
                "a.css",
                "-j",
                "b.js",
                "--no-default-css",
                "--no-default-js",
            ]
        )

        self.assertEqual("build", args.command)
        self.assertEqual("cfg.toml", args.config)
        self.assertEqual(["toc", "admonition"], args.extension)
        self.assertEqual(["a.css"], args.stylesheet)
        self.assertEqual(["b.js"], args.javascript)
        self.assertTrue(args.no_default_css)
        self.assertTrue(args.no_default_js)


if __name__ == "__main__":
    unittest.main()
