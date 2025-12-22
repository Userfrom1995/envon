from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys
from pathlib import Path
import stat

try:
    from virtualenv.run.plugin.base import PluginLoader
except ImportError:
    # Fallback if plugin system not available
    PluginLoader = None

try:  # version info for managed bootstrap tagging
    from virtualenv.version import __version__ as VENV_VERSION
except Exception:  # pragma: no cover - defensive fallback
    VENV_VERSION = "unknown"

PREFERRED_NAMES = (".venv", "venv", "env", ".env")


class EnvonError(Exception):
    pass


def is_venv_dir(path: Path) -> bool:
    """Return True if the given path looks like a Python virtual environment directory."""
    if not path or not path.is_dir():
        return False

    # Check for pyvenv.cfg file - this is the most reliable indicator
    if (path / "pyvenv.cfg").exists():
        return True

    # Try to use virtualenv's activation system to detect available scripts
    if PluginLoader:
        try:
            activators = PluginLoader.entry_points_for("virtualenv.activate")
            # Check if any activation scripts exist
            for activator_name in ["bash", "batch", "powershell", "fish", "cshell", "nushell"]:
                if activator_name in activators:
                    # Check common script locations based on platform
                    if activator_name == "bash" and (path / "bin" / "activate").exists():
                        return True
                    if activator_name == "batch" and (path / "Scripts" / "activate.bat").exists():
                        return True
                    if activator_name == "powershell" and (path / "Scripts" / "Activate.ps1").exists():
                        return True
                    if activator_name == "fish" and (path / "bin" / "activate.fish").exists():
                        return True
                    if activator_name == "cshell" and (path / "bin" / "activate.csh").exists():
                        return True
                    if activator_name == "nushell" and (path / "bin" / "activate.nu").exists():
                        return True
        except Exception:
            # Fall back to hardcoded detection
            pass

    # Fallback: hardcoded detection for compatibility
    # Windows layout
    if (path / "Scripts" / "activate.bat").exists() or (path / "Scripts" / "Activate.ps1").exists():
        return True
    # POSIX layout
    if (path / "bin" / "activate").exists():
        return True
    # Other shells
    if (path / "bin" / "activate.fish").exists() or (path / "bin" / "activate.csh").exists() or (
            path / "bin" / "activate.nu").exists():
        return True
    return False


def find_nearest_venv(start: Path) -> Path | None:
    """Walk upwards from start to root and try common names; return the first venv path found."""
    cur = start
    tried: list[Path] = []
    while True:
        for name in PREFERRED_NAMES:
            cand = cur / name
            tried.append(cand)
            if is_venv_dir(cand):
                return cand
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return None


def _list_venvs_in_dir(root: Path) -> list[Path]:
    """Return all virtualenv directories directly under root.

    Preference order: common names first (PREFERRED_NAMES) in that order, then any other subdirectory
    that looks like a venv in alphabetical order.
    """
    found: list[Path] = []
    seen: set[Path] = set()
    for name in PREFERRED_NAMES:
        cand = root / name
        if is_venv_dir(cand):
            found.append(cand)
            seen.add(cand)
    # Scan all subdirectories
    try:
        for child in sorted([p for p in root.iterdir() if p.is_dir()]):
            if child in seen:
                continue
            if is_venv_dir(child):
                found.append(child)
    except FileNotFoundError:
        pass
    return found


def _choose_interactively(candidates: list[Path], context: str) -> Path:
    """Prompt the user to choose a venv when multiple are found.

    If stdin is not a TTY, print options and raise EnvonError.
    """
    if not sys.stdin.isatty():
        lines = "\n".join(f"  {i + 1}) {p}" for i, p in enumerate(candidates))
        raise EnvonError(
            f"Multiple virtual environments found in {context}. Choose one by passing a path or name:\n{lines}"
        )
    print(f"Multiple virtual environments found in {context}:", file=sys.stderr)
    for i, p in enumerate(candidates, 1):
        print(f"  {i}) {p}", file=sys.stderr)
    while True:
        # Print prompt to stderr so command substitution doesn't capture it
        sys.stderr.write("Select [1-{}]: ".format(len(candidates)))
        sys.stderr.flush()
        try:
            sel = sys.stdin.readline()
        except Exception:
            raise EnvonError("Aborted.")
        if not sel:
            raise EnvonError("Aborted.")
        sel = sel.strip()
        if not sel:
            continue
        if sel.isdigit():
            idx = int(sel)
            if 1 <= idx <= len(candidates):
                return candidates[idx - 1]
        print("Invalid selection.", file=sys.stderr)


