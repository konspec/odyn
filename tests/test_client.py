from collections.abc import Generator
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, call, patch

import pytest
import requests
import requests.exceptions as requests_exceptions
from loguru import logger as default_logger
from loguru._logger import Logger

from odyn import (
    InvalidLoggerError,
    InvalidSessionError,
    InvalidTimeoutError,
    InvalidURLError,
    Odyn,
)

if TYPE_CHECKING:
    from odyn._client import TimeoutType

# Constants for testing
BASE_URL: str = "https://api.example.com/v1.0/"
VALID_SESSION: requests.Session = requests.Session()


@pytest.fixture
def mock_logger() -> MagicMock:
    """Provides a MagicMock substitute for the loguru Logger.

    Returns:
        A MagicMock object configured with the spec of a loguru.Logger.
    """
    return MagicMock(spec=Logger)


@pytest.fixture
def odyn_client(mock_logger: MagicMock) -> Odyn:
    """Provides a default Odyn client instance with a mocked logger.

    Args:
        mock_logger: A mocked logger fixture.

    Returns:
        An Odyn client instance initialized with standard parameters for testing.
    """
    return Odyn(
        base_url=BASE_URL,
        session=VALID_SESSION,
        logger=mock_logger,
        timeout=(10, 20),
    )


class TestInitialization:
    """Tests for the Odyn client's __init__ method and its validators."""

    def test_init_success_with_all_parameters(self, mock_logger: MagicMock) -> None:
        """Verifies the client is initialized correctly with valid custom parameters."""
        session: requests.Session = requests.Session()
        timeout: TimeoutType = (5, 15)
        client: Odyn = Odyn(
            base_url="http://custom.url/api/",
            session=session,
            logger=mock_logger,
            timeout=timeout,
        )

        assert client.base_url == "http://custom.url/api/"
        assert client.session == session
        assert client.logger == mock_logger
        assert client.timeout == timeout

        # Verify initialization logging flow
        mock_logger.debug.assert_has_calls(
            [
                call("Initializing Odyn client..."),
                call("Using provided custom logger."),
                call("Base URL validation successful", url="http://custom.url/api/"),
                call("Session validation successful."),
                call("Timeout validation successful", timeout=timeout),
                call(
                    "Odyn client initialized successfully.",
                    base_url="http://custom.url/api/",
                    timeout=timeout,
                ),
            ]
        )

    def test_init_success_with_defaults(self) -> None:
        """Verifies the client initializes with the default logger and timeout."""
        session: requests.Session = requests.Session()
        client: Odyn = Odyn(base_url=BASE_URL, session=session, logger=None, timeout=Odyn.DEFAULT_TIMEOUT)

        assert client.base_url == BASE_URL
        assert client.session == session
        assert client.logger is default_logger
        assert client.timeout == Odyn.DEFAULT_TIMEOUT

    # --- URL Validation Tests ---
    @pytest.mark.parametrize(
        ("url_input", "expected_sanitized_url"),
        [
            ("https://api.example.com", "https://api.example.com/"),
            (" https://api.example.com/v2.0 ", "https://api.example.com/v2.0/"),
            ("https://api.example.com/v2.0/", "https://api.example.com/v2.0/"),
        ],
    )
    def test_init_sanitizes_url_correctly(self, url_input: str, expected_sanitized_url: str) -> None:
        """Verifies that the base URL is correctly sanitized (whitespace, trailing slash)."""
        client: Odyn = Odyn(base_url=url_input, session=VALID_SESSION)
        assert client.base_url == expected_sanitized_url

    @pytest.mark.parametrize(
        ("invalid_url", "error_message"),
        [
            (123, "base_url must be a str, got int"),
            ("", "URL cannot be empty"),
            ("   ", "URL cannot be empty"),
            (
                "no_scheme.com",
                r"URL must have a valid scheme \(http or https\), got no_scheme\.com",
            ),
            (
                "ftp://invalid.scheme",
                r"URL must have a valid scheme \(http or https\), got ftp://invalid\.scheme",
            ),
            ("https://", r"URL must contain a valid domain, got https://"),
        ],
    )
    def test_init_raises_invalid_url_error_for_invalid_urls(self, invalid_url: Any, error_message: str) -> None:
        """Verifies InvalidURLError is raised for malformed or invalid URLs."""
        with pytest.raises(InvalidURLError, match=error_message):
            Odyn(base_url=invalid_url, session=VALID_SESSION)

    # --- Session Validation Tests ---
    @pytest.mark.parametrize(
        ("invalid_session", "expected_type_name"),
        [
            (None, "NoneType"),
            ("not a session", "str"),
            (123, "int"),
            (object(), "object"),
        ],
    )
    def test_init_raises_invalid_session_error_for_invalid_session(
        self, invalid_session: Any, expected_type_name: str
    ) -> None:
        """Verifies InvalidSessionError is raised if the session is not a requests.Session."""
        expected_message: str = f"session must be a Session, got {expected_type_name}"
        with pytest.raises(InvalidSessionError, match=expected_message):
            Odyn(base_url=BASE_URL, session=invalid_session)

    # --- Logger Validation Tests ---
    def test_init_uses_default_logger_if_none_provided(self) -> None:
        """Verifies the default loguru logger is used when none is passed."""
        client: Odyn = Odyn(base_url=BASE_URL, session=VALID_SESSION, logger=None)
        assert client.logger is default_logger

    @pytest.mark.parametrize(
        ("invalid_logger", "expected_type_name"),
        [
            (123, "int"),
            ("not a logger", "str"),
            (object(), "object"),
        ],
    )
    def test_init_raises_invalid_logger_error_for_invalid_logger(
        self, invalid_logger: Any, expected_type_name: str
    ) -> None:
        """Verifies InvalidLoggerError is raised for invalid logger types."""
        expected_message: str = f"logger must be a Logger, got {expected_type_name}"
        with pytest.raises(InvalidLoggerError, match=expected_message):
            Odyn(base_url=BASE_URL, session=VALID_SESSION, logger=invalid_logger)

    # --- Timeout Validation Tests ---
    @pytest.mark.parametrize(
        ("invalid_timeout", "error_message"),
        [
            (1, "Timeout must be a tuple, got int"),
            ((10,), "Timeout must be a tuple of length 2, got length 1"),
            ((10, 20, 30), "Timeout must be a tuple of length 2, got length 3"),
            (("ten", 20), "Timeout values must be int or float, but value at index 0 is str"),
            ((10, "twenty"), "Timeout values must be int or float, but value at index 1 is str"),
            ((-10, 20), "Timeout values must be greater than 0, got -10"),
            ((10, 0), "Timeout values must be greater than 0, got 0"),
        ],
    )
    def test_init_raises_invalid_timeout_error_for_invalid_timeout(
        self, invalid_timeout: Any, error_message: str
    ) -> None:
        """Verifies InvalidTimeoutError is raised for malformed or invalid timeouts."""
        with pytest.raises(InvalidTimeoutError, match=error_message):
            Odyn(base_url=BASE_URL, session=VALID_SESSION, timeout=invalid_timeout)


