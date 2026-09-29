import io
import os
import sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import unittest

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
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / "pyvenv.cfg").write_text("home = /usr/bin/python\n", encoding="utf-8")
    bin_dir = dirpath / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    (bin_dir / "activate").write_text("# activate", encoding="utf-8")
    return dirpath


def make_windows_venv(dirpath: Path):
    dirpath.mkdir(parents=True, exist_ok=True)
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

    def test_is_venv_dir_non_venv(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            root = Path(td)
            empty_dir = root / "empty"
            empty_dir.mkdir()
            self.assertFalse(envon_mod.is_venv_dir(empty_dir))

    def test_resolve_target_walks_up(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            root = Path(td).resolve()
            proj = root / "proj"
            (proj / "sub" / "dir").mkdir(parents=True)
            venv = make_posix_venv(proj / ".venv")
            with TempCwd(proj / "sub" / "dir"):
                resolved = envon_mod.resolve_target(None)
                self.assertIsNotNone(resolved)
                self.assertEqual(resolved.resolve(), venv.resolve())

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
            self.assertEqual(cmd, f"source '{(venv / 'bin' / 'activate.csh').as_posix()}'")

    def test_emit_activation_powershell(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_windows_venv(Path(td) / ".venv")
            cmd = envon_mod.emit_activation(venv, "powershell")
            scripts_dir = (venv / "Scripts").as_posix().lower()
            self.assertTrue(
                cmd.lower().startswith(f". '{scripts_dir}/activate.ps1'"),
                f"Unexpected command: {cmd}",
            )

    def test_emit_activation_cmd(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_windows_venv(Path(td) / ".venv")
            cmd = envon_mod.emit_activation(venv, "cmd")
            self.assertIn("call \"" + str(venv / "Scripts" / "activate.bat") + "\"", cmd)

    def test_emit_activation_nushell_posix(self):
        if os.name == "nt" and not envon_mod._is_posix_layer_on_windows():
            self.skipTest("Nushell activation unsupported on native Windows")
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            (venv / "bin" / "activate.nu").write_text("# nu", encoding="utf-8")
            cmd = envon_mod.emit_activation(venv, "nushell")
            self.assertIn("overlay use \"" + (venv / "bin" / "activate.nu").as_posix() + "\"", cmd)

    def test_emit_activation_nushell_fallback(self):
        if os.name == "nt" and not envon_mod._is_posix_layer_on_windows():
            self.skipTest("Nushell activation unsupported on native Windows")
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            cmd = envon_mod.emit_activation(venv, "nushell")
            self.assertIn("load-env", cmd)
            self.assertIn((venv / "bin").as_posix(), cmd)

    def test_emit_activation_powershell_posix(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            venv = make_posix_venv(Path(td) / ".venv")
            (venv / "bin" / "Activate.ps1").write_text("# ps1", encoding="utf-8")
            cmd = envon_mod.emit_activation(venv, "powershell")
            bin_dir = (venv / "bin").as_posix().lower()
            self.assertTrue(
                cmd.lower().startswith(f". '{bin_dir}/activate.ps1'"),
                f"Unexpected command: {cmd}",
            )

    def test_emit_deactivation_all_shells(self):
        for shell in ["bash", "zsh", "sh", "fish", "csh", "tcsh", "cshell", "nushell", "powershell", "cmd"]:
            cmd = envon_mod.emit_deactivation(shell)
            self.assertEqual(cmd, "deactivate")

    def test_emit_bootstrap(self):
        for shell in ["bash", "zsh", "sh", "fish", "csh", "nushell", "powershell"]:
            content = envon_mod.emit_bootstrap(shell)
            self.assertTrue(len(content) > 0)
            self.assertFalse(content.startswith("\ufeff"))  # No BOM

    def test_detect_shell_explicit(self):
        self.assertEqual(envon_mod.detect_shell("Fish"), "fish")
        self.assertEqual(envon_mod.detect_shell("BASH"), "bash")

    def test_managed_content_contains_version(self):
        content = envon_mod._managed_content_for_shell("bash")
        self.assertIn(f"version: {envon_mod.__version__}", content)

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

    def test_main_deactivate(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = envon_mod.main(["--deactivate", "bash"])
        self.assertEqual(rc, 0)
        self.assertEqual(f.getvalue().strip(), "deactivate")

    def test_main_unknown_flag(self):
        err = io.StringIO()
        with redirect_stderr(err):
            with self.assertRaises(SystemExit):
                envon_mod.main(["--nonexistent-flag"])

    def test_main_help_command(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with self.assertRaises(SystemExit) as ctx:
                envon_mod.main(["help"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("Emit the activation command", f.getvalue())

    def test_managed_content_csh_header(self):
        content = envon_mod._managed_content_for_shell("csh")
        self.assertIn(f"version: {envon_mod.__version__}", content)
        self.assertIn("set _envon_cmd =", content)

    def test_csh_bootstrap_content(self):
        content = envon_mod.emit_bootstrap("csh")
        self.assertIn("_envon_args", content)
        self.assertIn("(exit $_envon_ec)", content)

    def test_nushell_bootstrap_wrapped(self):
        content = envon_mod.emit_bootstrap("nushell")
        self.assertIn("def --wrapped --env envon", content)
        self.assertIn("def --env deactivate", content)
        self.assertIn("load-env", content)
        self.assertIn("$env.LAST_EXIT_CODE = ($e.exit_code? | default 1)", content)

    def test_ensure_rc_sources_managed_quoting(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as td:
            rc_file = Path(td) / ".bashrc"
            managed_file = Path(td) / "path with spaces" / "envon.bash"
            envon_mod._ensure_rc_sources_managed(rc_file, managed_file, "bash")
            text = rc_file.read_text(encoding="utf-8")
            self.assertIn(f'[ -f "{managed_file.as_posix()}" ]', text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