def resolve_target(target: str | None) -> Path:
    if not target:
        # First, prefer venvs directly in the current directory; if multiple, ask.
        cwd = Path.cwd()
        in_here = _list_venvs_in_dir(cwd)
        if len(in_here) == 1:
            return in_here[0]
        if len(in_here) > 1:
            return _choose_interactively(in_here, str(cwd))
        # Fallback to walking upwards to find a named venv (e.g., project/.venv)
        venv = find_nearest_venv(cwd)
        if not venv:
            # Fallback: if a virtual environment is already active, respect it
            ve = os.environ.get("VIRTUAL_ENV")
            if ve and is_venv_dir(Path(ve)):
                return Path(ve)
            raise EnvonError("No virtual environment found here. Create one (e.g., '.venv') or pass a path.")
        return venv

    p = Path(target)
    if p.exists():
        if p.is_dir() and is_venv_dir(p):
            return p
        # Allow passing project root; try common children
        multiple = _list_venvs_in_dir(p)
        if len(multiple) == 1:
            return multiple[0]
        if len(multiple) > 1:
            return _choose_interactively(multiple, str(p))
        raise EnvonError(f"Path does not appear to contain a virtual environment: {p}")

    # Fallback: WORKON_HOME name
    workon = os.environ.get("WORKON_HOME")
    if workon:
        cand = Path(workon) / target
        if is_venv_dir(cand):
            return cand
    raise EnvonError(f"Cannot resolve virtual environment from argument: {target}")


def detect_shell(explicit: str | None) -> str:
    if explicit:
        return explicit.lower()

    # Heuristics by platform/env
    if os.name == "nt":
        # Prefer PowerShell if available, else default to cmd
        if "PSModulePath" in os.environ:
            return "powershell"
        return "cmd"
    # POSIX
    # 1) Environment variables set by the shell itself (most reliable when present)
    if os.environ.get("ZSH_VERSION"):
        return "zsh"
    if os.environ.get("BASH_VERSION"):
        return "bash"
    if os.environ.get("FISH_VERSION"):
        return "fish"
    # nushell does not (always) export a dedicated var; try a common one if present
    if os.environ.get("NU_VERSION"):
        return "nushell"

    # 2) Inspect parent process (the shell) via /proc when available (Linux/WSL)
    try:
        ppid = os.getppid()
        proc_comm = Path("/proc") / str(ppid) / "comm"
        name = ""
        if proc_comm.exists():
            try:
                name = proc_comm.read_text(encoding="utf-8").strip().lower()
            except Exception:
                name = ""
        if not name:
            proc_exe = Path("/proc") / str(ppid) / "exe"
            if proc_exe.exists():
                try:
                    name = os.path.basename(os.readlink(proc_exe)).lower()
                except Exception:
                    name = ""
        if name:
            # Normalize common names
            if "zsh" in name:
                return "zsh"
            if name in {"bash", "sh"} or "bash" in name:
                return "bash" if "bash" in name else "sh"
            if "fish" in name:
                return "fish"
            if name in {"csh", "tcsh"} or "csh" in name or "tcsh" in name:
                return "cshell"
            if "nu" in name:
                return "nushell"
            if name in {"pwsh", "powershell"}:
                return "powershell"
            if name in {"cmd", "cmd.exe"}:
                return "cmd"
    except Exception:
        pass

    # 3) Fallback to $SHELL login shell
    shell = os.environ.get("SHELL", "").lower()
    if "zsh" in shell:
        return "zsh"
    if "fish" in shell:
        return "fish"
    if "csh" in shell or "tcsh" in shell:
        return "cshell"
    if "nu" in shell or "nushell" in shell:
        return "nushell"
    if shell.endswith("sh") and "bash" not in shell:
        return "sh"
    return "bash"


