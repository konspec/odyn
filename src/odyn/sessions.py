import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from odyn._exceptions import (
    InvalidBackoffFactorError,
    InvalidRetryError,
    InvalidStatusForcelistError,
)


class OdynSession(requests.Session):
    """Session for Odyn API requests."""

    def __init__(
        self,
        retry: int = 5,
        backoff_factor: float = 2.0,
        status_forcelist: list[int] | None = None,
    ) -> None:
        """Initialize the session."""
        super().__init__()
        self._retry = self._validate_retry(retry)
        self._backoff_factor = self._validate_backoff_factor(backoff_factor)
        self._status_forcelist = self._validate_status_forcelist(status_forcelist)
        self._mount_retry_adapters()

    def _validate_retry(self, retry: int) -> int:
        """Validate the retry."""
        if not isinstance(retry, int):
            error_msg: str = "Retry must be an integer."
            raise InvalidRetryError(error_msg)
        if retry <= 0:
            error_msg: str = "Retry must be greater than 0."
            raise InvalidRetryError(error_msg)
        return retry

    def _validate_backoff_factor(self, backoff_factor: float) -> float:
        """Validate the backoff factor."""
        if not isinstance(backoff_factor, float | int):
            error_msg: str = "Backoff factor must be a float."
            raise InvalidBackoffFactorError(error_msg)
        if backoff_factor <= 0:
            error_msg: str = "Backoff factor must be greater than 0."
            raise InvalidBackoffFactorError(error_msg)
        return float(backoff_factor)

    def _validate_status_forcelist(
        self, status_forcelist: list[int] | None
    ) -> list[int] | None:
        """Validate the status forcelist."""
        if status_forcelist is None:
            return [500, 502, 503, 504, 429]
        if not isinstance(status_forcelist, list):
            error_msg: str = "Status forcelist must be a list of integers."
            raise InvalidStatusForcelistError(error_msg)
        if not all(isinstance(status, int) for status in status_forcelist):
            error_msg: str = "Status forcelist must be a list of integers."
            raise InvalidStatusForcelistError(error_msg)
        return status_forcelist

    def _mount_retry_adapters(self) -> None:
        """Mount the retry adapters."""
        retry_strategy: Retry = Retry(
            total=self._retry,
            backoff_factor=self._backoff_factor,
            status_forcelist=self._status_forcelist,
        )
        adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("https://", adapter)
        self.mount("http://", adapter)


class BasicAuthSession(OdynSession):
    """Session for Odyn API requests with basic authentication."""

    def __init__(
        self,
        username: str,
        password: str,
        retry: int = 5,
        backoff_factor: float = 2,
        status_forcelist: list[int] | None = None,
    ) -> None:
        """Initialize the session with basic authentication.

        Args:
            username: The username to use for basic authentication.
            password: The password to use for basic authentication.
            retry: The number of times to retry the request.
            backoff_factor: The factor to use for the backoff.
            status_forcelist: The list of status codes to force retry.

        Returns:
            None
        """
        super().__init__(retry, backoff_factor, status_forcelist)
        self.auth = (username, password)


class BearerAuthSession(OdynSession):
    """Session for Odyn API requests with bearer authentication."""

    def __init__(
        self,
        token: str,
        retry: int = 5,
        backoff_factor: float = 2,
        status_forcelist: list[int] | None = None,
    ) -> None:
        """Initialize the session with bearer authentication.

        Args:
            token: The token to use for bearer authentication.
            retry: The number of times to retry the request.
            backoff_factor: The factor to use for the backoff.
            status_forcelist: The list of status codes to force retry.

        Returns:
            None
        """
        super().__init__(retry, backoff_factor, status_forcelist)
        self.headers.update({"Authorization": f"Bearer {token}"})
