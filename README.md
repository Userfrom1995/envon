# envon

Emit the exact shell command to activate the nearest or specified Python virtual environment. Optionally install a small shell wrapper so you can just type `envon` to activate a venv in-place.

Works across shells: bash, zsh, sh, fish, Nushell, PowerShell, and csh/tcsh. The `virtualenv` package is installed automatically and `envon` uses its activation plug-ins; when not applicable, it falls back to common activation paths.

## Installation

From PyPI:

```bash
python -m pip install envon
```

This installs a console script named `envon` into your environment.

## Quick usage

- In a project with a `.venv` (or `venv`, `env`, `.env`) folder:
	- Run `envon` and it will print the activation command for your current shell.
	- Wrap it with the provided bootstrap so it executes the activation command for you.

Examples:

```bash
# Print the shell command to activate the nearest venv
envon

# Activate now (bash/zsh):
eval "$(envon)"

# Or install the bootstrap once so `envon` activates directly
envon --install
```

You can target a specific environment:

```bash
envon /path/to/project/.venv
envon /path/to/project               # will search for .venv, venv, env, .env under the dir
envon myenv                          # will resolve from $WORKON_HOME/myenv if set
```

## Shell bootstrap

`envon --install` detects your shell and adds a small wrapper to your shell profile. After that, typing `envon` will activate the nearest venv (or a specified one) without having to `eval`.

Supported shells: bash, zsh, sh, fish, Nushell, PowerShell (Windows and POSIX), csh/tcsh.

To force a particular shell during installation:

```bash
envon --install bash
envon --install fish
envon --install nushell
envon --install powershell
envon --install csh
```

## How it works

- Searches for a venv in the current directory first; if multiple exist, it prompts to choose (when in a TTY).
- If none, walks up parent directories to find a common venv name like `.venv`.
- If still none, and an environment is already active via `$VIRTUAL_ENV`, it respects that.
- Otherwise, errors with guidance to create a venv or pass a path.
- Determines the current shell and emits the corresponding activation command (or uses `virtualenv` activators when available).

## Development

This project uses a modern PEP 517 build via `pyproject.toml`.

Setup a dev environment:

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
python -m pip install -U pip build
pip install -e .
```

Run the CLI from source:

```bash
python -m envon --help
envon --help
```

Build artifacts:

```bash
python -m build
```

Publish to PyPI (requires `twine` and credentials):

```bash
python -m pip install -U twine
twine upload dist/*
```

## License

MIT
