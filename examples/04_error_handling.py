"""Error Handling Example.

This example demonstrates comprehensive error handling techniques for odyn,
including handling various types of exceptions and implementing robust error recovery.
"""

import time
from typing import Any

import requests
from loguru import logger

from odyn import BearerAuthSession, InvalidLoggerError, InvalidSessionError, InvalidTimeoutError, InvalidURLError, Odyn


def setup_client() -> Odyn:
    """Setup the client with authentication."""
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"

    session = BearerAuthSession(token=ACCESS_TOKEN)
    return Odyn(base_url=BASE_URL, session=session)


def handle_validation_errors() -> None:
    """Demonstrate handling of validation errors during client initialization."""
    print("🔍 Validation Error Handling Examples")
    print("=" * 50)

    # Test invalid URL
    try:
        session = BearerAuthSession(token="dummy-token")
        Odyn(base_url="not-a-valid-url", session=session)
    except InvalidURLError as e:
        print(f"✅ Caught InvalidURLError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test invalid session
    try:
        Odyn(
            base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
            session="not-a-session",
        )
    except InvalidSessionError as e:
        print(f"✅ Caught InvalidSessionError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test invalid timeout
    try:
        session = BearerAuthSession(token="dummy-token")
        Odyn(
            base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
            session=session,
            timeout=(-1, 60),  # Invalid negative timeout
        )
    except InvalidTimeoutError as e:
        print(f"✅ Caught InvalidTimeoutError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test invalid logger
    try:
        session = BearerAuthSession(token="dummy-token")
        Odyn(
            base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
            session=session,
            logger="not-a-logger",
        )
    except InvalidLoggerError as e:
        print(f"✅ Caught InvalidLoggerError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()


def handle_http_errors(client: Odyn) -> None:
    """Demonstrate handling of HTTP errors."""
    print("🌐 HTTP Error Handling Examples")
    print("=" * 50)

    # Test 401 Unauthorized (invalid token)
    try:
        # Create client with invalid token
        invalid_session = BearerAuthSession(token="invalid-token")
        invalid_client = Odyn(base_url=client.base_url, session=invalid_session)
        invalid_client.get("customers")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"✅ Caught 401 Unauthorized: {e}")
        else:
            print(f"⚠️  Unexpected HTTP error: {e.response.status_code} - {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 404 Not Found (invalid endpoint)
    try:
        client.get("non-existent-endpoint")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"✅ Caught 404 Not Found: {e}")
        else:
            print(f"⚠️  Unexpected HTTP error: {e.response.status_code} - {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 403 Forbidden (insufficient permissions)
    try:
        # Try to access admin endpoint without proper permissions
        client.get("adminSettings")  # This might not exist or require admin access
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"✅ Caught 403 Forbidden: {e}")
        else:
            print(f"⚠️  Unexpected HTTP error: {e.response.status_code} - {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()


def handle_network_errors() -> None:
    """Demonstrate handling of network-related errors."""
    print("🌍 Network Error Handling Examples")
    print("=" * 50)

    # Test connection timeout
    try:
        # Create client with very short timeout
        fast_session = BearerAuthSession(token="dummy-token")
        fast_client = Odyn(
            base_url="https://httpbin.org/delay/10",  # 10 second delay
            session=fast_session,
            timeout=(1, 1),  # 1 second timeout
        )
        fast_client.get("")
    except requests.exceptions.ConnectTimeout as e:
        print(f"✅ Caught ConnectTimeout: {e}")
    except requests.exceptions.ReadTimeout as e:
        print(f"✅ Caught ReadTimeout: {e}")
    except requests.exceptions.Timeout as e:
        print(f"✅ Caught Timeout: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test connection refused (invalid host)
    try:
        invalid_session = BearerAuthSession(token="dummy-token")
        invalid_client = Odyn(base_url="https://invalid-host-that-does-not-exist.com/", session=invalid_session)
        invalid_client.get("customers")
    except requests.exceptions.ConnectionError as e:
        print(f"✅ Caught ConnectionError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()


def handle_json_parsing_errors(client: Odyn) -> None:
    """Demonstrate handling of JSON parsing errors."""
    print("📄 JSON Parsing Error Handling Examples")
    print("=" * 50)

    # Note: This is a theoretical example since odyn handles JSON parsing internally
    # In practice, you might encounter this if the API returns malformed JSON

    try:
        # This would only happen if the API returns non-JSON response
        # which is rare with Business Central APIs
        client.get("customers")
    except ValueError as e:
        if "Failed to decode JSON" in str(e):
            print(f"✅ Caught JSON parsing error: {e}")
        else:
            print(f"⚠️  Unexpected ValueError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()


def retry_with_exponential_backoff(client: Odyn, max_retries: int = 3) -> None:
    """Demonstrate custom retry logic with exponential backoff."""
    print("🔄 Custom Retry Logic Example")
    print("=" * 50)

    def make_request_with_retry(endpoint: str, max_attempts: int = max_retries) -> list[dict[str, Any]] | None:
        """Make a request with custom retry logic."""
        for attempt in range(max_attempts):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_attempts}")
                return client.get(endpoint, params={"$top": 5})

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_attempts - 1:
                        wait_time = 2**attempt  # Exponential backoff
                        print(f"⚠️  HTTP {e.response.status_code}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    print(f"❌ Max retries reached for HTTP {e.response.status_code}")
                    raise
                print(f"❌ Non-retryable HTTP error: {e.response.status_code}")
                raise

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt < max_attempts - 1:
                    wait_time = 2**attempt
                    print(f"⚠️  Network error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                print("❌ Max retries reached for network error")
                raise

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                raise

        return None

    try:
        result = make_request_with_retry("customers")
        if result:
            print(f"✅ Successfully retrieved {len(result)} customers after retries")
    except Exception as e:
        print(f"❌ All retry attempts failed: {e}")

    print()


def graceful_degradation_example(client: Odyn) -> None:
    """Demonstrate graceful degradation when some operations fail."""
    print("🛡️  Graceful Degradation Example")
    print("=" * 50)

    def safe_get_data(endpoint: str, fallback_data: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        """Safely get data with fallback."""
        try:
            return client.get(endpoint, params={"$top": 5})
        except requests.exceptions.HTTPError as e:
            print(f"⚠️  HTTP error for {endpoint}: {e.response.status_code}")
            return fallback_data or []
        except Exception as e:
            print(f"⚠️  Unexpected error for {endpoint}: {e}")
            return fallback_data or []

    # Try to get multiple types of data, with graceful handling of failures
    data_sources = {"customers": [], "vendors": [], "items": [], "salesOrders": []}

    for endpoint in data_sources:
        data = safe_get_data(endpoint)
        data_sources[endpoint] = data
        print(f"📊 {endpoint}: {len(data)} records retrieved")

    # Summary
    total_records = sum(len(data) for data in data_sources.values())
    print(f"\n📈 Total records across all endpoints: {total_records}")

    print()


def logging_and_monitoring_example(client: Odyn) -> None:
    """Demonstrate logging and monitoring for error tracking."""
    print("📝 Logging and Monitoring Example")
    print("=" * 50)

    # Create a custom logger for this example
    custom_logger = logger.bind(component="business-central-client", operation="data-retrieval")

    def monitored_request(endpoint: str) -> list[dict[str, Any]] | None:
        """Make a monitored request with detailed logging."""
        start_time = time.time()

        try:
            custom_logger.info(f"Starting request to {endpoint}")
            result = client.get(endpoint, params={"$top": 3})

            duration = time.time() - start_time
            custom_logger.info(
                f"Successfully retrieved {len(result)} records from {endpoint}",
                duration=duration,
                record_count=len(result),
            )

        except requests.exceptions.HTTPError as e:
            duration = time.time() - start_time
            custom_logger.exception(
                f"HTTP error for {endpoint}",
                status_code=e.response.status_code,
                duration=duration,
                error_message=str(e),
            )
            return None

        except Exception as e:
            duration = time.time() - start_time
            custom_logger.exception(f"Unexpected error for {endpoint}", duration=duration, error_type=type(e).__name__)
            return None

        return result

    # Test monitored requests
    endpoints = ["customers", "vendors", "items"]

    for endpoint in endpoints:
        result = monitored_request(endpoint)
        if result:
            print(f"✅ {endpoint}: {len(result)} records")
        else:
            print(f"❌ {endpoint}: Failed")

    print()


def main() -> None:
    """Run all error handling examples."""
    print("🚀 Odyn Error Handling Examples")
    print("=" * 60)
    print()

    # Setup client
    client = setup_client()

    # Run all examples
    handle_validation_errors()
    handle_http_errors(client)
    handle_network_errors(client)
    handle_json_parsing_errors(client)
    retry_with_exponential_backoff(client)
    graceful_degradation_example(client)
    logging_and_monitoring_example(client)

    print("📝 Note: Replace placeholder values with your actual credentials")
    print("🛡️  Always implement proper error handling in production applications")


if __name__ == "__main__":
    main()
