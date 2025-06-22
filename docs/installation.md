# Installation

This guide covers how to install Odyn in your project. We strongly recommend using a virtual environment to manage dependencies.

## Prerequisites

- **Python 3.12 or higher**
- A virtual environment (see below for setup instructions)

## Using a Virtual Environment

Using a virtual environment is crucial for isolating project dependencies and avoiding conflicts.

### Recommended: `uv`

[uv](https://github.com/astral-sh/uv) is a modern, extremely fast Python package installer and resolver.

```bash
# Create and activate a virtual environment in one step
uv venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\\Scripts\\activate
```

### Standard: `venv`

You can also use Python's built-in `venv` module.

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\\Scripts\\activate
```

## Production Installation

Once your virtual environment is activated, you can install Odyn using your preferred tool.

### Recommended: `uv`

```bash
# Install the latest version of Odyn
uv pip install odyn
```

To upgrade to the latest version:

```bash
uv pip install --upgrade odyn
```

### Standard: `pip`

```bash
# Install the latest version of Odyn
pip install odyn
```

To upgrade to the latest version:
```bash
pip install --upgrade odyn
```

### Poetry

If you use Poetry for dependency management:

```bash
poetry add odyn
```

## Development Installation

If you plan to contribute to Odyn, you need to install it in editable mode with its development dependencies.

### Recommended: `uv`

This is the fastest and recommended way to set up a development environment.

```bash
# 1. Clone the repository
git clone https://github.com/konspec/odyn.git
cd odyn

# 2. Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate # Or .venv\Scripts\activate on Windows
uv pip install -e .[dev]

# 3. Verify the installation
ruff check .
pytest
```

### `pip` and `venv`

```bash
# 1. Clone the repository
git clone https://github.com/konspec/odyn.git
cd odyn

# 2. Create a virtual environment and activate it
python -m venv .venv
source .venv/bin/activate # Or .venv\Scripts\activate on Windows

# 3. Install in editable mode with development dependencies
pip install -e .[dev]
```

## Verification

After installation, you can verify that Odyn is installed correctly by running this snippet. No output means it was successful.

```python
try:
    from odyn import Odyn, BearerAuthSession
    print("Odyn was imported successfully.")
except ImportError as e:
    print(f"Failed to import Odyn: {e}")

```

## Troubleshooting

### Common Installation Issues

**Python Version Error**
- **Error**: `ERROR: Package 'odyn' requires a different Python...`
- **Solution**: Ensure you are using Python 3.12 or higher. Check with `python --version`.

**Permission Errors**
- **Error**: `ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied...`
- **Solution**: This typically happens when not using a virtual environment. Activate a virtual environment before installing. If you must install globally, use the `--user` flag: `pip install --user odyn`.

**Network Issues**
- **Error**: `ERROR: Could not find a version that satisfies the requirement odyn...`
- **Solution**: Check your internet connection and firewall settings. Ensure you can reach PyPI by running `pip install odyn -i https://pypi.org/simple/`.

## Next Steps

Once Odyn is installed, you can:

1. [Get started](getting-started.md) with your first API call
2. Learn about [authentication sessions](usage/sessions.md)
3. Explore the [complete API reference](usage/odyn.md)
