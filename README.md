<p align="center">
  <img src="https://konspec.com/wp-content/uploads/2024/05/Konspec-web1.png" alt="Konspec Logo" width="320"/>
</p>

# Odyn

**A modern, typed, and robust Python client for the Microsoft Dynamics 365 Business Central OData V4 API**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](docs/index.md)
[![Tests](https://github.com/konspec/odyn/workflows/CI/badge.svg)](https://github.com/konspec/odyn/actions)
[![codecov](https://codecov.io/gh/konspec/odyn/graph/badge.svg?token=H8MK6DP96P)](https://codecov.io/gh/konspec/odyn)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

Odyn provides a convenient and feature-rich interface for interacting with Microsoft Dynamics 365 Business Central, including automatic retry mechanisms, pagination handling, and pluggable authentication sessions.

## ✨ Features

- **🔒 Type Safety**: Fully typed with comprehensive type annotations for better IDE support and runtime safety
- **🔄 Automatic Retry Logic**: Built-in exponential backoff retry mechanism for handling transient failures
- **📄 Smart Pagination**: Automatic handling of OData pagination with transparent multi-page data retrieval
- **🔐 Flexible Authentication**: Support for Basic Authentication and Bearer Token authentication
- **📊 Comprehensive Logging**: Detailed logging with loguru integration for debugging and monitoring
- **⚡ Production Ready**: Robust error handling, validation, and timeout management
- **🔧 Extensible Design**: Pluggable session management for custom authentication strategies

## 🚀 Quick Install

```bash
pip install odyn
```

Or see [full installation instructions](docs/installation.md) for pip, uv, and poetry.

## 📖 Quick Start

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

## 🛠️ Requirements

- **Python 3.12+**
- **requests** (≥2.32.4)
- **loguru** (≥0.7.3)

## 📚 Documentation

- 📚 **Full documentation:** [docs/index.md](docs/index.md)

### Getting Started
- [Installation](docs/installation.md) - Install Odyn using pip, uv, or poetry
- [Getting Started](docs/getting-started.md) - Quick setup and first API call

### Usage Guides
- [Odyn Client](docs/usage/odyn.md) - Complete API reference for the main client
- [Authentication Sessions](docs/usage/sessions.md) - Session management and authentication
- [Exception Handling](docs/usage/exceptions.md) - Understanding and handling errors

### Advanced Topics
- [Configuration](docs/advanced/configuration.md) - Timeouts, retries, and advanced settings
- [Logging](docs/advanced/logging.md) - Logging behavior and customization

### Reference
- [FAQ](docs/faq.md) - Frequently asked questions
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🔧 Examples

### Basic Usage
```python
from odyn import Odyn, BearerAuthSession

session = BearerAuthSession("your-token")
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session
)

# Get all customers
customers = client.get("customers")

# Get items with filtering
items = client.get("items", params={"$filter": "blocked eq false"})

# Get vendors with custom headers
vendors = client.get("vendors", headers={"Accept": "application/json;odata.metadata=minimal"})
```

### Advanced Configuration
```python
from odyn import Odyn, BearerAuthSession
from loguru import logger

# Custom logger
custom_logger = logger.bind(component="business-central-client")

# Session with aggressive retry settings
session = BearerAuthSession(
    token="your-token",
    retries=10,
    backoff_factor=0.5,
    status_forcelist=[408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524]
)

# Client with custom timeout and logger
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session,
    logger=custom_logger,
    timeout=(30, 180)  # 30s connect, 3min read timeout
)
```

### Error Handling
```python
from odyn import Odyn, BearerAuthSession
from odyn import InvalidURLError, InvalidSessionError
import requests

try:
    session = BearerAuthSession("your-token")
    client = Odyn(
        base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
        session=session
    )

    customers = client.get("customers")

except InvalidURLError as e:
    print(f"❌ Invalid URL: {e}")
except InvalidSessionError as e:
    print(f"❌ Invalid session: {e}")
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
except requests.exceptions.RequestException as e:
    print(f"❌ Network Error: {e}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/odyn.git
cd odyn

# Install in development mode
pip install -e .

# Run tests
pytest

# Run linting
ruff check .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](docs/index.md)
- ❓ [FAQ](docs/faq.md)
- 🐛 [Troubleshooting](docs/troubleshooting.md)
- 💬 [Issues](https://github.com/your-username/odyn/issues)

## 🔗 Related

- [Microsoft Dynamics 365 Business Central API](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
- [OData V4 Specification](https://docs.oasis-open.org/odata/odata/v4.0/os/part1-protocol/odata-v4.0-os-part1-protocol.html)
- [requests](https://docs.python-requests.org/) - HTTP library
- [loguru](https://loguru.readthedocs.io/) - Logging library
