<p align="center">
  <img src="https://konspec.com/wp-content/uploads/2024/05/Konspec-web1.png" alt="Konspec Logo" width="320"/>
</p>

# Odyn

**A modern, typed, and robust Python client for the Microsoft Dynamics 365 Business Central OData V4 API**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/konspec/odyn)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://konspec.github.io/odyn/)
[![Tests](https://github.com/konspec/odyn/workflows/CI/badge.svg)](https://github.com/konspec/odyn/actions)
[![codecov](https://codecov.io/gh/konspec/odyn/graph/badge.svg?token=H8MK6DP96P)](https://codecov.io/gh/konspec/odyn)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[![PyPI version](https://img.shields.io/pypi/v/odyn.svg)](https://img.shields.io/pypi/v/odyn)

---

[PyPi link](https://pypi.org/project/odyn)

Odyn provides a convenient and feature-rich interface for interacting with Microsoft Dynamics 365 Business Central, including automatic retry mechanisms, pagination handling, and pluggable authentication sessions.

## Features

- **Type Safety**: Fully typed with comprehensive type annotations for better IDE support and runtime safety.
- **Automatic Retry Logic**: Built-in exponential backoff retry mechanism for handling transient network failures.
- **Smart Pagination**: Automatic handling of OData pagination with transparent multi-page data retrieval.
- **Flexible Authentication**: Pluggable `requests.Session` based authentication. Comes with `BearerAuthSession` and `BasicAuthSession` out of the box.
- **Comprehensive Logging**: Detailed logging with `loguru` integration for easy debugging and monitoring.
- **Production Ready**: Robust error handling, validation, and timeout management.
- **Extensible Design**: Easily extendable to support custom authentication strategies or other session-level features.

## Quick Install

```bash
pip install odyn
```

Or see [full installation instructions](https://konspec.github.io/odyn/installation/) for pip, uv, and poetry.

## Quick Start

```python
from odyn import Odyn, BearerAuthSession

# Create an authenticated session
session = BearerAuthSession("your-access-token")

# Initialize the client
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session
)

# Fetch data with automatic pagination
customers = client.get("customers")
print(f"Retrieved {len(customers)} customers")

# Use OData query parameters
filtered_customers = client.get(
    "customers",
    params={
        "$top": 10,
        "$filter": "contains(name, 'Adventure')",
        "$select": "id,name,phoneNumber"
    }
)
```

## Requirements

- **Python 3.12+**
- **requests** (≥2.32.4)
- **loguru** (≥0.7.3)

## Documentation

- 📚 **Full documentation:** [https://konspec.github.io/odyn/](https://konspec.github.io/odyn/)

### Getting Started
- [Installation](https://konspec.github.io/odyn/installation/) - Install Odyn using pip, uv, or poetry
- [Getting Started](https://konspec.github.io/odyn/getting-started/) - Quick setup and first API call

### Usage Guides
- [Odyn Client](https://konspec.github.io/odyn/usage/odyn/) - Complete API reference for the main client
- [Authentication Sessions](https://konspec.github.io/odyn/usage/sessions/) - Session management and authentication
- [Exception Handling](https://konspec.github.io/odyn/usage/exceptions/) - Understanding and handling errors

### Advanced Topics
- [Configuration](https://konspec.github.io/odyn/advanced/configuration/) - Timeouts, retries, and advanced settings
- [Logging](https://konspec.github.io/odyn/advanced/logging/) - Logging behavior and customization

### Reference
- [FAQ](https://konspec.github.io/odyn/faq/) - Frequently asked questions
- [Troubleshooting](https://konspec.github.io/odyn/troubleshooting/) - Common issues and solutions

## Examples

### Bearer Token Authentication
```python
from odyn import Odyn, BearerAuthSession

# Create a session with your bearer token
session = BearerAuthSession(token="your-access-token")

# Initialize the client
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=session,
)

# Get all customers with automatic pagination handling
customers = client.get("customers")
print(f"Retrieved {len(customers)} customers")

# Get the top 10 items, filtering by name and selecting specific fields
items = client.get(
    "items",
    params={
        "$top": 10,
        "$filter": "contains(displayName, 'Desk')",
        "$select": "id,displayName,itemCategoryCode",
    },
)
print(f"Filtered items: {items}")
```

### Basic Authentication
```python
from odyn import Odyn, BasicAuthSession

# Create a session with your username and web service access key
session = BasicAuthSession(username="your-username", password="your-web-service-access-key")

# Initialize the client
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=session,
)

# Get all vendors
vendors = client.get("vendors")
print(f"Retrieved {len(vendors)} vendors")
```

### Advanced Configuration
```python
from odyn import Odyn, BearerAuthSession
from loguru import logger

# Bind a custom component to the logger for easy filtering
custom_logger = logger.bind(component="business-central-client")

# Create a session with custom retry settings
# This example uses a more aggressive retry strategy than the default.
session = BearerAuthSession(
    token="your-token",
    retries=10,
    backoff_factor=0.5,
    status_forcelist=[408, 429, 500, 502, 503, 504],
)

# Initialize a client with a custom timeout and the custom logger
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=session,
    logger=custom_logger,
    timeout=(10, 60),  # 10s connect timeout, 60s read timeout
)
```

### Error Handling
```python
from odyn import (
    Odyn,
    BearerAuthSession,
    InvalidURLError,
    InvalidSessionError,
    InvalidTimeoutError,
    InvalidLoggerError,
)
import requests

try:
    # Intentionally create an invalid session
    session = BearerAuthSession(token=None) # type: ignore
    client = Odyn(base_url="not-a-valid-url", session=session)
    client.get("customers")

except InvalidURLError as e:
    print(f"Invalid URL: {e}")
except InvalidSessionError as e:
    print(f"Invalid session: {e}")
except InvalidTimeoutError as e:
    print(f"Invalid timeout configuration: {e}")
except InvalidLoggerError as e:
    print(f"Invalid logger object provided: {e}")
except requests.exceptions.HTTPError as e:
    # Handle HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
    print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
except requests.exceptions.RequestException as e:
    # Handle network-related errors (e.g., connection refused)
    print(f"Network Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/konspec/odyn.git
cd odyn

# Install dependencies (we recommend using uv)
uv pip install -e .[dev]

# Run tests
pytest

# Run linting
ruff check .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Documentation](docs/index.md)
- [FAQ](docs/faq.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Issues](https://github.com/konspec/odyn/issues)

## Related

- [Microsoft Dynamics 365 Business Central OData Web Services](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/odata-web-services)
- [OData V4 Specification](https://docs.oasis-open.org/odata/odata/v4.0/os/part1-protocol/odata-v4.0-os-part1-protocol.html)
- [requests](https://docs.python-requests.org/) - HTTP library
- [loguru](https://loguru.readthedocs.io/) - Logging library

---
[Konkan Speciality Polyproducts Pvt Ltd.](https://www.konspec.com)
