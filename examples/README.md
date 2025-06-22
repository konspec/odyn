# Odyn Examples

This folder contains comprehensive examples demonstrating various use cases and patterns for the odyn library. Each example is designed to be self-contained and includes detailed explanations and best practices.

## 📁 Example Files

### 1. [01_basic_setup.py](01_basic_setup.py)
**Basic Setup Example**
- Fundamental usage of odyn with bearer token authentication
- Simple API calls to Business Central
- Basic error handling
- Perfect starting point for beginners

**Key Features:**
- Client initialization
- Basic data retrieval
- Automatic pagination handling
- Simple error handling

### 2. [02_authentication_methods.py](02_authentication_methods.py)
**Authentication Methods Example**
- Different authentication strategies available in odyn
- Bearer token authentication (recommended)
- Basic authentication (username/password)
- Custom session configuration
- Advanced retry settings

**Key Features:**
- Multiple authentication methods
- Custom session headers
- Retry configuration examples
- Environment-specific settings

### 3. [03_odata_queries.py](03_odata_queries.py)
**OData Queries Example**
- Comprehensive OData query operations
- Filtering, sorting, and field selection
- Complex query patterns
- Pagination handling
- Search and count operations

**Key Features:**
- Basic and advanced filtering
- Multi-field sorting
- Field selection optimization
- Complex logical operators
- Search functionality

### 4. [04_error_handling.py](04_error_handling.py)
**Error Handling Example**
- Comprehensive error handling strategies
- Validation error handling
- HTTP error handling
- Network error handling
- Custom retry logic
- Graceful degradation

**Key Features:**
- Exception type handling
- Custom retry mechanisms
- Graceful degradation patterns
- Logging and monitoring
- Error recovery strategies

### 5. [05_business_scenarios.py](05_business_scenarios.py)
**Business Scenarios Example**
- Real-world business use cases
- Customer analytics dashboard
- Inventory management reporting
- Sales performance analysis
- Vendor relationship management
- Data export and integration

**Key Features:**
- Business intelligence patterns
- Data analysis examples
- Reporting scenarios
- Integration patterns
- Real-time monitoring

### 6. [06_advanced_configuration.py](06_advanced_configuration.py)
**Advanced Configuration Example**
- Custom logging configuration
- Performance optimization
- Environment-specific settings
- Monitoring and metrics
- Batch processing optimization

**Key Features:**
- Custom logger setup
- Performance tuning
- Environment management
- Monitoring capabilities
- Batch processing

### 7. [07_integration_patterns.py](07_integration_patterns.py)
**Integration Patterns Example**
- Design patterns for larger applications
- Dependency injection
- Caching strategies
- Decorator patterns
- Context managers
- Async patterns
- Factory patterns

**Key Features:**
- Software design patterns
- Caching implementations
- Async/await patterns
- Resource management
- Scalable architectures

### 8. [08_testing_examples.py](08_testing_examples.py)
**Testing Examples**
- Unit testing patterns
- Integration testing
- Mocking strategies
- Error scenario testing
- Performance testing

**Key Features:**
- Comprehensive test suites
- Mock implementations
- Error scenario coverage
- Performance benchmarks
- Testing best practices

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- odyn library installed
- Business Central tenant access
- Valid authentication credentials

### Installation
```bash
# Install odyn
pip install odyn

# Or using uv
uv add odyn

# Or using poetry
poetry add odyn
```

### Running Examples
Each example can be run independently:

```bash
# Run basic setup example
python examples/01_basic_setup.py

# Run authentication methods example
python examples/02_authentication_methods.py

# Run OData queries example
python examples/03_odata_queries.py

# Run all examples
python examples/run_all_examples.py
```

### Configuration
Before running any example, update the configuration values:

1. **Base URL**: Replace `your-tenant-id` with your actual Business Central tenant ID
2. **Access Token**: Replace `your-access-token` with your actual access token
3. **Username/Password**: For basic authentication examples, replace with actual credentials

