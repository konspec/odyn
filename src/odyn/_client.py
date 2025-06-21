from typing import Any, ClassVar
from urllib.parse import ParseResult, urlencode, urljoin, urlparse

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
    """Python adapter for MS Dynamics 365 Business Central OData V4 API.

    Attributes:
        DEFAULT_TIMEOUT: The default timeout for requests as (connect, read).
        logger: The logger instance used by the client.
        base_url: The sanitized base URL of the OData service.
        session: The requests.Session object used for making HTTP requests.
        timeout: The timeout configuration for requests.
    """

    DEFAULT_TIMEOUT: ClassVar[TimeoutType] = (60, 60)
    logger: Logger
    base_url: str
    session: requests.Session
    timeout: TimeoutType

    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        logger: Logger | None = None,
        timeout: TimeoutType = DEFAULT_TIMEOUT,
    ) -> None:
        """Initializes the Odyn client.

        Args:
            base_url: The base URL of the OData service. It will be sanitized to end with a "/".
            session: The requests session to use for the client. Any authentication should be handled by the session.
            logger: The logger to use for the client. If None, a default loguru logger is used.
            timeout: The timeout to use for the client as (connect_timeout, read_timeout). Defaults to (60, 60).

        Raises:
            InvalidURLError: If the URL is invalid.
            InvalidSessionError: If the session is invalid.
            InvalidLoggerError: If the logger is invalid.
            InvalidTimeoutError: If the timeout is invalid.
        """
        # The logger must be validated first so it can be used by other methods.
        self.logger = self._validate_logger(logger)
        self.logger.debug("Initializing Odyn client...")

        if logger is None:
            self.logger.debug("No logger provided, using default logger.")
        else:
            self.logger.debug("Using provided custom logger.")

        self.base_url = self._validate_url(base_url)
        self.session = self._validate_session(session)
        self.timeout = self._validate_timeout(timeout)

        self.logger.debug(
            "Odyn client initialized successfully.",
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def _validate_type(self, value: Any, expected_type: type, param_name: str, exception_class: type) -> None:
        """Validates the type of a given parameter.

        Args:
            value: The value to validate.
            expected_type: The type the value is expected to be.
            param_name: The name of the parameter being validated.
            exception_class: The exception to raise upon validation failure.

        Raises:
            Exception: An exception of the type `exception_class` if validation fails.
        """
        if not isinstance(value, expected_type):
            error_msg: str = f"{param_name} must be a {expected_type.__name__}, got {type(value).__name__}"
            self.logger.error(error_msg)
            raise exception_class(error_msg)

    def _validate_url(self, url: str) -> str:
        """Validates and sanitizes the URL to ensure it is a valid base for API calls.

        Args:
            url: The base URL string to validate.

        Returns:
            The sanitized URL, guaranteed to end with a "/".

        Raises:
            InvalidURLError: If the URL is empty, has an invalid scheme, or is missing a domain.
        """
        self._validate_type(url, str, "base_url", InvalidURLError)

        sanitized_url: str = url.strip()
        if not sanitized_url:
            raise InvalidURLError("URL cannot be empty")

        parsed: ParseResult = urlparse(sanitized_url)
        if not parsed.scheme or parsed.scheme not in ["http", "https"]:
            raise InvalidURLError(f"URL must have a valid scheme (http or https), got {url}")
        if not parsed.netloc:
            raise InvalidURLError(f"URL must contain a valid domain, got {url}")

        # Ensure the base URL ends with a slash for robust joining with endpoints.
        if not sanitized_url.endswith("/"):
            sanitized_url += "/"

        self.logger.debug("Base URL validation successful", url=sanitized_url)
        return sanitized_url

    def _validate_session(self, session: requests.Session) -> requests.Session:
        """Validates that the session is a requests.Session object.

        Args:
            session: The session object to validate.

        Returns:
            The validated session object.

        Raises:
            InvalidSessionError: If the provided object is not a requests.Session.
        """
        self._validate_type(session, requests.Session, "session", InvalidSessionError)
        self.logger.debug("Session validation successful.")
        return session

    def _validate_logger(self, logger: Logger | None) -> Logger:
        """Validates the logger, returning the default logger if None is provided.

        Args:
            logger: The logger object to validate.

        Returns:
            A valid Logger instance.

        Raises:
            InvalidLoggerError: If the provided object is not a loguru Logger.
        """
        if logger is None:
            return default_logger  # ty:ignore[invalid-return-type]

        # This validation is special. It runs before self.logger is set,
        # so it cannot use the generic _validate_type helper which tries to log.
        if not isinstance(logger, Logger):
            error_msg: str = f"logger must be a {Logger.__name__}, got {type(logger).__name__}"
            raise InvalidLoggerError(error_msg)
        return logger

    def _validate_timeout(self, timeout: TimeoutType) -> TimeoutType:
        """Validates that the timeout is a tuple of two positive numbers.

        Args:
            timeout: The timeout tuple to validate.

        Returns:
            The validated timeout tuple.

        Raises:
            InvalidTimeoutError: If timeout is not a tuple of two positive numbers.
        """
        self._validate_type(timeout, tuple, "Timeout", InvalidTimeoutError)
        if len(timeout) != 2:
            raise InvalidTimeoutError(f"Timeout must be a tuple of length 2, got length {len(timeout)}")

        for i, value in enumerate(timeout):
            if not isinstance(value, int | float):
                raise InvalidTimeoutError(
                    f"Timeout values must be int or float, but value at index {i} is {type(value).__name__}"
                )
            if value <= 0:
                raise InvalidTimeoutError(f"Timeout values must be greater than 0, got {value}")

        self.logger.debug("Timeout validation successful", timeout=timeout)
        return timeout

    def _request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        """Sends a request to the API and handles the response.

        Args:
            url: The full URL for the request.
            params: Query parameters for the request.
            headers: Additional request headers.
            method: The HTTP method to use (e.g., "GET", "POST").

        Returns:
            The JSON response from the API as a dictionary.

        Raises:
            requests.exceptions.HTTPError: For HTTP 4xx or 5xx status codes.
            requests.exceptions.RequestException: For other network-level errors.
            ValueError: If the response is not valid JSON.
        """
        self.logger.debug("Sending request", method=method, url=url, params=params, headers=headers)
        try:
            response: requests.Response = self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            self.logger.debug(
                "Request completed",
                status_code=response.status_code,
                url=response.url,
            )
            response.raise_for_status()
            return response.json()

        except requests_exceptions.HTTPError as http_err:
            self.logger.exception(
                "Request failed with HTTP error",
                status_code=http_err.response.status_code,
                response_text=http_err.response.text,
                url=url,
            )
            raise
        except requests_exceptions.JSONDecodeError as json_err:
            self.logger.exception(
                "Failed to decode JSON response",
                url=url,
            )
            raise ValueError("Failed to decode JSON from response") from json_err
        except requests_exceptions.RequestException:
            self.logger.exception("Request failed due to a network error", url=url)
            raise

    def _build_url(self, endpoint: str, params: dict[str, Any] | None = None) -> str:
        """Builds the full URL for an API request using a robust join method.

        Args:
            endpoint: The API endpoint path.
            params: A dictionary of query parameters to append to the URL.

        Returns:
            The fully constructed URL string.
        """
        # Use urljoin for robustly combining the base URL and endpoint.
        # lstrip("/") from endpoint prevents urljoin from treating it as a root path.
        full_url: str = urljoin(self.base_url, endpoint.lstrip("/"))
        if params:
            full_url += "?" + urlencode(params)
        self.logger.debug("Built request URL", final_url=full_url)
        return full_url

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """Sends a GET request and automatically handles OData pagination.

        Args:
            endpoint: The API endpoint to query.
            params: Query parameters for the request.
            headers: Additional request headers.

        Returns:
            A list containing all items retrieved from all pages.

        Raises:
            TypeError: If the OData response is malformed (e.g., missing 'value' key or 'value' is not a list).
        """
        self.logger.debug("Initiating GET request with pagination", endpoint=endpoint, params=params)
        next_url: str | None = self._build_url(endpoint, params)
        all_items: list[dict[str, Any]] = []
        page_num: int = 1

        while next_url:
            self.logger.debug("Fetching page {page_num}", page_num=page_num, url=next_url)
            response_data: dict[str, Any] = self._request(next_url, headers=headers)

            items: Any = response_data.get("value")
            if not isinstance(items, list):
                self.logger.error(
                    "OData response format is invalid: 'value' key is missing or not a list.",
                    response_keys=list(response_data.keys()),
                    url=next_url,
                )
                raise TypeError("OData response missing 'value' list.")

            all_items.extend(items)
            self.logger.debug(
                "Fetched {count} items from page {page_num}. Total items so far: {total}",
                count=len(items),
                page_num=page_num,
                total=len(all_items),
            )

            next_url = response_data.get("@odata.nextLink")
            if next_url:
                page_num += 1
                self.logger.debug("Pagination link found, preparing to fetch next page.")
            else:
                self.logger.debug("No more pages found for endpoint '{endpoint}'.", endpoint=endpoint)

        self.logger.debug(
            "Finished fetching all pages for endpoint '{endpoint}'. Total items: {total}",
            endpoint=endpoint,
            total=len(all_items),
        )
        return all_items

    def __repr__(self) -> str:
        """Returns the string representation of the client.

        Returns:
            A string representation of the Odyn client instance.
        """
        return f"Odyn(base_url='{self.base_url}', timeout={self.timeout})"