def emit_activation(venv: Path, shell: str) -> str:
    """Generate activation command using virtualenv's activation plugin system."""
    shell = shell.lower()

    # Nushell is not supported on Windows — refuse to emit activation for it
    if os.name == "nt" and shell in {"nu", "nushell"}:
        raise EnvonError(
            "Nushell activation is not supported on Windows. Use PowerShell (powershell/pwsh) or cmd."
        )

    # Map shell names to activator entry point names
    shell_to_activator = {
        "bash": "bash",
        "zsh": "bash",  # zsh uses bash activator
        "sh": "bash",  # sh uses bash activator
        "fish": "fish",
        "csh": "cshell",
        "tcsh": "cshell",
        "cshell": "cshell",
        "nu": "nushell",  # Map nushell to its activator
        "nushell": "nushell",  # Map nushell to its activator
        "powershell": "powershell",
        "pwsh": "powershell",
        "cmd": "batch",
        "batch": "batch",
        "bat": "batch",
    }

    activator_name = shell_to_activator.get(shell)
    if not activator_name:
        supported = ", ".join(sorted(shell_to_activator.keys()))
        raise EnvonError(
            f"Unsupported shell: {shell}. Supported shells: {supported}. "
            f"Specify --emit <shell> explicitly or omit --emit to auto-detect."
        )

    # Try to use the plugin system to get proper script names
    if PluginLoader:
        try:
            activators = PluginLoader.entry_points_for("virtualenv.activate")
            if activator_name in activators:
                activator_class = activators[activator_name]

                # Create a minimal mock creator to get script names
                class MockCreator:
                    def __init__(self, venv_path):
                        self.dest = venv_path
                        if (venv_path / "Scripts").exists():  # Windows
                            self.bin_dir = venv_path / "Scripts"
                        else:  # POSIX
                            self.bin_dir = venv_path / "bin"

                mock_creator = MockCreator(venv)

                # Try to determine activation script name from the activator
                try:
                    # Create a temporary activator instance with minimal options
                    class MockOptions:
                        prompt = None

                    activator = activator_class(MockOptions())

                    # Get the templates to determine script names
                    if hasattr(activator, 'templates'):
                        for template in activator.templates():
                            if hasattr(activator, 'as_name'):
                                script_name = activator.as_name(template)
                            else:
                                script_name = template

                            script_path = mock_creator.bin_dir / script_name
                            if script_path.exists():
                                return _generate_activation_command(script_path, shell)
                except Exception:
                    # Fall back to hardcoded approach if activator instantiation fails
                    pass
        except Exception:
            # Fall back to hardcoded paths if plugin system fails
            pass

    # Fallback: Use hardcoded script detection
    return _emit_activation_fallback(venv, shell)


def _generate_activation_command(script_path: Path, shell: str) -> str:
    """Generate the appropriate activation command for the given script and shell."""
    shell = shell.lower()

    if shell in {"bash", "zsh", "sh"}:
        return f". '{script_path.as_posix()}'"
    elif shell == "fish":
        return f"source '{script_path.as_posix()}'"
    if shell in {"csh", "tcsh", "cshell"}:
        return f"source {script_path.as_posix()}"
    elif shell in {"nu", "nushell"}:
        # For Nushell we only print the overlay use on the activation script path.
        return f"overlay use \"{script_path.as_posix()}\""
    elif shell in {"powershell", "pwsh"}:
        return f". '{script_path.as_posix()}'"
    elif shell in {"cmd", "batch", "bat"}:
        return f"call \"{script_path}\""

    raise EnvonError(f"Unknown shell command format for: {shell}")


def _emit_activation_fallback(venv: Path, shell: str) -> str:
    """Fallback activation detection using hardcoded paths."""
    shell = shell.lower()

    if shell in {"bash", "zsh", "sh"}:
        act = venv / "bin" / "activate"
        if act.exists():
            return f". '{act.as_posix()}'"
    elif shell == "fish":
        act = venv / "bin" / "activate.fish"
        if act.exists():
            return f"source '{act.as_posix()}'"
    elif shell in {"csh", "tcsh", "cshell"}:
        act = venv / "bin" / "activate.csh"
        if act.exists():
            return f"source {act.as_posix()}"
    elif shell in {"nu", "nushell"}:
        # Check for activate.nu in both Windows and POSIX locations and print overlay use on it.
        act_posix = venv / "bin" / "activate.nu"
        act_windows = venv / "Scripts" / "activate.nu"
        act = act_posix if act_posix.exists() else act_windows if act_windows.exists() else None
        if act and act.exists():
            return f"overlay use \"{act.as_posix()}\""
        raise EnvonError(
            f"Virtual environment '{venv}' does not support Nushell activation: 'activate.nu' is missing. "
            "Create or upgrade the environment with a tool that generates Nushell activation scripts, "
            "or use a different shell (bash/zsh/fish)."
        )
    elif shell in {"powershell", "pwsh"}:
        act = venv / "Scripts" / "Activate.ps1"
        if act.exists():
            return f". '{act.as_posix()}'"
    elif shell in {"cmd", "batch", "bat"}:
        act = venv / "Scripts" / "activate.bat"
        if act.exists():
            return f"call \"{act}\""

    raise EnvonError(
        f"No activation script found for shell '{shell}' in '{venv}'. "
        "Try specifying --emit explicitly, or ensure the virtualenv's activation scripts exist."
    )


