from typing import Any

import pytest
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from odyn._exceptions import (
    InvalidBackoffFactorError,
    InvalidRetryError,
    InvalidStatusForcelistError,
)
from odyn.sessions import BasicAuthSession, BearerAuthSession, OdynSession


class TestOdynSession:
    """Tests for the base OdynSession class."""

    def test_init_with_defaults(self) -> None:
        """Verifies the session initializes with correct default retry parameters."""
        session = OdynSession()

        # Check internal state
        assert session._retries == 5
        assert session._backoff_factor == 2.0
        assert session._status_forcelist == OdynSession.DEFAULT_STATUS_FORCELIST

        # Check the mounted adapter's retry strategy
        adapter = session.adapters["https://"]
        assert isinstance(adapter, HTTPAdapter)
        retry_strategy = adapter.max_retries
        assert isinstance(retry_strategy, Retry)
        assert retry_strategy.total == 5
        assert retry_strategy.backoff_factor == 2.0
        assert retry_strategy.status_forcelist == OdynSession.DEFAULT_STATUS_FORCELIST

    def test_init_with_custom_valid_parameters(self) -> None:
        """Verifies the session initializes correctly with custom valid parameters."""
        session = OdynSession(retries=3, backoff_factor=1, status_forcelist=[429])

        # Check internal state
        assert session._retries == 3
        assert session._backoff_factor == 1.0  # Should be cast to float
        assert session._status_forcelist == [429]

        # Check the mounted adapter's retry strategy
        retry_strategy = session.adapters["https://"].max_retries
        assert retry_strategy.total == 3
        assert retry_strategy.backoff_factor == 1.0
        assert retry_strategy.status_forcelist == [429]

    @pytest.mark.parametrize("invalid_retries", [0, -1, 3.5, "five", None, [5]])
    def test_init_with_invalid_retries_raises_error(self, invalid_retries: Any) -> None:
        """Verifies that providing invalid `retries` raises an InvalidRetryError.

        Args:
            invalid_retries: An invalid value for the retries parameter.
        """
        with pytest.raises(InvalidRetryError, match="Retries must be a positive integer."):
            OdynSession(retries=invalid_retries)

    @pytest.mark.parametrize("invalid_backoff", [0, -1.0, "two", None, [2.0]])
    def test_init_with_invalid_backoff_factor_raises_error(self, invalid_backoff: Any) -> None:
        """Verifies that providing an invalid `backoff_factor` raises an error.

        Args:
            invalid_backoff: An invalid value for the backoff_factor parameter.
        """
        with pytest.raises(InvalidBackoffFactorError, match="Backoff factor must be a positive number."):
            OdynSession(backoff_factor=invalid_backoff)

    @pytest.mark.parametrize("invalid_forcelist", [[500, "429"], "429,500", 500, {"status": 500}])
    def test_init_with_invalid_status_forcelist_raises_error(self, invalid_forcelist: Any) -> None:
        """Verifies that providing an invalid `status_forcelist` raises an error.

        Args:
            invalid_forcelist: An invalid value for the status_forcelist parameter.
        """
        with pytest.raises(InvalidStatusForcelistError, match="Status forcelist must be a list of integers."):
            OdynSession(status_forcelist=invalid_forcelist)


class TestBasicAuthSession:
    """Tests for the BasicAuthSession subclass."""

    def test_init_sets_basic_auth(self) -> None:
        """Verifies that the session correctly sets the `auth` tuple."""
        session = BasicAuthSession("user", "pass")
        assert session.auth == ("user", "pass")

    def test_init_forwards_retry_kwargs_to_parent(self) -> None:
        """Verifies that retry-related kwargs are passed to the parent OdynSession."""
        session = BasicAuthSession("user", "pass", retries=10, backoff_factor=0.5, status_forcelist=[503])

        # Verify parent class attributes were set
        assert session._retries == 10
        assert session._backoff_factor == 0.5
        assert session._status_forcelist == [503]

        # Verify the adapter's retry strategy reflects the kwargs
        retry_strategy = session.adapters["https://"].max_retries
        assert retry_strategy.total == 10
        assert retry_strategy.backoff_factor == 0.5
        assert retry_strategy.status_forcelist == [503]


class TestBearerAuthSession:
    """Tests for the BearerAuthSession subclass."""

    def test_init_sets_bearer_header(self) -> None:
        """Verifies that the session correctly sets the Authorization header."""
        session = BearerAuthSession("my-secret-token")
        assert session.headers["Authorization"] == "Bearer my-secret-token"

    def test_init_forwards_retry_kwargs_to_parent(self) -> None:
        """Verifies that retry-related kwargs are passed to the parent OdynSession."""
        session = BearerAuthSession("my-secret-token", retries=2, backoff_factor=3, status_forcelist=[])

        # Verify parent class attributes were set
        assert session._retries == 2
        assert session._backoff_factor == 3.0
        assert session._status_forcelist == []

        # Verify the adapter's retry strategy reflects the kwargs
        retry_strategy = session.adapters["https://"].max_retries
        assert retry_strategy.total == 2
        assert retry_strategy.backoff_factor == 3.0
        assert retry_strategy.status_forcelist == set()
