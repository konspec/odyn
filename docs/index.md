# Odyn

**A modern, typed, and robust Python client for the Microsoft Dynamics 365 Business Central OData V4 API**

Odyn provides a convenient and feature-rich interface for interacting with Microsoft Dynamics 365 Business Central, including automatic retry mechanisms, pagination handling, and pluggable authentication sessions.

## Key Features

- **🔒 Type Safety**: Fully typed with comprehensive type annotations for better IDE support and runtime safety
- **🔄 Automatic Retry Logic**: Built-in exponential backoff retry mechanism for handling transient failures
- **📄 Smart Pagination**: Automatic handling of OData pagination with transparent multi-page data retrieval
- **🔐 Flexible Authentication**: Support for Basic Authentication and Bearer Token authentication
- **📊 Comprehensive Logging**: Detailed logging with loguru integration for debugging and monitoring
- **⚡ Production Ready**: Robust error handling, validation, and timeout management
- **🔧 Extensible Design**: Pluggable session management for custom authentication strategies

## Supported Python Versions

- **Python 3.12+** (required)

## Core Dependencies

- **requests** (≥2.32.4) - HTTP client library
- **loguru** (≥0.7.3) - Advanced logging framework

## When to Use Odyn

Use Odyn when you need to:

- **Integrate with Microsoft Dynamics 365 Business Central** via OData V4 API
- **Handle complex API interactions** with automatic retry and pagination
- **Build production applications** that require robust error handling and logging
- **Maintain type safety** throughout your API client code
- **Customize authentication strategies** for different deployment scenarios

## Microsoft Dynamics 365 Business Central OData V4

Odyn is specifically designed to work with the [Microsoft Dynamics 365 Business Central OData V4 API](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/). This API provides programmatic access to Business Central data and operations through RESTful endpoints.

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

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.
