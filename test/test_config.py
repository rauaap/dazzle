from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from dazzle.config import BuildCliOptions, load_build_config


class LoadBuildConfigTests(unittest.TestCase):
    def test_uses_local_config_then_merges_cli_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)
            (cwd / "cfg.css").write_text("h1 { color: red; }", encoding="utf-8")
            (cwd / "cfg.js").write_text("window.A=1;", encoding="utf-8")
            (cwd / "cli.css").write_text("h2 { color: blue; }", encoding="utf-8")
            (cwd / "cli.js").write_text("window.B=2;", encoding="utf-8")
            (cwd / "dazzle.toml").write_text(
                'extension=["toc"]\nstylesheet=["./cfg.css"]\njavascript=["./cfg.js"]',
                encoding="utf-8",
            )
            cli = BuildCliOptions(
                config_path=None,
                extensions=["admonition"],
                stylesheets=["./cli.css"],
                javascripts=["./cli.js"],
                no_default_css=False,
                no_default_js=False,
            )
            cfg = load_build_config(cli, cwd=cwd, home=cwd / "home")
            self.assertEqual(["toc", "admonition"], cfg.extensions)
            self.assertEqual(["h1 { color: red; }", "h2 { color: blue; }"], cfg.css_chunks)
            self.assertEqual(["window.A=1;", "window.B=2;"], cfg.js_chunks)

    def test_loads_home_fallback_when_no_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cwd = root / "cwd"
            home = root / "home"
            cwd.mkdir()
            home_cfg = home / ".config" / "dazzle" / "config.toml"
            home_cfg.parent.mkdir(parents=True)
            home_cfg.write_text('extension=["toc"]', encoding="utf-8")

            cli = BuildCliOptions(
                config_path=None,
                extensions=[],
                stylesheets=[],
                javascripts=[],
                no_default_css=False,
                no_default_js=False,
            )
            cfg = load_build_config(cli, cwd=cwd, home=home)
            self.assertEqual(["toc"], cfg.extensions)

    def test_missing_explicit_config_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)
            cli = BuildCliOptions(
                config_path=cwd / "missing.toml",
                extensions=[],
                stylesheets=[],
                javascripts=[],
                no_default_css=False,
                no_default_js=False,
            )
            with self.assertRaises(FileNotFoundError):
                load_build_config(cli, cwd=cwd, home=cwd / "home")


if __name__ == "__main__":
    unittest.main()
