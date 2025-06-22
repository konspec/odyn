# Getting Started

This guide will help you set up Odyn and make your first API call to Microsoft Dynamics 365 Business Central.

## Prerequisites

Before you begin, ensure you have:

1. **Odyn installed** - See [Installation](installation.md) for details
2. **Microsoft Dynamics 365 Business Central access** - You'll need:
   - A Business Central tenant URL
   - Authentication credentials (username/password or access token)

## Quick Setup

### Step 1: Import Required Classes

```python
from odyn import Odyn, BearerAuthSession
```

### Step 2: Create an Authenticated Session

Choose the authentication method that matches your Business Central setup:

#### Using Bearer Token (Recommended)

```python
# Create a session with your access token
session = BearerAuthSession("your-access-token-here")
```

#### Using Basic Authentication

```python
from odyn import BasicAuthSession

# Create a session with username and password
session = BasicAuthSession("your-username", "your-password")
```

### Step 3: Initialize the Odyn Client

```python
# Initialize the client with your Business Central URL
client = Odyn(
    base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
    session=session
)
```

### Step 4: Make Your First API Call

```python
# Fetch customers (this will automatically handle pagination)
customers = client.get("customers")

# Print the results
print(f"Retrieved {len(customers)} customers")
for customer in customers[:3]:  # Show first 3 customers
    print(f"- {customer.get('name', 'N/A')} (ID: {customer.get('id', 'N/A')})")
```

## Complete Example

Here's a complete working example:

```python
from odyn import Odyn, BearerAuthSession

def main():
    # 1. Set up authentication
    session = BearerAuthSession("your-access-token-here")

    # 2. Initialize the client
    client = Odyn(
        base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
        session=session
    )

    # 3. Make API calls
    try:
        # Fetch customers
        customers = client.get("customers")
        print(f"✅ Retrieved {len(customers)} customers")

        # Fetch items
        items = client.get("items")
        print(f"✅ Retrieved {len(items)} items")

        # Fetch vendors
        vendors = client.get("vendors")
        print(f"✅ Retrieved {len(vendors)} vendors")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

## Expected Output Structure

The `client.get()` method returns a list of dictionaries, where each dictionary represents an entity from Business Central:

```python
# Example response structure
customers = [
    {
        "id": "12345678-1234-1234-1234-123456789012",
        "number": "10000",
        "name": "Adventure Works",
        "address": {
            "street": "123 Main St",
            "city": "Seattle",
            "state": "WA",
            "country": "US"
        },
        "phoneNumber": "+1-555-0123",
        "email": "contact@adventureworks.com",
        # ... other fields
    },
    # ... more customers
]
```

## Working with Query Parameters

You can add OData query parameters to filter, sort, and limit your results:

```python
# Get only the first 10 customers
customers = client.get("customers", params={"$top": 10})

# Filter customers by name
customers = client.get("customers", params={"$filter": "contains(name, 'Adventure')"})

# Sort customers by name
customers = client.get("customers", params={"$orderby": "name"})

# Select specific fields only
customers = client.get("customers", params={"$select": "id,name,phoneNumber"})

# Combine multiple parameters
customers = client.get(
    "customers",
    params={
        "$top": 5,
        "$filter": "contains(name, 'Adventure')",
        "$orderby": "name",
        "$select": "id,name,phoneNumber"
    }
)
```

## Error Handling

Odyn provides comprehensive error handling. Here's how to handle common scenarios:

```python
from odyn import Odyn, BearerAuthSession
from odyn import InvalidURLError, InvalidSessionError
import requests

def safe_api_call():
    try:
        session = BearerAuthSession("your-token")
        client = Odyn(
            base_url="https://your-tenant.businesscentral.dynamics.com/api/v2.0/",
            session=session
        )

        customers = client.get("customers")
        return customers

    except InvalidURLError as e:
        print(f"❌ Invalid URL: {e}")
    except InvalidSessionError as e:
        print(f"❌ Invalid session: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

    return []

# Use the function
customers = safe_api_call()
```

## Next Steps

Now that you've made your first API call, you can:

1. **Explore the API**: Learn about [all available endpoints](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
2. **Customize Configuration**: See [Configuration](advanced/configuration.md) for timeout and retry settings
3. **Handle Authentication**: Learn more about [session management](usage/sessions.md)
4. **Error Handling**: Understand [exception types](usage/exceptions.md) and how to handle them
5. **Logging**: Configure [logging behavior](advanced/logging.md) for debugging

## Troubleshooting

### Common Issues

**Authentication Errors**
```
HTTP Error: 401 - Unauthorized
```
**Solution**: Verify your access token or credentials are correct and have the necessary permissions.

**URL Errors**
```
Invalid URL: URL must have a valid scheme (http or https)
```
**Solution**: Ensure your base URL starts with `https://` and includes the full path to the API.

**Timeout Errors**
```
RequestException: Connection timeout
```
**Solution**: Check your network connection and consider adjusting timeout settings (see [Configuration](advanced/configuration.md)).

For more detailed troubleshooting, see the [Troubleshooting](troubleshooting.md) guide.
