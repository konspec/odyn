# Authentication and Session Management

This guide is the definitive source for understanding and configuring authentication, retries, and session handling in Odyn.

## The Role of the Session

In Odyn, the `Odyn` client is responsible for building requests and handling responses, but it does not directly manage authentication or network resilience. That responsibility is delegated to a **Session object**.

This design pattern offers significant flexibility:
-   **Separation of Concerns**: Your authentication logic (e.g., refreshing a token) is kept separate from your API-calling logic (e.g., fetching customers).
-   **Configurability**: You can fine-tune retry behavior for different network conditions without altering the client.
-   **Extensibility**: You can provide your own custom authentication mechanism by creating a custom session class.

Every `Odyn` client requires a session object during initialization. This object must be an instance of `requests.Session`. Odyn provides several powerful, pre-built session classes that you can use out of the box.

---

## The `OdynSession`: A Foundation with Retries

The cornerstone of session management in Odyn is the `OdynSession` class. This class inherits from `requests.Session` but adds a powerful, automatic retry mechanism with exponential backoff.

It serves as the base class for Odyn's other sessions and is the perfect foundation for your own custom sessions.

### Configuring Retry Behavior

You can customize the retry logic by passing parameters to any of Odyn's built-in session classes.

```python
OdynSession(
    retries: int = 5,
    backoff_factor: float = 2.0,
    status_forcelist: list[int] | None = None
)
```

-   `retries` (`int`): The total number of retry attempts for a failed request. Must be a positive integer.
-   `backoff_factor` (`float`): A multiplier used to calculate the delay between retries.
-   `status_forcelist` (`list[int]`): A list of HTTP status codes that will trigger a retry. By default, this is `[429, 500, 502, 503, 504]`.

### The Exponential Backoff Algorithm

The delay between retries is calculated using this formula, which prevents overwhelming an API that is temporarily struggling:

`delay = backoff_factor * (2 ** (retry_attempt - 1))`

**Example**: With the default `retries=5` and `backoff_factor=2.0`, the delays will be:
-   Retry 1: `2.0 * (2 ** 0)` = 2 seconds
-   Retry 2: `2.0 * (2 ** 1)` = 4 seconds
-   Retry 3: `2.0 * (2 ** 2)` = 8 seconds
-   Retry 4: `2.0 * (2 ** 3)` = 16 seconds
-   Retry 5: `2.0 * (2 ** 4)` = 32 seconds

---

## Built-in Session Implementations

Odyn provides two ready-to-use sessions for the most common Business Central authentication methods.

### `BearerAuthSession` (Recommended)

This session handles modern token-based authentication. It extends `OdynSession` and automatically adds the `Authorization: Bearer <your-token>` header to every request.

```python
from odyn import BearerAuthSession

# Create a session with your access token
# You can also customize the retry logic here
session = BearerAuthSession(
    token="your-super-secret-access-token",
    retries=3,
    backoff_factor=1.0
)
```

### `BasicAuthSession`

This session handles legacy username and password authentication. It extends `OdynSession` and uses the `auth` property of the underlying `requests.Session`.

**Security Warning**: Basic Authentication is less secure than token-based methods. Only use it if your environment does not support modern authentication.

```python
from odyn import BasicAuthSession

# Create a session with your username and Web Service Access Key
session = BasicAuthSession(
    username="your-username",
    password="your-web-service-access-key",
    retries=10 # Example: more aggressive retries
)
```

---

## Creating a Custom Session

You have two primary methods for implementing custom session logic.

### Method 1: Extending `OdynSession` (Recommended)

This is the best approach for most custom authentication scenarios because you **inherit the robust, built-in retry mechanism**.

Follow this pattern to create a session that adds a custom header (e.g., `X-Api-Key`).

#### Step 1: Create a New Session Class

Inherit from `OdynSession`. In the `__init__` method, accept your secret and any `**kwargs`. The `**kwargs` are crucial for allowing users of your class to customize the retry settings.

#### Step 2: Call the Parent Constructor

Call `super().__init__(**kwargs)` to ensure the retry logic is initialized correctly.

#### Step 3: Implement Your Custom Logic

Modify the session as needed. In this case, we'll add a header.

```python
# custom_sessions.py
from odyn import OdynSession, Odyn

# Step 1: Inherit from OdynSession
class ApiKeyAuthSession(OdynSession):
    """
    A custom session that authenticates using a static API key in a header.
    It inherits the retry logic from OdynSession.
    """
    def __init__(self, api_key: str, **kwargs):
        # Step 2: Pass retry kwargs to the parent
        super().__init__(**kwargs)

        if not api_key or not isinstance(api_key, str):
            raise ValueError("A valid API key (string) is required.")

        # Step 3: Add the custom authentication header
        self.headers.update({"X-Api-Key": api_key})

# How to use your custom session:
api_key = "your-secret-api-key"

# You can configure retries just like with the built-in sessions
session = ApiKeyAuthSession(api_key=api_key, retries=3, backoff_factor=0.5)

client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=session
)

print("Client created with custom API Key session.")
# All requests made with this client will now include the X-Api-Key header.
```

