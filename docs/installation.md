# Installation

This guide covers how to install Odyn using different package managers and dependency management tools.

## Prerequisites

- **Python 3.12 or higher** (required)
- A virtual environment (recommended)

## Installation Methods

### Using pip

The most common way to install Odyn is using pip:

```bash
pip install odyn
```

To upgrade to the latest version:

```bash
pip install --upgrade odyn
```

### Using uv

[uv](https://github.com/astral-sh/uv) is a fast dependency resolver built in Rust, compatible with pip workflows:

```bash
uv add odyn
```

To upgrade:

```bash
uv pip install --upgrade odyn
```

### Using Poetry

If you're using Poetry for dependency management:

```bash
poetry add odyn
```

To add as a development dependency:

```bash
poetry add --group dev odyn
```

## Virtual Environment Best Practices

It's recommended to use a virtual environment to isolate your project dependencies:

### Using venv (built-in)

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Odyn
pip install odyn
```

### Using uv

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Odyn
uv pip install odyn
```

### Using Poetry

```bash
# Create a new project (if starting fresh)
poetry new my-odyn-project
cd my-odyn-project

# Or add to existing project
poetry add odyn
```

## Core Dependencies

Odyn automatically installs these core dependencies:

- **requests** (≥2.32.4) - HTTP client library for making API requests
- **loguru** (≥0.7.3) - Advanced logging framework for comprehensive logging

## Verification

After installation, you can verify that Odyn is installed correctly:

```python
# Test import
from odyn import Odyn, BearerAuthSession

# Check version (if you need to verify)
import odyn
print(odyn.__version__)  # Note: version info may not be available in all releases
```

## Development Installation

If you want to install Odyn in development mode (for contributing):

```bash
# Clone the repository
git clone https://github.com/your-username/odyn.git
cd odyn

# Install in development mode
pip install -e .

# Or with uv
uv pip install -e .

# Or with Poetry
poetry install
```

## Troubleshooting

### Common Installation Issues

**Python Version Error**
```
ERROR: Package 'odyn' requires a different Python: 3.12.0 not in '>=3.12'
```
**Solution**: Upgrade to Python 3.12 or higher.

**Permission Errors**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```
**Solution**: Use a virtual environment or add `--user` flag:
```bash
pip install --user odyn
```

**Network Issues**
```
ERROR: Could not find a version that satisfies the requirement odyn
```
**Solution**: Check your internet connection and try using a different package index if needed:
```bash
pip install odyn -i https://pypi.org/simple/
```

## Next Steps

Once Odyn is installed, you can:

1. [Get started](getting-started.md) with your first API call
2. Learn about [authentication sessions](usage/sessions.md)
3. Explore the [complete API reference](usage/odyn.md)