Example configuration:
```python
BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-actual-tenant-id/production/"
ACCESS_TOKEN = "your-actual-access-token"
```

## 📚 Example Categories

### 🔰 Beginner Examples
- `01_basic_setup.py` - Start here if you're new to odyn
- `02_authentication_methods.py` - Learn about authentication options

### 🔍 Intermediate Examples
- `03_odata_queries.py` - Master OData query operations
- `04_error_handling.py` - Build robust error handling

### 💼 Business Examples
- `05_business_scenarios.py` - Real-world business applications
- `06_advanced_configuration.py` - Advanced configuration options

### 🏗️ Advanced Examples
- `07_integration_patterns.py` - Design patterns and architectures
- `08_testing_examples.py` - Testing strategies and patterns

## 🛠️ Common Patterns

### Basic Client Setup
```python
from odyn import Odyn, BearerAuthSession

# Create session
session = BearerAuthSession(token="your-access-token")

# Create client
client = Odyn(
    base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
    session=session
)

# Make requests
customers = client.get("customers")
```

### OData Queries
```python
# Filtering
filtered_customers = client.get(
    "customers",
    params={
        "$filter": "contains(displayName, 'Adventure')",
        "$top": 10,
        "$select": "id,displayName,phoneNumber"
    }
)

# Sorting
sorted_items = client.get(
    "items",
    params={
        "$orderby": "unitPrice desc",
        "$top": 5
    }
)
```

### Error Handling
```python
try:
    customers = client.get("customers")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed")
    elif e.response.status_code == 404:
        print("Endpoint not found")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
```

## 🔧 Customization

### Custom Logging
```python
from loguru import logger

# Create custom logger
custom_logger = logger.bind(component="business-central-client")

# Use with client
client = Odyn(
    base_url=base_url,
    session=session,
    logger=custom_logger
)
```

### Custom Session Configuration
```python
# High-performance session
session = BearerAuthSession(
    token="your-token",
    retries=2,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)

# Reliable session
session = BearerAuthSession(
    token="your-token",
    retries=10,
    backoff_factor=2.0,
    status_forcelist=[408, 429, 500, 502, 503, 504]
)
```

## 📖 Best Practices

### 1. **Authentication**
- Use bearer token authentication for production applications
- Store credentials securely (environment variables, secure config)
- Implement token refresh mechanisms for long-running applications

### 2. **Error Handling**
- Always implement comprehensive error handling
- Use specific exception types for different error scenarios
- Implement retry logic for transient failures
- Log errors appropriately for debugging

### 3. **Performance**
- Use field selection (`$select`) to minimize data transfer
- Implement caching for frequently accessed data
- Use appropriate timeouts for your use case
- Consider batch processing for large datasets

### 4. **Monitoring**
- Implement logging for all API operations
- Monitor response times and error rates
- Set up alerts for critical failures
- Track API usage and rate limits

### 5. **Testing**
- Write unit tests for business logic
- Use mocking for API calls in tests
- Test error scenarios and edge cases
- Implement integration tests for critical workflows

## 🔗 Related Documentation

- [Odyn Documentation](https://github.com/konspec/odyn)
- [Business Central API Documentation](https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
- [OData Query Syntax](https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/use-filtering-in-web-services)

## 🤝 Contributing

If you have additional examples or improvements to existing ones, please:

1. Fork the repository
2. Create a feature branch
3. Add your example with proper documentation
4. Submit a pull request

## 📄 License

These examples are provided under the same license as the odyn library (MIT License).

## 🆘 Support

If you encounter issues with these examples:

1. Check the [main documentation](https://github.com/konspec/odyn)
2. Review the [FAQ](https://github.com/konspec/odyn/blob/main/docs/faq.md)
3. Open an issue on GitHub with details about your problem

---

**Happy coding with odyn! 🚀**
