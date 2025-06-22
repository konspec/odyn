# Odyn Client API Reference

The `Odyn` class is the main client for interacting with Microsoft Dynamics 365 Business Central OData V4 API. It provides a robust, typed interface with automatic pagination, retry logic, and comprehensive error handling.

## Class Overview

```python
class Odyn:
    """Python adapter for MS Dynamics 365 Business Central OData V4 API."""

    DEFAULT_TIMEOUT: ClassVar[TimeoutType] = (60, 60)
    logger: Logger
    base_url: str
    session: requests.Session
    timeout: TimeoutType
```

## Constructor

### `__init__(base_url, session, logger=None, timeout=DEFAULT_TIMEOUT)`

Initializes the Odyn client with the specified configuration.

#### Parameters

- **`base_url`** (`str`) - The base URL of the OData service. Will be sanitized to end with a "/".
- **`session`** (`requests.Session`) - The requests session to use for HTTP requests. Any authentication should be handled by the session.
- **`logger`** (`Logger | None`, optional) - The loguru logger to use. If `None`, a default loguru logger is used.
- **`timeout`** (`TimeoutType`, optional) - The timeout configuration as `(connect_timeout, read_timeout)`. Defaults to `(60, 60)`.

#### Raises

- **`InvalidURLError`** - If the URL is invalid, empty, or has an invalid scheme.
- **`InvalidSessionError`** - If the session is not a valid `requests.Session` object.
- **`InvalidLoggerError`** - If the logger is not a valid loguru `Logger` object.
- **`InvalidTimeoutError`** - If the timeout is not a valid tuple of two positive numbers.

#### Example

```python
from odyn import Odyn, BearerAuthSession

# Basic initialization
session = BearerAuthSession("your-token")
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session
)

# With custom timeout and logger
from loguru import logger

custom_logger = logger.bind(component="odyn-client")
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session,
    logger=custom_logger,
    timeout=(30, 120)  # 30s connect, 120s read timeout
)
```

## Core Methods

### `get(endpoint, params=None, headers=None)`

Sends a GET request to the specified endpoint and automatically handles OData pagination.

#### Parameters

- **`endpoint`** (`str`) - The API endpoint to query (e.g., "customers", "items").
- **`params`** (`dict[str, Any] | None`, optional) - Query parameters for the request (OData filters, sorting, etc.).
- **`headers`** (`dict[str, str] | None`, optional) - Additional request headers.

#### Returns

- **`list[dict[str, Any]]`** - A list containing all items retrieved from all pages.

#### Raises

- **`TypeError`** - If the OData response is malformed (missing 'value' key or 'value' is not a list).
- **`requests.exceptions.HTTPError`** - For HTTP 4xx or 5xx status codes.
- **`requests.exceptions.RequestException`** - For network-level errors.
- **`ValueError`** - If the response is not valid JSON.

#### Example

```python
# Basic GET request
customers = client.get("customers")

# With OData query parameters
customers = client.get(
    "customers",
    params={
        "$top": 10,
        "$filter": "contains(name, 'Adventure')",
        "$orderby": "name",
        "$select": "id,name,phoneNumber"
    }
)

# With custom headers
customers = client.get(
    "customers",
    headers={"Accept": "application/json;odata.metadata=minimal"}
)
```

## Internal Methods

### `_request(url, params=None, headers=None, method="GET")`

Internal method that sends HTTP requests and handles responses.

#### Parameters

- **`url`** (`str`) - The full URL for the request.
- **`params`** (`dict[str, Any] | None`, optional) - Query parameters.
- **`headers`** (`dict[str, str] | None`, optional) - Request headers.
- **`method`** (`str`, optional) - HTTP method. Defaults to "GET".

#### Returns

- **`dict[str, Any]`** - The JSON response from the API.

#### Raises

- **`requests.exceptions.HTTPError`** - For HTTP 4xx or 5xx status codes.
- **`requests.exceptions.RequestException`** - For network-level errors.
- **`ValueError`** - If the response is not valid JSON.

### `_build_url(endpoint, params=None)`

Builds the full URL for an API request using robust URL joining.

#### Parameters

- **`endpoint`** (`str`) - The API endpoint path.
- **`params`** (`dict[str, Any] | None`, optional) - Query parameters to append to the URL.

#### Returns

- **`str`** - The fully constructed URL string.

#### Example

```python
# Internal usage - builds URLs like:
# https://api.example.com/customers?$top=10&$filter=contains(name,'Adventure')
url = client._build_url("customers", {"$top": 10, "$filter": "contains(name,'Adventure')"})
```

## Validation Methods

### `_validate_url(url)`

Validates and sanitizes the base URL.

#### Parameters

- **`url`** (`str`) - The base URL string to validate.

#### Returns

