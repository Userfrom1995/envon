# User Guide

## CLI Flags

- `target` (optional): Path to venv directory, project root containing venvs, or venv name (WORKON_HOME fallback only)
- `--emit [SHELL]`: Emit activation command for the specified shell. If omitted, auto-detects shell.
- `--print-path`: Print only the resolved virtual environment path.
- `--install [SHELL]`: Install envon bootstrap function. If omitted, auto-detects shell.
- `-d`, `--deactivate [SHELL]`: Emit deactivation command for the specified shell. If omitted, auto-detects shell.
- `-V`, `--version`: Print the current version of envon.
- `-h`, `--help`: Show help.

**Note:** When no target is provided, envon searches the current directory first, then walks up parent directories.

## Basic Functionality

envon searches for virtual environments in this order:
1. **Current directory**: Looks for preferred names (`.venv`, `venv`, `env`, `.env`) and any other venv subdirectories
2. **Parent directories**: Walks upward checking each parent for preferred names only
3. **Active environment**: Uses `VIRTUAL_ENV` if set and valid
4. **Error**: If nothing found

When multiple venvs are found at the same level, prompts for interactive selection.

## Shell Support

| Shell         | Auto-activation| Deactivation | Notes                                              |
|---------------|----------------|--------------|----------------------------------------------------|
| bash          | Yes            | Yes          | Full support                                       |
| zsh           | Yes            | Yes          | Uses bash bootstrap                                |
| sh            | Yes            | Yes          | Full support                                       |
| fish          | Yes            | Yes          | Full support                                       |
| powershell    | Yes            | Manual       | Manual profile edit required on Windows            |
| pwsh          | Yes            | Manual       | Same as powershell                                 |
| nushell, nu   | Manual         | Manual       | Prints commands for manual activation/deactivation |
| cmd, batch, bat | Manual       | Manual       | Prints commands for manual activation/deactivation |
| csh, tcsh, cshell | Manual     | Manual       | Prints commands for manual activation/deactivation |


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

## Target Resolution Logic

The optional `target` argument (e.g., `envon myenv` or `envon /path/to/project`) works with all commands.

### With a Target Argument
- **Behavior:** Resolves the venv from the provided name or path.
- **Search Logic:**
  1. **Direct Path:** If the argument is an existing directory and is a valid venv, use it directly.
  2. **Container Directory:** If the argument is an existing directory but *not* a venv, scan its subdirectories for venvs.
     - Checks for preferred names (`.venv`, `venv`, `env`, `.env`) first, then any other venv-like subdirectories.
     - **Interactive Selection:** If multiple venvs are found in the directory, prompts the user to choose one.
  3. **WORKON_HOME Fallback:** If local resolution fails (either the path doesn't exist, or it exists but contains no venvs), check the `WORKON_HOME` environment variable for a venv with that name.
  - **No Upward Search:** Does not walk up parent directories when a target is specified.
- **Examples:**
  - `envon myenv`: Checks `./myenv` (as venv or container), then `$WORKON_HOME/myenv`.
  - `envon /path/to/project`: Checks `/path/to/project` for venvs (e.g., `/path/to/project/.venv`).

### Without a Target Argument (Default)
- **Behavior:** Uses full auto-detection: current directory, then up parent directories, then VIRTUAL_ENV.
- **Search Logic:**
  - Scan the current directory for venvs (preferred names first, then any subdirectories).
  - If multiple, prompt for selection.
  - If none, walk up parent directories checking preferred names.
  - If still none, check if `VIRTUAL_ENV` is set and points to a valid venv.
  - **WORKON_HOME Fallback:** If all else fails and `WORKON_HOME` is set, list all available environments in `WORKON_HOME` and prompt for selection.
  - If that fails too, error out.
- **Examples:**
  - `envon --emit fish`: Auto-detects venv and emits Fish activation.
  - `envon --print-path`: Prints the path of the auto-detected venv.

### Install bootstrap for a shell
```bash
envon --install
envon --install zsh
envon --install powershell
```

### Deactivate virtual environment
```bash
envon -d
envon --deactivate
envon --deactivate bash
```

**Note:** Deactivation support varies by shell:
- **bash, zsh, sh, fish**: Full auto-deactivation
- **powershell, pwsh**: Prints deactivation command for manual execution
- **nushell, cmd, csh/tcsh**: Prints deactivation command for manual execution
