"""OData Queries Example.

This example demonstrates various OData query operations and filtering techniques
available when working with Business Central through odyn.
"""

from odyn import BearerAuthSession, Odyn


def setup_client() -> Odyn:
    """Setup the client with authentication."""
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"

    session = BearerAuthSession(token=ACCESS_TOKEN)
    return Odyn(base_url=BASE_URL, session=session)


def basic_filtering_example(client: Odyn) -> None:
    """Demonstrate basic filtering operations."""
    print("🔍 Basic Filtering Examples")
    print("=" * 50)

    try:
        # Filter customers by name containing "Adventure"
        adventure_customers = client.get(
            "customers", params={"$filter": "contains(displayName, 'Adventure')", "$top": 10}
        )
        print(f"✅ Found {len(adventure_customers)} customers with 'Adventure' in name")

        # Filter items by category
        inventory_items = client.get("items", params={"$filter": "itemCategoryCode eq 'INVENTORY'", "$top": 5})
        print(f"✅ Found {len(inventory_items)} inventory items")

        # Filter by multiple conditions
        active_customers = client.get(
            "customers", params={"$filter": "blocked eq false and creditLimit gt 10000", "$top": 5}
        )
        print(f"✅ Found {len(active_customers)} active customers with credit limit > 10000")

    except Exception as e:
        print(f"❌ Basic filtering failed: {e}")

    print()


def sorting_examples(client: Odyn) -> None:
    """Demonstrate sorting operations."""
    print("📊 Sorting Examples")
    print("=" * 50)

    try:
        # Sort customers by name ascending
        customers_asc = client.get("customers", params={"$orderby": "displayName asc", "$top": 5})
        print("✅ Customers sorted by name (ascending):")
        for customer in customers_asc:
            print(f"  - {customer.get('displayName', 'N/A')}")

        # Sort items by price descending
        items_desc = client.get("items", params={"$orderby": "unitPrice desc", "$top": 5})
        print("\n✅ Items sorted by price (descending):")
        for item in items_desc:
            print(f"  - {item.get('displayName', 'N/A')}: ${item.get('unitPrice', 0)}")

        # Multi-field sorting
        multi_sorted = client.get("customers", params={"$orderby": "countryRegionCode asc, displayName asc", "$top": 5})
        print("\n✅ Customers sorted by country then name:")
        for customer in multi_sorted:
            print(f"  - {customer.get('countryRegionCode', 'N/A')}: {customer.get('displayName', 'N/A')}")

    except Exception as e:
        print(f"❌ Sorting failed: {e}")

    print()


def field_selection_examples(client: Odyn) -> None:
    """Demonstrate field selection to optimize data transfer."""
    print("📋 Field Selection Examples")
    print("=" * 50)

    try:
        # Select only specific fields for customers
        customer_summary = client.get("customers", params={"$select": "id,displayName,phoneNumber,email", "$top": 5})
        print("✅ Customer summary (selected fields only):")
        for customer in customer_summary:
            print(f"  - {customer.get('displayName', 'N/A')}")
            print(f"    Phone: {customer.get('phoneNumber', 'N/A')}")
            print(f"    Email: {customer.get('email', 'N/A')}")
            print()

        # Select fields for items with pricing
        item_pricing = client.get(
            "items", params={"$select": "id,displayName,unitPrice,itemCategoryCode,baseUnitOfMeasure", "$top": 3}
        )
        print("✅ Item pricing (selected fields only):")
        for item in item_pricing:
            print(f"  - {item.get('displayName', 'N/A')}")
            print(f"    Price: ${item.get('unitPrice', 0)}")
            print(f"    Category: {item.get('itemCategoryCode', 'N/A')}")
            print(f"    Unit: {item.get('baseUnitOfMeasure', 'N/A')}")
            print()

    except Exception as e:
        print(f"❌ Field selection failed: {e}")

    print()


