"""Business Scenarios Example.

This example demonstrates real-world business scenarios and use cases for odyn,
showing how to solve common Business Central integration challenges.
"""

import json
from datetime import datetime

from odyn import BearerAuthSession, Odyn


def setup_client() -> Odyn:
    """Setup the client with authentication."""
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ACCESS_TOKEN = "your-access-token"

    session = BearerAuthSession(token=ACCESS_TOKEN)
    return Odyn(base_url=BASE_URL, session=session)


def customer_analytics_dashboard(client: Odyn) -> None:
    """Scenario: Building a customer analytics dashboard."""
    print("📊 Customer Analytics Dashboard Scenario")
    print("=" * 50)

    try:
        # Get customer data with key metrics
        customers = client.get(
            "customers",
            params={
                "$select": "id,displayName,creditLimit,balance,blocked,countryRegionCode,phoneNumber,email",
                "$filter": "blocked eq false",
                "$orderby": "balance desc",
            },
        )

        # Calculate analytics
        total_customers = len(customers)
        total_credit_limit = sum(c.get("creditLimit", 0) for c in customers)
        total_balance = sum(c.get("balance", 0) for c in customers)
        avg_credit_limit = total_credit_limit / total_customers if total_customers > 0 else 0
        avg_balance = total_balance / total_customers if total_customers > 0 else 0

        # Top customers by balance
        top_customers = customers[:5]

        print("📈 Customer Analytics Summary:")
        print(f"  • Total Active Customers: {total_customers}")
        print(f"  • Total Credit Limit: ${total_credit_limit:,.2f}")
        print(f"  • Total Outstanding Balance: ${total_balance:,.2f}")
        print(f"  • Average Credit Limit: ${avg_credit_limit:,.2f}")
        print(f"  • Average Balance: ${avg_balance:,.2f}")

        print("\n🏆 Top 5 Customers by Balance:")
        for i, customer in enumerate(top_customers, 1):
            print(f"  {i}. {customer.get('displayName', 'N/A')}")
            print(f"     Balance: ${customer.get('balance', 0):,.2f}")
            print(f"     Credit Limit: ${customer.get('creditLimit', 0):,.2f}")
            print(f"     Country: {customer.get('countryRegionCode', 'N/A')}")

    except Exception as e:
        print(f"❌ Customer analytics failed: {e}")

    print()


def inventory_management_report(client: Odyn) -> None:
    """Scenario: Inventory management and reporting."""
    print("📦 Inventory Management Report Scenario")
    print("=" * 50)

    try:
        # Get inventory items with key data
        items = client.get(
            "items",
            params={
                "$select": "id,displayName,itemCategoryCode,baseUnitOfMeasure,unitPrice,inventory,blocked",
                "$filter": "blocked eq false",
                "$orderby": "inventory asc",
            },
        )

        # Analyze inventory
        total_items = len(items)
        low_stock_threshold = 10
        out_of_stock = [item for item in items if item.get("inventory", 0) == 0]
        low_stock = [item for item in items if 0 < item.get("inventory", 0) <= low_stock_threshold]
        well_stocked = [item for item in items if item.get("inventory", 0) > low_stock_threshold]

        # Calculate total inventory value
        total_inventory_value = sum(item.get("inventory", 0) * item.get("unitPrice", 0) for item in items)

        print("📊 Inventory Summary:")
        print(f"  • Total Items: {total_items}")
        print(f"  • Out of Stock: {len(out_of_stock)}")
        print(f"  • Low Stock (≤{low_stock_threshold}): {len(low_stock)}")
        print(f"  • Well Stocked: {len(well_stocked)}")
        print(f"  • Total Inventory Value: ${total_inventory_value:,.2f}")

        print("\n⚠️  Items Requiring Attention:")
        for item in out_of_stock[:5]:
            print(f"  • {item.get('displayName', 'N/A')} - OUT OF STOCK")

        for item in low_stock[:5]:
            print(f"  • {item.get('displayName', 'N/A')} - Low Stock ({item.get('inventory', 0)} units)")

    except Exception as e:
        print(f"❌ Inventory management failed: {e}")

    print()


