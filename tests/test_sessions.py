import pytest

from odyn import Odyn
from odyn._exceptions import (
    InvalidBackoffFactorError,
    InvalidRetryError,
    InvalidStatusForcelistError,
)
from odyn.sessions import BasicAuthSession, BearerAuthSession, OdynSession


class TestBasicAuthSession:
    """Test the BasicAuthSession class."""

    def test_basic_auth_session_init(self) -> None:
        """Test the initialization of the BasicAuthSession class."""
        session: BasicAuthSession = BasicAuthSession("test_username", "test_password")
        assert session.auth == ("test_username", "test_password")


class TestBearerAuthSession:
    """Test the BearerAuthSession class."""

    def test_bearer_auth_session_init(self) -> None:
        """Test the initialization of the BearerAuthSession class."""
        session: BearerAuthSession = BearerAuthSession("test_token")
        assert session.headers["Authorization"] == "Bearer test_token"


class TestOdynClientWithSession:
    """Test the OdynClient class with a session."""

    BASE_URL: str = "https://api.odyn.com"

    BASIC_AUTH_SESSION: BasicAuthSession = BasicAuthSession(
        "test_username", "test_password"
    )
    BEARER_AUTH_SESSION: BearerAuthSession = BearerAuthSession("test_token")

    def test_odyn_client_with_basic_auth_session(self) -> None:
        """Test the OdynClient class with a BasicAuthSession."""
        client: Odyn = Odyn(
            base_url=self.BASE_URL,
            session=self.BASIC_AUTH_SESSION,
        )
        assert client.session.auth == ("test_username", "test_password")
        assert client.base_url == self.BASE_URL
        assert client.session == self.BASIC_AUTH_SESSION

    def test_odyn_client_with_bearer_auth_session(self) -> None:
        """Test the OdynClient class with a BearerAuthSession."""
        client: Odyn = Odyn(
            base_url=self.BASE_URL,
            session=self.BEARER_AUTH_SESSION,
        )
        assert client.session.headers["Authorization"] == "Bearer test_token"
        assert client.base_url == self.BASE_URL
        assert client.session == self.BEARER_AUTH_SESSION


class TestOdynSessionRetry:
    """Test the OdynSession class."""

    def test_odyn_session_init_retry_default(self) -> None:
        """Test the initialization of the OdynSession class."""
        session: OdynSession = OdynSession()
        assert session._retry == 5
        assert session.adapters["https://"].max_retries.total == 5
        assert session.adapters["http://"].max_retries.total == 5

    def test_odyn_session_init_retry_valid(self) -> None:
        """Test the initialization of the OdynSession class."""
        session: OdynSession = OdynSession(retry=1)
        assert session._retry == 1
        assert session.adapters["https://"].max_retries.total == 1
        assert session.adapters["http://"].max_retries.total == 1

    @pytest.mark.parametrize(
        "retry",
        [
            "invalid",
            -1,
            0,
            [0],
            (0,),
            {
                0,
            },
        ],
    )
    def test_odyn_session_init_retry_invalid(self, retry: int) -> None:
        """Test the initialization of the OdynSession class."""
        with pytest.raises(InvalidRetryError):
            OdynSession(retry=retry)


class TestOdynSessionBackoffFactor:
    """Test the OdynSession class."""

    def test_odyn_session_init_backoff_factor_default(self) -> None:
        """Test the initialization of the OdynSession class."""
        session: OdynSession = OdynSession()
        assert session._backoff_factor == 2.0
        assert session.adapters["https://"].max_retries.backoff_factor == 2.0
        assert session.adapters["http://"].max_retries.backoff_factor == 2.0

    @pytest.mark.parametrize(
        "backoff_factor",
        [
            "invalid",
            -1,
            0,
            [0],
            (0,),
            {
                0,
            },
        ],
    )
    def test_odyn_session_init_backoff_factor_invalid(
        self, backoff_factor: float | int
    ) -> None:
        """Test the initialization of the OdynSession class."""
        with pytest.raises(InvalidBackoffFactorError):
            OdynSession(backoff_factor=backoff_factor)

    def test_odyn_session_init_backoff_factor_valid(self) -> None:
        """Test the initialization of the OdynSession class."""
        session: OdynSession = OdynSession(backoff_factor=1.5)
        assert session._backoff_factor == 1.5
        assert session.adapters["https://"].max_retries.backoff_factor == 1.5
        assert session.adapters["http://"].max_retries.backoff_factor == 1.5


class TestOdynSessionStatusForcelist:
    """Test the OdynSession class."""

    def test_odyn_session_init_status_forcelist_default(self) -> None:
        """Test the initialization of the OdynSession class."""
        session: OdynSession = OdynSession()
        assert session._status_forcelist == [500, 502, 503, 504, 429]
        assert session.adapters["https://"].max_retries.status_forcelist == [
            500,
            502,
            503,
            504,
            429,
        ]
        assert session.adapters["http://"].max_retries.status_forcelist == [
            500,
            502,
            503,
            504,
            429,
        ]

    def test_odyn_session_init_status_forcelist_valid(self) -> None:
        """Test the initialization of the OdynSession class."""
        session: OdynSession = OdynSession(
            status_forcelist=[500, 502, 503, 504, 429, 505]
        )
        assert session._status_forcelist == [500, 502, 503, 504, 429, 505]
        assert session.adapters["https://"].max_retries.status_forcelist == [
            500,
            502,
            503,
            504,
            429,
            505,
        ]
        assert session.adapters["http://"].max_retries.status_forcelist == [
            500,
            502,
            503,
            504,
            429,
            505,
        ]

    @pytest.mark.parametrize(
        "status_forcelist",
        [
            "invalid",
            -1,
            [0, "invalid"],
            (0,),
            {
                0,
            },
        ],
    )
    def test_odyn_session_init_status_forcelist_invalid(
        self, status_forcelist: list[int]
    ) -> None:
        """Test the initialization of the OdynSession class."""
        with pytest.raises(InvalidStatusForcelistError):
            OdynSession(status_forcelist=status_forcelist)
