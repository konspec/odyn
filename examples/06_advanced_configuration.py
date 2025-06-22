"""Advanced Configuration Example.

This example demonstrates advanced configuration options and customizations for odyn,
including custom logging, session management, and performance optimizations.
"""

import os
import time

from loguru import logger

from odyn import BearerAuthSession, Odyn, OdynSession


def setup_custom_logger() -> None:
    """Setup a custom logger with specific configuration."""
    print("📝 Custom Logger Configuration Example")
    print("=" * 50)

    # Remove default logger
    logger.remove()

    # Add custom logger with specific format and level
    logger.add(
        "logs/odyn_client.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    # Add console logger with custom format
    logger.add(
        lambda msg: print(f"🔍 {msg}"), format="{time:HH:mm:ss} | {level} | {message}", level="DEBUG", colorize=True
    )

    # Create a bound logger for this component
    custom_logger = logger.bind(component="business-central-client", version="1.0")

    print("✅ Custom logger configured with:")
    print("  • File logging to logs/odyn_client.log")
    print("  • Console output with custom format")
    print("  • Log rotation and compression")
    print("  • Component-specific binding")

    return custom_logger


def advanced_session_configuration() -> tuple[BearerAuthSession, BearerAuthSession, BearerAuthSession]:
    """Demonstrate advanced session configuration options."""
    print("\n⚙️  Advanced Session Configuration Example")
    print("=" * 50)

    # Configuration with aggressive retry settings
    aggressive_session = BearerAuthSession(
        token="your-access-token",
        retries=15,  # More retries for critical operations
        backoff_factor=0.3,  # Faster backoff
        status_forcelist=[408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
    )

    # Configuration for high-traffic scenarios
    high_traffic_session = BearerAuthSession(
        token="your-access-token",
        retries=3,  # Fewer retries to avoid overwhelming the server
        backoff_factor=1.0,  # Standard backoff
        status_forcelist=[429, 500, 502, 503, 504],  # Only retry on server errors
    )

    # Configuration for development/testing
    dev_session = BearerAuthSession(
        token="your-access-token",
        retries=1,  # Minimal retries for fast feedback
        backoff_factor=0.1,  # Very fast backoff
        status_forcelist=[500, 502, 503, 504],  # Only retry on server errors
    )

    print("✅ Session configurations created:")
    print("  • Aggressive: 15 retries, fast backoff, comprehensive error list")
    print("  • High Traffic: 3 retries, standard backoff, server errors only")
    print("  • Development: 1 retry, very fast backoff, minimal error list")

    return aggressive_session, high_traffic_session, dev_session


def custom_session_with_headers() -> OdynSession:
    """Demonstrate custom session with additional headers and configuration."""
    print("\n🔧 Custom Session with Headers Example")
    print("=" * 50)

    # Create a custom session
    custom_session = OdynSession(retries=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])

    # Add custom headers for tracking and monitoring
    custom_session.headers.update(
        {
            "Authorization": "Bearer your-access-token",
            "User-Agent": "MyBusinessApp/2.1.0",
            "X-Request-ID": f"req_{int(time.time())}",
            "X-Client-Version": "1.0.0",
            "X-Environment": "production",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    # Add custom request hooks for monitoring
    def log_request(request):
        logger.info(f"Making request to {request.url}")
        return request

    def log_response(response):
        logger.info(f"Received response {response.status_code} from {response.url}")
        return response

    print("✅ Custom session configured with:")
    print("  • Custom headers for tracking and identification")
    print("  • Request/response logging hooks")
    print("  • Environment-specific configuration")

    return custom_session


def performance_optimized_client() -> Odyn:
    """Demonstrate performance-optimized client configuration."""
    print("\n🚀 Performance Optimized Client Example")
    print("=" * 50)

    # Create a session optimized for performance
    perf_session = BearerAuthSession(
        token="your-access-token",
        retries=2,  # Minimal retries for speed
        backoff_factor=0.1,  # Fast backoff
        status_forcelist=[500, 502, 503, 504],  # Only critical server errors
    )

    # Create client with optimized settings
    perf_client = Odyn(
        base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
        session=perf_session,
        timeout=(5, 30),  # Fast connect, reasonable read timeout
        logger=logger.bind(component="perf-client"),
    )

    print("✅ Performance-optimized client configured:")
    print("  • Fast connection timeout (5s)")
    print("  • Reasonable read timeout (30s)")
    print("  • Minimal retries for speed")
    print("  • Fast backoff strategy")

    return perf_client


def environment_specific_configuration() -> Odyn:
    """Demonstrate environment-specific configuration."""
    print("\n🌍 Environment-Specific Configuration Example")
    print("=" * 50)

    # Get environment
    env = os.getenv("ENVIRONMENT", "development")

    # Environment-specific configurations
    configs = {
        "development": {
            "base_url": "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/sandbox/",
            "timeout": (10, 60),
            "retries": 1,
            "backoff_factor": 0.1,
            "log_level": "DEBUG",
        },
        "staging": {
            "base_url": "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/staging/",
            "timeout": (10, 60),
            "retries": 3,
            "backoff_factor": 0.5,
            "log_level": "INFO",
        },
        "production": {
            "base_url": "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
            "timeout": (5, 30),
            "retries": 5,
            "backoff_factor": 1.0,
            "log_level": "WARNING",
        },
    }

    config = configs.get(env, configs["development"])

    # Create session with environment-specific settings
    env_session = BearerAuthSession(
        token="your-access-token", retries=config["retries"], backoff_factor=config["backoff_factor"]
    )

    # Create client with environment-specific settings
    env_client = Odyn(
        base_url=config["base_url"], session=env_session, timeout=config["timeout"], logger=logger.bind(environment=env)
    )

    print(f"✅ Environment-specific client configured for {env}:")
    print(f"  • Base URL: {config['base_url']}")
    print(f"  • Timeout: {config['timeout']}")
    print(f"  • Retries: {config['retries']}")
    print(f"  • Backoff Factor: {config['backoff_factor']}")
    print(f"  • Log Level: {config['log_level']}")

    return env_client


def monitoring_and_metrics_client() -> Odyn:
    """Demonstrate client with monitoring and metrics capabilities."""
    print("\n📊 Monitoring and Metrics Client Example")
    print("=" * 50)

    class MonitoredOdynSession(OdynSession):
        """Custom session with monitoring capabilities."""

        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            super().__init__(*args, **kwargs)
            self.request_count = 0
            self.total_response_time = 0
            self.error_count = 0

        def request(self, method, url, **kwargs):
            start_time = time.time()
            self.request_count += 1

            try:
                response = super().request(method, url, **kwargs)
                response_time = time.time() - start_time
                self.total_response_time += response_time

                logger.info(
                    "Request completed",
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    response_time=response_time,
                    total_requests=self.request_count,
                )

            except Exception as e:
                self.error_count += 1
                logger.error("Request failed", method=method, url=url, error=str(e), total_errors=self.error_count)
                raise

            return response

    # Create monitored session
    monitored_session = MonitoredOdynSession(token="your-access-token", retries=3, backoff_factor=0.5)

    # Create client with monitoring
    monitored_client = Odyn(
        base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
        session=monitored_session,
        logger=logger.bind(component="monitored-client"),
    )

    print("✅ Monitored client configured with:")
    print("  • Request counting")
    print("  • Response time tracking")
    print("  • Error counting")
    print("  • Detailed logging")

    return monitored_client


def batch_processing_client() -> Odyn:
    """Demonstrate client optimized for batch processing."""
    print("\n📦 Batch Processing Client Example")
    print("=" * 50)

    # Create session optimized for batch operations
    batch_session = BearerAuthSession(
        token="your-access-token",
        retries=10,  # More retries for batch operations
        backoff_factor=2.0,  # Slower backoff to avoid overwhelming
        status_forcelist=[429, 500, 502, 503, 504],
    )

    # Create client with batch-optimized settings
    batch_client = Odyn(
        base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
        session=batch_session,
        timeout=(30, 300),  # Longer timeouts for batch operations
        logger=logger.bind(component="batch-client"),
    )

    print("✅ Batch processing client configured:")
    print("  • Extended timeouts for large operations")
    print("  • More retries for reliability")
    print("  • Slower backoff to avoid rate limiting")
    print("  • Batch-specific logging")

    return batch_client


def main() -> None:
    """Run all advanced configuration examples."""
    print("🚀 Odyn Advanced Configuration Examples")
    print("=" * 60)
    print()

    setup_custom_logger()

    advanced_session_configuration()
    custom_session_with_headers()
    performance_optimized_client()
    environment_specific_configuration()
    monitoring_and_metrics_client()
    batch_processing_client()

    print("\n📝 Note: Replace placeholder values with your actual credentials")
    print("🔧 These configurations demonstrate advanced odyn customization options")
    print("📊 Choose the configuration that best fits your use case")


if __name__ == "__main__":
    main()
