# Installation Guide

This document is the definitive guide to installing Odyn. Whether you are using Odyn in your application or contributing to its development, please follow these instructions carefully.

Odyn is a modern, typed, and robust Python client for the Microsoft Dynamics 365 Business Central OData V4 API.

## Prerequisites

Before you begin, ensure your development environment meets these requirements.

### Python Version

- **Python 3.12 or newer is required.**

Odyn leverages modern Python features for performance, correctness, and type safety.

To check your Python version, run:
```bash
# This command should output "Python 3.12.x" or higher
python3 --version

# On Windows, you might use the Python Launcher:
py --version
```
If you have multiple Python versions, ensure you are using `python3` or `py -3.12` consistently.

### Virtual Environment

- **A virtual environment is essential for all Python projects.**

A virtual environment isolates your project's dependencies from your system's global Python installation. This prevents version conflicts and ensures your application has a consistent, reproducible set of packages. **Do not skip this step.**

---

## Part 1: Standard Installation (For Users)

Follow these steps to use Odyn in your own project.

### Step 1: Create and Activate a Virtual Environment

Choose one of the following methods. We recommend `uv` for its speed.

#### Recommended: Using `uv`
[uv](https://github.com/astral-sh/uv) is an extremely fast, next-generation Python package manager.

```bash
# Install uv if you don't have it
pip install uv

# Create and activate a virtual environment named .venv
uv venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows
```

#### Standard: Using `venv`
`venv` is Python's built-in tool for creating virtual environments.

```bash
# Create a virtual environment named .venv
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows
```
After activation, your command prompt will typically be prefixed with `(.venv)`, indicating the virtual environment is active.

### Step 2: Install Odyn

With your virtual environment active, install Odyn.

#### Recommended: Using `uv`
```bash
# Install the latest version of Odyn
uv pip install odyn

# To install a specific version for reproducible builds:
uv pip install odyn==0.1.0
```

#### Standard: Using `pip`
```bash
# Install the latest version of Odyn
pip install odyn

# To install a specific version for reproducible builds:
pip install odyn==0.1.0
```

### Step 3: Verify the Installation

Create a Python file (e.g., `test_odyn.py`) and run it to confirm Odyn is installed correctly.

```python
# test_odyn.py
try:
    from odyn import Odyn, BearerAuthSession
    print("✅ Odyn was imported successfully.")
except ImportError as e:
    print(f"❌ Failed to import Odyn: {e}")
```

Running `python test_odyn.py` should print a success message.

---

## Part 2: Development Setup (For Contributors)

Follow these steps if you wish to contribute to Odyn, run tests, or modify the source code.

### Step 1: Clone the Repository

First, get a local copy of the source code.

```bash
git clone https://github.com/konspec/odyn.git
cd odyn
```

### Step 2: Create Environment and Install Dependencies

This process installs the library in "editable" mode along with all development tools.

#### Recommended: Using `uv`
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate # On macOS/Linux, use .venv\Scripts\activate on Windows

# Install in editable mode with development dependencies
uv pip install -e ".[dev]"
```

#### Understanding the Command (`uv pip install -e ".[dev]"`)
- `-e` or `--editable`: This flag is crucial. It installs the package in a way that your changes to the source code in `src/odyn/` are immediately effective without needing to reinstall the package.
- `".[dev]"`: This tells the installer to:
    - Look for the project in the current directory (`.`).
    - Install the extra dependency group named `[dev]`, defined in `pyproject.toml`. This group includes linters, formatters, and testing tools like `ruff` and `pytest`.
    - **Note**: The quotes are important on some systems (like macOS with Zsh) to prevent the shell from interpreting the square brackets.

### Step 3: Run Quality and Test Suites

After installation, verify that the development environment is set up correctly by running the project's quality checks and test suite.

```bash
# Run the linter to check for code style and quality
ruff check .

# Run the automated test suite
pytest
```
Both commands should complete successfully on a fresh clone.

---

## Troubleshooting Guide

### Issue: Command Not Found (`python3`, `uv`, `git`)
- **Error**: `command not found: python3` or `command not found: uv`.
- **Solution**: The command is either not installed or not available in your system's `PATH`.
    - For Python, download it from [python.org](https://www.python.org/).
    - For `uv`, install it via `pip install uv`.
    - For `git`, install it from [git-scm.com](https://git-scm.com/).

### Issue: Permission Denied
- **Error**: `OSError: [Errno 13] Permission denied`.
- **Solution**: This error occurs when you try to install packages to a system-level directory without sufficient permissions. **Always use a virtual environment to avoid this issue.** It's the correct and safest way to manage project dependencies.

### Issue: `zsh: no matches found: .[dev]`
- **Error**: Occurs on macOS or Linux systems using Zsh.
- **Solution**: Your shell is trying to interpret the square brackets `[]` as a special pattern. To prevent this, wrap the argument in quotes:
  ```bash
  # Incorrect
  pip install -e .[dev]

  # Correct
  pip install -e ".[dev]"
  ```

### Issue: Network Error
- **Error**: `Could not find a version that satisfies the requirement odyn`.
- **Solution**: This usually indicates a problem connecting to the Python Package Index (PyPI). Check your internet connection, VPN, or corporate firewall settings that might be blocking access to `pypi.org`.

## Next Steps

Once Odyn is installed, you can:

1. [Get started](getting-started.md) with your first API call
2. Learn about [authentication sessions](usage/sessions.md)
3. Explore the [complete API reference](usage/odyn.md)
