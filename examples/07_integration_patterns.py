"""Integration Patterns Example.

This example demonstrates integration patterns and best practices for using odyn
in larger applications, including dependency injection, caching, and async patterns.
"""

import asyncio
import json
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any

from odyn import BearerAuthSession, Odyn


def setup_client() -> Odyn:
    """Setup the client with authentication."""
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"

    session = BearerAuthSession(token=ACCESS_TOKEN)
    return Odyn(base_url=BASE_URL, session=session)


def dependency_injection_pattern():
    """Demonstrate dependency injection pattern for odyn client."""
    print("🔧 Dependency Injection Pattern Example")
    print("=" * 50)

    @dataclass
    class BusinessCentralConfig:
        """Configuration class for Business Central client."""

        base_url: str
        access_token: str
        timeout: tuple[int, int] = (60, 60)
        retries: int = 5
        backoff_factor: float = 1.0

    class BusinessCentralService:
        """Service class that uses odyn client through dependency injection."""

        def __init__(self, config: BusinessCentralConfig):
            self.config = config
            self._client: Odyn | None = None

        @property
        def client(self) -> Odyn:
            """Lazy initialization of the client."""
            if self._client is None:
                session = BearerAuthSession(
                    token=self.config.access_token,
                    retries=self.config.retries,
                    backoff_factor=self.config.backoff_factor,
                )
                self._client = Odyn(base_url=self.config.base_url, session=session, timeout=self.config.timeout)
            return self._client

        def get_customers(self, limit: int = 100) -> list[dict[str, Any]]:
            """Get customers with dependency injection."""
            return self.client.get("customers", params={"$top": limit})

        def get_items(self, limit: int = 100) -> list[dict[str, Any]]:
            """Get items with dependency injection."""
            return self.client.get("items", params={"$top": limit})

    # Usage example
    config = BusinessCentralConfig(
        base_url="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
        access_token="your-access-token",
        timeout=(30, 60),
        retries=3,
    )

    service = BusinessCentralService(config)

    print("✅ Dependency injection pattern implemented:")
    print("  • Configuration class for settings")
    print("  • Service class with lazy client initialization")
    print("  • Clean separation of concerns")
    print("  • Easy testing and mocking")

    return service


def caching_pattern():
    """Demonstrate caching patterns for odyn requests."""
    print("\n💾 Caching Pattern Example")
    print("=" * 50)

    class CachedBusinessCentralClient:
        """Client with caching capabilities."""

        def __init__(self, client: Odyn):
            self.client = client
            self._cache: dict[str, Any] = {}
            self._cache_timestamps: dict[str, float] = {}
            self.cache_ttl = 300  # 5 minutes default TTL

        def _get_cache_key(self, endpoint: str, params: dict[str, Any] | None = None) -> str:
            """Generate cache key for request."""
            param_str = json.dumps(params or {}, sort_keys=True)
            return f"{endpoint}:{param_str}"

        def _is_cache_valid(self, cache_key: str) -> bool:
            """Check if cache entry is still valid."""
            if cache_key not in self._cache_timestamps:
                return False

            age = time.time() - self._cache_timestamps[cache_key]
            return age < self.cache_ttl

        def get(
            self,
            endpoint: str,
            params: dict[str, Any] | None = None,
            use_cache: bool = True,  # noqa: FBT001, FBT002
        ) -> list[dict[str, Any]]:
            """Get data with optional caching."""
            if not use_cache:
                return self.client.get(endpoint, params=params)

            cache_key = self._get_cache_key(endpoint, params)

            # Check cache first
            if self._is_cache_valid(cache_key):
                print(f"📋 Cache hit for {endpoint}")
                return self._cache[cache_key]

            # Fetch from API
            print(f"🌐 Fetching from API: {endpoint}")
            data = self.client.get(endpoint, params=params)

            # Store in cache
            self._cache[cache_key] = data
            self._cache_timestamps[cache_key] = time.time()

            return data

        def clear_cache(self):
            """Clear all cached data."""
            self._cache.clear()
            self._cache_timestamps.clear()
            print("🗑️  Cache cleared")

        def get_cache_stats(self) -> dict[str, Any]:
            """Get cache statistics."""
            return {
                "cache_size": len(self._cache),
                "cache_ttl": self.cache_ttl,
                "oldest_entry": min(self._cache_timestamps.values()) if self._cache_timestamps else None,
                "newest_entry": max(self._cache_timestamps.values()) if self._cache_timestamps else None,
            }

    # Usage example
    base_client = setup_client()
    cached_client = CachedBusinessCentralClient(base_client)

    print("✅ Caching pattern implemented:")
    print("  • TTL-based cache invalidation")
    print("  • Cache key generation from endpoint and params")
    print("  • Cache statistics and management")
    print("  • Optional cache bypass")

    return cached_client


