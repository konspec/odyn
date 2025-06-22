# Advanced Configuration

This guide covers advanced configuration options for Odyn, including timeout settings, retry logic, backoff strategies, and parameter validation.

## Timeout Configuration

Odyn uses a tuple-based timeout configuration that separates connection and read timeouts.

### Timeout Format

```python
TimeoutType = tuple[int, int] | tuple[float, float]
timeout = (connect_timeout, read_timeout)
```

### Default Timeout

```python
DEFAULT_TIMEOUT = (60, 60)  # 60 seconds for both connect and read
```

### Timeout Examples

```python
from odyn import Odyn, BearerAuthSession

# Quick connections, long reads (good for large datasets)
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    timeout=(10, 300)  # 10s connect, 5min read
)

# Conservative timeouts (good for slow networks)
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    timeout=(120, 180)  # 2min connect, 3min read
)

# Aggressive timeouts (good for fast networks)
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    timeout=(5, 30)  # 5s connect, 30s read
)
```

### Timeout Recommendations

| Use Case | Connect Timeout | Read Timeout | Rationale |
|----------|----------------|--------------|-----------|
| **Development** | 10s | 60s | Fast feedback, moderate data |
| **Production (stable)** | 30s | 120s | Reliable networks, large datasets |
| **Production (unreliable)** | 60s | 300s | Slow networks, retry scenarios |
| **Batch processing** | 30s | 600s | Large data transfers |
| **Real-time applications** | 5s | 30s | Quick responses needed |

## Retry Logic and Exponential Backoff

Odyn sessions include built-in retry logic with exponential backoff to handle transient failures.

### Retry Configuration

```python
from odyn import BearerAuthSession

# Default retry settings
session = BearerAuthSession("token")  # 5 retries, 2.0 backoff factor

# Custom retry settings
session = BearerAuthSession(
    token="token",
    retries=10,                    # Total retry attempts
    backoff_factor=1.5,            # Backoff multiplier
    status_forcelist=[429, 500, 502, 503, 504]  # Status codes to retry
)
```

### Backoff Calculation

The retry delay is calculated using exponential backoff:

```
delay = backoff_factor * (2 ** (retry_number - 1))
```

### Backoff Timing Examples

| Backoff Factor | 1st Retry | 2nd Retry | 3rd Retry | 4th Retry | 5th Retry |
|----------------|-----------|-----------|-----------|-----------|-----------|
| **0.5** | 0.5s | 1.0s | 2.0s | 4.0s | 8.0s |
| **1.0** | 1.0s | 2.0s | 4.0s | 8.0s | 16.0s |
| **2.0** (default) | 2.0s | 4.0s | 8.0s | 16.0s | 32.0s |
| **3.0** | 3.0s | 6.0s | 12.0s | 24.0s | 48.0s |

### Status Code Forcelist

The `status_forcelist` determines which HTTP status codes trigger retries:

```python
# Default status codes that trigger retries
DEFAULT_STATUS_FORCELIST = [500, 502, 503, 504, 429]

# Common status codes and their meanings
STATUS_CODES = {
    408: "Request Timeout",
    429: "Too Many Requests (Rate Limited)",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    520: "Unknown Error (Cloudflare)",
    521: "Web Server Down (Cloudflare)",
    522: "Connection Timed Out (Cloudflare)",
    523: "Origin Unreachable (Cloudflare)",
    524: "A Timeout Occurred (Cloudflare)"
}
```

### Retry Strategy Examples

```python
# Conservative retry strategy (many retries, slow backoff)
session = BearerAuthSession(
    token="token",
    retries=15,
    backoff_factor=3.0,
    status_forcelist=[408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524]
)

# Aggressive retry strategy (few retries, fast backoff)
session = BearerAuthSession(
    token="token",
    retries=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504]
)

# Rate limit focused (retry on 429, few other retries)
session = BearerAuthSession(
    token="token",
    retries=5,
    backoff_factor=1.0,
    status_forcelist=[429]  # Only retry on rate limits
)
```

## Parameter Validation Strategy

Odyn implements comprehensive parameter validation to catch configuration errors early.

### Validation Flow

1. **Logger Validation** - Validated first (needed for other validations)
2. **URL Validation** - Sanitizes and validates base URL
3. **Session Validation** - Ensures proper session object
4. **Timeout Validation** - Validates timeout tuple format