def emit_deactivation(shell: str) -> str:
    """Generate deactivation command for the given shell."""
    shell = shell.lower()

    # Map shell names to their deactivation commands
    # Most shells use a simple 'deactivate' function/command provided by the venv
    if shell in {"bash", "zsh", "sh", "fish", "csh", "tcsh", "cshell", "powershell", "pwsh"}:
        return "deactivate"
    elif shell in {"nu", "nushell"}:
        # Nushell uses deactivate function when available
        return "deactivate"
    elif shell in {"cmd", "batch", "bat"}:
        # cmd uses the deactivate command
        return "deactivate"
    else:
        # Fallback - most virtualenvs provide a deactivate function
        return "deactivate"


## Nushell: uses overlay use on activate.nu directly


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="envon",
        description="Emit the activation command for the nearest or specified virtual environment.",
    )
    p.add_argument("target", nargs="?", help="Path, project root, or name (searched in WORKON_HOME)")
    p.add_argument(
        "--emit",
        nargs="?",
        const="",
        metavar="SHELL",
        help=(
            "Emit activation command. If SHELL is provided, use it (bash, zsh, sh, fish, cshell, nushell, powershell, pwsh, cmd); "
            "if omitted, auto-detect the current shell."
        ),
    )
    p.add_argument(
        "--print-path",
        action="store_true",
        help="Print only the resolved virtual environment path and exit.",
    )
    p.add_argument(
        "--install",
        nargs="?",
        const="",
        metavar="SHELL",
        help=(
            "Install envon bootstrap function directly to shell configuration file. "
            "If SHELL is omitted, auto-detect."
        ),
    )
    p.add_argument(
        "-d",
        "--deactivate",
        nargs="?",
        const="",
        metavar="SHELL",
        help=(
            "Emit deactivation command. If SHELL is provided, use it; "
            "if omitted, auto-detect the current shell."
        ),
    )
    return p.parse_args(argv)


def emit_bootstrap(shell: str) -> str:
    """Generate the bootstrap function for the given shell by reading from dedicated files."""
    shell = shell.lower()
    bootstrap_dir = Path(__file__).parent  # Directory of envon.py

    file_map = {
        "bash": "bootstrap_bash.sh",
        "zsh": "bootstrap_bash.sh",  # zsh reuses bash
        "sh": "bootstrap_sh.sh",
        "fish": "bootstrap_fish.fish",
        "nushell": "bootstrap_nushell.nu",
        "nu": "bootstrap_nushell.nu",
        "powershell": "bootstrap_powershell.ps1",
        "pwsh": "bootstrap_powershell.ps1",
        "csh": "bootstrap_csh.csh",
        "tcsh": "bootstrap_csh.csh",
        "cshell": "bootstrap_csh.csh",
    }

    if shell not in file_map:
        raise EnvonError(f"Unsupported shell: {shell}")

    bootstrap_file = bootstrap_dir / file_map[shell]
    if not bootstrap_file.exists():
        raise EnvonError(f"Bootstrap file missing: {bootstrap_file}")

    text = bootstrap_file.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):  # strip BOM
        text = text.lstrip("\ufeff")
    return text


