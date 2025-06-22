# Exception Handling

Odyn provides comprehensive exception handling with custom exception types for different error scenarios. All exceptions inherit from the base `OdynError` class, making them easy to catch and handle appropriately.

## Exception Hierarchy

```
OdynError (base exception)
├── InvalidURLError
├── InvalidSessionError
├── InvalidLoggerError
├── InvalidTimeoutError
├── InvalidRetryError
├── InvalidBackoffFactorError
└── InvalidStatusForcelistError
```

## Exception Reference Table

| Exception | Raised When | Suggested Fix |
|-----------|-------------|---------------|
| `InvalidURLError` | URL is empty, invalid, or has wrong scheme | Provide a valid HTTPS URL |
| `InvalidSessionError` | Session is not a `requests.Session` object | Use proper session classes |
| `InvalidLoggerError` | Logger is not a loguru `Logger` object | Use loguru logger or pass `None` |
| `InvalidTimeoutError` | Timeout is not a tuple of two positive numbers | Use `(connect_timeout, read_timeout)` format |
| `InvalidRetryError` | Retries parameter is not a positive integer | Use positive integer values |
| `InvalidBackoffFactorError` | Backoff factor is not a positive number | Use positive float/int values |
| `InvalidStatusForcelistError` | Status forcelist is not a list of integers | Use list of HTTP status codes |

## Detailed Exception Descriptions

### OdynError

Base exception class for all Odyn-specific exceptions.

```python
class OdynError(Exception):
    """Base exception for all Odyn exceptions."""
```

### InvalidURLError

Raised when an invalid URL is provided to the Odyn client.

**Common Causes:**
- Empty or whitespace-only URL
- Missing HTTP/HTTPS scheme
- Invalid URL format
- Missing domain

**Example:**
```python
from odyn import Odyn, InvalidURLError
import requests

try:
    client = Odyn(
        base_url="",  # Empty URL
        session=requests.Session()
    )
except InvalidURLError as e:
    print(f"URL Error: {e}")  # "URL cannot be empty"

try:
    client = Odyn(
        base_url="ftp://invalid.scheme",  # Invalid scheme
        session=requests.Session()
    )
except InvalidURLError as e:
    print(f"URL Error: {e}")  # "URL must have a valid scheme (http or https)"
```

**Fix:**
```python
# ✅ Correct
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=requests.Session()
)
```

### InvalidSessionError

Raised when an invalid session object is provided.

**Common Causes:**
- Passing `None` instead of a session
- Passing a string or other object instead of `requests.Session`
- Using an uninitialized session object

**Example:**
```python
from odyn import Odyn, InvalidSessionError

try:
    client = Odyn(
        base_url="https://api.example.com/",
        session=None  # Invalid session
    )
except InvalidSessionError as e:
    print(f"Session Error: {e}")  # "session must be a Session, got NoneType"

try:
    client = Odyn(
        base_url="https://api.example.com/",
        session="not a session"  # Invalid session
    )
except InvalidSessionError as e:
    print(f"Session Error: {e}")  # "session must be a Session, got str"
```

**Fix:**
```python
from odyn import BearerAuthSession

# ✅ Correct
session = BearerAuthSession("your-token")
client = Odyn(
    base_url="https://api.example.com/",
    session=session
)
```

### InvalidLoggerError

Raised when an invalid logger object is provided.

**Common Causes:**
- Passing a non-loguru logger object
- Passing an incompatible logging library

**Example:**
```python
from odyn import Odyn, InvalidLoggerError
import logging

try:
    # Using standard logging instead of loguru
    std_logger = logging.getLogger("my_app")
    client = Odyn(
        base_url="https://api.example.com/",
        session=requests.Session(),
        logger=std_logger  # Invalid logger type
    )
except InvalidLoggerError as e:
    print(f"Logger Error: {e}")  # "logger must be a Logger, got Logger"
```

**Fix:**
```python
from loguru import logger

# ✅ Correct
custom_logger = logger.bind(component="odyn-client")
client = Odyn(
    base_url="https://api.example.com/",
    session=session,
    logger=custom_logger
)

# Or use default logger
client = Odyn(
    base_url="https://api.example.com/",
    session=session,
    logger=None  # Uses default loguru logger
)
```

