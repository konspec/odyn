import requests
from loguru import logger as default_logger
from loguru._logger import Logger

from odyn._exceptions import InvalidLoggerError, InvalidSessionError, InvalidURLError


class Odyn:
    def __init__(
        self, base_url: str, session: requests.Session, logger: Logger | None = None
    ):
        """Initialize the Odyn client.

        Args:
            base_url: The base URL of the OData service.
            session: The requests session to use for the client.
                Any authentication should be handled by the session.
            logger: The logger to use for the client.
        """
        self.base_url: str = self._validate_url(base_url)
        self.session: requests.Session = self._validate_session(session)
        self.logger: Logger = self._validate_logger(logger)

    def _validate_url(self, url: str) -> str:
        """Validate the URL.

        Args:
            url: The URL to validate.
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
            session: The session to validate.
        """
        if not isinstance(session, requests.Session):
            error_msg: str = f"Session must be a requests.Session, got {type(session)}"
            raise InvalidSessionError(error_msg)
        return session

    def _validate_logger(self, logger: Logger | None) -> Logger:
        """Validate the logger.

        Args:
            logger: The logger to validate.
        """
        if logger is None:
            return default_logger  # type: ignore[invalid-return-type]
        if not isinstance(logger, Logger):
            error_msg: str = f"Logger must be a loguru.Logger, got {type(logger)}"
            raise InvalidLoggerError(error_msg)
        return logger