class TestStringRepresentation:
    """Tests the __repr__ method."""

    def test_repr_returns_correct_string(self) -> None:
        """Verifies the __repr__ of the client is correctly formatted."""
        client: Odyn = Odyn(base_url=BASE_URL, session=VALID_SESSION, timeout=(10, 30))
        expected_repr: str = f"Odyn(base_url='{BASE_URL}', timeout=(10, 30))"
        assert repr(client) == expected_repr


class TestBuildURL:
    """Tests the internal _build_url method."""

    @pytest.mark.parametrize(
        ("base_url", "endpoint", "params", "expected"),
        [
            ("https://a.com/", "items", None, "https://a.com/items"),
            ("https://a.com", "items", None, "https://a.com/items"),
            ("https://a.com/", "/items", None, "https://a.com/items"),  # Handles leading slash
            ("https://a.com/", "items", {"$top": 5}, "https://a.com/items?%24top=5"),
            ("https://a.com/api/", "items", {"$filter": "id eq 1"}, "https://a.com/api/items?%24filter=id+eq+1"),
        ],
    )
    def test_build_url_constructs_correctly(
        self, odyn_client: Odyn, base_url: str, endpoint: str, params: dict[str, Any] | None, expected: str
    ) -> None:
        """Verifies _build_url combines base, endpoint, and params correctly."""
        odyn_client.base_url = base_url  # Override fixture base_url
        built_url: str = odyn_client._build_url(endpoint, params)
        assert built_url == expected
        odyn_client.logger.debug.assert_called_with("Built request URL", final_url=expected)