def complex_filtering_examples(client: Odyn) -> None:
    """Demonstrate complex filtering with logical operators."""
    print("🔗 Complex Filtering Examples")
    print("=" * 50)

    try:
        # Complex filter with AND/OR operators
        complex_filter = client.get(
            "customers",
            params={
                "$filter": (
                    "(contains(displayName, 'Adventure') or contains(displayName, 'Sports')) and blocked eq false",
                ),
                "$top": 10,
            },
        )
        print(f"✅ Found {len(complex_filter)} customers matching complex criteria")

        # Date-based filtering (example for sales orders)
        # Note: This is an example - actual field names may vary
        try:
            recent_orders = client.get(
                "salesOrders",
                params={"$filter": "documentDate ge 2024-01-01", "$orderby": "documentDate desc", "$top": 5},
            )
            print(f"✅ Found {len(recent_orders)} recent sales orders")
        except Exception:
            print("⚠️  Sales orders endpoint not available or different field names")

        # Numeric range filtering
        price_range_items = client.get(
            "items",
            params={"$filter": "unitPrice ge 100 and unitPrice le 1000", "$orderby": "unitPrice asc", "$top": 5},
        )
        print(f"✅ Found {len(price_range_items)} items in price range $100-$1000")

    except Exception as e:
        print(f"❌ Complex filtering failed: {e}")

    print()


def pagination_examples(client: Odyn) -> None:
    """Demonstrate pagination handling (automatic in odyn)."""
    print("📄 Pagination Examples")
    print("=" * 50)

    try:
        # Get all customers (odyn handles pagination automatically)
        all_customers = client.get("customers")
        print(f"✅ Retrieved all {len(all_customers)} customers (automatic pagination)")

        # Get all items (odyn handles pagination automatically)
        all_items = client.get("items")
        print(f"✅ Retrieved all {len(all_items)} items (automatic pagination)")

        # Manual pagination simulation with $top and $skip
        # Note: odyn handles this automatically, but you can still use these parameters
        first_page = client.get("customers", params={"$top": 10, "$skip": 0})
        second_page = client.get("customers", params={"$top": 10, "$skip": 10})
        print(f"✅ Manual pagination: {len(first_page)} customers on page 1, {len(second_page)} on page 2")

    except Exception as e:
        print(f"❌ Pagination failed: {e}")

    print()


def search_and_count_examples(client: Odyn) -> None:
    """Demonstrate search and count operations."""
    print("🔎 Search and Count Examples")
    print("=" * 50)

    try:
        # Count total customers
        customer_count = client.get(
            "customers",
            params={
                "$count": "true",
                "$top": 0,  # Don't retrieve actual records, just count
            },
        )
        print(f"✅ Total customer count: {len(customer_count)}")

        # Search with contains (case-insensitive)
        search_results = client.get(
            "customers", params={"$filter": "contains(tolower(displayName), 'adventure')", "$top": 5}
        )
        print(f"✅ Search results for 'adventure': {len(search_results)} customers")

        # Filter with startsWith
        starts_with_results = client.get(
            "customers", params={"$filter": "startswith(displayName, 'Adventure')", "$top": 5}
        )
        print(f"✅ Customers starting with 'Adventure': {len(starts_with_results)}")

    except Exception as e:
        print(f"❌ Search and count failed: {e}")

    print()


def main() -> None:
    """Run all OData query examples."""
    print("🚀 Odyn OData Queries Examples")
    print("=" * 60)
    print()

    # Setup client
    client = setup_client()

    # Run all examples
    basic_filtering_example(client)
    sorting_examples(client)
    field_selection_examples(client)
    complex_filtering_examples(client)
    pagination_examples(client)
    search_and_count_examples(client)

    print("📝 Note: Replace placeholder values with your actual credentials")
    print(
        "🔍 OData query syntax: https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/use-filtering-in-web-services"
    )


if __name__ == "__main__":
    main()
