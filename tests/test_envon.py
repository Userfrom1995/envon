import io
import os
import sys
import textwrap
from contextlib import redirect_stdout
from pathlib import Path

import unittest

# Ensure 'src' is on sys.path for direct test runs without install
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from envon import envon as envon_mod


class TempCwd:
    def __init__(self, path: Path):
        self.path = path
        self.prev = None

    def __enter__(self):
        self.prev = Path.cwd()
        os.chdir(self.path)
        return self.path

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self.prev)


def make_posix_venv(dirpath: Path):
    (dirpath / "pyvenv.cfg").write_text("home = /usr/bin/python\n", encoding="utf-8")
    bin_dir = dirpath / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    (bin_dir / "activate").write_text("# activate", encoding="utf-8")
    return dirpath


def make_windows_venv(dirpath: Path):
    (dirpath / "pyvenv.cfg").write_text("home = C:\\Python\\python.exe\n", encoding="utf-8")
    scripts = dirpath / "Scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "activate.bat").write_text("@echo off", encoding="utf-8")
    (scripts / "Activate.ps1").write_text("# ps1", encoding="utf-8")
    return dirpath


class TestEnvon(unittest.TestCase):
    def test_is_venv_dir_pyvenv_cfg(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            root = Path(td)
            venv = root / ".venv"
            venv.mkdir()
            (venv / "pyvenv.cfg").write_text("home = /usr/bin/python\n", encoding="utf-8")
            self.assertTrue(envon_mod.is_venv_dir(venv))

    def test_resolve_target_walks_up(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            root = Path(td)
            proj = root / "proj"
            (proj / "sub" / "dir").mkdir(parents=True)
            venv = make_posix_venv(proj / ".venv")
            with TempCwd(proj / "sub" / "dir"):
                resolved = envon_mod.resolve_target(None)
                self.assertEqual(resolved, venv)

    def test_emit_activation_bash(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            cmd = envon_mod.emit_activation(venv, "bash")
            self.assertIn(". '" + (venv / "bin" / "activate").as_posix() + "'", cmd)

    def test_emit_activation_fish(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            (venv / "bin" / "activate.fish").write_text("# fish", encoding="utf-8")
            cmd = envon_mod.emit_activation(venv, "fish")
            self.assertIn("source '" + (venv / "bin" / "activate.fish").as_posix() + "'", cmd)

    def test_emit_activation_cshell(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            (venv / "bin" / "activate.csh").write_text("# csh", encoding="utf-8")
            cmd = envon_mod.emit_activation(venv, "csh")
            self.assertIn("source " + (venv / "bin" / "activate.csh").as_posix(), cmd)

    def test_emit_activation_powershell(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_windows_venv(Path(td) / ".venv")
            cmd = envon_mod.emit_activation(venv, "powershell")
            self.assertIn(". '" + (venv / "Scripts" / "Activate.ps1").as_posix() + "'", cmd)

    def test_emit_activation_nushell_posix(self):
        if os.name == "nt":
            self.skipTest("Nushell activation intentionally unsupported on Windows in this implementation")
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            (venv / "bin" / "activate.nu").write_text("# nu", encoding="utf-8")
            cmd = envon_mod.emit_activation(venv, "nushell")
            self.assertIn("overlay use \"" + (venv / "bin" / "activate.nu").as_posix() + "\"", cmd)

    def test_main_print_path(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            f = io.StringIO()
            with redirect_stdout(f):
                rc = envon_mod.main([str(venv), "--print-path"])
            self.assertEqual(rc, 0)
            out = f.getvalue().strip()
            self.assertEqual(Path(out), venv)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