### InvalidTimeoutError

Raised when an invalid timeout configuration is provided.

**Common Causes:**
- Passing a single number instead of a tuple
- Using negative or zero values
- Using wrong data types

**Example:**
```python
from odyn import Odyn, InvalidTimeoutError

try:
    client = Odyn(
        base_url="https://api.example.com/",
        session=requests.Session(),
        timeout=30  # Single number instead of tuple
    )
except InvalidTimeoutError as e:
    print(f"Timeout Error: {e}")  # "Timeout must be a tuple, got int"

try:
    client = Odyn(
        base_url="https://api.example.com/",
        session=requests.Session(),
        timeout=(30,)  # Single-element tuple
    )
except InvalidTimeoutError as e:
    print(f"Timeout Error: {e}")  # "Timeout must be a tuple of length 2, got length 1"

try:
    client = Odyn(
        base_url="https://api.example.com/",
        session=requests.Session(),
        timeout=(-10, 30)  # Negative value
    )
except InvalidTimeoutError as e:
    print(f"Timeout Error: {e}")  # "Timeout values must be greater than 0, got -10"
```

**Fix:**
```python
# ✅ Correct
client = Odyn(
    base_url="https://api.example.com/",
    session=requests.Session(),
    timeout=(30, 60)  # (connect_timeout, read_timeout)
)
```

### InvalidRetryError

Raised when an invalid retry configuration is provided to session classes.

**Common Causes:**
- Using zero or negative retry values
- Using non-integer values

**Example:**
```python
from odyn import OdynSession, InvalidRetryError

try:
    session = OdynSession(retries=0)  # Zero retries
except InvalidRetryError as e:
    print(f"Retry Error: {e}")  # "Retries must be a positive integer."

try:
    session = OdynSession(retries=-1)  # Negative retries
except InvalidRetryError as e:
    print(f"Retry Error: {e}")  # "Retries must be a positive integer."
```

**Fix:**
```python
# ✅ Correct
session = OdynSession(retries=5)  # Positive integer
```

### InvalidBackoffFactorError

Raised when an invalid backoff factor is provided to session classes.

**Common Causes:**
- Using zero or negative backoff factors
- Using non-numeric values

**Example:**
```python
from odyn import OdynSession, InvalidBackoffFactorError

try:
    session = OdynSession(backoff_factor=0)  # Zero backoff
except InvalidBackoffFactorError as e:
    print(f"Backoff Error: {e}")  # "Backoff factor must be a positive number."

try:
    session = OdynSession(backoff_factor=-1.5)  # Negative backoff
except InvalidBackoffFactorError as e:
    print(f"Backoff Error: {e}")  # "Backoff factor must be a positive number."
```

**Fix:**
```python
# ✅ Correct
session = OdynSession(backoff_factor=2.0)  # Positive number
```

### InvalidStatusForcelistError

Raised when an invalid status forcelist is provided to session classes.

**Common Causes:**
- Using non-list values
- Including non-integer values in the list

**Example:**
```python
from odyn import OdynSession, InvalidStatusForcelistError

try:
    session = OdynSession(status_forcelist=[500, "429"])  # String in list
except InvalidStatusForcelistError as e:
    print(f"Status Forcelist Error: {e}")  # "Status forcelist must be a list of integers."

try:
    session = OdynSession(status_forcelist="500,429")  # String instead of list
except InvalidStatusForcelistError as e:
    print(f"Status Forcelist Error: {e}")  # "Status forcelist must be a list of integers."
```

**Fix:**
```python
# ✅ Correct
session = OdynSession(status_forcelist=[429, 500, 502, 503, 504])
```

## Comprehensive Error Handling

Here's a complete example showing how to handle all Odyn exceptions:

