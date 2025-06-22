# Authentication Sessions

Odyn provides flexible session management for handling authentication with Microsoft Dynamics 365 Business Central. All session classes include built-in retry logic and exponential backoff for handling transient failures.

## Session Classes Overview

Odyn offers three session classes:

- **`OdynSession`** - Base session with retry logic (no authentication)
- **`BasicAuthSession`** - Session with Basic Authentication
- **`BearerAuthSession`** - Session with Bearer Token Authentication

## OdynSession

The base session class that provides automatic retry functionality without authentication.

### Constructor

```python
OdynSession(
    retries: int = 5,
    backoff_factor: float = 2.0,
    status_forcelist: list[int] | None = None
)
```

### Parameters

- **`retries`** (`int`, optional) - Total number of retry attempts. Defaults to `5`.
- **`backoff_factor`** (`float`, optional) - Factor for calculating delay between retries. Defaults to `2.0`.
- **`status_forcelist`** (`list[int] | None`, optional) - HTTP status codes that trigger retries. Defaults to `[500, 502, 503, 504, 429]`.

### Default Retry Configuration

```python
DEFAULT_STATUS_FORCELIST = [500, 502, 503, 504, 429]
```

### Example

```python
from odyn import OdynSession

# Basic session with default retry settings
session = OdynSession()

# Custom retry configuration
session = OdynSession(
    retries=3,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 503]
)
```

### Retry Logic

The session uses exponential backoff with the formula:
```
delay = backoff_factor * (2 ** (retry_number - 1))
```

**Example backoff timing with default settings:**
- 1st retry: 2.0 seconds
- 2nd retry: 4.0 seconds
- 3rd retry: 8.0 seconds
- 4th retry: 16.0 seconds
- 5th retry: 32.0 seconds

## BasicAuthSession

A session that uses Basic Authentication with username and password.

### Constructor

```python
BasicAuthSession(
    username: str,
    password: str,
    **kwargs: Any
)
```

### Parameters

- **`username`** (`str`) - The username for Basic Authentication.
- **`password`** (`str`) - The password for Basic Authentication.
- **`**kwargs`** - Additional keyword arguments passed to `OdynSession` (retries, backoff_factor, status_forcelist).

### Security Notice

⚠️ **Warning**: Basic Authentication sends credentials in base64-encoded format. For production use, prefer Bearer Token authentication when possible.

### Example

```python
from odyn import BasicAuthSession

# Basic authentication with default retry settings
session = BasicAuthSession("your-username", "your-password")

# With custom retry configuration
session = BasicAuthSession(
    username="your-username",
    password="your-password",
    retries=10,
    backoff_factor=0.5,
    status_forcelist=[429, 500]
)
```

## BearerAuthSession

A session that uses Bearer Token authentication (recommended for production).

### Constructor

```python
BearerAuthSession(
    token: str,
    **kwargs: Any
)
```

### Parameters

- **`token`** (`str`) - The bearer token for authentication.
- **`**kwargs`** - Additional keyword arguments passed to `OdynSession` (retries, backoff_factor, status_forcelist).

### Example

```python
from odyn import BearerAuthSession

# Bearer token authentication with default retry settings
session = BearerAuthSession("your-access-token")

# With custom retry configuration
session = BearerAuthSession(
    token="your-access-token",
    retries=3,
    backoff_factor=1.0,
    status_forcelist=[429, 500, 502, 503, 504]
)
```

## Using Sessions with Odyn Client

### Basic Setup

```python
from odyn import Odyn, BearerAuthSession

# Create an authenticated session
session = BearerAuthSession("your-access-token")

# Initialize the client with the session
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session
)

# Make API calls
customers = client.get("customers")
```

### Advanced Configuration

```python
from odyn import Odyn, BearerAuthSession

# Create a session with aggressive retry settings for unreliable networks
session = BearerAuthSession(
    token="your-access-token",
    retries=10,
    backoff_factor=0.5,  # Faster retries
    status_forcelist=[408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524]
)

# Initialize client with custom timeout
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session,
    timeout=(30, 180)  # 30s connect, 3min read timeout
)
```

## Custom Authentication Strategies

You can create custom authentication by extending `OdynSession`:

```python
from odyn import OdynSession
import requests

class CustomAuthSession(OdynSession):
    """Custom session with API key authentication."""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.headers.update({"X-API-Key": api_key})

# Usage
session = CustomAuthSession("your-api-key", retries=5)
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session
)
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
- [Configuration](advanced/configuration.md) - Advanced retry and timeout settings
- [Logging](advanced/logging.md) - Monitoring session behavior
