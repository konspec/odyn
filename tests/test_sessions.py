from odyn import Odyn
from odyn.sessions import BasicAuthSession, BearerAuthSession


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
