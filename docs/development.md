# Development Guide

## Project Structure

- `src/envon/`: Main package code.
  - `envon.py`: Core logic for venv detection, activation, and CLI.
  - `__main__.py`: Entry point for `python -m envon`.
  - `bootstrap_*.sh`, `bootstrap_*.fish`, etc.: Shell-specific bootstrap scripts.
- `docs/`: Documentation.
  - `installation.md`: Installation details.
  - `user_guide.md`: Usage and flags.
  - `development.md`: This file.
- `tests/`: Unit tests (currently removed, to be re-added later).
- `pyproject.toml`: Build configuration.
- `README.md`: Main project description.

## Setup Development Environment

1. Clone the repo:
   ```bash
   git clone https://github.com/userfrom1995/envon.git
   cd envon
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   ```

3. Install in editable mode:
   ```bash
   pip install -e .
   ```

4. (Optional) Install dev dependencies:
   ```bash
   pip install build twine  # For building and publishing
   ```

## Running the CLI

From source:
```bash
python -m envon --help
envon --help
```

## Building and Publishing

1. Build the package:
   ```bash
   python -m build
   ```
   This creates `dist/` with `.whl` and `.tar.gz` files.

2. Publish to PyPI:
   ```bash
   pip install twine
   twine upload dist/*
   ```
   Enter your PyPI credentials when prompted.

For TestPyPI:
```bash
twine upload --repository testpypi dist/*
```

## Testing

Tests are currently removed. To re-add, create `tests/test_envon.py` with unit tests for key functions.

Run tests (once added):
```bash
python -m unittest discover tests/
```

## Contributing

See the Contributor Note in README.md. Fork, make changes, and submit a PR!