# Contributing to Odyn

This is a personal library for Microsoft Dynamics 365 Business Central OData V4 API integration. While primarily for personal use, contributions and feedback are welcome.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/konspec/odyn.git
cd odyn
```

### 2. Set Up Development Environment

We use [uv](https://github.com/astral-sh/uv) for project management.

```bash
# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
uv pip install -e .[dev]
```

### 3. Set Up Pre-commit Hooks

```bash
pre-commit install
pre-commit install --hook-type=commit-msg
pre-commit install --hook-type=pre-push
```

## Development Workflow

### Running Checks and Tests

```bash
# Run all checks and tests
task all

# Run specific tools
task ruff ty    # Linting and type checking
task test       # Run tests
```

### Code Standards

- **Code Style**: We use [Ruff](https://docs.astral.sh/ruff/) for formatting and linting
- **Type Hints**: All public APIs must include type hints
- **Docstrings**: Google-style docstrings for public functions and classes
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/) specification

## Reporting Issues

If you find bugs or have suggestions, please [open an issue](https://github.com/konspec/odyn/issues) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)

## Personal Use Notes

This library is primarily developed for personal use cases with Microsoft Dynamics 365 Business Central. The focus is on:
- Type safety and robust error handling
- Simple, intuitive API design
- Production-ready reliability
- Comprehensive logging and debugging support

Thank you for your interest in Odyn!
