import requests


class BasicAuthSession(requests.Session):
    """Session for Odyn API requests with basic authentication."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the session with basic authentication.

        Args:
            username: The username to use for basic authentication.
            password: The password to use for basic authentication.

        Returns:
            None
        """
        super().__init__()
        self.auth = (username, password)


class BearerAuthSession(requests.Session):
    """Session for Odyn API requests with bearer authentication."""

    def __init__(self, token: str) -> None:
        """Initialize the session with bearer authentication.

        Args:
            token: The token to use for bearer authentication.

        Returns:
            None
        """
        super().__init__()
        self.headers.update({"Authorization": f"Bearer {token}"})