- **`str`** - The sanitized URL, guaranteed to end with a "/".

#### Raises

- **`InvalidURLError`** - If the URL is empty, has an invalid scheme, or is missing a domain.

### `_validate_session(session)`

Validates that the session is a `requests.Session` object.

#### Parameters

- **`session`** (`requests.Session`) - The session object to validate.

#### Returns

- **`requests.Session`** - The validated session object.

#### Raises

- **`InvalidSessionError`** - If the provided object is not a `requests.Session`.

### `_validate_logger(logger)`

Validates the logger, returning the default logger if `None` is provided.

#### Parameters

- **`logger`** (`Logger | None`) - The logger object to validate.

#### Returns

- **`Logger`** - A valid Logger instance.

#### Raises

- **`InvalidLoggerError`** - If the provided object is not a loguru `Logger`.

### `_validate_timeout(timeout)`

Validates that the timeout is a tuple of two positive numbers.

#### Parameters

- **`timeout`** (`TimeoutType`) - The timeout tuple to validate.

#### Returns

- **`TimeoutType`** - The validated timeout tuple.

#### Raises

- **`InvalidTimeoutError`** - If timeout is not a tuple of two positive numbers.

## Attributes

### `DEFAULT_TIMEOUT`

Class variable defining the default timeout configuration.

```python
DEFAULT_TIMEOUT: ClassVar[TimeoutType] = (60, 60)  # (connect_timeout, read_timeout)
```

### `base_url`

The sanitized base URL of the OData service.

```python
base_url: str  # Always ends with "/"
```

### `session`

The `requests.Session` object used for making HTTP requests.

```python
session: requests.Session
```

### `timeout`

The timeout configuration for requests.

```python
timeout: TimeoutType  # (connect_timeout, read_timeout)
```

### `logger`

The logger instance used by the client.

```python
logger: Logger
```

## Special Methods

### `__repr__()`

Returns a string representation of the client.

#### Returns

- **`str`** - A string representation of the Odyn client instance.

#### Example

```python
client = Odyn(base_url="https://api.example.com/", session=session)
print(client)  # Output: Odyn(base_url='https://api.example.com/', timeout=(60, 60))
```

## Type Definitions

### `TimeoutType`

```python
TimeoutType = tuple[int, int] | tuple[float, float]
```

A type alias for timeout configuration, representing `(connect_timeout, read_timeout)`.

## Complete Example

Here's a comprehensive example showing all major features:

```python
from odyn import Odyn, BearerAuthSession
from loguru import logger

def create_odyn_client():
    """Create and configure an Odyn client with custom settings."""

    # Create a custom logger
    custom_logger = logger.bind(component="business-central-client")

    # Create an authenticated session
    session = BearerAuthSession("your-access-token")

    # Initialize the client with custom configuration
    client = Odyn(
        base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
        session=session,
        logger=custom_logger,
        timeout=(30, 120)  # 30s connect, 2min read timeout
    )

    return client

def fetch_business_data(client):
    """Fetch various types of business data with different query parameters."""

    # Fetch customers with filtering and sorting
    customers = client.get(
        "customers",
        params={
            "$top": 50,
            "$filter": "contains(name, 'Adventure')",
            "$orderby": "name",
            "$select": "id,name,phoneNumber,email"
        }
    )

    # Fetch items with pagination (handled automatically)
    items = client.get(
        "items",
        params={
            "$filter": "blocked eq false",
            "$orderby": "description"
        }
    )

    # Fetch vendors with custom headers
    vendors = client.get(
        "vendors",
        headers={
            "Accept": "application/json;odata.metadata=minimal",
            "Prefer": "odata.maxpagesize=100"
        }
    )

    return {
        "customers": customers,
        "items": items,
        "vendors": vendors
    }

# Usage
if __name__ == "__main__":
    try:
        client = create_odyn_client()
        data = fetch_business_data(client)

        print(f"Retrieved {len(data['customers'])} customers")
        print(f"Retrieved {len(data['items'])} items")
        print(f"Retrieved {len(data['vendors'])} vendors")

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
```

## Best Practices

1. **Use Type Hints**: Leverage the comprehensive type annotations for better IDE support and code safety.

2. **Handle Exceptions**: Always wrap API calls in try-catch blocks to handle potential errors gracefully.

3. **Use Query Parameters**: Utilize OData query parameters to filter and limit data on the server side.

4. **Customize Logging**: Use custom loggers to integrate with your application's logging system.

5. **Set Appropriate Timeouts**: Adjust timeout values based on your network conditions and data volume.

6. **Reuse Sessions**: Create session objects once and reuse them for multiple requests to improve performance.

For more advanced configuration options, see [Configuration](advanced/configuration.md) and [Logging](advanced/logging.md).