```python
from odyn import (
    Odyn, BearerAuthSession,
    InvalidURLError, InvalidSessionError, InvalidLoggerError, InvalidTimeoutError,
    InvalidRetryError, InvalidBackoffFactorError, InvalidStatusForcelistError
)
import requests
from loguru import logger

def create_odyn_client_safely():
    """Create an Odyn client with comprehensive error handling."""

    try:
        # Create session with error handling
        try:
            session = BearerAuthSession(
                token="your-access-token",
                retries=5,
                backoff_factor=2.0,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        except (InvalidRetryError, InvalidBackoffFactorError, InvalidStatusForcelistError) as e:
            logger.error(f"Session configuration error: {e}")
            # Fall back to default settings
            session = BearerAuthSession("your-access-token")

        # Create client with error handling
        try:
            client = Odyn(
                base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
                session=session,
                logger=logger.bind(component="odyn-client"),
                timeout=(30, 120)
            )
            return client

        except InvalidURLError as e:
            logger.error(f"Invalid URL: {e}")
            raise
        except InvalidSessionError as e:
            logger.error(f"Invalid session: {e}")
            raise
        except InvalidLoggerError as e:
            logger.error(f"Invalid logger: {e}")
            # Fall back to default logger
            client = Odyn(
                base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
                session=session,
                logger=None,  # Use default logger
                timeout=(30, 120)
            )
            return client
        except InvalidTimeoutError as e:
            logger.error(f"Invalid timeout: {e}")
            # Fall back to default timeout
            client = Odyn(
                base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
                session=session,
                logger=logger.bind(component="odyn-client")
                # Use default timeout
            )
            return client

    except Exception as e:
        logger.error(f"Unexpected error creating client: {e}")
        raise

def safe_api_call(client, endpoint, params=None):
    """Make a safe API call with error handling."""

    try:
        return client.get(endpoint, params=params)

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Network Error: {e}")
        raise
    except ValueError as e:
        logger.error(f"JSON Decode Error: {e}")
        raise
    except TypeError as e:
        logger.error(f"OData Response Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        raise

# Usage
if __name__ == "__main__":
    try:
        client = create_odyn_client_safely()
        customers = safe_api_call(client, "customers")
        print(f"Retrieved {len(customers)} customers")

    except Exception as e:
        print(f"Failed to retrieve customers: {e}")
```

## Best Practices

### 1. Use Specific Exception Handling

```python
# ✅ Good - Handle specific exceptions
try:
    client = Odyn(base_url=url, session=session)
except InvalidURLError as e:
    print(f"URL problem: {e}")
except InvalidSessionError as e:
    print(f"Session problem: {e}")

# ❌ Avoid - Catching all exceptions
try:
    client = Odyn(base_url=url, session=session)
except Exception as e:
    print(f"Something went wrong: {e}")
```

### 2. Provide Meaningful Error Messages

```python
def validate_config(config):
    """Validate configuration with helpful error messages."""

    if not config.get("base_url"):
        raise InvalidURLError("base_url is required in configuration")

    if not config.get("token"):
        raise ValueError("access_token is required for authentication")

    if config.get("timeout") and not isinstance(config["timeout"], tuple):
        raise InvalidTimeoutError("timeout must be a tuple of (connect_timeout, read_timeout)")
```

### 3. Log Errors Appropriately

```python
from loguru import logger

try:
    client = Odyn(base_url=url, session=session)
except InvalidURLError as e:
    logger.error(f"Configuration error - invalid URL: {url}", error=str(e))
    # Handle gracefully or re-raise
except InvalidSessionError as e:
    logger.error("Configuration error - invalid session", error=str(e))
    # Handle gracefully or re-raise
```

### 4. Use Fallback Values

```python
def create_client_with_fallbacks(config):
    """Create client with fallback values for invalid configuration."""

    # Try custom timeout, fall back to default
    try:
        timeout = config.get("timeout", (60, 60))
        client = Odyn(base_url=config["base_url"], session=session, timeout=timeout)
    except InvalidTimeoutError:
        logger.warning("Invalid timeout configuration, using defaults")
        client = Odyn(base_url=config["base_url"], session=session)

    return client
```

## Related Documentation

- [Odyn Client API](odyn.md) - Understanding client initialization errors
- [Authentication Sessions](sessions.md) - Session-related exceptions
- [Troubleshooting](troubleshooting.md) - Common error scenarios and solutions
- [Configuration](advanced/configuration.md) - Valid configuration options
