# Frequently Asked Questions (FAQ)

This FAQ provides answers to common questions about Odyn. If you don't find your answer here, please check the other documentation pages or [open an issue](https://github.com/kon-fin/odyn/issues).

---

## General

### What is Odyn?
Odyn is a modern Python client for the Microsoft Dynamics 365 Business Central OData V4 API. It is designed to be robust and easy to use, with features like automatic retries, pagination handling, and type-safe interfaces.

### What are the requirements?
- **Python**: 3.12 or higher
- **Core Dependencies**:
    - `requests` (>=2.32.4)
    - `loguru` (>=0.7.3)

---

## Authentication

### How do I authenticate?
Authentication is handled via session objects. Odyn provides two ready-to-use sessions: `BearerAuthSession` (recommended for OAuth) and `BasicAuthSession`.

```python
from odyn import BearerAuthSession

# Use a bearer token for authentication
session = BearerAuthSession("your-access-token")

# For more details, see the Authentication Sessions guide.
```
**See**: [Authentication Sessions](usage/sessions.md)

---

## Making Requests

### How does pagination work?
It's automatic. The `client.get()` method handles OData's `@odata.nextLink` pagination for you, returning a complete list of all records from all pages.

### How do I select specific fields or filter results?
Use OData's standard query parameters (`$select`, `$filter`, `$top`, etc.) in the `params` argument of the `get` method.

```python
# Select the 'id' and 'name' fields, and filter by name
customers = client.get(
    "customers",
    params={"$select": "id,displayName", "$filter": "contains(displayName, 'Adatum')"}
)
```

### Is there `asyncio` support?
No. Odyn is a synchronous library built on `requests`. It does not support `asyncio` out of the box.

---

## Configuration

### How do I change the request timeout?
Pass a `(connect, read)` tuple to the `timeout` parameter of the `Odyn` client. Both values are in seconds.

```python
# Set a 5-second connect timeout and a 30-second read timeout
client = Odyn(..., timeout=(5, 30))
```
**See**: [Advanced Configuration](advanced/configuration.md)

### How do I configure the retry logic?
You can customize the number of `retries`, the `backoff_factor`, and the `status_forcelist` when creating a session object.

```python
session = BearerAuthSession(
    token="your-token",
    retries=10,
    backoff_factor=1.5
)
```
**See**: [Advanced Configuration](advanced/configuration.md)

---

## Troubleshooting

### How do I debug failed requests?
Provide a configured `loguru` logger to the `Odyn` client to see detailed logs, including request/response information.

**See**: [Logging Guide](advanced/logging.md)

### What does `InvalidURLError` mean?
The `base_url` provided to the client was invalid. Ensure it's a non-empty string that starts with `http://` or `https://` and includes a domain name.

### What does `InvalidSessionError` mean?
The `session` object was not a valid `requests.Session` instance. Make sure you are using one of Odyn's session classes or a valid custom session.

### What does `InvalidTimeoutError` mean?
The `timeout` value was not a tuple of two positive numbers. It must be in the format `(connect_timeout, read_timeout)`.

---

## Contributing

### How can I contribute to Odyn?
We welcome contributions! Please read our [Contributing Guide](contributing.md) to get started with the development setup and pull request process.

---

## More Help
- [Troubleshooting Guide](troubleshooting.md)
- [Exception Reference](usage/exceptions.md)
- [Microsoft OData V4 Docs](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
