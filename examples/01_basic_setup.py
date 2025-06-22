"""Basic Setup Example.

This example demonstrates the fundamental usage of odyn with bearer token authentication.
It shows how to create a client and make basic API calls to Business Central.
"""

from odyn import BearerAuthSession, Odyn


def main() -> None:
    """Main function."""
    # Configuration - in production, use environment variables or secure config management
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"  # Replace with your actual token

    # Create an authenticated session
    session = BearerAuthSession(token=ACCESS_TOKEN)

    # Initialize the client
    client = Odyn(base_url=BASE_URL, session=session)

    print("🔗 Connected to Business Central")
    print(f"📡 Base URL: {client.base_url}")
    print(f"⏱️  Timeout: {client.timeout}")

    # Example 1: Get all customers (with automatic pagination)
    print("\n📋 Fetching all customers...")
    try:
        customers = client.get("customers")
        print(f"✅ Retrieved {len(customers)} customers")

        # Display first few customers
        for i, customer in enumerate(customers[:3]):
            print(f"  {i + 1}. {customer.get('displayName', 'N/A')} (ID: {customer.get('id', 'N/A')})")

    except Exception as e:
        print(f"❌ Error fetching customers: {e}")

    # Example 2: Get items with pagination and basic filtering
    print("\n📦 Fetching items...")
    try:
        items = client.get("items")
        print(f"✅ Retrieved {len(items)} items")

        # Display first few items
        for i, item in enumerate(items[:3]):
            print(f"  {i + 1}. {item.get('displayName', 'N/A')} (Category: {item.get('itemCategoryCode', 'N/A')})")

    except Exception as e:
        print(f"❌ Error fetching items: {e}")


if __name__ == "__main__":
    main()
