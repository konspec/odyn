# Advanced Configuration

The `odyn` client is designed to be robust and flexible. This guide covers advanced configuration options for timeouts, retry strategies, and common setup patterns to help you tailor the client to your specific needs.

## Timeout Configuration

Odyn allows you to set separate timeouts for connecting to the server and for reading the response. This is useful for handling network conditions and long-running queries independently.

The timeout is a tuple of two numbers (integers or floats): `(connect_timeout, read_timeout)`.

- **`connect_timeout`**: The time (in seconds) to wait for a connection to the server to be established.
- **`read_timeout`**: The time (in seconds) to wait for the server to send a response after the connection is established.

By default, the timeout is `(60, 60)`.

### Timeout Examples

```python
from odyn import Odyn, BearerAuthSession

# Default timeout (60s connect, 60s read)
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("your-token")
)

# Aggressive timeout for fast networks (5s connect, 30s read)
fast_client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("your-token"),
    timeout=(5, 30)
)

# Conservative timeout for large data exports (15s connect, 5min read)
bulk_client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("your-token"),
    timeout=(15, 300)
)
```

## Retry and Backoff Strategy

The `OdynSession` and its subclasses (`BearerAuthSession`, `BasicAuthSession`) automatically retry failed requests using an exponential backoff strategy. This helps the client recover from transient network errors or temporary server issues.

### Configuring Retries

You can customize the retry behavior when creating a session instance.

```python
from odyn import Odyn, BearerAuthSession

# Customize retry attempts, backoff factor, and status codes to retry on
session = BearerAuthSession(
    token="your-token",
    retries=10,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504]
)

client = Odyn(base_url="https://api.example.com/", session=session)
```

- **`retries`**: The total number of retry attempts. Default: `5`.
- **`backoff_factor`**: A multiplier for calculating the delay between retries. The delay is `backoff_factor * (2 ** (retry_number - 1))`. Default: `2.0`.
- **`status_forcelist`**: A list of HTTP status codes that will trigger a retry. Default: `[500, 502, 503, 504, 429]`.

### Backoff Timing Examples

The table below shows the delay (in seconds) for each retry attempt based on the `backoff_factor`.

| Backoff Factor | 1st Retry | 2nd Retry | 3rd Retry | 4th Retry | 5th Retry |
|----------------|-----------|-----------|-----------|-----------|-----------|
| **0.5**        | 0.5s      | 1.0s      | 2.0s      | 4.0s      | 8.0s      |
| **1.0**        | 1.0s      | 2.0s      | 4.0s      | 8.0s      | 16.0s     |
| **2.0** (Default)| 2.0s      | 4.0s      | 8.0s      | 16.0s     | 32.0s     |

## Input Validation

To prevent common errors, `odyn` performs strict validation on its initial parameters. If validation fails, a descriptive error is raised immediately.

- **Logger**: Must be a `loguru.Logger` instance. This is validated first so it can be used in subsequent validation steps.
- **Base URL**:
    - Must be a non-empty string.
    - Must have a valid scheme (`http` or `https`).
    - Must contain a network location (domain).
    - Is automatically sanitized to ensure it ends with a `/`.
- **Session**: Must be an instance of `requests.Session`.
- **Timeout**:
    - Must be a tuple.
    - Must contain exactly two elements.
    - Both elements must be positive numbers (int or float).

## Common Configuration Patterns

Here are some common patterns for managing `odyn` client configuration in your applications.

### Environment-Based Configuration

A common practice is to configure the client using environment variables, which is ideal for containerized or cloud-native applications.

```python
import os
from odyn import Odyn, BearerAuthSession

def create_client_from_env():
    """Creates a client using settings from environment variables."""
    session = BearerAuthSession(
        token=os.environ["BC_TOKEN"],
        retries=int(os.getenv("BC_RETRIES", 5)),
        backoff_factor=float(os.getenv("BC_BACKOFF", 2.0))
    )

    client = Odyn(
        base_url=os.environ["BC_BASE_URL"],
        session=session,
        timeout=(
            int(os.getenv("BC_CONNECT_TIMEOUT", 60)),
            int(os.getenv("BC_READ_TIMEOUT", 60))
        )
    )
    return client
```

### Configuration via Factory Pattern

A factory can help create consistently configured clients for different environments (e.g., development vs. production).

```python
from odyn import Odyn, BearerAuthSession

class OdynClientFactory:
    """A factory for creating pre-configured Odyn clients."""

    @staticmethod
    def create(base_url: str, token: str, environment: str = "production") -> Odyn:
        if environment == "development":
            session = BearerAuthSession(token=token, retries=3, backoff_factor=1.0)
            timeout = (10, 60) # Fast timeouts for dev
        else: # production
            session = BearerAuthSession(token=token, retries=10, backoff_factor=2.0)
            timeout = (30, 180) # Conservative timeouts for prod

        return Odyn(base_url=base_url, session=session, timeout=timeout)

# Usage
# dev_client = OdynClientFactory.create(base_url, token, environment="development")
# prod_client = OdynClientFactory.create(base_url, token, environment="production")
```

## Monitoring Retry Attempts

Because retries are handled by the underlying `urllib3` library, they are not logged through `odyn`'s logger by default. To see these logs, you must intercept the standard `logging` library messages and redirect them to `loguru`.

This is the recommended way to monitor retry behavior and diagnose transient issues.

```python
import logging
from loguru import logger

# Configure loguru to intercept logs from the standard logging library
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# Apply the interceptor
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Now, when a request is retried, you will see a WARNING log from urllib3.
# Example: WARNING: Retrying (Retry(total=2, connect=None, read=None, ...))
```

For more details on logging, see the [Logging](logging.md) documentation.

## Related Documentation

- [Odyn Client API](../usage/odyn.md)
- [Authentication Sessions](../usage/sessions.md)
- [Logging Guide](logging.md)
- [Exception Handling](../usage/exceptions.md)
