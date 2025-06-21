import logging
from unittest.mock import MagicMock, patch

import pytest
import requests
import requests.exceptions as requests_exceptions
from loguru import logger
from loguru._logger import Logger

from odyn import (
    InvalidLoggerError,
    InvalidSessionError,
    InvalidTimeoutError,
    InvalidURLError,
    Odyn,
)
from odyn._client import TimeoutType


class TestOdynRepr:
    """Test the client representation."""

    VALID_URL: str = "https://api.example.com"
    SESSION: requests.Session = requests.Session()
    VALID_LOGGER: Logger = logger
    VALID_TIMEOUT: TimeoutType = (60, 60)

    def test_class_repr_valid(self):
        """Test the client representation with valid parameters."""
        odyn: Odyn = Odyn(
            base_url=self.VALID_URL,
            session=self.SESSION,
            logger=self.VALID_LOGGER,
            timeout=self.VALID_TIMEOUT,
        )
        assert repr(odyn) == (
            f"Odyn(base_url={self.VALID_URL}, session={self.SESSION}, "
            f"logger={self.VALID_LOGGER}, timeout={self.VALID_TIMEOUT})"
        )


class TestOdynInitURL:
    VALID_URL: str = "https://api.example.com"
    VALID_URL_WITH_TRAILING_SLASH: str = "https://api.example.com/"
    VALID_URL_WITH_DOUBLE_SLASH: str = "https://api.example.com//"
    VALID_URL_WITH_LEADING_WHITESPACE: str = " https://api.example.com"
    VALID_URL_WITH_TRAILING_WHITESPACE: str = "https://api.example.com  "
    FTP_URL: str = "ftp://api.example.com"
    INVALID_URL: str = "invalid_url"
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

    def test_class_init_invalid_url_type(self):
        """Netlock is required."""
        with pytest.raises(InvalidURLError):
            Odyn(base_url=self.INVALID_URL, session=self.SESSION)

    def test_class_init_invalid_ftp_url(self):
        """FTP URLs are not allowed."""
        with pytest.raises(InvalidURLError):
            Odyn(base_url=self.FTP_URL, session=self.SESSION)


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


class TestOdynRequest:
    """Test the client's internal _request method."""

    VALID_URL: str = "https://api.example.com"
    SESSION: requests.Session = requests.Session()

    @pytest.fixture
    def odyn_client(self) -> Odyn:
        """Return a default Odyn client for testing with a mocked logger."""
        return Odyn(
            base_url=self.VALID_URL,
            session=self.SESSION,
            logger=MagicMock(spec=Logger),
        )

    @patch("requests.Session.request")
    def test_request_success(self, mock_request: MagicMock, odyn_client: Odyn):
        """Test a successful request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_data = {"key": "value"}
        mock_response.json.return_value = expected_data
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/test"
        response_data = odyn_client._request(url=test_url)

        mock_request.assert_called_once_with(
            method="GET",
            url=test_url,
            params=None,
            headers=None,
            timeout=odyn_client.timeout,
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()
        assert response_data == expected_data
        odyn_client.logger.debug.assert_any_call(
            f"Successfully fetched data from {test_url}."
        )

    @patch("requests.Session.request")
    def test_request_success_with_all_args(
        self, mock_request: MagicMock, odyn_client: Odyn
    ):
        """Test a successful request with custom method, params, and headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_data = {"status": "created"}
        mock_response.json.return_value = expected_data
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/items"
        test_params = {"filter": "id eq 1"}
        test_headers = {"Authorization": "Bearer token"}
        test_method = "POST"

        response_data = odyn_client._request(
            url=test_url,
            params=test_params,
            headers=test_headers,
            method=test_method,
        )

        mock_request.assert_called_once_with(
            method=test_method,
            url=test_url,
            params=test_params,
            headers=test_headers,
            timeout=odyn_client.timeout,
        )
        assert response_data == expected_data
        odyn_client.logger.debug.assert_any_call(
            f"Successfully fetched data from {test_url}."
        )

    @patch("requests.Session.request")
    def test_request_http_error(self, mock_request: MagicMock, odyn_client: Odyn):
        """Test that HTTPError is raised for non-2xx responses."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = requests_exceptions.HTTPError("Not Found")
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/notfound"
        with pytest.raises(requests_exceptions.HTTPError):
            odyn_client._request(url=test_url)

        odyn_client.logger.exception.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_not_called()

    @pytest.mark.parametrize(
        "exception_to_raise",
        [
            requests_exceptions.ConnectionError,
            requests_exceptions.Timeout,
            requests_exceptions.RequestException,
        ],
    )
    @patch("requests.Session.request")
    def test_request_level_exceptions(
        self,
        mock_request: MagicMock,
        exception_to_raise: type[requests_exceptions.RequestException],
        odyn_client: Odyn,
    ):
        """Test that request-level exceptions are caught, logged, and re-raised."""
        mock_request.side_effect = exception_to_raise("Request failed")

        test_url = f"{self.VALID_URL}/fail"
        with pytest.raises(exception_to_raise):
            odyn_client._request(url=test_url)

        odyn_client.logger.exception.assert_called_once()

    @patch("requests.Session.request")
    def test_json_decode_error(self, mock_request: MagicMock, odyn_client: Odyn):
        """Test that JSONDecodeError is caught, logged, and re-raised."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        json_error = requests_exceptions.JSONDecodeError("msg", "doc", 0)
        mock_response.json.side_effect = json_error
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/badjson"
        with pytest.raises(requests_exceptions.JSONDecodeError):
            odyn_client._request(url=test_url)

        odyn_client.logger.exception.assert_called_once()
        mock_response.raise_for_status.assert_called_once()


