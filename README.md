# envon

Emit the activation command for the nearest or specified Python virtual environment, and install shell bootstrap wrappers for seamless activation in your favorite shell.

## Features
- Auto-detects and activates Python virtual environments in your project.
- Supports multiple shells: bash, zsh, sh, fish, powershell, pwsh, nushell, cmd, csh/tcsh/cshell.
- Installs a shell bootstrap function for one-command activation.
- Flexible CLI flags for advanced usage.

## Supported Shells
- **bash** (full auto-activation and deactivation)
- **zsh** (full auto-activation and deactivation)
- **sh** (full auto-activation and deactivation)
- **fish** (full auto-activation and deactivation)
- **powershell**, **pwsh** (full auto-activation, manual deactivation)
- **cmd**, **batch**, **bat** (prints command for manual activation and deactivation)
- **nushell**, **nu** (prints command for manual activation and deactivation)
- **csh**, **tcsh**, **cshell** (prints command for manual activation and deactivation)

For detailed shell support and limitations, see [docs/user_guide.md](https://github.com/userfrom1995/envon/blob/main/docs/user_guide.md).

## Installation
**Recommended:** Install with pipx for isolated environments:
```bash
pipx install envon
```

**Alternative:** Install with pip (may fail on some distros like Ubuntu or Windows due to PEP 668):
```bash
python3 -m pip install envon
```

After installation, run:
```bash
envon --install
```
This detects your shell and sets up the bootstrap for auto-activation.

For more detailed installation instructions, see [docs/installation.md](https://github.com/userfrom1995/envon/blob/main/docs/installation.md).

## Usage
After installation and bootstrap setup, run:
```bash
envon
```
This will activate the nearest virtual environment in your project.

Supported flags: `--emit [SHELL]`, `--print-path`, `--install [SHELL]`.

For advanced usage, examples, and all flags, see [docs/user_guide.md](https://github.com/userfrom1995/envon/blob/main/docs/user_guide.md).

## Development
For development setup, building, and project structure, see [docs/development.md](https://github.com/userfrom1995/envon/blob/main/docs/development.md).

## Contributor Note

**envon is in its early phase. Basic functionality is solid, but we welcome help!**
- TCSH/cshell and Nushell support need improvement (auto-activation, overlays).
- If you find issues, please [raise an issue](https://github.com/userfrom1995/envon/issues).
- If you'd like to contribute, fork and submit a PR—contributions are very welcome!

Let's make envon the best Python venv activator for every shell!

## Release Notes

**Version 0.1.1 (First Release)**  
This is the initial release of envon. A lot of work is still ongoing, especially in the testing, CI, and adding support for missing shells (e.g., full auto-activation for Nushell and csh/tcsh).  

If you see any issues, feel free to [open an issue](https://github.com/userfrom1995/envon/issues). If you're interested in contributing, feel free to submit a PR. If you have ideas or anything regarding the project, feel free to open a discussion or feature request in an issue.  

Check out the project on [PyPI](https://pypi.org/project/envon/).