def sales_performance_analysis(client: Odyn) -> None:
    """Scenario: Sales performance analysis and reporting."""
    print("💰 Sales Performance Analysis Scenario")
    print("=" * 50)

    try:
        # Get sales orders (if available)
        # Note: Field names may vary depending on your Business Central setup
        try:
            sales_orders = client.get(
                "salesOrders",
                params={
                    "$select": "id,orderDate,customerNumber,customerName,currencyCode,amountIncludingTax",
                    "$filter": "orderDate ge 2024-01-01",
                    "$orderby": "orderDate desc",
                    "$top": 100,
                },
            )

            if sales_orders:
                # Calculate sales metrics
                total_orders = len(sales_orders)
                total_sales = sum(order.get("amountIncludingTax", 0) for order in sales_orders)
                avg_order_value = total_sales / total_orders if total_orders > 0 else 0

                # Group by customer
                customer_sales = {}
                for order in sales_orders:
                    customer = order.get("customerName", "Unknown")
                    amount = order.get("amountIncludingTax", 0)
                    customer_sales[customer] = customer_sales.get(customer, 0) + amount

                # Top customers
                top_customers = sorted(customer_sales.items(), key=lambda x: x[1], reverse=True)[:5]

                print("📈 Sales Performance Summary:")
                print(f"  • Total Orders: {total_orders}")
                print(f"  • Total Sales: ${total_sales:,.2f}")
                print(f"  • Average Order Value: ${avg_order_value:,.2f}")

                print("\n🏆 Top Customers by Sales:")
                for customer, sales in top_customers:
                    print(f"  • {customer}: ${sales:,.2f}")

        except Exception:
            print("⚠️  Sales orders endpoint not available or different field names")
            print("📝 This is a demonstration - actual field names may vary")

    except Exception as e:
        print(f"❌ Sales performance analysis failed: {e}")

    print()


def vendor_relationship_management(client: Odyn) -> None:
    """Scenario: Vendor relationship management and analysis."""
    print("🤝 Vendor Relationship Management Scenario")
    print("=" * 50)

    try:
        # Get vendor data
        vendors = client.get(
            "vendors",
            params={
                "$select": "id,displayName,phoneNumber,email,paymentTermsCode,currencyCode,balance,blocked",
                "$filter": "blocked eq false",
                "$orderby": "balance desc",
            },
        )

        # Analyze vendor relationships
        total_vendors = len(vendors)
        total_payables = sum(vendor.get("balance", 0) for vendor in vendors)
        avg_payable = total_payables / total_vendors if total_vendors > 0 else 0

        # Top vendors by balance (largest payables)
        top_vendors = vendors[:5]

        # Group by payment terms
        payment_terms = {}
        for vendor in vendors:
            terms = vendor.get("paymentTermsCode", "Unknown")
            payment_terms[terms] = payment_terms.get(terms, 0) + 1

        print("📊 Vendor Relationship Summary:")
        print(f"  • Total Active Vendors: {total_vendors}")
        print(f"  • Total Payables: ${total_payables:,.2f}")
        print(f"  • Average Payable per Vendor: ${avg_payable:,.2f}")

        print("\n💰 Top Vendors by Payable Balance:")
        for i, vendor in enumerate(top_vendors, 1):
            print(f"  {i}. {vendor.get('displayName', 'N/A')}")
            print(f"     Balance: ${vendor.get('balance', 0):,.2f}")
            print(f"     Payment Terms: {vendor.get('paymentTermsCode', 'N/A')}")
            print(f"     Currency: {vendor.get('currencyCode', 'N/A')}")

        print("\n📋 Payment Terms Distribution:")
        for terms, count in payment_terms.items():
            print(f"  • {terms}: {count} vendors")

    except Exception as e:
        print(f"❌ Vendor relationship management failed: {e}")

    print()


def data_export_and_integration(client: Odyn) -> None:
    """Scenario: Data export and integration with external systems."""
    print("📤 Data Export and Integration Scenario")
    print("=" * 50)

    try:
        # Export customer data for CRM integration
        customers_for_crm = client.get(
            "customers",
            params={
                "$select": "id,displayName,phoneNumber,email,address,countryRegionCode,creditLimit,balance",
                "$filter": "blocked eq false",
            },
        )

        # Export inventory data for warehouse management
        inventory_for_wms = client.get(
            "items",
            params={
                "$select": "id,displayName,itemCategoryCode,baseUnitOfMeasure,unitPrice,inventory,blocked",
                "$filter": "blocked eq false",
            },
        )

        # Export vendor data for procurement system
        vendors_for_procurement = client.get(
            "vendors",
            params={
                "$select": "id,displayName,phoneNumber,email,address,paymentTermsCode,currencyCode",
                "$filter": "blocked eq false",
            },
        )

        # Prepare export data
        export_data = {
            "export_timestamp": datetime.now().isoformat(),  # noqa: DTZ005
            "customers": {"count": len(customers_for_crm), "data": customers_for_crm},
            "inventory": {"count": len(inventory_for_wms), "data": inventory_for_wms},
            "vendors": {"count": len(vendors_for_procurement), "data": vendors_for_procurement},
        }

        print("📤 Data Export Summary:")
        print(f"  • Customers: {len(customers_for_crm)} records")
        print(f"  • Inventory Items: {len(inventory_for_wms)} records")
        print(f"  • Vendors: {len(vendors_for_procurement)} records")
        print(
            f"  • Total Records: {sum(len(export_data[key]['data']) for key in ['customers', 'inventory', 'vendors'])}"
        )

        # Simulate saving to different formats
        print("\n💾 Export Formats:")
        print(f"  • JSON: {len(json.dumps(export_data))} characters")
        print(f"  • CSV (customers): {len(customers_for_crm)} rows")
        print(f"  • CSV (inventory): {len(inventory_for_wms)} rows")
        print(f"  • CSV (vendors): {len(vendors_for_procurement)} rows")

    except Exception as e:
        print(f"❌ Data export failed: {e}")

    print()