class TestOdynRequestMethod:
    """Test the client's internal _request method."""

    VALID_URL: str = "https://api.example.com"
    SESSION: requests.Session = requests.Session()

    @pytest.fixture
    def odyn_client(self) -> Odyn:
        """Return a default Odyn client for testing with a mocked logger."""
        return Odyn(
            base_url=self.VALID_URL,
            session=self.SESSION,
            logger=MagicMock(spec=Logger),
        )

    @patch("requests.Session.request")
    def test_request_success(self, mock_request: MagicMock, odyn_client: Odyn):
        """Test a successful request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_data = {"key": "value"}
        mock_response.json.return_value = expected_data
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/test"
        response_data = odyn_client._request(url=test_url)

        mock_request.assert_called_once_with(
            method="GET",
            url=test_url,
            params=None,
            headers=None,
            timeout=odyn_client.timeout,
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()
        assert response_data == expected_data
        odyn_client.logger.debug.assert_any_call(
            f"Successfully fetched data from {test_url}."
        )

    @patch("requests.Session.request")
    def test_request_success_with_all_args(
        self, mock_request: MagicMock, odyn_client: Odyn
    ):
        """Test a successful request with custom method, params, and headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_data = {"status": "created"}
        mock_response.json.return_value = expected_data
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/items"
        test_params = {"filter": "id eq 1"}
        test_headers = {"Authorization": "Bearer token"}
        test_method = "POST"

        response_data = odyn_client._request(
            url=test_url,
            params=test_params,
            headers=test_headers,
            method=test_method,
        )

        mock_request.assert_called_once_with(
            method=test_method,
            url=test_url,
            params=test_params,
            headers=test_headers,
            timeout=odyn_client.timeout,
        )
        assert response_data == expected_data
        odyn_client.logger.debug.assert_any_call(
            f"Successfully fetched data from {test_url}."
        )

    @patch("requests.Session.request")
    def test_request_http_error(self, mock_request: MagicMock, odyn_client: Odyn):
        """Test that HTTPError is raised for non-2xx responses."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = requests_exceptions.HTTPError("Not Found")
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/notfound"
        with pytest.raises(requests_exceptions.HTTPError):
            odyn_client._request(url=test_url)

        odyn_client.logger.exception.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_not_called()

    @pytest.mark.parametrize(
        "exception_to_raise",
        [
            requests_exceptions.ConnectionError,
            requests_exceptions.Timeout,
            requests_exceptions.RequestException,
        ],
    )
    @patch("requests.Session.request")
    def test_request_level_exceptions(
        self,
        mock_request: MagicMock,
        exception_to_raise: type[requests_exceptions.RequestException],
        odyn_client: Odyn,
    ):
        """Test that request-level exceptions are caught, logged, and re-raised."""
        mock_request.side_effect = exception_to_raise("Request failed")

        test_url = f"{self.VALID_URL}/fail"
        with pytest.raises(exception_to_raise):
            odyn_client._request(url=test_url)

        odyn_client.logger.exception.assert_called_once()

    @patch("requests.Session.request")
    def test_json_decode_error(self, mock_request: MagicMock, odyn_client: Odyn):
        """Test that JSONDecodeError is caught, logged, and re-raised."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        json_error = requests_exceptions.JSONDecodeError("msg", "doc", 0)
        mock_response.json.side_effect = json_error
        mock_request.return_value = mock_response

        test_url = f"{self.VALID_URL}/badjson"
        with pytest.raises(requests_exceptions.JSONDecodeError):
            odyn_client._request(url=test_url)

        odyn_client.logger.exception.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
