# Guide to Exception Handling

Effective error handling is critical for building robust applications. This guide provides a comprehensive overview of the exceptions that Odyn can raise and the best practices for handling them.

## Two Categories of Exceptions

It is helpful to think of errors in two main categories:

1.  **Configuration Errors (`OdynError` and its subclasses)**
    These exceptions occur when you try to initialize an `Odyn` client or `Session` with invalid parameters. They are predictable and indicate a problem in your code that should be fixed during development. All of these inherit from the base `OdynError`.

2.  **Runtime & Network Errors (`requests.exceptions`)**
    These exceptions occur during a live API call. They are raised by the underlying `requests` library and indicate issues like network failures, timeouts, or HTTP error responses from the server (e.g., `401 Unauthorized`). These are the errors you need to handle gracefully in your production code.

---

## Configuration Errors: The `OdynError` Hierarchy

All custom exceptions raised by Odyn inherit from a single base class, `OdynError`. This allows you to catch any specific configuration error, or all of them at once by catching the base class.

```
OdynError
├── InvalidURLError
├── InvalidSessionError
├── InvalidTimeoutError
├── InvalidLoggerError
├── InvalidRetryError
├── InvalidBackoffFactorError
└── InvalidStatusForcelistError
```

### `InvalidURLError`
Raised when initializing an `Odyn` client with a malformed `base_url`.

-   **Common Causes**: The URL string is empty, does not start with `http://` or `https://`, or is otherwise invalid.
-   **Example Trigger**:
    ```python
    import requests
    from odyn import Odyn, InvalidURLError
    try:
        # This will fail because the scheme is missing
        client = Odyn(base_url="api.example.com", session=requests.Session())
    except InvalidURLError as e:
        print(f"Caught expected error: {e}")
    ```

### `InvalidSessionError`
Raised when initializing an `Odyn` client with an object that is not an instance of `requests.Session`.

-   **Common Causes**: Passing `None` or a non-session object (like a string or dict) to the `session` parameter.
-   **Example Trigger**:
    ```python
    from odyn import Odyn, InvalidSessionError
    try:
        # This will fail because a string is not a session object
        client = Odyn(base_url="https://api.example.com", session="not-a-session")
    except InvalidSessionError as e:
        print(f"Caught expected error: {e}")
    ```

### `InvalidTimeoutError`
Raised when initializing an `Odyn` client with a malformed `timeout`.

-   **Common Causes**: Providing a single number instead of a tuple, a tuple with the wrong number of elements, or a tuple containing non-positive values.
-   **Example Trigger**:
    ```python
    import requests
    from odyn import Odyn, InvalidTimeoutError
    try:
        # This will fail because the timeout must be a tuple of two positive numbers
        client = Odyn(base_url="https://api.example.com/", session=requests.Session(), timeout=(10, -30))
    except InvalidTimeoutError as e:
        print(f"Caught expected error: {e}")
    ```

### `InvalidLoggerError`
Raised when initializing an `Odyn` client with an object that is not a `loguru.Logger`.

-   **Common Causes**: Passing a logger from Python's standard `logging` library or any other non-loguru object.
-   **Example Trigger**:
    ```python
    import logging
    import requests
    from odyn import Odyn, InvalidLoggerError
    try:
        # This will fail because it's not a loguru logger
        std_logger = logging.getLogger("test")
        client = Odyn(base_url="https://api.example.com/", session=requests.Session(), logger=std_logger)
    except InvalidLoggerError as e:
        print(f"Caught expected error: {e}")
    ```

### `InvalidRetryError`
Raised when initializing an `OdynSession` (or its subclasses) with an invalid `retries` value.

-   **Common Causes**: Providing a zero, negative, or non-integer value for the retry count.
-   **Example Trigger**:
    ```python
    from odyn import BearerAuthSession, InvalidRetryError
    try:
        # This will fail because retries must be a positive integer
        session = BearerAuthSession(token="some-token", retries=0)
    except InvalidRetryError as e:
        print(f"Caught expected error: {e}")
    ```

