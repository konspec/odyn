import logging

import pytest
import requests
from loguru import logger
from loguru._logger import Logger

from odyn import (
    InvalidLoggerError,
    InvalidSessionError,
    InvalidTimeoutError,
    InvalidURLError,
    Odyn,
)


class TestOdynInitURL:
    VALID_URL: str = "https://api.example.com"
    VALID_URL_WITH_TRAILING_SLASH: str = "https://api.example.com/"
    VALID_URL_WITH_DOUBLE_SLASH: str = "https://api.example.com//"
    VALID_URL_WITH_LEADING_WHITESPACE: str = " https://api.example.com"
    VALID_URL_WITH_TRAILING_WHITESPACE: str = "https://api.example.com  "
    SESSION: requests.Session = requests.Session()

    def test_class_init_valid_url(self):
        """Test the client initialization with a valid URL."""
        odyn: Odyn = Odyn(base_url=self.VALID_URL, session=self.SESSION)
        assert odyn.base_url == self.VALID_URL

    def test_class_init_valid_url_with_trailing_slash(self):
        """Test the client initialization with a valid URL with a trailing slash."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL_WITH_TRAILING_SLASH, session=self.SESSION
        )
        assert odyn.base_url == self.VALID_URL

    def test_class_init_valid_url_with_double_slash(self):
        """Test the client initialization with a valid URL with a double slash."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL_WITH_DOUBLE_SLASH, session=self.SESSION
        )
        assert odyn.base_url == self.VALID_URL

    def test_class_init_valid_url_with_leading_whitespace(self):
        """Test the client initialization with a valid URL with leading whitespace."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL_WITH_LEADING_WHITESPACE, session=self.SESSION
        )
        assert odyn.base_url == self.VALID_URL

    def test_class_init_valid_url_with_trailing_whitespace(self):
        """Test the client initialization with a valid URL with trailing whitespace."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL_WITH_TRAILING_WHITESPACE, session=self.SESSION
        )
        assert odyn.base_url == self.VALID_URL

    @pytest.mark.parametrize("url", [1, 1.0, None, "", {1, 2}, [1, 2], "nohttps"])
    def test_class_init_invalid_url(self, url):
        """Test the client initialization with an invalid URL."""
        with pytest.raises(InvalidURLError):
            Odyn(base_url=url, session=self.SESSION)


class TestOdynInitSession:
    """Test the client initialization with a session."""

    VALID_URL: str = "https://api.example.com"

    class InvalidSession: ...

    def test_class_init_valid_session(self):
        """Test the client initialization with a valid session."""
        session: requests.Session = requests.Session()
        odyn: Odyn = Odyn(base_url=self.VALID_URL, session=session)
        assert odyn.session == session

    @pytest.mark.parametrize(
        "session",
        [1, 1.0, None, "", {1, 2}, [1, 2], "invalid_session", InvalidSession()],
    )
    def test_class_init_invalid_session(self, session):
        """Test the client initialization with an invalid session."""
        with pytest.raises(InvalidSessionError):
            Odyn(base_url=self.VALID_URL, session=session)


class TestOdynInitLogger:
    """Test the client initialization with a logger."""

    VALID_URL: str = "https://api.example.com"
    SESSION: requests.Session = requests.Session()
    VALID_LOGGER: Logger = logger

    LOGGING_LOGGER: Logger = logging.getLogger("test")

    def test_class_init_valid_logger(self):
        """Test the client initialization with a valid logger."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL, session=self.SESSION, logger=self.VALID_LOGGER
        )
        assert odyn.logger == self.VALID_LOGGER

    @pytest.mark.parametrize(
        "logger",
        [1, 1.0, "", {1, 2}, [1, 2], "invalid_logger", LOGGING_LOGGER],
    )
    def test_class_init_invalid_logger(self, logger):
        """Test the client initialization with an invalid logger."""
        with pytest.raises(InvalidLoggerError):
            Odyn(base_url=self.VALID_URL, session=self.SESSION, logger=logger)

    def test_class_init_no_logger(self):
        """Test the client initialization with no logger."""
        odyn: Odyn = Odyn(base_url=self.VALID_URL, session=self.SESSION)
        assert odyn.logger == self.VALID_LOGGER


class TestOdynInitTimeout:
    """Test the client initialization with a timeout."""

    VALID_URL: str = "https://api.example.com"
    SESSION: requests.Session = requests.Session()

    def test_class_init_valid_timeout_int_tuple(self):
        """Test the client initialization with a valid timeout."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL, session=self.SESSION, timeout=(40, 40)
        )
        assert odyn.timeout == (40, 40)

    def test_class_init_valid_timeout_float_tuple(self):
        """Test the client initialization with a valid timeout."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL, session=self.SESSION, timeout=(40.0, 40.0)
        )
        assert odyn.timeout == (40.0, 40.0)

    @pytest.mark.parametrize(
        "timeout",
        [
            1,
            1.0,
            "",
            {1, 2},
            [1, 2],
            "invalid_timeout",
            (0, 0),
            (40, 40, 40),
            (-10, 50),
            (-50, -50),
            (40, "abc"),
            ("abc", 40),
        ],
    )
    def test_class_init_invalid_timeout(self, timeout):
        """Test the client initialization with an invalid timeout."""
        with pytest.raises(InvalidTimeoutError):
            Odyn(base_url=self.VALID_URL, session=self.SESSION, timeout=timeout)

    def test_class_init_no_timeout(self):
        """Test the client initialization with no timeout."""
        odyn: Odyn = Odyn(base_url=self.VALID_URL, session=self.SESSION)
        assert odyn.timeout == (60, 60)
