import requests
from loguru import logger as default_logger
from loguru._logger import Logger

from odyn._exceptions import (
    InvalidLoggerError,
    InvalidSessionError,
    InvalidTimeoutError,
    InvalidURLError,
)


class Odyn:
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        logger: Logger | None = None,
        timeout: tuple[int, int] | tuple[float, float] | None = None,
    ) -> None:
        """Initialize the Odyn client.

        Args:
            base_url(str): The base URL of the OData service.
            session(requests.Session): The requests session to use for the client.
                Any authentication should be handled by the session.
            logger(Logger | None): The logger to use for the client.
            timeout: The timeout to use for the client.

        Raises:
            InvalidURLError: If the URL is invalid.
            InvalidSessionError: If the session is invalid.
            InvalidLoggerError: If the logger is invalid.
            InvalidTimeoutError: If the timeout is invalid.

        Returns:
            None
        """
        self.base_url: str = self._validate_url(base_url)
        self.session: requests.Session = self._validate_session(session)
        self.logger: Logger = self._validate_logger(logger)
        self.timeout: tuple[int, int] | tuple[float, float] = self._validate_timeout(
            timeout
        )

    def _validate_url(self, url: str) -> str:
        """Validate the URL.

        Args:
            url(str): The URL to validate.

        Raises:
            InvalidURLError: If the URL is invalid.

        Returns:
            The validated URL.
        """
        if not isinstance(url, str):
            error_msg: str = f"URL must be a string, got {type(url)}"
            raise InvalidURLError(error_msg)

        sanitized_url: str = url.strip().rstrip("/")

        if not sanitized_url:
            error_msg: str = "URL cannot be empty"
            raise InvalidURLError(error_msg)
        if not sanitized_url.startswith(("http", "https")):
            error_msg: str = f"URL must start with http or https, got {url}"
            raise InvalidURLError(error_msg)
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
        if not isinstance(session, requests.Session):
            error_msg: str = f"Session must be a requests.Session, got {type(session)}"
            raise InvalidSessionError(error_msg)
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
        if not isinstance(logger, Logger):
            error_msg: str = f"Logger must be a loguru.Logger, got {type(logger)}"
            raise InvalidLoggerError(error_msg)
        return logger

    def _validate_timeout(
        self, timeout: tuple[int, int] | tuple[float, float] | None
    ) -> tuple[int, int] | tuple[float, float]:
        """Validate the timeout.

        Args:
            timeout: The timeout to validate.

        Raises:
            InvalidTimeoutError: If the timeout is invalid.

        Returns:
            The validated timeout.
        """
        # Default timeout is 60 seconds
        if timeout is None:
            return (60, 60)
        if not isinstance(timeout, tuple):
            error_msg: str = f"Timeout must be a tuple, got {type(timeout)}"
            raise InvalidTimeoutError(error_msg)
        if len(timeout) != 2:
            error_msg: str = f"Timeout must be a tuple of length 2, got {timeout}"
            raise InvalidTimeoutError(error_msg)
        if not all(isinstance(t, int | float) for t in timeout):
            error_msg: str = f"Timeout must be a tuple of ints or floats, got {timeout}"
            raise InvalidTimeoutError(error_msg)
        if not all(t > 0 for t in timeout):
            error_msg: str = f"Timeout must be greater than 0, got {timeout}"
            raise InvalidTimeoutError(error_msg)
        return timeout