### `InvalidBackoffFactorError`
Raised when initializing an `OdynSession` with an invalid `backoff_factor`.

-   **Common Causes**: Providing a zero or negative number for the backoff factor.
-   **Example Trigger**:
    ```python
    from odyn import BearerAuthSession, InvalidBackoffFactorError
    try:
        # This will fail because the backoff factor must be positive
        session = BearerAuthSession(token="some-token", backoff_factor=-1.0)
    except InvalidBackoffFactorError as e:
        print(f"Caught expected error: {e}")
    ```

### `InvalidStatusForcelistError`
Raised when initializing an `OdynSession` with a `status_forcelist` that is not a list of integers.

-   **Common Causes**: Providing a string or a list containing non-integer values.
-   **Example Trigger**:
    ```python
    from odyn import BearerAuthSession, InvalidStatusForcelistError
    try:
        # This will fail because the list contains a string
        session = BearerAuthSession(token="some-token", status_forcelist=[500, "429"])
    except InvalidStatusForcelistError as e:
        print(f"Caught expected error: {e}")
    ```

---

## Runtime & Network Errors

These errors occur during the `client.get()` call and must be handled in your code.

### `requests.exceptions.HTTPError`
-   **When it's raised**: When the Business Central API returns an HTTP error code (4xx or 5xx) that is **not** in the session's `status_forcelist` (and therefore not retried).
-   **Common Causes**:
    -   `401 Unauthorized`: Your token is invalid, expired, or lacks permissions.
    -   `404 Not Found`: The `base_url` or `endpoint` is incorrect.
    -   `400 Bad Request`: Your OData query (e.g., in `$filter`) is malformed.
-   **Handling**: You can inspect the `response` attribute on the exception to get the status code and the error message from the API.

### `requests.exceptions.RequestException`
-   **When it's raised**: For fundamental networking issues.
-   **Common Causes**: DNS failures, connection refused, or timeouts (both connect and read).
-   **Handling**: This is a base class for many `requests` exceptions. Catching it is a good way to handle most network-level problems.

---

## Best Practice: Error Handling Strategy

Here is a robust `try...except` block that demonstrates how to handle these exceptions in a structured way. The key is to catch more specific exceptions before more general ones.

```python
import requests
from odyn import Odyn, BearerAuthSession, OdynError

# Assume client is configured correctly for this example.
# In a real app, these would come from a secure config or environment variables.
session = BearerAuthSession(token="your-token")
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant/production/",
    session=session
)

try:
    # This is the operation that can fail at runtime
    customers = client.get(
        "customers",
        params={"$filter": "city eq 'New York'"}
    )
    print(f"Successfully retrieved {len(customers)} customers.")

except requests.exceptions.HTTPError as http_err:
    # Handle specific HTTP status codes from the API
    status_code = http_err.response.status_code
    response_text = http_err.response.text
    print(f"HTTP Error: {status_code}. The API responded with: {response_text}")
    if status_code == 401:
        print("Authentication failed. Please check your access token.")
    elif status_code == 404:
        print("The requested resource was not found. Please check your URL and endpoint.")

except requests.exceptions.RequestException as req_err:
    # Handle network-level errors (timeouts, connection issues)
    print(f"Network Error: Could not complete the request. {req_err}")

except (TypeError, ValueError) as data_err:
    # Handle cases where the API returns unexpected or malformed JSON
    print(f"Data Error: The API response was not in the expected format. {data_err}")

except OdynError as config_err:
    # This is for catching configuration errors during development.
    # In production, this block might be less critical if config is static.
    print(f"Configuration Error: The Odyn client or session is misconfigured. {config_err}")

except Exception as e:
    # A general fallback for any other unexpected errors
    print(f"An unexpected error occurred: {e}")

```
