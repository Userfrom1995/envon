# Installation Guide

## Quick Install

```bash
python3 -m pip install envon
```

## Development Install

```bash
python3 -m pip install -e .
```

## Shell Bootstrap

After installing, run:

```bash
envon --install
```

This will auto-detect your shell and update your shell config file (e.g., `.bashrc`, `.zshrc`, `config.fish`, PowerShell profile, etc.).

You can specify a shell explicitly:

```bash
envon --install bash
envon --install zsh
envon --install fish
envon --install powershell
envon --install nushell
envon --install csh
```

### PowerShell Note
On Windows, you must manually add the bootstrap block to your profile file as instructed by the installer output.

**Execution Policy Warning:** After adding the content to your profile file, you may still see execution policy-related warnings in your terminal. To make auto-activation work, set your execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This allows local scripts to run while maintaining security for remote scripts.

### Nushell and csh/tcsh/cshell
Auto-activation is not fully supported; you may need to run the printed command manually.