def decorator_pattern():
    """Demonstrate decorator patterns for odyn operations."""
    print("\n🎨 Decorator Pattern Example")
    print("=" * 50)

    def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
        """Decorator to retry operations on failure."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            print(f"⚠️  Attempt {attempt + 1} failed, retrying in {delay}s...")
                            time.sleep(delay)
                        else:
                            print(f"❌ All {max_retries} attempts failed")

                raise last_exception

            return wrapper

        return decorator

    def log_operation(operation_name: str):
        """Decorator to log operation details."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                print(f"🚀 Starting {operation_name}...")

                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    print(f"✅ {operation_name} completed in {duration:.2f}s")
                except Exception as e:
                    duration = time.time() - start_time
                    print(f"❌ {operation_name} failed after {duration:.2f}s: {e}")
                    raise
                return result

            return wrapper

        return decorator

    def validate_response(func: Callable) -> Callable:
        """Decorator to validate response data."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if not isinstance(result, list):
                raise ValueError("Expected list response")

            if not result:
                print("⚠️  Empty response received")

            return result

        return wrapper

    # Usage example with decorators
    class DecoratedBusinessCentralService:
        def __init__(self, client: Odyn):
            self.client = client

        @retry_on_failure(max_retries=3, delay=1.0)
        @log_operation("customer_fetch")
        @validate_response
        def get_customers(self, limit: int = 100) -> list[dict[str, Any]]:
            return self.client.get("customers", params={"$top": limit})

        @retry_on_failure(max_retries=3, delay=1.0)
        @log_operation("item_fetch")
        @validate_response
        def get_items(self, limit: int = 100) -> list[dict[str, Any]]:
            return self.client.get("items", params={"$top": limit})

    # Usage
    base_client = setup_client()
    decorated_service = DecoratedBusinessCentralService(base_client)

    print("✅ Decorator pattern implemented:")
    print("  • Retry decorator for resilience")
    print("  • Logging decorator for monitoring")
    print("  • Validation decorator for data integrity")
    print("  • Composable and reusable decorators")

    return decorated_service


def context_manager_pattern():
    """Demonstrate context manager patterns for odyn operations."""
    print("\n🔒 Context Manager Pattern Example")
    print("=" * 50)

    @contextmanager
    def business_central_session(config: dict[str, Any]):
        """Context manager for Business Central session."""
        session = None
        client = None

        try:
            print("🔗 Establishing Business Central connection...")
            session = BearerAuthSession(
                token=config["access_token"],
                retries=config.get("retries", 5),
                backoff_factor=config.get("backoff_factor", 1.0),
            )

            client = Odyn(base_url=config["base_url"], session=session, timeout=config.get("timeout", (60, 60)))

            print("✅ Business Central connection established")
            yield client

        except Exception as e:
            print(f"❌ Failed to establish connection: {e}")
            raise
        finally:
            if session:
                session.close()
                print("🔌 Business Central connection closed")

    @contextmanager
    def rate_limited_operation(client: Odyn, max_requests: int = 10, time_window: float = 60.0):
        """Context manager for rate-limited operations."""
        start_time = time.time()
        request_count = 0

        try:
            yield client
        finally:
            elapsed = time.time() - start_time
            if elapsed < time_window and request_count >= max_requests:
                sleep_time = time_window - elapsed
                print(f"⏸️  Rate limit reached, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)

    # Usage example
    config = {
        "base_url": "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/",
        "access_token": "your-access-token",
        "retries": 3,
        "backoff_factor": 0.5,
        "timeout": (30, 60),
    }

    print("✅ Context manager pattern implemented:")
    print("  • Automatic connection management")
    print("  • Rate limiting context manager")
    print("  • Resource cleanup guarantees")
    print("  • Clean error handling")

    return config


def async_pattern():
    """Demonstrate async patterns for odyn operations."""
    print("\n⚡ Async Pattern Example")
    print("=" * 50)

    class AsyncBusinessCentralService:
        """Async service wrapper for odyn client."""

        def __init__(self, client: Odyn, max_workers: int = 4):
            self.client = client
            self.executor = ThreadPoolExecutor(max_workers=max_workers)

        async def get_customers_async(self, limit: int = 100) -> list[dict[str, Any]]:
            """Async wrapper for getting customers."""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, self.client.get, "customers", {"$top": limit})

        async def get_items_async(self, limit: int = 100) -> list[dict[str, Any]]:
            """Async wrapper for getting items."""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, self.client.get, "items", {"$top": limit})

        async def get_vendors_async(self, limit: int = 100) -> list[dict[str, Any]]:
            """Async wrapper for getting vendors."""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, self.client.get, "vendors", {"$top": limit})

        async def get_all_data_async(self, limit: int = 100) -> dict[str, list[dict[str, Any]]]:
            """Get all data concurrently."""
            tasks = [self.get_customers_async(limit), self.get_items_async(limit), self.get_vendors_async(limit)]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            return {
                "customers": results[0] if not isinstance(results[0], Exception) else [],
                "items": results[1] if not isinstance(results[1], Exception) else [],
                "vendors": results[2] if not isinstance(results[2], Exception) else [],
            }

        def __del__(self):
            """Cleanup executor on deletion."""
            if hasattr(self, "executor"):
                self.executor.shutdown(wait=False)

    # Usage example
    base_client = setup_client()
    async_service = AsyncBusinessCentralService(base_client)

    print("✅ Async pattern implemented:")
    print("  • Thread pool executor for blocking operations")
    print("  • Concurrent data fetching")
    print("  • Async/await interface")
    print("  • Automatic resource cleanup")

    return async_service


def factory_pattern():
    """Demonstrate factory pattern for creating odyn clients."""
    print("\n🏭 Factory Pattern Example")
    print("=" * 50)

    class BusinessCentralClientFactory:
        """Factory for creating Business Central clients."""

        @staticmethod
        def create_standard_client(base_url: str, access_token: str, timeout: tuple[int, int] = (60, 60)) -> Odyn:
            """Create a standard client."""
            session = BearerAuthSession(token=access_token)
            return Odyn(base_url=base_url, session=session, timeout=timeout)

        @staticmethod
        def create_high_performance_client(
            base_url: str, access_token: str, timeout: tuple[int, int] = (5, 30)
        ) -> Odyn:
            """Create a high-performance client."""
            session = BearerAuthSession(
                token=access_token, retries=2, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
            )
            return Odyn(base_url=base_url, session=session, timeout=timeout)

        @staticmethod
        def create_reliable_client(base_url: str, access_token: str, timeout: tuple[int, int] = (30, 120)) -> Odyn:
            """Create a highly reliable client."""
            session = BearerAuthSession(
                token=access_token,
                retries=10,
                backoff_factor=2.0,
                status_forcelist=[408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            )
            return Odyn(base_url=base_url, session=session, timeout=timeout)

        @staticmethod
        def create_development_client(base_url: str, access_token: str, timeout: tuple[int, int] = (10, 60)) -> Odyn:
            """Create a development client with verbose logging."""
            session = BearerAuthSession(
                token=access_token, retries=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
            )
            return Odyn(base_url=base_url, session=session, timeout=timeout)

    # Usage example
    factory = BusinessCentralClientFactory()

    # Create different types of clients
    factory.create_standard_client(
        "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/", "your-access-token"
    )

    factory.create_high_performance_client(
        "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/", "your-access-token"
    )

    factory.create_reliable_client(
        "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/", "your-access-token"
    )

    print("✅ Factory pattern implemented:")
    print("  • Standard client for general use")
    print("  • High-performance client for speed")
    print("  • Reliable client for critical operations")
    print("  • Development client for debugging")

    return factory


def main():
    """Run all integration pattern examples."""
    print("🚀 Odyn Integration Patterns Examples")
    print("=" * 60)
    print()

    # Run all pattern examples
    dependency_injection_pattern()
    caching_pattern()
    decorator_pattern()
    context_manager_pattern()
    async_pattern()
    factory_pattern()

    print("\n📝 Note: Replace placeholder values with your actual credentials")
    print("🔧 These patterns demonstrate best practices for integrating odyn")
    print("🏗️  Choose patterns that fit your application architecture")


if __name__ == "__main__":
    main()
