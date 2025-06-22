# Logging

Odyn uses [loguru](https://github.com/Delgan/loguru) for comprehensive logging throughout the library. This provides structured logging with rich formatting, automatic rotation, and easy integration with existing logging systems.

## Default Logging Behavior

By default, Odyn uses loguru's default logger if no custom logger is provided:

```python
from odyn import Odyn, BearerAuthSession

# Uses default loguru logger
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token")
)
```

## What Gets Logged

Odyn logs various events at different levels:

### DEBUG Level
- Client initialization details
- URL validation and sanitization
- Session validation
- Timeout validation
- Request URL construction
- Request details (method, URL, parameters, headers)
- Response details (status code, URL)
- Pagination progress
- Retry attempts and backoff timing

### INFO Level
- Client initialization success
- Request completion
- Pagination completion

### WARNING Level
- Retry attempts (when configured)
- Non-critical validation issues

### ERROR Level
- Validation failures
- HTTP errors
- Network errors
- JSON decode errors
- OData response format errors

### Example Log Output

```
2024-01-15 10:30:15.123 | DEBUG | Initializing Odyn client...
2024-01-15 10:30:15.124 | DEBUG | Using provided custom logger.
2024-01-15 10:30:15.125 | DEBUG | Base URL validation successful | url=https://api.example.com/
2024-01-15 10:30:15.126 | DEBUG | Session validation successful.
2024-01-15 10:30:15.127 | DEBUG | Timeout validation successful | timeout=(60, 60)
2024-01-15 10:30:15.128 | INFO  | Odyn client initialized successfully. | base_url=https://api.example.com/ | timeout=(60, 60)
2024-01-15 10:30:15.129 | DEBUG | Initiating GET request with pagination | endpoint=customers | params=None
2024-01-15 10:30:15.130 | DEBUG | Built request URL | final_url=https://api.example.com/customers
2024-01-15 10:30:15.131 | DEBUG | Sending request | method=GET | url=https://api.example.com/customers | params=None | headers=None
2024-01-15 10:30:16.234 | DEBUG | Request completed | status_code=200 | url=https://api.example.com/customers
2024-01-15 10:30:16.235 | DEBUG | Fetched 50 items from page 1. Total items so far: 50 | count=50 | page_num=1 | total=50
2024-01-15 10:30:16.236 | DEBUG | No more pages found for endpoint 'customers'. | endpoint=customers
2024-01-15 10:30:16.237 | INFO  | Finished fetching all pages for endpoint 'customers'. Total items: 50 | endpoint=customers | total=50
```

## Custom Logger Configuration

### Using a Custom Logger

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Create a custom logger
custom_logger = logger.bind(component="business-central-client")

# Use the custom logger
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=custom_logger
)
```

### Logger with Context

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Create logger with context
context_logger = logger.bind(
    component="odyn-client",
    tenant="production",
    environment="prod"
)

client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=context_logger
)
```

### Structured Logging

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Configure structured logging
logger.configure(
    handlers=[
        {
            "sink": "logs/odyn.json",
            "format": "{time} | {level} | {extra} | {message}",
            "serialize": True,  # Output as JSON
            "rotation": "1 day",
            "retention": "30 days"
        }
    ]
)

# Create client with structured logging
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=logger.bind(client_id="bc-client-001")
)
```

## Log Levels and Filtering

### Setting Log Levels

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Configure logger with specific level
logger.remove()  # Remove default handler
logger.add(
    "logs/odyn.log",
    level="INFO",  # Only INFO and above
    format="{time} | {level} | {message}",
    rotation="1 day"
)

client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=logger
)
```

### Filtering by Component

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Filter logs by component
def filter_odyn_logs(record):
    """Filter to only show Odyn-related logs."""
    return "odyn" in record["extra"].get("component", "")

logger.add(
    "logs/odyn_only.log",
    filter=filter_odyn_logs,
    format="{time} | {level} | {extra[component]} | {message}"
)

odyn_logger = logger.bind(component="odyn-client")
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=odyn_logger
)
```

### Environment-Based Logging

```python
import os
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Configure logging based on environment
environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    # Production: Log to file with rotation
    logger.add(
        "logs/odyn.log",
        level="INFO",
        format="{time} | {level} | {extra} | {message}",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
elif environment == "development":
    # Development: Console output with colors
    logger.add(
        lambda msg: print(msg, end=""),
        level="DEBUG",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=logger.bind(env=environment)
)
```

## Integration with Existing Logging Systems

### Integration with Standard Logging

```python
import logging
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Intercept standard logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# Setup integration
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Create Odyn client with integrated logging
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=logger.bind(component="odyn")
)
```

### Integration with Application Logging

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

class BusinessCentralService:
    def __init__(self, base_url: str, token: str):
        # Create logger for this service
        self.logger = logger.bind(
            service="business-central",
            component="odyn-client"
        )

        # Create Odyn client with service logger
        session = BearerAuthSession(token)
        self.client = Odyn(
            base_url=base_url,
            session=session,
            logger=self.logger
        )

    def get_customers(self):
        self.logger.info("Fetching customers from Business Central")
        try:
            customers = self.client.get("customers")
            self.logger.info(f"Successfully retrieved {len(customers)} customers")
            return customers
        except Exception as e:
            self.logger.error(f"Failed to fetch customers: {e}")
            raise

# Usage
service = BusinessCentralService(
    base_url="https://api.example.com/",
    token="your-token"
)
customers = service.get_customers()
```

## Advanced Logging Patterns

