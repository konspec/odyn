# Troubleshooting

This guide covers common errors and misconfigurations when using Odyn with Microsoft Dynamics 365 Business Central OData V4 API.

---

## Table of Contents
- [Invalid URL](#invalid-url)
- [Incorrect Authentication](#incorrect-authentication)
- [Timeout Misconfiguration](#timeout-misconfiguration)
- [JSONDecodeError](#jsondecodeerror)
- [Pagination Failures](#pagination-failures)
- [Other Common Issues](#other-common-issues)

---

## Invalid URL

**Symptoms:**
- `InvalidURLError` raised
- Stack trace: `InvalidURLError: URL cannot be empty` or `URL must have a valid scheme (http or https)`

**Root Causes:**
- Base URL is empty, missing, or has wrong scheme
- Typo in the URL

**Solution:**
- Ensure the base URL is a non-empty string, starts with `https://`, and includes a valid domain.
- Example:
  ```python
  client = Odyn(base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/", session=session)
  ```

---

## Incorrect Authentication

**Symptoms:**
- HTTP 401 Unauthorized
- Stack trace: `requests.exceptions.HTTPError: 401 Client Error: Unauthorized`

**Root Causes:**
- Invalid or expired access token
- Wrong username/password
- Missing authentication header

**Solution:**
- Use a valid `BearerAuthSession` or `BasicAuthSession`.
- Refresh your access token if expired.
- Example:
  ```python
  session = BearerAuthSession("your-access-token")
  client = Odyn(base_url=..., session=session)
  ```

---

## Timeout Misconfiguration

**Symptoms:**
- `InvalidTimeoutError` raised
- Stack trace: `InvalidTimeoutError: Timeout must be a tuple, got int` or `Timeout values must be greater than 0, got 0`
- `requests.exceptions.Timeout`

**Root Causes:**
- Timeout is not a tuple of two positive numbers
- Network is slow or unresponsive

**Solution:**
- Use a tuple for timeout: `(connect_timeout, read_timeout)`
- Increase timeout values for slow networks
- Example:
  ```python
  client = Odyn(base_url=..., session=session, timeout=(30, 120))
  ```

---

## JSONDecodeError

**Symptoms:**
- `ValueError: Failed to decode JSON from response`
- Stack trace: `requests.exceptions.JSONDecodeError`

**Root Causes:**
- API returned non-JSON response (e.g., HTML error page)
- Network issues or server errors

**Solution:**
- Check the response content (log it if needed)
- Ensure the endpoint is correct and the server is healthy
- Example:
  ```python
  try:
      data = client.get("customers")
  except ValueError as e:
      print(f"JSON error: {e}")
  ```

---

## Pagination Failures

**Symptoms:**
- `TypeError: OData response missing 'value' list.`
- Stack trace: `TypeError: OData response format is invalid: 'value' key is missing or not a list.`

**Root Causes:**
- API endpoint does not return OData-compliant response
- Incorrect endpoint or query

**Solution:**
- Check the endpoint and query parameters
- Ensure the API returns a JSON object with a `value` key containing a list
- Example expected response:
  ```json
  {
    "@odata.context": "...",
    "value": [ ... ]
  }
  ```

---

## Other Common Issues

### SSL Errors
- **Symptoms:** `requests.exceptions.SSLError`
- **Solution:** Ensure your system trusts the server's SSL certificate. Use `verify=False` only for testing.

### Network Errors
- **Symptoms:** `requests.exceptions.ConnectionError`, `requests.exceptions.Timeout`
- **Solution:** Check your internet connection and firewall settings.

### Rate Limiting
- **Symptoms:** HTTP 429 Too Many Requests
- **Solution:** Increase backoff factor and retries. See [Advanced Configuration](advanced/configuration.md).

---

## Debugging Tips

- Enable debug logging with loguru to see request/response details:
  ```python
  from loguru import logger
  logger.add("odyn_debug.log", level="DEBUG")
  ```
- Print or inspect the full stack trace for errors.
- Use [Exception Handling](usage/exceptions.md) to catch and resolve specific errors.
- Review [FAQ](faq.md) for more help.

---

## Still Stuck?
- Review the [FAQ](faq.md)
- Check the [Exception Reference](usage/exceptions.md)
- File an issue or ask for help via [Contributing](contributing.md)
- Consult the [Microsoft OData V4 Docs](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