def get_shell_config_path(shell: str) -> Path:
    """Get the configuration file path for a given shell."""
    shell = shell.lower()
    home = Path.home()

    if shell == "bash":
        # Try .bashrc first, fall back to .bash_profile
        bashrc = home / ".bashrc"
        if bashrc.exists():
            return bashrc
        return home / ".bash_profile"
    if shell == "sh":
        # POSIX sh typically sources ~/.profile (login shells); there is no standard per-shell rc
        # We choose ~/.profile as the install target.
        return home / ".profile"
    elif shell == "zsh":
        return home / ".zshrc"
    elif shell == "fish":
        config_dir = home / ".config" / "fish"
        return config_dir / "config.fish"
    elif shell in {"nushell", "nu"}:
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA", home)) / "nushell"
        else:  # POSIX
            config_dir = home / ".config" / "nushell"
        return config_dir / "config.nu"
    elif shell in {"powershell", "pwsh"}:
        if os.name == "nt":  # Windows
            documents = Path.home() / "Documents"
            # Check for both possible profile file names
            if shell == "pwsh":
                core_profile = documents / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
                alt_core_profile = documents / "PowerShell" / "profile.ps1"
                if core_profile.exists():
                    return core_profile
                if alt_core_profile.exists():
                    return alt_core_profile
                # Default to core_profile if neither exists
                return core_profile
            else:
                win_profile = documents / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
                alt_win_profile = documents / "WindowsPowerShell" / "profile.ps1"
                if win_profile.exists():
                    return win_profile
                if alt_win_profile.exists():
                    return alt_win_profile
                # Default to win_profile if neither exists
                return win_profile
        else:  # POSIX PowerShell Core
            return home / ".config" / "powershell" / "Microsoft.PowerShell_profile.ps1"
    elif shell in {"csh", "tcsh", "cshell"}:
        if shell == "tcsh":
            return home / ".tcshrc"
        return home / ".cshrc"

    raise EnvonError(f"Unknown shell configuration path for: {shell}")


def install_bootstrap(shell: str | None) -> str:
    """Install envon bootstrap function to shell configuration file."""
    shell = detect_shell(shell)  # auto-detect when None or empty string
    shell = shell.lower()
    # Windows-specific policy: do not modify any profile files automatically
    # - Nushell is not supported on Windows for installation
    # - For PowerShell, write the managed file and instruct the user to update their profile manually
    if os.name == "nt":
        if shell in {"nushell", "nu"}:
            raise EnvonError(
                "Nushell is not supported on Windows. Please use PowerShell (powershell/pwsh)."
            )

        # Default to PowerShell on Windows installs
        ps_shell = "powershell" if shell == "powershell" else ("pwsh" if shell == "pwsh" else "powershell")
        managed_file = get_managed_bootstrap_path(ps_shell)
        managed_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate and write the managed content (PowerShell)
        content = _managed_content_for_shell("powershell" if ps_shell == "powershell" else "powershell")
        _write_managed_if_changed(managed_file, content)

        # Compute the recommended profile path to show the user
        profile_path = get_shell_config_path(ps_shell)

        manual_block = (
            f"$envonPath = '{managed_file}'\nif (Test-Path $envonPath) {{ . $envonPath }}"
        )

        return (
            "envon bootstrap prepared for Windows (no profile auto-edit performed).\n"
            f"- managed file: {managed_file}\n"
            f"- PowerShell profile: {profile_path}\n\n"
            "Add the following lines to your PowerShell profile manually, then restart the shell:\n\n"
            f"{manual_block}"
        )

    # Non-Windows: proceed with automated RC update
    config_path = get_shell_config_path(shell)

    # Ensure parent directory exists and target is a file path
    config_path.parent.mkdir(parents=True, exist_ok=True)
    # Guard against a directory accidentally existing at the profile path
    if config_path.exists() and config_path.is_dir():
        raise EnvonError(
            f"Profile path points to a directory, not a file: {config_path}. "
            "Please remove/rename this directory or set the correct profile file."
        )

    # Managed bootstrap: write function to a stable file and source it from RC with markers
    managed_file = get_managed_bootstrap_path(shell)
    managed_file.parent.mkdir(parents=True, exist_ok=True)

    # Generate function content for the managed file
    target_shell = (
        "bash" if shell == "bash" else
        "zsh" if shell == "zsh" else
        "sh" if shell == "sh" else
        "fish" if shell == "fish" else
        "nushell" if shell in {"nushell", "nu"} else
        "powershell" if shell in {"powershell", "pwsh"} else
        "csh" if shell in {"csh", "tcsh", "cshell"} else None
    )
    if target_shell is None:
        supported = "bash, zsh, sh, fish, nushell, nu, powershell, pwsh, csh, tcsh, cshell"
        raise EnvonError(
            f"Unsupported shell for installation: {shell}. Supported: {supported}. "
            f"Specify '--install <shell>' explicitly or run 'envon --bootstrap <shell>' and source it manually."
        )
    content = _managed_content_for_shell(target_shell)
    _write_managed_if_changed(managed_file, content)

    # Ensure RC contains a single, marked source block
    _ensure_rc_sources_managed(config_path, managed_file, shell)
    # Pick correct source command for user hint
    source_cmd = (
        "." if shell in {"sh", "powershell", "pwsh"} else "source"
    )
    return (
        f"envon bootstrap installed:\n- managed: {managed_file}\n- rc: {config_path}\n"
        f"Restart your shell or run: {source_cmd} {config_path}"
    )


