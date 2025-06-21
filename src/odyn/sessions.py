from typing import Any, ClassVar

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from odyn._exceptions import (
    InvalidBackoffFactorError,
    InvalidRetryError,
    InvalidStatusForcelistError,
)


class OdynSession(requests.Session):
    """A requests.Session enhanced with automatic retries on failures.

    This session is configured to retry requests that fail due to specific
    HTTP status codes or connection errors, with an exponential backoff strategy.

    Attributes:
        DEFAULT_STATUS_FORCELIST: Default list of HTTP status codes that trigger a retry.
    """

    DEFAULT_STATUS_FORCELIST: ClassVar[list[int]] = [500, 502, 503, 504, 429]

    _retries: int
    _backoff_factor: float
    _status_forcelist: list[int]

    def __init__(
        self,
        retries: int = 5,
        backoff_factor: float = 2.0,
        status_forcelist: list[int] | None = None,
    ) -> None:
        """Initializes the session with a retry strategy.

        Args:
            retries: The total number of times to retry a request.
            backoff_factor: A factor to calculate the delay between retries.
                (e.g., {backoff factor} * (2 ** ({number of total retries} - 1)))
            status_forcelist: A list of HTTP status codes to force a retry on.
                Defaults to [500, 502, 503, 504, 429].
        """
        super().__init__()

        self._retries = self._validate_retries(retries)
        self._backoff_factor = self._validate_backoff_factor(backoff_factor)

        if status_forcelist is None:
            self._status_forcelist = self.DEFAULT_STATUS_FORCELIST
        else:
            self._status_forcelist = self._validate_status_forcelist(status_forcelist)

        self._mount_retry_adapter()

    def _validate_retries(self, retries: int) -> int:
        """Validates the retries parameter.

        Args:
            retries: The number of retries to validate.

        Returns:
            The validated number of retries.

        Raises:
            InvalidRetryError: If retries is not a positive integer.
        """
        if not isinstance(retries, int) or retries <= 0:
            raise InvalidRetryError("Retries must be a positive integer.")
        return retries

    def _validate_backoff_factor(self, backoff_factor: float | int) -> float:
        """Validates the backoff_factor parameter.

        Args:
            backoff_factor: The backoff factor to validate.

        Returns:
            The validated backoff factor as a float.

        Raises:
            InvalidBackoffFactorError: If the backoff factor is not a positive number.
        """
        if not isinstance(backoff_factor, int | float) or backoff_factor <= 0:
            raise InvalidBackoffFactorError("Backoff factor must be a positive number.")
        return float(backoff_factor)

    def _validate_status_forcelist(self, status_list: list[int]) -> list[int]:
        """Validates the status_forcelist parameter.

        Args:
            status_list: The list of status codes to validate.

        Returns:
            The validated list of status codes.

        Raises:
            InvalidStatusForcelistError: If the status forcelist is not a list of integers.
        """
        if not isinstance(status_list, list) or not all(isinstance(status, int) for status in status_list):
            raise InvalidStatusForcelistError("Status forcelist must be a list of integers.")
        return status_list

    def _mount_retry_adapter(self) -> None:
        """Creates and mounts the HTTPAdapter with the retry strategy.

        This method configures a Retry object with the session's retry parameters
        and mounts an HTTPAdapter for both http and https protocols.
        """
        retry_strategy: Retry = Retry(
            total=self._retries,
            backoff_factor=self._backoff_factor,
            status_forcelist=self._status_forcelist,
        )
        adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("https://", adapter)
        self.mount("http://", adapter)


class BasicAuthSession(OdynSession):
    """An OdynSession that uses Basic Authentication."""

    def __init__(self, username: str, password: str, **kwargs: Any) -> None:
        """Initializes the session with Basic Authentication.

        Args:
            username: The username for Basic Authentication.
            password: The password for Basic Authentication.
            **kwargs: Keyword arguments passed to the parent OdynSession.
                (e.g., retries, backoff_factor, status_forcelist).
        """
        super().__init__(**kwargs)
        self.auth = (username, password)


class BearerAuthSession(OdynSession):
    """An OdynSession that uses Bearer Token Authentication."""

    def __init__(self, token: str, **kwargs: Any) -> None:
        """Initializes the session with Bearer Token Authentication.

        Args:
            token: The bearer token for authentication.
            **kwargs: Keyword arguments passed to the parent OdynSession
                (e.g., retries, backoff_factor, status_forcelist).
        """
        # Pass all retry-related arguments to the parent class
        super().__init__(**kwargs)
        self.headers.update({"Authorization": f"Bearer {token}"})
