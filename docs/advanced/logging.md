# Logging in Odyn

Odyn uses the powerful [loguru](https://github.com/Delgan/loguru) library for its internal logging. This provides users with flexible, structured, and easy-to-configure logging right out of the box.

## Default Logging

By default, the `Odyn` client will use a standard `loguru` logger instance without any specific configuration. This means logs will be printed to `sys.stderr` at the `DEBUG` level.

```python
from odyn import Odyn, BearerAuthSession

# This client will use the default loguru logger.
client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("your-token")
)
```

## Providing a Custom Logger

You can easily integrate Odyn with your application's existing `loguru` setup by passing your own logger instance. This is the recommended approach for production applications.

```python
from loguru import logger
from odyn import Odyn, BearerAuthSession

# Configure your application's logger
logger.add("my_app.log", level="INFO", rotation="10 MB")

# Bind context and pass the logger to the client
service_logger = logger.bind(component="odyn-client")

client = Odyn(
    base_url="https://api.example.com/",
    session=BearerAuthSession("your-token"),
    logger=service_logger
)
```

## What Gets Logged

The `Odyn` client logs various events during its lifecycle. The logs are structured, meaning extra data is often attached to the log record for better context.

### Log Levels

Here’s a summary of what is logged at each level by the `Odyn` client:

- **`DEBUG`**:
    - Client initialization steps.
    - Validation success for URL, session, and timeout.
    - Request URL construction.
    - Details of outgoing requests (method, URL, params).
    - Details of incoming responses (status code, URL).
    - Pagination progress (pages fetched, item counts).
- **`INFO`**:
    - Final confirmation of successful client initialization.
    - Completion of a full pagination cycle for an endpoint.
- **`ERROR`**:
    - Validation failures (`InvalidURLError`, `InvalidSessionError`, etc.).
    - HTTP errors (4xx, 5xx), network errors, or JSON decoding failures. These logs include the full exception traceback.

### Example Log Output

Here is what you might see in your logs when making a simple `get` call:

```log
DEBUG: Initializing Odyn client...
DEBUG: Using provided custom logger.
DEBUG: Base URL validation successful url='https://api.example.com/'
DEBUG: Session validation successful.
DEBUG: Timeout validation successful timeout=(60, 60)
INFO: Odyn client initialized successfully. base_url='https://api.example.com/' timeout=(60, 60)
DEBUG: Initiating GET request with pagination endpoint='customers' params=None
DEBUG: Built request URL final_url='https://api.example.com/customers'
DEBUG: Sending request method='GET' url='https://api.example.com/customers' params=None headers=None
DEBUG: Request completed status_code=200 url='https://api.example.com/customers'
DEBUG: Fetched 50 items from page 1. Total items so far: 50 count=50 page_num=1 total=50
DEBUG: No more pages found for endpoint 'customers'. endpoint='customers'
INFO: Finished fetching all pages for endpoint 'customers'. Total items: 50 endpoint='customers' total=50
```

## Capturing Retry Attempts

The `OdynSession` automatically retries failed requests (e.g., on HTTP `502`, `503`, `504`, `429`). These retries are handled by the underlying `urllib3` library, which logs to the standard `logging` module, not `loguru`, by default.

To see these retry attempts, you must configure `loguru` to intercept messages from the standard `logging` library. This is straightforward to set up.

### How to Intercept Standard Logging

Add this `InterceptHandler` to your application's setup to redirect `logging` messages to `loguru`.

```python
import logging
from loguru import logger
from odyn import Odyn, OdynSession

# 1. Define the InterceptHandler
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# 2. Configure logging to use the handler
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# 3. Now, your Odyn client will show retry attempts
# Note: Set the session retries to a low number for easy testing
session = OdynSession(retries=1)
client = Odyn(
    base_url="https://api.example.com/",
    session=session,
    logger=logger
)
```

With this configuration, you will now see `WARNING` level logs from `urllib3` when a retry occurs.

## Advanced Configuration & Best Practices

### Structured Logging (JSON)

For production systems, structured JSON logs are highly recommended. They are machine-readable and integrate well with log analysis platforms.

```python
from loguru import logger

logger.configure(
    handlers=[
        {
            "sink": "logs/odyn.json",
            "format": "{message}", # The message itself contains key-value pairs
            "serialize": True,    # Convert to JSON
            "level": "INFO",
            "rotation": "1 day",
            "retention": "30 days",
        }
    ]
)

# Use a bound logger to add consistent context to all logs
client_logger = logger.bind(
    client_id="bc-client-001",
    tenant="production"
)

# client = Odyn(..., logger=client_logger)
```

### Filtering Logs

You can add filters to send different logs to different places. For example, you could send `ERROR` logs to a separate file.

```python
# Send ERROR logs to a separate file
logger.add(
    "logs/errors.log",
    level="ERROR",
    format="{time} {level} {extra} {message}"
)

# Send performance-related logs to another file
logger.add(
    "logs/performance.log",
    filter=lambda record: "performance" in record["extra"]
)
```

### Use `enqueue=True` for Performance

In high-throughput applications, logging can become a bottleneck. Setting `enqueue=True` makes logging calls non-blocking by moving the work to a separate process.

```python
logger.add(
    "app.log",
    enqueue=True,  # Make logging asynchronous
    level="INFO"
)
```

## Related Documentation

- [Odyn Client API](../usage/odyn.md) - See the `logger` parameter.
- [Configuration](configuration.md) - General configuration patterns.
- [Exception Handling](../usage/exceptions.md) - How errors are handled.
- [Troubleshooting](../troubleshooting.md) - Using logs for debugging.
