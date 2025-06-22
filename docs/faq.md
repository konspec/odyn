# Frequently Asked Questions (FAQ)

This FAQ addresses common questions about using Odyn with Microsoft Dynamics 365 Business Central OData V4 API.

---

## General

### What is Odyn?
Odyn is a typed, extensible, and production-ready Python client for the Microsoft Dynamics 365 Business Central OData V4 API. It provides robust session management, retry logic, pagination, and flexible authentication.

### What Python versions are supported?
Odyn requires **Python 3.12 or higher**.

### What are the core dependencies?
- [requests](https://docs.python-requests.org/en/latest/) (≥2.32.4)
- [loguru](https://loguru.readthedocs.io/en/stable/) (≥0.7.3)

---

## Usage

### Why is my request retrying?
Odyn sessions include automatic retry logic for transient errors (e.g., 429, 500, 502, 503, 504). You can configure retry count, backoff factor, and status forcelist. See [Advanced Configuration](advanced/configuration.md).

### How do I change the retry logic?
Pass `retries`, `backoff_factor`, and `status_forcelist` to your session class:

```python
from odyn import BearerAuthSession
session = BearerAuthSession(
    token="your-token",
    retries=10,
    backoff_factor=1.0,
    status_forcelist=[429, 500, 503]
)
```
See [Session Configuration](usage/sessions.md).

### What does `InvalidSessionError` mean?
You passed an invalid session object to the Odyn client. Use a valid `requests.Session` or one of Odyn's session classes. See [Exception Handling](usage/exceptions.md).

### How do I authenticate?
Use `BearerAuthSession` (recommended) or `BasicAuthSession`:

```python
from odyn import BearerAuthSession
session = BearerAuthSession("your-access-token")
```
See [Authentication Sessions](usage/sessions.md).

### How do I handle pagination?
Odyn's `.get()` method automatically handles OData pagination. You always get a complete list of results.

### How do I log requests and responses?
Odyn uses loguru for logging. You can inject a custom logger or use the default. See [Logging](advanced/logging.md).

### How do I select specific fields or filter results?
Use OData query parameters in the `params` argument:

```python
customers = client.get("customers", params={"$select": "id,name", "$filter": "contains(name, 'Acme')"})
```
See [Getting Started](getting-started.md).

### Can I use Odyn with async code?
Odyn is built on `requests` and is synchronous. For async support, use a separate async HTTP client.

---

## Errors & Troubleshooting

### Why am I getting `InvalidURLError`?
Check that your base URL is a non-empty string, starts with `http://` or `https://`, and includes a domain.

### Why do I get a timeout error?
Increase your timeout values or check your network connection. See [Advanced Configuration](advanced/configuration.md).

### How do I debug failed requests?
Enable debug logging with loguru and inspect the logs for request/response details. See [Logging](advanced/logging.md).

### How do I contribute to Odyn?
See [Contributing](contributing.md) for guidelines.

---

## More Help
- [Troubleshooting Guide](troubleshooting.md)
- [Exception Reference](usage/exceptions.md)
- [Microsoft OData V4 Docs](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
