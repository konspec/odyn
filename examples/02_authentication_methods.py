"""Authentication Methods Example.

This example demonstrates the different authentication methods available in odyn:
1. Bearer Token Authentication (recommended for most scenarios)
2. Basic Authentication (username/password)
3. Custom Session (for advanced use cases)
"""

from odyn import BasicAuthSession, BearerAuthSession, Odyn, OdynSession


def bearer_token_example():
    """Example using Bearer Token Authentication."""
    print("🔐 Bearer Token Authentication Example")
    print("=" * 50)

    # Configuration
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"

    # Create session with bearer token
    session = BearerAuthSession(token=ACCESS_TOKEN)

    # Initialize client
    client = Odyn(base_url=BASE_URL, session=session)

    try:
        # Test the connection
        customers = client.get("customers", params={"$top": 5})
        print("✅ Successfully authenticated with bearer token")
        print(f"📊 Retrieved {len(customers)} customers")

    except Exception as e:
        print(f"❌ Bearer token authentication failed: {e}")

    print()


def basic_auth_example():
    """Example using Basic Authentication."""
    print("🔑 Basic Authentication Example")
    print("=" * 50)

    # Configuration
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    USERNAME = "your-username"
    PASSWORD = "your-web-service-access-key"  # This is the web service access key, not your regular password

    # Create session with basic auth
    session = BasicAuthSession(username=USERNAME, password=PASSWORD)

    # Initialize client
    client = Odyn(base_url=BASE_URL, session=session)

    try:
        # Test the connection
        vendors = client.get("vendors", params={"$top": 5})
        print("✅ Successfully authenticated with basic auth")
        print(f"📊 Retrieved {len(vendors)} vendors")

    except Exception as e:
        print(f"❌ Basic authentication failed: {e}")

    print()


def custom_session_example():
    """Example using a custom session with additional headers."""
    print("⚙️  Custom Session Example")
    print("=" * 50)

    # Configuration
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"

    # Create a custom session with additional configuration
    session = OdynSession(retries=3, backoff_factor=1.0, status_forcelist=[429, 500, 502, 503, 504])

    # Add custom headers
    session.headers.update(
        {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "User-Agent": "MyCustomApp/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    # Initialize client
    client = Odyn(base_url=BASE_URL, session=session)

    try:
        # Test the connection
        items = client.get("items", params={"$top": 5})
        print("✅ Successfully authenticated with custom session")
        print(f"📊 Retrieved {len(items)} items")
        print(f"🔧 Custom headers: {dict(session.headers)}")

    except Exception as e:
        print(f"❌ Custom session authentication failed: {e}")

    print()


def session_with_retry_configuration():
    """Example showing advanced retry configuration."""
    print("🔄 Advanced Retry Configuration Example")
    print("=" * 50)

    # Configuration
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"

    # Create session with aggressive retry settings
    session = BearerAuthSession(
        token=ACCESS_TOKEN,
        retries=10,  # More retries than default
        backoff_factor=0.5,  # Faster backoff
        status_forcelist=[408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524],  # More status codes
    )

    # Initialize client with custom timeout
    client = Odyn(
        base_url=BASE_URL,
        session=session,
        timeout=(5, 30),  # 5s connect, 30s read timeout
    )

    try:
        # Test the connection
        customers = client.get("customers", params={"$top": 3})
        print("✅ Successfully connected with advanced retry configuration")
        print(f"📊 Retrieved {len(customers)} customers")
        print(f"⏱️  Timeout: {client.timeout}")

    except Exception as e:
        print(f"❌ Advanced retry configuration failed: {e}")

    print()


def main():
    """Run all authentication examples."""
    print("🚀 Odyn Authentication Methods Examples")
    print("=" * 60)
    print()

    # Run all examples
    bearer_token_example()
    basic_auth_example()
    custom_session_example()
    session_with_retry_configuration()

    print("📝 Note: Replace placeholder values with your actual credentials")
    print("🔒 In production, use environment variables or secure configuration management")


if __name__ == "__main__":
    main()