class TestRequest:
    """Tests the internal _request method."""

    @patch("requests.Session.request")
    def test_request_success(self, mock_request: MagicMock, odyn_client: Odyn) -> None:
        """Verifies a successful request returns JSON and logs correctly."""
        mock_response: MagicMock = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://api.example.com/v1.0/test"
        mock_response.json.return_value = {"data": "success"}
        mock_request.return_value = mock_response

        url: str = odyn_client._build_url("test")
        result: dict[str, Any] = odyn_client._request(url, method="GET", params={"q": 1}, headers={"X-Test": "true"})

        mock_request.assert_called_once_with(
            method="GET",
            url=url,
            params={"q": 1},
            headers={"X-Test": "true"},
            timeout=odyn_client.timeout,
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == {"data": "success"}
        odyn_client.logger.debug.assert_any_call("Request completed", status_code=200, url=mock_response.url)

    @patch("requests.Session.request")
    def test_request_raises_and_logs_http_error(self, mock_request: MagicMock, odyn_client: Odyn) -> None:
        """Verifies HTTPError from a response is raised and logged."""
        mock_response: MagicMock = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        # The HTTPError object needs the response attached to it for the logger to access it
        http_error: requests_exceptions.HTTPError = requests_exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        url: str = odyn_client._build_url("notfound")
        with pytest.raises(requests_exceptions.HTTPError):
            odyn_client._request(url)

        odyn_client.logger.exception.assert_called_once_with(
            "Request failed with HTTP error",
            status_code=404,
            response_text="Not Found",
            url=url,
        )

    @patch("requests.Session.request")
    def test_request_raises_and_logs_network_error(self, mock_request: MagicMock, odyn_client: Odyn) -> None:
        """Verifies RequestException during a request is raised and logged."""
        network_error: requests_exceptions.Timeout = requests_exceptions.Timeout("Connection timed out")
        mock_request.side_effect = network_error

        url: str = odyn_client._build_url("timeout")
        with pytest.raises(requests_exceptions.Timeout):
            odyn_client._request(url)

        odyn_client.logger.exception.assert_called_once_with("Request failed due to a network error", url=url)

    @patch("requests.Session.request")
    def test_request_wraps_and_logs_json_decode_error(self, mock_request: MagicMock, odyn_client: Odyn) -> None:
        """Verifies JSONDecodeError is caught, logged, and re-raised as a ValueError."""
        mock_response: MagicMock = MagicMock()
        mock_response.status_code = 200
        json_error: requests_exceptions.JSONDecodeError = requests_exceptions.JSONDecodeError("msg", "doc", 0)
        mock_response.json.side_effect = json_error
        mock_request.return_value = mock_response

        url: str = odyn_client._build_url("badjson")
        with pytest.raises(ValueError, match="Failed to decode JSON from response") as exc_info:
            odyn_client._request(url)

        assert isinstance(exc_info.value.__cause__, requests_exceptions.JSONDecodeError)
        odyn_client.logger.exception.assert_called_once_with("Failed to decode JSON response", url=url)


class TestGetMethod:
    """Tests the public get() method, including pagination."""

    @pytest.fixture
    def mock_request_method(self, odyn_client: Odyn) -> Generator[MagicMock, None, None]:
        """Fixture to mock the internal _request method of the Odyn client.

        Args:
            odyn_client: The Odyn client instance.

        Yields:
            A MagicMock object replacing the _request method.
        """
        with patch.object(odyn_client, "_request") as mock:
            yield mock

    def test_get_single_page(self, odyn_client: Odyn, mock_request_method: MagicMock, mock_logger: MagicMock) -> None:
        """Verifies get() retrieves a single page of results correctly."""
        endpoint: str = "items"
        expected_items: list[dict[str, int]] = [{"id": 1}, {"id": 2}]
        mock_request_method.return_value = {"value": expected_items}

        result: list[dict[str, Any]] = odyn_client.get(endpoint, params={"$top": 2})

        assert result == expected_items
        built_url: str = odyn_client._build_url(endpoint, {"$top": 2})
        mock_request_method.assert_called_once_with(built_url, headers=None)
        mock_logger.debug.assert_any_call("No more pages found for endpoint '{endpoint}'.", endpoint=endpoint)

    def test_get_multiple_pages(
        self, odyn_client: Odyn, mock_request_method: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Verifies get() handles pagination and aggregates results from multiple pages."""
        endpoint: str = "customers"
        next_link: str = "https://api.example.com/v1.0/customers?$skip=2"
        page1_items: list[dict[str, str]] = [{"id": "C01"}, {"id": "C02"}]
        page2_items: list[dict[str, str]] = [{"id": "C03"}]

        mock_request_method.side_effect = [
            {"value": page1_items, "@odata.nextLink": next_link},
            {"value": page2_items},  # Final page
        ]

        result: list[dict[str, Any]] = odyn_client.get(endpoint)

        assert result == page1_items + page2_items
        assert mock_request_method.call_count == 2
        first_call_url: str = odyn_client._build_url(endpoint, None)
        mock_request_method.assert_has_calls([call(first_call_url, headers=None), call(next_link, headers=None)])

        mock_logger.debug.assert_any_call("Pagination link found, preparing to fetch next page.")
        mock_logger.debug.assert_any_call(
            "Finished fetching all pages for endpoint '{endpoint}'. Total items: {total}", endpoint=endpoint, total=3
        )

    def test_get_empty_result(self, odyn_client: Odyn, mock_request_method: MagicMock) -> None:
        """Verifies get() returns an empty list for an empty 'value' field."""
        mock_request_method.return_value = {"value": []}
        result: list[dict[str, Any]] = odyn_client.get("empty")
        assert result == []

    @pytest.mark.parametrize(
        "malformed_response",
        [
            {"data": []},  # Missing 'value' key
            {"value": "not-a-list"},  # 'value' is not a list
        ],
    )
    def test_get_raises_typeerror_for_malformed_odata_response(
        self, odyn_client: Odyn, mock_request_method: MagicMock, malformed_response: dict[str, Any]
    ) -> None:
        """Verifies get() raises TypeError if the OData response is not a list of values."""
        mock_request_method.return_value = malformed_response
        with pytest.raises(TypeError, match="OData response missing 'value' list."):
            odyn_client.get("malformed")
        odyn_client.logger.error.assert_called_once()
