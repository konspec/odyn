from typing import Any
from urllib.parse import urlencode, urlparse

import requests
import requests.exceptions as requests_exceptions
from loguru import logger as default_logger
from loguru._logger import Logger

from odyn._exceptions import (
    InvalidLoggerError,
    InvalidSessionError,
    InvalidTimeoutError,
    InvalidURLError,
)

TimeoutType = tuple[int, int] | tuple[float, float]


class Odyn:
    """Python adapter for MS Dynamics 365 Business Central OData V4 API."""

    DEFAULT_TIMEOUT: TimeoutType = (60, 60)

    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        logger: Logger | None = None,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Odyn client.

        Args:
            base_url(str): The base URL of the OData service.
            session(requests.Session): The requests session to use for the client.
                Any authentication should be handled by the session.
            logger(Logger | None): The logger to use for the client.
            timeout: The timeout to use for the client as
                (connect_timeout, read_timeout). Defaults to (60, 60).

        Raises:
            InvalidURLError: If the URL is invalid.
            InvalidSessionError: If the session is invalid.
            InvalidLoggerError: If the logger is invalid.
            InvalidTimeoutError: If the timeout is invalid.
        """
        self.base_url: str = self._validate_url(base_url)
        self.session: requests.Session = self._validate_session(session)
        self.logger: Logger = self._validate_logger(logger)
        self.timeout: TimeoutType = self._validate_timeout(timeout)

    def _validate_type(self, value: Any, expected_type: type, param_name: str, exception_class: type) -> None:
        """Generic type validation helper.

        Args:
            value: The value to validate.
            expected_type: The expected type.
            param_name: The parameter name for error messages.
            exception_class: The exception class to raise.

        Raises:
            exception_class: If the type validation fails.
        """
        if not isinstance(value, expected_type):
            error_msg: str = f"{param_name} must be a {expected_type.__name__}, got {type(value).__name__}"
            raise exception_class(error_msg)

    def _validate_url(self, url: str) -> str:
        """Validate the URL.

        Args:
            url(str): The URL to validate.

        Raises:
            InvalidURLError: If the URL is invalid.

        Returns:
            The validated and sanitized URL.
        """
        self._validate_type(url, str, "url", InvalidURLError)

        sanitized_url: str = url.strip().rstrip("/")

        if not sanitized_url:
            raise InvalidURLError("URL cannot be empty")

        parsed = urlparse(sanitized_url)

        if not parsed.netloc:
            raise InvalidURLError(f"URL must contain a valid domain, got {url}")

        if not parsed.scheme or parsed.scheme not in ["http", "https"]:
            raise InvalidURLError(f"URL must have a valid scheme (http or https), got {url}")

        return sanitized_url

    def _validate_session(self, session: requests.Session) -> requests.Session:
        """Validate the session.

        Args:
            session(requests.Session): The session to validate.

        Raises:
            InvalidSessionError: If the session is invalid.

        Returns:
            The validated session.
        """
        self._validate_type(session, requests.Session, "session", InvalidSessionError)
        return session

    def _validate_logger(self, logger: Logger | None) -> Logger:
        """Validate the logger.

        Args:
            logger(Logger | None): The logger to validate.

        Raises:
            InvalidLoggerError: If the logger is invalid.

        Returns:
            The validated logger.
        """
        if logger is None:
            return default_logger  # type: ignore[invalid-return-type]
        self._validate_type(logger, Logger, "logger", InvalidLoggerError)
        return logger

    def _validate_timeout(self, timeout: TimeoutType) -> TimeoutType:
        """Validate the timeout.

        Args:
            timeout: The timeout to validate.

        Raises:
            InvalidTimeoutError: If the timeout is invalid.

        Returns:
            The validated timeout.
        """
        self._validate_type(timeout, tuple, "Timeout", InvalidTimeoutError)
        if len(timeout) != 2:
            raise InvalidTimeoutError(f"Timeout must be a tuple of length 2, got length {len(timeout)}")
        for _, value in enumerate(timeout):
            if not isinstance(value, int | float):
                raise InvalidTimeoutError(f"Timeout must be a tuple of ints or floats, got {timeout}")
            if value <= 0:
                raise InvalidTimeoutError(f"Timeout must be greater than 0, got {timeout}")
        return timeout

    def _request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        method: str = "GET",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Send a request to the API.

        Args:
            url(str): The URL to send the request to.
            params(dict[str, Any] | None): The parameters to send with the request.
            headers(dict[str, str] | None): The headers to send with the request.
            method(str): The HTTP method to use. Defaults to "GET".

        Returns:
            The response from the API as a dictionary or list of dictionaries.

        Raises:
            requests.exceptions.RequestException: For connection, timeout, or
                other request-level errors.
            requests.exceptions.HTTPError: For HTTP 4xx or 5xx status codes.
            requests.exceptions.JSONDecodeError: If the response body cannot be
                decoded as JSON.
        """
        # For more concise logging
        request_details = f"method={method}, url={url}, params={params}, headers={headers}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            self.logger.debug(f"Request finished with status {response.status_code} for {request_details}")
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"Successfully fetched data from {url}.")

        except (
            requests_exceptions.RequestException,
            requests_exceptions.JSONDecodeError,
        ) as e:
            self.logger.exception(f"Request failed: {e.__class__.__name__} for {request_details}. ")
            raise
        return data

    def _build_url(self, endpoint: str, params: dict[str, Any] | None = None) -> str:
        """Build the URL for the request.

        Args:
            endpoint(str): The endpoint to build the URL for.
            params(dict[str, Any] | None): The parameters to add to the URL.

        Returns:
            The built URL.
        """
        params = params or {}
        url = f"{self.base_url}/{endpoint.strip('/').strip()}"
        if params:
            url += "?" + urlencode(params)
        return url

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """Send a GET request to the API. and get paginated data.

        Args:
            endpoint(str): The endpoint to send the request to.
            params(dict[str, Any] | None): The parameters to send with the request.
            headers(dict[str, str] | None): The headers to send with the request.

        Returns:
            The response from the API as a list of dictionaries.
        """
        url = self._build_url(endpoint, params)
        data: list[dict[str, Any]] = []
        while True:
            response = self._request(url, headers=headers)
            data.extend(response)
            if "@odata.nextLink" not in response:
                break
            url = response["@odata.nextLink"]
        return data

    def __repr__(self) -> str:
        """Return the string representation of the client.

        Returns:
            The string representation of the client.
        """
        return f"Odyn(base_url={self.base_url}, session={self.session}, logger={self.logger}, timeout={self.timeout})"
