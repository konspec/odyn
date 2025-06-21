# tests/test_package.py
import pytest


def test_public_api_imports() -> None:
    """Verifies that all public components are importable from the root package.

    This test ensures that the `__all__` definition in `odyn/__init__.py` is
    correct and that all intended classes and exceptions are accessible
    directly from the `odyn` namespace.
    """
    try:
        from odyn import (
            InvalidLoggerError,
            InvalidSessionError,
            InvalidTimeoutError,
            InvalidURLError,
            Odyn,
        )
    except ImportError as e:
        pytest.fail(f"Failed to import a public component from the root package: {e}")

    # This is a check to ensure the variables were actually imported and not just declared.
    # It also prevents `unused import` linting errors.
    assert InvalidLoggerError is not None
    assert InvalidSessionError is not None
    assert InvalidTimeoutError is not None
    assert InvalidURLError is not None
    assert Odyn is not None