def real_time_monitoring_dashboard(client: Odyn) -> None:
    """Scenario: Real-time monitoring dashboard for business metrics."""
    print("📊 Real-time Monitoring Dashboard Scenario")
    print("=" * 50)

    try:
        # Get real-time metrics
        metrics = {}

        # Customer metrics
        customers = client.get(
            "customers", params={"$select": "id,blocked,balance,creditLimit", "$filter": "blocked eq false"}
        )
        metrics["customers"] = {
            "total": len(customers),
            "total_balance": sum(c.get("balance", 0) for c in customers),
            "total_credit_limit": sum(c.get("creditLimit", 0) for c in customers),
        }

        # Inventory metrics
        items = client.get("items", params={"$select": "id,inventory,unitPrice,blocked", "$filter": "blocked eq false"})
        metrics["inventory"] = {
            "total_items": len(items),
            "total_value": sum(item.get("inventory", 0) * item.get("unitPrice", 0) for item in items),
            "out_of_stock": len([item for item in items if item.get("inventory", 0) == 0]),
        }

        # Vendor metrics
        vendors = client.get("vendors", params={"$select": "id,balance,blocked", "$filter": "blocked eq false"})
        metrics["vendors"] = {"total": len(vendors), "total_payables": sum(v.get("balance", 0) for v in vendors)}

        # Calculate key performance indicators
        kpis = {
            "customer_credit_utilization": (
                metrics["customers"]["total_balance"] / metrics["customers"]["total_credit_limit"] * 100
            )
            if metrics["customers"]["total_credit_limit"] > 0
            else 0,
            "inventory_turnover_risk": (
                metrics["inventory"]["out_of_stock"] / metrics["inventory"]["total_items"] * 100
            )
            if metrics["inventory"]["total_items"] > 0
            else 0,
            "total_business_value": metrics["customers"]["total_balance"]
            + metrics["inventory"]["total_value"]
            + metrics["vendors"]["total_payables"],
        }

        print("📈 Real-time Business Metrics:")
        print(f"  • Active Customers: {metrics['customers']['total']}")
        print(f"  • Customer Credit Utilization: {kpis['customer_credit_utilization']:.1f}%")
        print(f"  • Total Customer Balance: ${metrics['customers']['total_balance']:,.2f}")

        print("\n📦 Inventory Status:")
        print(f"  • Total Items: {metrics['inventory']['total_items']}")
        print(f"  • Inventory Value: ${metrics['inventory']['total_value']:,.2f}")
        print(f"  • Out of Stock Items: {metrics['inventory']['out_of_stock']}")
        print(f"  • Stock-out Risk: {kpis['inventory_turnover_risk']:.1f}%")

        print("\n🤝 Vendor Status:")
        print(f"  • Active Vendors: {metrics['vendors']['total']}")
        print(f"  • Total Payables: ${metrics['vendors']['total_payables']:,.2f}")

        print(f"\n💰 Overall Business Value: ${kpis['total_business_value']:,.2f}")

    except Exception as e:
        print(f"❌ Real-time monitoring failed: {e}")

    print()


def main() -> None:
    """Run all business scenario examples."""
    print("🚀 Odyn Business Scenarios Examples")
    print("=" * 60)
    print()

    # Setup client
    client = setup_client()

    # Run all business scenarios
    customer_analytics_dashboard(client)
    inventory_management_report(client)
    sales_performance_analysis(client)
    vendor_relationship_management(client)
    data_export_and_integration(client)
    real_time_monitoring_dashboard(client)

    print("📝 Note: Replace placeholder values with your actual credentials")
    print("💼 These scenarios demonstrate real-world Business Central integration patterns")


if __name__ == "__main__":
    main()
