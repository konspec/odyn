# Odyn Client API Reference

This document provides a detailed API reference for the `odyn.Odyn` client, which is the primary interface for interacting with the Microsoft Dynamics 365 Business Central API.

## `Odyn` Class

The `Odyn` client orchestrates API requests, manages endpoint URLs, and handles the automatic pagination of results. It relies on a [Session object](./sessions.md) for authentication and retry logic.

---

## Initialization

An `Odyn` client is initialized with the following constructor:

```python
class Odyn:
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        logger: loguru.Logger | None = None,
        timeout: tuple[int, int] = (60, 60),
    ) -> None:
```

### **Parameters**

#### `base_url`
-   **Type**: `str`
-   **Description**: The full base URL of your Business Central OData V4 API endpoint. This URL must be well-formed and include the schema (`https://`). The client will sanitize the URL to ensure it ends with a `/`.
-   **Validation**: The URL must be a valid string, start with `http` or `https` and contain a network location (domain).
-   **Raises**: `InvalidURLError` if the validation fails.

#### `session`
-   **Type**: `requests.Session`
-   **Description**: An instance of a `requests.Session` (or a subclass like `OdynSession`) that will be used to perform all HTTP requests. This object is responsible for handling authentication (e.g., adding `Authorization` headers) and retry logic.
-   **See Also**: [Authentication and Session Management](./sessions.md) for details on creating and configuring sessions.
-   **Validation**: Must be a valid `requests.Session` instance.
-   **Raises**: `InvalidSessionError` if the object is not a `requests.Session`.

#### `timeout`
-   **Type**: `tuple[int, int]`
-   **Default**: `(60, 60)`
-   **Description**: A tuple specifying the `(connect_timeout, read_timeout)` in seconds for all requests made by the client.
    -   `connect_timeout`: The time to wait for a connection to be established.
    -   `read_timeout`: The time to wait for the server to send a response after the connection is established.
-   **Validation**: Must be a tuple containing two positive `int` or `float` values.
-   **Raises**: `InvalidTimeoutError` if the validation fails.

#### `logger`
-   **Type**: `loguru.Logger | None`
-   **Default**: A default, pre-configured `loguru` logger instance.
-   **Description**: A `loguru` logger instance for structured, context-rich logging. If you provide your own, the client will use it for all its logging output. If `None`, Odyn's default logger is used.
-   **Validation**: Must be a valid `loguru.Logger` instance.
-   **Raises**: `InvalidLoggerError` if a non-logger object is provided.

### **Initialization Example**

```python
from odyn import Odyn, BearerAuthSession
from loguru import logger

# A session to handle authentication and retries
session = BearerAuthSession(
    token="your-secret-token",
    retries=3
)

# A custom logger to capture context
custom_logger = logger.bind(service="BusinessCentralClient")

# Initialize the client with advanced configuration
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=session,
    timeout=(10, 45),  # 10s connect, 45s read
    logger=custom_logger
)
```

---

## Public Attributes

Once initialized, you can inspect the following public attributes on a client instance:

-   `base_url` (`str`): The sanitized base URL used by the client.
-   `session` (`requests.Session`): The session object used for requests.
-   `timeout` (`tuple[int, int]`): The timeout configuration.
-   `logger` (`loguru.Logger`): The logger instance.

---

## Methods

### `get()`

This is the primary method for retrieving data from Business Central. It sends a `GET` request and automatically handles OData's server-side pagination.

```python
def get(
    self,
    endpoint: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
```

#### **Parameters**

-   `endpoint` (`str`): The API endpoint path to query (e.g., `"customers"`, `"salesInvoices"`). This is appended to the `base_url`.
-   `params` (`dict | None`): A dictionary of OData query parameters (e.g., `"$filter"`, `"$select"`). These are automatically URL-encoded.
-   `headers` (`dict | None`): Any additional HTTP headers to include in the request, which will be merged with the headers from the session object.

#### **Returns**

-   `list[dict[str, Any]]`: A list containing all records retrieved from the API. If the API response spans multiple pages, this method will fetch all pages and concatenate the results into a single list before returning.

#### **How Pagination Works**

The `get` method inspects the API response for an `@odata.nextLink` key. If this key is present, it indicates more data is available. The client automatically follows this link to fetch the next page of results and continues doing so until all pages have been retrieved. This entire process is transparent to the caller.

#### **Raises**

-   `requests.exceptions.HTTPError`: For any HTTP 4xx (client) or 5xx (server) error responses that are not handled by the session's retry mechanism.
-   `requests.exceptions.RequestException`: For fundamental network errors (e.g., connection timeout, DNS failure).
-   `ValueError`: If the API returns a response that is not valid JSON.
-   `TypeError`: If the API returns a valid JSON response that is not in the expected OData format (e.g., it is missing the `value` key, or the value is not a list).

### `get()` Examples

**1. Simple GET Request**
This fetches all records from the `items` endpoint.

```python
# Fetches all items across all pages
all_items = client.get("items")
print(f"Retrieved {len(all_items)} items.")
```

**2. GET Request with OData Parameters**
This fetches the top 10 vendors, filtered by a specific location code, and selects only three fields to reduce payload size.

```python
filtered_vendors = client.get(
    "vendors",
    params={
        "$top": 10,
        "$filter": "locationCode eq 'EAST'",
        "$select": "number,displayName,blocked"
    }
)
```

**3. GET Request with Custom Headers**
You can provide additional headers if a specific API endpoint requires them.

```python
# The odata.metadata parameter can control the verbosity of the response
response = client.get(
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

For more advanced configuration options, see [Configuration](../advanced/configuration.md) and [Logging](../advanced/logging.md).