MARK_START = "# >>> envon bootstrap >>>"
MARK_END = "# <<< envon bootstrap <<<"


def get_managed_bootstrap_path(shell: str) -> Path:
    """Return the managed bootstrap file path for a shell."""
    shell = shell.lower()
    # Determine config base dir
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    envon_dir = base / "envon"

    name = (
        "envon.bash" if shell == "bash" else
        "envon.zsh" if shell == "zsh" else
        "envon.sh" if shell == "sh" else
        "envon.fish" if shell == "fish" else
        "envon.nu" if shell in {"nushell", "nu"} else
        "envon.ps1" if shell in {"powershell", "pwsh"} else
        "envon.csh" if shell in {"csh", "tcsh", "cshell"} else None
    )
    if name is None:
        raise EnvonError(f"Unsupported shell: {shell}")
    return envon_dir / name


# def get_nushell_venv_path() -> Path:
#     """Return the path to the managed Nushell venv.nu file."""
#     if os.name == "nt":
#         base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
#     else:
#         base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
#     envon_dir = base / "envon"
#     return envon_dir / "venv.nu"


# def _ensure_nushell_venv_file() -> None:
#     """Ensure the managed Nushell venv.nu file and parent dir exist."""
#     venv_path = get_nushell_venv_path()
#     venv_path.parent.mkdir(parents=True, exist_ok=True)
#     if not venv_path.exists():
#         # create a placeholder file that will be overwritten on activation
#         venv_path.write_text("# envon venv.nu - will be overwritten when activating environments\n", encoding="utf-8")