### Validation Rules

#### URL Validation

```python
def validate_url(url: str) -> str:
    """URL validation rules."""

    # Must be a string
    if not isinstance(url, str):
        raise InvalidURLError(f"URL must be a string, got {type(url).__name__}")

    # Must not be empty
    if not url.strip():
        raise InvalidURLError("URL cannot be empty")

    # Must have valid scheme
    parsed = urlparse(url)
    if not parsed.scheme or parsed.scheme not in ["http", "https"]:
        raise InvalidURLError(f"URL must have valid scheme (http or https), got {url}")

    # Must have domain
    if not parsed.netloc:
        raise InvalidURLError(f"URL must contain valid domain, got {url}")

    # Sanitize (ensure trailing slash)
    sanitized = url.strip()
    if not sanitized.endswith("/"):
        sanitized += "/"

    return sanitized
```

#### Timeout Validation

```python
def validate_timeout(timeout: TimeoutType) -> TimeoutType:
    """Timeout validation rules."""

    # Must be a tuple
    if not isinstance(timeout, tuple):
        raise InvalidTimeoutError(f"Timeout must be a tuple, got {type(timeout).__name__}")

    # Must have exactly 2 elements
    if len(timeout) != 2:
        raise InvalidTimeoutError(f"Timeout must be a tuple of length 2, got length {len(timeout)}")

    # Both elements must be positive numbers
    for i, value in enumerate(timeout):
        if not isinstance(value, (int, float)):
            raise InvalidTimeoutError(f"Timeout values must be int or float, but value at index {i} is {type(value).__name__}")
        if value <= 0:
            raise InvalidTimeoutError(f"Timeout values must be greater than 0, got {value}")

    return timeout
```

#### Session Validation

```python
def validate_session(session: requests.Session) -> requests.Session:
    """Session validation rules."""

    if not isinstance(session, requests.Session):
        raise InvalidSessionError(f"session must be a Session, got {type(session).__name__}")

    return session
```

## Configuration Patterns

### Environment-Based Configuration

```python
import os
from odyn import Odyn, BearerAuthSession

def create_client_from_env():
    """Create client using environment variables."""

    # Get configuration from environment
    base_url = os.getenv("BC_BASE_URL")
    token = os.getenv("BC_ACCESS_TOKEN")
    connect_timeout = int(os.getenv("BC_CONNECT_TIMEOUT", "30"))
    read_timeout = int(os.getenv("BC_READ_TIMEOUT", "120"))
    retries = int(os.getenv("BC_RETRIES", "5"))
    backoff_factor = float(os.getenv("BC_BACKOFF_FACTOR", "2.0"))

    # Create session
    session = BearerAuthSession(
        token=token,
        retries=retries,
        backoff_factor=backoff_factor
    )

    # Create client
    client = Odyn(
        base_url=base_url,
        session=session,
        timeout=(connect_timeout, read_timeout)
    )

    return client
```

### Configuration File Pattern

```python
import yaml
from odyn import Odyn, BearerAuthSession

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_client_from_config(config: dict):
    """Create client from configuration dictionary."""

    # Extract configuration
    odyn_config = config.get("odyn", {})
    session_config = odyn_config.get("session", {})

    # Create session
    session = BearerAuthSession(
        token=session_config["token"],
        retries=session_config.get("retries", 5),
        backoff_factor=session_config.get("backoff_factor", 2.0),
        status_forcelist=session_config.get("status_forcelist", [500, 502, 503, 504, 429])
    )

    # Create client
    client = Odyn(
        base_url=odyn_config["base_url"],
        session=session,
        timeout=tuple(odyn_config.get("timeout", [60, 60]))
    )

    return client

# Example configuration file (config.yaml):
"""
odyn:
  base_url: "https://your-tenant.businesscentral.dynamics.com/api/v2.0/"
  timeout: [30, 120]
  session:
    token: "your-access-token"
    retries: 5
    backoff_factor: 2.0
    status_forcelist: [429, 500, 502, 503, 504]
"""
```

### Factory Pattern

