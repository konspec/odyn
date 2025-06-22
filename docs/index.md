# Odyn Documentation

**A modern, typed, and robust Python client for the Microsoft Dynamics 365 Business Central OData V4 API**

Odyn provides a convenient and feature-rich interface for interacting with Microsoft Dynamics 365 Business Central, including automatic retry mechanisms, pagination handling, and pluggable authentication sessions.

## Key Features

- **Type Safety**: Fully typed with comprehensive type annotations for better IDE support and runtime safety.
- **Automatic Retry Logic**: Built-in exponential backoff retry mechanism for handling transient network failures.
- **Smart Pagination**: Automatic handling of OData pagination with transparent multi-page data retrieval.
- **Flexible Authentication**: Pluggable `requests.Session` based authentication. Comes with `BearerAuthSession` and `BasicAuthSession` out of the box.
- **Comprehensive Logging**: Detailed logging with `loguru` integration for easy debugging and monitoring.
- **Production Ready**: Robust error handling, validation, and timeout management.
- **Extensible Design**: Easily extendable to support custom authentication strategies or other session-level features.

## Supported Python Versions

- **Python 3.12+**

## Core Dependencies

- **requests** (≥2.32.4)
- **loguru** (≥0.7.3)

## When to Use Odyn

Use Odyn when you need to:

- Integrate with Microsoft Dynamics 365 Business Central via its OData V4 API.
- Handle complex API interactions with automatic retries and pagination.
- Build production applications that require robust error handling and logging.
- Maintain type safety throughout your API client code.
- Customize authentication strategies for different deployment scenarios.

## Microsoft Dynamics 365 Business Central OData Web Services

Odyn is specifically designed to work with the [Microsoft Dynamics 365 Business Central OData Web Services](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/odata-web-services). This API provides programmatic access to Business Central data and operations through RESTful endpoints.

## Quick Start

```python
from odyn import Odyn, BearerAuthSession

# Create an authenticated session with your access token
session = BearerAuthSession(token="your-access-token")

# Initialize the client with your production tenant URL
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=session,
)

# Fetch data with automatic pagination
customers = client.get("customers")
print(f"Retrieved {len(customers)} customers")
```

## Documentation

### Getting Started
- [Installation](installation.md) - Install Odyn using pip, uv, or poetry
- [Getting Started](getting-started.md) - Quick setup and first API call

### Usage Guides
- [Odyn Client](usage/odyn.md) - Complete API reference for the main client
- [Authentication Sessions](usage/sessions.md) - Session management and authentication
- [Exception Handling](usage/exceptions.md) - Understanding and handling errors

### Advanced Topics
- [Configuration](advanced/configuration.md) - Timeouts, retries, and advanced settings
- [Logging](advanced/logging.md) - Logging behavior and customization

### Reference
- [FAQ](faq.md) - Frequently asked questions
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Contributing](contributing.md) - How to contribute to Odyn

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
