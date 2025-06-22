# Contributing to Odyn

Thank you for your interest in contributing to Odyn! This guide will help you get started with development and contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- A GitHub account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/odyn.git
   cd odyn
   ```

## Development Setup

### 1. Create a Virtual Environment

```bash
# Using venv (recommended)
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
# Or if using uv:
uv pip install -e .
uv pip install -r requirements-dev.txt
```

### 3. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (optional)
pre-commit run --all-files
```

## Code Style

Odyn follows strict code style guidelines to maintain consistency and quality.

### Python Code Style

- **Ruff**: Code formatting, linting, and import sorting
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google-style docstrings for all public functions and classes

### Running Code Quality Checks

```bash
# Format and lint with Ruff
ruff check src/ tests/
ruff format src/ tests/

# Type checking with mypy
mypy src/

# Run all checks
pre-commit run --all-files
```

### Code Style Examples

#### Type Hints
```python
# ✅ Good
def get_customers(self, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Get customers from the API."""
    pass

# ❌ Avoid
def get_customers(self, params=None):
    """Get customers from the API."""
    pass
```

#### Docstrings
```python
# ✅ Good - Google style
def validate_url(self, url: str) -> str:
    """Validates and sanitizes the URL to ensure it is a valid base for API calls.

    Args:
        url: The base URL string to validate.

    Returns:
        The sanitized URL, guaranteed to end with a "/".

    Raises:
        InvalidURLError: If the URL is empty, has an invalid scheme, or is missing a domain.
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests with coverage (recommended)
./scripts/test.sh

# On Windows
scripts\test.bat

# Run tests with verbose output
./scripts/test.sh --verbose

# Run only tests (skip linting and type checking)
./scripts/test.sh --no-lint --no-type-check

# Run all tests
pytest

# Run tests with coverage
pytest --cov=odyn --cov-report=html

# Run tests in parallel
pytest -n auto

# Run specific test file
pytest tests/test_client.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Tests should be in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Use fixtures for common setup

#### Test Example

```python
import pytest
from odyn import Odyn, BearerAuthSession, InvalidURLError

class TestOdynClient:
    """Tests for the Odyn client."""

    def test_init_with_valid_url(self):
        """Test that client initializes with valid URL."""
        session = BearerAuthSession("test-token")
        client = Odyn(
            base_url="https://api.example.com/",
            session=session
        )
        assert client.base_url == "https://api.example.com/"

    def test_init_with_invalid_url_raises_error(self):
        """Test that invalid URL raises InvalidURLError."""
        session = BearerAuthSession("test-token")
        with pytest.raises(InvalidURLError, match="URL cannot be empty"):
            Odyn(base_url="", session=session)
```

### Test Coverage

We aim for high test coverage. Run coverage reports to ensure new code is well-tested:

```bash
pytest --cov=odyn --cov-report=term-missing
```

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clear, descriptive commit messages
- Follow the code style guidelines
- Add tests for new functionality
- Update documentation if needed

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new authentication method

- Add OAuth2 authentication support
- Include comprehensive tests
- Update documentation"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- **Clear title**: Describe the change concisely
- **Description**: Explain what and why, not how
- **Related issues**: Link to any related issues
- **Checklist**: Ensure all requirements are met

### 5. Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] Tests pass and coverage is maintained
- [ ] Documentation is updated
- [ ] Type hints are added
- [ ] Pre-commit hooks pass
- [ ] No breaking changes (or clearly documented)

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment**: Python version, OS, Odyn version
2. **Steps to reproduce**: Clear, step-by-step instructions
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Error messages**: Full error traceback
6. **Code example**: Minimal code to reproduce the issue

### Feature Requests

For feature requests, please include:

1. **Use case**: Why this feature is needed
2. **Proposed solution**: How you envision it working
3. **Alternatives considered**: Other approaches you've thought about

## Code of Conduct

### Our Standards

We are committed to providing a welcoming and inspiring community for all. Please:

- Be respectful and inclusive
- Focus on what is best for the community
- Show empathy towards other community members

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers.

## Development Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

### Release Process

1. **Version bump**: Update version in `pyproject.toml`
2. **Changelog**: Update `CHANGELOG.md`
3. **Tag**: Create a git tag
4. **Release**: Create GitHub release
5. **Publish**: Publish to PyPI

## Getting Help

If you need help with development:

- Check the [documentation](index.md)
- Look at existing issues and pull requests
- Ask questions in GitHub discussions
- Contact the maintainers

## Recognition

Contributors will be recognized in:

- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to Odyn! 🚀