```python
from typing import Optional
from odyn import Odyn, BearerAuthSession, BasicAuthSession

class OdynClientFactory:
    """Factory for creating Odyn clients with different configurations."""

    @staticmethod
    def create_bearer_client(
        base_url: str,
        token: str,
        timeout: tuple[int, int] = (60, 60),
        retries: int = 5,
        backoff_factor: float = 2.0
    ) -> Odyn:
        """Create client with Bearer token authentication."""

        session = BearerAuthSession(
            token=token,
            retries=retries,
            backoff_factor=backoff_factor
        )

        return Odyn(
            base_url=base_url,
            session=session,
            timeout=timeout
        )

    @staticmethod
    def create_basic_auth_client(
        base_url: str,
        username: str,
        password: str,
        timeout: tuple[int, int] = (60, 60),
        retries: int = 5,
        backoff_factor: float = 2.0
    ) -> Odyn:
        """Create client with Basic authentication."""

        session = BasicAuthSession(
            username=username,
            password=password,
            retries=retries,
            backoff_factor=backoff_factor
        )

        return Odyn(
            base_url=base_url,
            session=session,
            timeout=timeout
        )

    @staticmethod
    def create_development_client(base_url: str, token: str) -> Odyn:
        """Create client optimized for development."""
        return OdynClientFactory.create_bearer_client(
            base_url=base_url,
            token=token,
            timeout=(10, 60),  # Fast timeouts for development
            retries=3,         # Fewer retries
            backoff_factor=1.0 # Faster backoff
        )

    @staticmethod
    def create_production_client(base_url: str, token: str) -> Odyn:
        """Create client optimized for production."""
        return OdynClientFactory.create_bearer_client(
            base_url=base_url,
            token=token,
            timeout=(30, 180), # Conservative timeouts
            retries=10,        # More retries
            backoff_factor=2.0 # Standard backoff
        )

# Usage
factory = OdynClientFactory()

# Development client
dev_client = factory.create_development_client(
    base_url="https://dev-tenant.businesscentral.dynamics.com/api/v2.0/",
    token="dev-token"
)

# Production client
prod_client = factory.create_production_client(
    base_url="https://prod-tenant.businesscentral.dynamics.com/api/v2.0/",
    token="prod-token"
)
```

## Performance Optimization

### Connection Pooling

Odyn sessions automatically use connection pooling through `requests.Session`:

```python
# Reuse session for multiple clients (recommended)
session = BearerAuthSession("token")

client1 = Odyn(base_url="https://api1.example.com/", session=session)
client2 = Odyn(base_url="https://api2.example.com/", session=session)
client3 = Odyn(base_url="https://api3.example.com/", session=session)
```

### Timeout Optimization

```python
# For small, frequent requests
fast_client = Odyn(
    base_url="https://api.example.com/",
    session=session,
    timeout=(5, 30)  # Quick timeouts
)

# For large data transfers
bulk_client = Odyn(
    base_url="https://api.example.com/",
    session=session,
    timeout=(30, 600)  # Long read timeout for large datasets
)
```

### Retry Optimization

```python
# For stable networks
stable_session = BearerAuthSession(
    token="token",
    retries=3,           # Fewer retries
    backoff_factor=2.0   # Standard backoff
)

# For unreliable networks
unreliable_session = BearerAuthSession(
    token="token",
    retries=15,          # More retries
    backoff_factor=0.5   # Faster backoff
)
```

## Monitoring and Debugging

### Enable Debug Logging

```python
from loguru import logger

# Configure detailed logging
logger.add("odyn_debug.log", level="DEBUG", rotation="1 day")

# Create client with debug logger
client = Odyn(
    base_url="https://api.example.com/",
    session=session,
    logger=logger.bind(component="odyn-debug")
)
```

### Monitor Retry Behavior

```python
from loguru import logger

def log_retry_attempts(response, *args, **kwargs):
    """Log retry attempts for monitoring."""
    if hasattr(response, 'retry') and response.retry:
        logger.warning(
            f"Request retried {response.retry.total} times",
            url=response.url,
            status_code=response.status_code
        )

# Add retry monitoring to session
session = BearerAuthSession("token")
session.hooks["response"].append(log_retry_attempts)
```

## Related Documentation

- [Odyn Client API](../usage/odyn.md) - Core client configuration
- [Authentication Sessions](../usage/sessions.md) - Session configuration
- [Exception Handling](../usage/exceptions.md) - Configuration validation errors
- [Logging](logging.md) - Advanced logging configuration
