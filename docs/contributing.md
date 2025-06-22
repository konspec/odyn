# Contributing to Odyn

First off, thank you for considering contributing to Odyn! Your help is greatly appreciated. This guide will provide everything you need to get started with development.

## Getting Started

Ready to contribute? Here’s how to set up `odyn` for local development.

### 1. Fork and Clone the Repository

If you haven't done so already, fork the repository on GitHub. Then, clone your fork to your local machine:

```bash
git clone https://github.com/your-username/odyn.git
cd odyn
```

### 2. Set Up Your Development Environment

We use [uv](https://github.com/astral-sh/uv) for project and environment management. It's a fast, all-in-one tool that handles virtual environments and package installation.

First, create and activate a virtual environment. `uv` will automatically use it.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

Next, install the project dependencies. The following command installs the `odyn` package in editable mode along with all development dependencies defined in `pyproject.toml`.

```bash
# Install all dependencies using uv
uv pip install -e .[dev]
```

### 4. Set Up Pre-commit Hooks

We use pre-commit hooks to ensure code style and quality are maintained automatically. To set them up, run:

```bash
pre-commit install
pre-commit install --hook-type=commit-msg
pre-commit install --hook-type=pre-push
```

This will run checks automatically every time you make a commit.

## Development Workflow

With your environment set up, you're ready to start coding!

### Running Checks and Tests

We use `Taskfile` to provide simple commands for common development tasks.

- **To run all linters, formatters, and type checkers:**
  ```bash
  task ruff ty
  ```

- **To run the full test suite:**
  ```bash
  task test
  ```

- **To run everything (all checks and tests):**
  ```bash
  task all
  ```

You can also run tools individually, for example, using `pytest` directly:

```bash
# Run tests with coverage report
pytest --cov=odyn --cov-report=html

# Run tests in parallel
pytest -n auto
```

### Writing Code

- **Branching**: Create a descriptive branch for your work (e.g., `feature/new-auth-session`, `fix/url-validation-bug`).
- **Code Style**: We use [Ruff](https://docs.astral.sh/ruff/) for formatting and linting. The pre-commit hooks will handle this automatically.
- **Type Hints**: All public APIs must include type hints.
- **Docstrings**: All public functions and classes should have Google-style docstrings.

### Submitting a Pull Request

Once your changes are ready, it's time to create a pull request.

1.  **Commit Your Changes**: We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
    ```bash
    git commit -m "feat(auth): add support for OAuth2 sessions"
    ```

2.  **Push to Your Fork**:
    ```bash
    git push origin feature/your-feature-name
    ```

3.  **Open a Pull Request**: On GitHub, open a pull request from your fork to the `main` branch of the original repository. Provide a clear title and a detailed description of your changes. Link to any relevant issues.

## Reporting Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/kon-fin/odyn/issues). Provide as much detail as possible, including:
- A clear and descriptive title.
- Steps to reproduce the issue.
- The expected and actual behavior.
- Your environment details (Python version, OS, Odyn version).

Thank you for contributing!