def _write_managed_if_changed(path: Path, content: str) -> None:
    """Write content to path if missing or different."""
    try:
        if path.exists() and path.read_text() == content:
            return
    except Exception:
        # If read fails, attempt to overwrite
        pass
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _ensure_rc_sources_managed(config_path: Path, managed_file: Path, shell: str) -> None:
    """Ensure the user's RC/profile sources the managed file, using idempotent markers."""
    rc_exists = config_path.exists() and config_path.is_file()
    rc_text = config_path.read_text(encoding="utf-8") if rc_exists else ""

    # If already installed with markers, do nothing
    if MARK_START in rc_text and MARK_END in rc_text:
        return

    mf = managed_file.as_posix()
    if shell in {"bash", "zsh", "sh"}:
        block = f"\n{MARK_START}\n[ -f {mf} ] && . {mf}\n{MARK_END}\n"
    elif shell == "fish":
        block = f"\n{MARK_START}\nif test -f {mf}\n    source {mf}\nend\n{MARK_END}\n"
    elif shell in {"nushell", "nu"}:
        # Always quote the managed file path to avoid extra positional argument errors
        block = (
            f"\n{MARK_START}\n"
            f"if (ls '{mf}' | is-empty) == false {{\n    source '{mf}'\n}}\n"
            f"{MARK_END}\n"
        )
    elif shell in {"powershell", "pwsh"}:
        block = (
            f"\n{MARK_START}\n"
            f"$envonPath = '{managed_file}'\nif (Test-Path $envonPath) {{ . $envonPath }}\n"
            f"{MARK_END}\n"
        )
    elif shell in {"csh", "tcsh", "cshell"}:
        block = f"\n{MARK_START}\nif ( -f {mf} ) source {mf}\n{MARK_END}\n"
    else:
        raise EnvonError(f"Unsupported shell: {shell}")

    # Write or append the block with a robust fallback for Windows I/O quirks
    try:
        # Try to clear read-only flag if present
        if rc_exists:
            try:
                os.chmod(config_path, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass
        if not rc_exists:
            # Create new profile file with our block
            config_path.write_text(block, encoding="utf-8")
        else:
            with config_path.open("a", encoding="utf-8") as f:
                f.write(block)
    except OSError as e:
        # Fallback: write the full combined content (existing + block)
        combined = rc_text + block
        try:
            config_path.write_text(combined, encoding="utf-8")
        except Exception as e2:
            # On PowerShell, also try the alternate profile file name
            if shell in {"powershell", "pwsh"}:
                try:
                    alt_name = (
                        "Microsoft.PowerShell_profile.ps1"
                        if config_path.name.lower() == "profile.ps1"
                        else "profile.ps1"
                    )
                    alt_path = config_path.with_name(alt_name)
                    alt_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        # Clear read-only if exists
                        if alt_path.exists():
                            try:
                                os.chmod(alt_path, stat.S_IWRITE | stat.S_IREAD)
                            except Exception:
                                pass
                        # If alternate exists and already contains our block, we're done
                        try:
                            alt_text = alt_path.read_text(encoding="utf-8")
                        except Exception:
                            alt_text = ""
                        if MARK_START in alt_text and MARK_END in alt_text:
                            return
                        # Otherwise write combined content to alternate profile
                        alt_combined = alt_text + block if alt_text else block
                        alt_path.write_text(alt_combined, encoding="utf-8")
                        return
                    except Exception as e3:
                        raise EnvonError(
                            "Failed to update PowerShell profile. Tried both: "
                            f"{config_path} (error: {e2}) and {alt_path} (error: {e3}). "
                            "Close any editor locking the file, ensure it's not a directory or read-only, "
                            "or create the file manually and re-run."
                        ) from e3
                except Exception:
                    # If building alt path failed, fall through to generic error
                    pass
            # Generic failure if all fallbacks failed
            raise EnvonError(
                f"Failed to update shell profile at {config_path}: {e2}"
            ) from e


def _managed_content_for_shell(shell: str) -> str:
    """Build the content stored in the managed file, tagged with the package version.

    Including the version allows us to detect when an upgrade may require refreshing
    the managed file, while avoiding unnecessary rewrites.
    """
    body = emit_bootstrap(shell)
    header = f"# envon managed bootstrap - version: {VENV_VERSION}\n"
    return header + body


def _maybe_update_managed_current_shell(explicit_shell: str | None) -> None:
    """If a managed bootstrap file exists for the current/detected shell, refresh it when outdated.

    This runs silently on each invocation and only writes when the content differs,
    so normal runs stay fast and side-effect free for already up-to-date installs.
    """
    try:
        shell = detect_shell(explicit_shell)
        managed = get_managed_bootstrap_path(shell)
        if managed.exists():
            desired = _managed_content_for_shell(
                "bash" if shell == "bash" else
                "zsh" if shell == "zsh" else
                "sh" if shell == "sh" else
                "fish" if shell == "fish" else
                "nushell" if shell in {"nushell", "nu"} else
                "powershell" if shell in {"powershell", "pwsh"} else
                "csh" if shell in {"csh", "tcsh", "cshell"} else shell
            )
            try:
                current = managed.read_text(encoding="utf-8")
            except Exception:
                current = ""
            if current != desired:
                _write_managed_if_changed(managed, desired)
    except Exception:
        # Never fail the main command due to a managed-file refresh issue
        pass


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])
    try:
        # Opportunistic refresh of managed bootstrap (no-op if not installed)
        _maybe_update_managed_current_shell(None)
        if ns.install is not None:
            result = install_bootstrap(ns.install)
            print(result)
            return 0
        if ns.deactivate is not None:
            shell = detect_shell(ns.deactivate)
            cmd = emit_deactivation(shell)
            print(cmd)
            return 0
        venv = resolve_target(ns.target)
        if ns.print_path:
            print(str(venv))
            return 0
        shell = detect_shell(ns.emit)
        cmd = emit_activation(venv, shell)
        print(cmd)
        return 0
    except EnvonError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
