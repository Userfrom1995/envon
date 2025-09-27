# User Guide

## CLI Flags

- `target` (positional): Path, project root, or name (searched in WORKON_HOME)
- `--emit [SHELL]`: Emit activation command for the specified shell (bash, zsh, sh, fish, cshell, nushell, powershell, pwsh, cmd). If omitted, auto-detects shell.
- `--print-path`: Print only the resolved virtual environment path and exit.
- `--install [SHELL]`: Install envon bootstrap function directly to shell configuration file. If omitted, auto-detects shell.
- `-h`, `--help`: Show help message and exit.

## Basic Functionality

- If no target is provided, envon searches for a virtual environment in the current directory (preferred names: `.venv`, `venv`, `env`, `.env`).
- If multiple venvs are found, prompts for selection.
- If none found, walks up parent directories for preferred names.
- If still none, checks if `VIRTUAL_ENV` is set and valid.
- If all fail, raises an error.

## Shell Support

| Shell         | Auto-activation | Notes                                      |
|---------------|----------------|--------------------------------------------|
| bash          | Yes            | Full support                               |
| zsh           | Yes            | Uses bash bootstrap                        |
| sh            | Yes            | Full support                               |
| fish          | Yes            | Full support                               |
| powershell    | Yes            | Manual profile edit required on Windows     |
| pwsh          | Yes            | Same as powershell                         |
| nushell, nu   | No             | Prints overlay use command; manual run      |
| cmd, batch, bat | Yes          | Prints activation command                   |
| csh, tcsh, cshell | No         | Only prints command; no auto-activation     |


## CLI Usage Patterns

### Activate nearest venv (auto-detect shell)
```bash
envon
```

### Activate a specific venv by name or path
```bash
envon myenv
envon /path/to/venv
```

### Emit activation command for a specific shell
```bash
envon --emit fish
envon myenv --emit bash
envon /path/to/venv --emit powershell
```

### Print only the resolved venv path
```bash
envon --print-path
envon myenv --print-path
envon /path/to/venv --print-path
```

### Combine flags (order is flexible)
```bash
envon --emit zsh --print-path
envon myenv --emit fish --print-path
envon --print-path --emit powershell
```

## Argument Support for --emit and --print-path

Both `--emit` and `--print-path` support an optional positional argument for the virtual environment name or path. If provided, they resolve the venv from that argument; if omitted, they use the default search logic.

### With a Virtual Environment Argument
- **Behavior:** Resolves the venv from the provided name or path.
- **Search Logic:**
  - If the argument is an existing directory and is a valid venv, use it directly.
  - If the argument is an existing directory but not a venv, scan its subdirectories for venvs (preferred names first, then any valid venv subdirs).
  - If the argument is not an existing path (i.e., a name), check the `WORKON_HOME` environment variable for a venv with that name.
  - If multiple venvs are found in a directory, prompt for selection (if interactive).
  - No upward walking to parent directories.
- **Examples:**
  - `envon myenv --emit bash`: If "myenv" exists as a venv in WORKON_HOME or as a directory with venvs, use it.
  - `envon /path/to/venv --print-path`: If `/path/to/venv` is a valid venv, print its path.

### Without a Virtual Environment Argument (Default)
- **Behavior:** Uses full auto-detection: current directory, then up parent directories, then VIRTUAL_ENV.
- **Search Logic:**
  - Scan the current directory for venvs (preferred names first, then any subdirectories).
  - If multiple, prompt for selection.
  - If none, walk up parent directories checking preferred names.
  - If still none, check if `VIRTUAL_ENV` is set and points to a valid venv.
  - If all fail, error out.
- **Examples:**
  - `envon --emit fish`: Auto-detects venv and emits Fish activation.
  - `envon --print-path`: Prints the path of the auto-detected venv.

### Install bootstrap for a shell
```bash
envon --install
envon --install zsh
envon --install powershell
```
