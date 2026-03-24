# MSYS2 / Git Bash Support

envon fully supports POSIX shells (bash, fish, nushell) running inside
[MSYS2](https://www.msys2.org/) and [Git Bash](https://gitforwindows.org/)
on Windows.

## How It Works

MSYS2 and Git Bash set the `MSYSTEM` environment variable (e.g. `MINGW64`,
`UCRT64`, `MSYS`, `CLANG64`). When envon detects this variable it treats the
session as a POSIX-like environment, enabling:

- **Shell auto-detection** — bash, fish, and nushell are detected normally
  instead of defaulting to PowerShell/cmd.
- **Automated bootstrap install** — `envon --install` writes directly to
  `~/.bashrc` (or equivalent) rather than printing manual instructions.
- **Nushell activation** — nushell `overlay use` commands work as on Linux.

## Quick Start

```bash
# Inside MSYS2 or Git Bash
pip install envon          # or pipx install envon
envon --install bash       # writes bootstrap to ~/.bashrc
source ~/.bashrc           # or restart the terminal
envon                      # activates nearest venv
```

## Supported Environments

| MSYSTEM value | Description              |
|---------------|--------------------------|
| `MSYS`        | MSYS2 native (Cygwin-like) |
| `MINGW64`     | MinGW 64-bit (GCC)      |
| `UCRT64`      | UCRT 64-bit (GCC)       |
| `CLANG64`     | Clang 64-bit             |
| `MINGW32`     | MinGW 32-bit (GCC)      |
| `CLANGARM64`  | Clang ARM64              |

Git Bash typically sets `MSYSTEM=MINGW64`.

## Troubleshooting

**envon still defaults to PowerShell?**
Ensure you are running Python *from inside* the MSYS2/Git Bash terminal.
Verify with:

```bash
python -c "import os; print(os.environ.get('MSYSTEM', 'NOT SET'))"
```

If it prints `NOT SET`, the MSYS2 environment is not active.

**Using Windows-native Python?**
That's fine — envon reads `MSYSTEM` regardless of which Python binary you use.
As long as the env var is set, POSIX detection kicks in.
