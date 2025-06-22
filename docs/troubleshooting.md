# Troubleshooting Guide

This guide will help you diagnose and resolve common errors when using the Odyn client. For a list of all custom exceptions, see the [Exception Reference](usage/exceptions.md).

---

A good first step for any issue is to [enable detailed logging](#1-enable-logging), which can provide crucial context about the problem.

## 1. Configuration Errors

These errors are raised by Odyn's internal validation before a network request is made. They indicate a problem with how the client was initialized.

### InvalidURLError
- **Symptom**: `InvalidURLError: URL must have a valid scheme (http or https)...` or `URL cannot be empty`.
- **Cause**: The `base_url` is missing, malformed, or does not start with `http://` or `https://`.
- **Solution**: Provide a valid, non-empty base URL.

```python
# Correct
client = Odyn(base_url="https://api.example.com/api/v2.0/", ...)
```

### InvalidSessionError
- **Symptom**: `InvalidSessionError: session must be a Session, got <class 'str'>`.
- **Cause**: The object passed to the `session` parameter is not an instance of `requests.Session`.
- **Solution**: Pass a valid session object, such as `BearerAuthSession` or `BasicAuthSession`.

```python
from odyn import BearerAuthSession

# Correct
session = BearerAuthSession("your-token")
client = Odyn(..., session=session)
```

### InvalidTimeoutError
- **Symptom**: `InvalidTimeoutError: Timeout must be a tuple...` or `...must be greater than 0`.
- **Cause**: The `timeout` parameter was not a tuple of two positive numbers.
- **Solution**: Ensure the timeout is in the format `(connect_timeout, read_timeout)`.

```python
# Correct
client = Odyn(..., timeout=(10, 60))
```

### InvalidLoggerError
- **Symptom**: `InvalidLoggerError: logger must be a Logger, got ...`
- **Cause**: The object passed to the `logger` parameter is not a `loguru.Logger` instance.
- **Solution**: Provide a valid `loguru` logger.

---

## 2. HTTP & Network Errors

These errors occur during the network request and are typically raised by the underlying `requests` library.

### 401 Unauthorized
- **Symptom**: `requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: ...`
- **Cause**: The access token is invalid, expired, or lacks the required permissions.
- **Solution**:
    1.  Ensure your access token is correct and not expired.
    2.  Verify the associated application has the correct API permissions in Business Central.

### 429 Too Many Requests
- **Symptom**: `requests.exceptions.HTTPError: 429 Client Error: Too Many Requests for url: ...`
- **Cause**: The Business Central API is rate-limiting your client due to too many requests in a short period.
- **Solution**: Adjust the retry settings on your session to use a higher `backoff_factor` or more `retries`.

```python
# Increase backoff to wait longer between retries
session = BearerAuthSession(..., backoff_factor=3.0, retries=10)
```
**See**: [Advanced Configuration](advanced/configuration.md)

### Request Timeouts
- **Symptom**: `requests.exceptions.ConnectTimeout` or `requests.exceptions.ReadTimeout`.
- **Cause**: The request took longer than the configured `timeout` values. This is distinct from `InvalidTimeoutError`.
- **Solution**: Increase the `connect` or `read` timeout values in the client configuration.

```python
# Increase read timeout to 5 minutes for a long-running query
client = Odyn(..., timeout=(15, 300))
```

### Connection & SSL Errors
- **Symptom**: `requests.exceptions.ConnectionError` or `requests.exceptions.SSLError`.
- **Cause**: A network problem (e.g., DNS, firewall, proxy) or an SSL certificate issue is preventing a connection.
- **Solution**: Check your network environment and ensure your system's root certificates are up to date.

---

## 3. API Response Errors

These errors indicate that the client received a response from the API, but the data was not in the expected format.

### JSON Decode Error
- **Symptom**: `ValueError: Failed to decode JSON from response`.
- **Cause**: The API returned a non-JSON response, which can happen if there is a server-side error that produces an HTML error page.
- **Solution**: Enable logging to inspect the raw response body. The endpoint you are calling may be incorrect or the server may be down.

### Invalid OData Response
- **Symptom**: `TypeError: OData response format is invalid: 'value' key is missing...`
- **Cause**: The API response, while valid JSON, does not follow the expected OData structure (i.e., it's missing the `value` key for a collection).
- **Solution**:
    1.  Confirm your endpoint URL is correct.
    2.  Ensure you are querying a collection endpoint (e.g., `/customers`) and not a single entity endpoint (e.g., `/customers(some_id)`).

---

## General Debugging Strategy

If you're not sure what the problem is, follow these steps:

### 1. Enable Logging
The most effective way to debug is to enable detailed logging. This will show you the exact requests being made, the responses received, and any validation warnings.
```python
import sys
from loguru import logger

# Send detailed logs to a file and INFO-level logs to the console
logger.add("debug.log", level="DEBUG")
logger.add(sys.stderr, level="INFO")

# Pass the logger to the client
client = Odyn(..., logger=logger)
```
**See**: [Logging Guide](advanced/logging.md)

### 2. Inspect the Exception
Examine the full traceback to understand where the error originated. An error from `odyn._exceptions` is a client-side validation issue, while an error from `requests.exceptions` is a network or HTTP issue.

### 3. Check the API Documentation
Consult the [Business Central API Docs](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/) to ensure your endpoints and parameters are correct.

---

## Still Stuck?
If you're still having trouble, please [open an issue](https://github.com/kon-fin/odyn/issues) and provide as much detail as possible, including logs and code to reproduce the problem.