### Request/Response Logging

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession
import time

class LoggedOdynClient:
    def __init__(self, base_url: str, token: str):
        self.logger = logger.bind(component="odyn-client")
        session = BearerAuthSession(token)
        self.client = Odyn(
            base_url=base_url,
            session=session,
            logger=self.logger
        )

    def get(self, endpoint: str, params=None):
        start_time = time.time()

        self.logger.info(f"Starting request to {endpoint}")
        if params:
            self.logger.debug(f"Request parameters: {params}")

        try:
            result = self.client.get(endpoint, params=params)
            duration = time.time() - start_time

            self.logger.info(
                f"Request completed successfully",
                endpoint=endpoint,
                duration=f"{duration:.2f}s",
                result_count=len(result)
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Request failed",
                endpoint=endpoint,
                duration=f"{duration:.2f}s",
                error=str(e)
            )
            raise

# Usage
client = LoggedOdynClient("https://api.example.com/", "token")
customers = client.get("customers")
```

### Performance Monitoring

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession
import time
from contextlib import contextmanager

class PerformanceMonitoredClient:
    def __init__(self, base_url: str, token: str):
        self.logger = logger.bind(component="odyn-performance")
        session = BearerAuthSession(token)
        self.client = Odyn(
            base_url=base_url,
            session=session,
            logger=self.logger
        )

    @contextmanager
    def measure_performance(self, operation: str):
        """Context manager for measuring operation performance."""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            yield
        finally:
            duration = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_diff = end_memory - start_memory

            self.logger.info(
                f"Performance metrics",
                operation=operation,
                duration=f"{duration:.3f}s",
                memory_usage=f"{end_memory:.2f}MB",
                memory_delta=f"{memory_diff:+.2f}MB"
            )

    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def get(self, endpoint: str, params=None):
        with self.measure_performance(f"GET {endpoint}"):
            return self.client.get(endpoint, params=params)

# Usage
client = PerformanceMonitoredClient("https://api.example.com/", "token")
customers = client.get("customers")
```

### Error Tracking

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession
import traceback

class ErrorTrackedClient:
    def __init__(self, base_url: str, token: str):
        self.logger = logger.bind(component="odyn-error-tracking")
        session = BearerAuthSession(token)
        self.client = Odyn(
            base_url=base_url,
            session=session,
            logger=self.logger
        )
        self.error_count = 0

    def get(self, endpoint: str, params=None):
        try:
            return self.client.get(endpoint, params=params)
        except Exception as e:
            self.error_count += 1

            # Log detailed error information
            self.logger.error(
                f"Error #{self.error_count} occurred",
                endpoint=endpoint,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                params=params
            )

            # Re-raise the exception
            raise

# Usage
client = ErrorTrackedClient("https://api.example.com/", "token")
try:
    customers = client.get("customers")
except Exception as e:
    print(f"Error occurred: {e}")
```

## Log File Management

### Log Rotation and Retention

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Configure comprehensive log management
logger.add(
    "logs/odyn.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra} | {message}",
    rotation="1 day",           # Rotate daily
    retention="30 days",        # Keep logs for 30 days
    compression="zip",          # Compress old logs
    backtrace=True,             # Include stack traces
    diagnose=True,              # Include variable values
    enqueue=True                # Thread-safe logging
)

client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=logger.bind(component="odyn")
)
```

### Multiple Log Files

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Configure multiple log files for different purposes
logger.add(
    "logs/odyn_errors.log",
    level="ERROR",
    format="{time} | {level} | {extra} | {message}",
    rotation="1 day",
    retention="90 days"
)

logger.add(
    "logs/odyn_performance.log",
    level="INFO",
    format="{time} | {level} | {extra} | {message}",
    filter=lambda record: "performance" in record["extra"],
    rotation="1 day",
    retention="30 days"
)

logger.add(
    "logs/odyn_debug.log",
    level="DEBUG",
    format="{time} | {level} | {extra} | {message}",
    rotation="1 day",
    retention="7 days"
)

client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("token"),
    logger=logger.bind(component="odyn")
)
```

## Best Practices

### 1. Use Structured Logging

```python
# ✅ Good - Structured logging with context
logger = logger.bind(
    component="odyn-client",
    tenant="production",
    user_id="user123"
)

# ❌ Avoid - Unstructured logging
print(f"Error: {error}")
```

### 2. Set Appropriate Log Levels

```python
# Development - Detailed logging
logger.add("dev.log", level="DEBUG")

# Production - Important events only
logger.add("prod.log", level="INFO")
```

### 3. Include Relevant Context

```python
# ✅ Good - Include relevant context
logger.error(
    "API request failed",
    endpoint="customers",
    status_code=500,
    retry_count=3,
    user_id="user123"
)

# ❌ Avoid - Minimal context
logger.error("Request failed")
```

### 4. Use Log Rotation

```python
# ✅ Good - Prevent log files from growing too large
logger.add(
    "app.log",
    rotation="1 day",
    retention="30 days",
    compression="zip"
)
```

### 5. Monitor Log Performance

```python
# Use async logging for high-volume applications
logger.add(
    "high_volume.log",
    enqueue=True,  # Thread-safe, async logging
    level="INFO"
)
```

## Related Documentation

- [Odyn Client API](../usage/odyn.md) - Logger parameter usage
- [Configuration](configuration.md) - Logging configuration patterns
- [Exception Handling](../usage/exceptions.md) - Error logging strategies
- [Troubleshooting](../troubleshooting.md) - Using logs for debugging