### Method 2: Providing Your Own `requests.Session` (Advanced)

The `Odyn` client will accept *any* object that is an instance of `requests.Session`. This provides maximum flexibility but comes with a major trade-off.

**Warning**: If you provide a plain `requests.Session`, you will **lose Odyn's built-in automatic retry logic**. This approach is only recommended if you have a complex, existing session object (e.g., from a library like `requests-oauthlib`) that already has its own retry and token-refresh mechanisms.

```python
import requests
from odyn import Odyn

# An existing, plain requests.Session object
# Note: This session has NO retry logic.
custom_session = requests.Session()
custom_session.headers.update({"X-Custom-Auth": "my-special-credentials"})

# The Odyn client will accept it
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=custom_session
)

print("Client created with a plain requests.Session.")
# This client will send the "X-Custom-Auth" header, but it will not
# automatically retry on 500-series errors or 429s.
```

## Session Validation

All session classes include comprehensive validation:

### Retry Validation

```python
# Valid retry values
session = OdynSession(retries=5)  # ✅ Valid

# Invalid retry values
session = OdynSession(retries=0)   # ❌ Raises InvalidRetryError
session = OdynSession(retries=-1)  # ❌ Raises InvalidRetryError
session = OdynSession(retries=3.5) # ❌ Raises InvalidRetryError
```

### Backoff Factor Validation

```python
# Valid backoff factors
session = OdynSession(backoff_factor=2.0)  # ✅ Valid
session = OdynSession(backoff_factor=1)    # ✅ Valid (converted to float)

# Invalid backoff factors
session = OdynSession(backoff_factor=0)    # ❌ Raises InvalidBackoffFactorError
session = OdynSession(backoff_factor=-1)   # ❌ Raises InvalidBackoffFactorError
```

### Status Forcelist Validation

```python
# Valid status forcelist
session = OdynSession(status_forcelist=[429, 500, 503])  # ✅ Valid

# Invalid status forcelist
session = OdynSession(status_forcelist=[500, "429"])     # ❌ Raises InvalidStatusForcelistError
session = OdynSession(status_forcelist="500,429")        # ❌ Raises InvalidStatusForcelistError
```

## Error Handling

Sessions can raise the following exceptions:

- **`InvalidRetryError`** - When retries parameter is invalid
- **`InvalidBackoffFactorError`** - When backoff_factor parameter is invalid
- **`InvalidStatusForcelistError`** - When status_forcelist parameter is invalid

### Example Error Handling

```python
from odyn import BearerAuthSession
from odyn import InvalidRetryError, InvalidBackoffFactorError

try:
    session = BearerAuthSession(
        token="your-token",
        retries=5,
        backoff_factor=2.0
    )
except (InvalidRetryError, InvalidBackoffFactorError) as e:
    print(f"Session configuration error: {e}")
    # Fall back to default settings
    session = BearerAuthSession("your-token")
```

## Best Practices

### 1. Choose the Right Authentication Method

- **Bearer Token** (recommended) - More secure, supports token refresh
- **Basic Auth** - Simpler but less secure, credentials in headers

### 2. Configure Retry Settings Appropriately

```python
# For stable networks
session = BearerAuthSession(
    token="your-token",
    retries=3,
    backoff_factor=2.0
)

# For unreliable networks
session = BearerAuthSession(
    token="your-token",
    retries=10,
    backoff_factor=0.5
)
```

### 3. Handle Token Expiration

```python
from odyn import BearerAuthSession
import requests

def create_session_with_token_refresh():
    """Create session with token refresh logic."""

    def refresh_token():
        # Implement your token refresh logic here
        return "new-access-token"

    session = BearerAuthSession("initial-token")

    # Add token refresh on 401 errors
    def auth_handler(response, *args, **kwargs):
        if response.status_code == 401:
            new_token = refresh_token()
            session.headers["Authorization"] = f"Bearer {new_token}"
            # Retry the request
            return session.request(*args, **kwargs)
        return response

    session.hooks["response"].append(auth_handler)
    return session
```

### 4. Reuse Sessions

```python
# Create session once
session = BearerAuthSession("your-token")

# Reuse for multiple clients or requests
client1 = Odyn(base_url="https://api1.example.com/", session=session)
client2 = Odyn(base_url="https://api2.example.com/", session=session)
```

### 5. Monitor Retry Behavior

```python
from loguru import logger

# Create a logger to monitor retry behavior
custom_logger = logger.bind(component="odyn-session")

session = BearerAuthSession(
    token="your-token",
    retries=5
)

# The session will log retry attempts automatically
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session,
    logger=custom_logger
)
```

## Related Documentation

- [Odyn Client API](odyn.md) - Complete client reference
- [Exception Handling](exceptions.md) - Understanding session-related errors
- [Configuration](../advanced/configuration.md) - Advanced retry and timeout settings
- [Logging](../advanced/logging.md) - Monitoring session behavior
