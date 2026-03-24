# Implementation Plan - Enable MSYS2 Shells on Windows

Currently, [envon](file:///home/myuser/envon/src/envon/bootstrap_bash.sh#1-14) forces PowerShell on Windows and blocks automated installs for other shells. This plan enables automated installation for Bash, Fish, and Nushell on Windows, primarily targeting environments like MSYS2 and Git Bash, and adds manual documentation for these scenarios.

## User Review Required

> [!IMPORTANT]
> This change will enable automated `.bashrc`, `config.fish`, and `config.nu` updates on Windows. Previously, Windows was exempt from automatic profile modifications.

## Proposed Changes

### [envon](file:///home/myuser/envon/src/envon)

#### [MODIFY] [envon.py](file:///home/myuser/envon/src/envon/envon.py)

- **[detect_shell](file:///home/myuser/envon/src/envon/envon.py#209-280)**:
  - Reorder checks to look for `BASH_VERSION`, `ZSH_VERSION`, `FISH_VERSION`, and `NU_VERSION` before falling back to `os.name == "nt"` defaults.
- **[install_bootstrap](file:///home/myuser/envon/src/envon/envon.py#596-678)**:
  - Remove the hardcoded override that forces PowerShell on Windows if the detected/requested shell is a POSIX shell (bash, zsh, sh, fish, cshell) or Nushell.
  - Lift the [EnvonError](file:///home/myuser/envon/src/envon/envon.py#25-27) for Nushell on Windows.
- **[get_shell_config_path](file:///home/myuser/envon/src/envon/envon.py#538-594)**:
  - Ensure it returns correct paths for Fish and Nushell on Windows.

#### [NEW] [docs/MSYS2.md](file:///home/myuser/envon/docs/MSYS2.md)

- Create a new documentation file with manual installation steps for MSYS2 users as a fallback and reference.

#### [MODIFY] [README.md](file:///home/myuser/envon/README.md)

- Add a link to the MSYS2 documentation or a "Manual Installation" section.

---

## Verification Plan

### Automated Tests
- I will create a new test file `tests/test_detection.py` to verify the logic of [detect_shell](file:///home/myuser/envon/src/envon/envon.py#209-280) by mocking `os.name` and `os.environ`.
- Command: `python3 tests/test_detection.py`

### Manual Verification
1.  **In MSYS2/Git Bash (Windows)**:
    -   Run `envon --install bash` and verify it updates `.bashrc`.
    -   Run `envon --install fish` and verify it updates `config.fish`.
2.  **In Native PowerShell (Windows)**:
    -   Run `envon --install`.
    -   Verify it still provides the manual instruction block for PowerShell.
