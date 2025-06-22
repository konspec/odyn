# Getting Started with Odyn

This guide provides a complete walkthrough for setting up Odyn and making your first API calls to Microsoft Dynamics 365 Business Central. We will cover the core concepts, provide a complete code example, and show you how to work with the results.

## Prerequisites

Before you start, please ensure you have completed the following:
1.  **Installed Odyn**: Follow the [Installation Guide](./installation.md) to install Odyn in a virtual environment.
2.  **Acquired Business Central Credentials**: You must have access to a Business Central tenant and the necessary credentials. This includes:
    *   Your tenant's specific API base URL.
    *   An authentication method, such as a Bearer Token (access token) or a username and Web Service Access Key for Basic Authentication.

---

## Core Concepts: The Client and The Session

Odyn is designed with a clear separation of concerns, which makes it both flexible and easy to use. The two most important components you will interact with are:

1.  **The `Odyn` Client**: This is the main entry point for all API operations. It handles request building, automatic pagination, logging, and response parsing. You create one instance of the client for a specific Business Central API endpoint.

2.  **The `Session` Object**: This object manages authentication and retry logic. It is passed to the `Odyn` client during initialization. Odyn comes with pre-built sessions:
    *   `BearerAuthSession`: For modern token-based authentication (recommended).
    *   `BasicAuthSession`: For legacy username/password authentication.
    *   `OdynSession`: A base session you can extend for custom authentication strategies.

This design means you can configure your authentication and retry policies once and reuse that session across multiple client instances if needed.

---

## A Complete Example

Let's walk through a complete, runnable script that demonstrates how to use Odyn. This example fetches a list of customers from Business Central, filtering for specific records and selecting only the fields we need.

Create a new Python file, for example `run_odyn.py`:

```python
# run_odyn.py
import os
import requests
from odyn import (
    Odyn,
    BearerAuthSession,
    InvalidURLError,
    InvalidSessionError,
)

def get_customers_by_city(city_name: str):
    """
    Connects to Business Central and retrieves customers from a specific city.
    """
    print(f"Attempting to fetch customers from city: {city_name}...")

    try:
        # Step 1: Get credentials and configuration
        # For this example, we load them from environment variables for security.
        # In a real application, you might use a secure vault or config file.
        access_token = os.getenv("BC_ACCESS_TOKEN")
        base_url = os.getenv("BC_BASE_URL")

        if not access_token or not base_url:
            print("Error: BC_ACCESS_TOKEN and BC_BASE_URL environment variables must be set.")
            return

        # Step 2: Create an Authenticated Session
        # The session handles adding the "Authorization: Bearer <token>" header
        # to every request and also manages automatic retries on transient errors.
        session = BearerAuthSession(token=access_token)

        # Step 3: Initialize the Odyn Client
        # The client needs the base URL for the API and the session object.
        client = Odyn(base_url=base_url, session=session)

        # Step 4: Make the API Call with OData Parameters
        # We use the params argument to pass OData query options.
        # This is more robust and readable than manually encoding them in the URL.
        customers = client.get(
            "customers",
            params={
                "$filter": f"city eq '{city_name}'",
                "$select": "number,displayName,phoneNumber",
                "$orderby": "displayName",
            },
        )

        # Step 5: Process the Results
        if not customers:
            print(f"No customers found in {city_name}.")
            return

        print(f"Successfully retrieved {len(customers)} customers from {city_name}:")
        for customer in customers:
            print(
                f"  - Name: {customer.get('displayName', 'N/A')}, "
                f"Number: {customer.get('number', 'N/A')}, "
                f"Phone: {customer.get('phoneNumber', 'N/A')}"
            )

    except InvalidURLError as e:
        print(f"Configuration Error: The provided base URL is invalid. {e}")
    except InvalidSessionError as e:
        print(f"Configuration Error: The session object is invalid. {e}")
    except requests.exceptions.HTTPError as e:
        # This catches errors like 401 Unauthorized or 404 Not Found.
        status = e.response.status_code
        print(f"HTTP Error: Received status {status}. Check your token and URL.")
        # For a 401, your access token may be expired or invalid.
        # For a 404, the base_url or endpoint might be incorrect.
    except requests.exceptions.RequestException as e:
        # This catches network-level errors (e.g., connection timeout).
        print(f"Network Error: Could not connect to the server. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Replace "New York" with a city you expect to have customers in.
    get_customers_by_city("New York")

```

### How to Run the Example

1.  **Set Environment Variables**: Before running, you must provide your credentials.
    ```bash
    # On macOS/Linux
    export BC_ACCESS_TOKEN="your-super-secret-token-here"
    export BC_BASE_URL="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"

    # On Windows (Command Prompt)
    set BC_ACCESS_TOKEN="your-super-secret-token-here"
    set BC_BASE_URL="https://api.businesscentral.dynamics.com/v2.0/your-tenant-id/production/"
    ```
2.  **Execute the Script**:
    ```bash
    python run_odyn.py
    ```

---

## Working with OData Query Parameters

A key feature of Business Central's API is its support for the OData protocol, which allows you to refine your requests. Odyn makes this easy via the `params` dictionary in `get()` requests.

Here are the most common OData options:

-   `$filter`: Restricts the data returned. Analogous to a `WHERE` clause in SQL.
    -   `params={"$filter": "blocked eq 'false'"}`
    -   `params={"$filter": "contains(displayName, 'Chairs')"}`
-   `$select`: Specifies which fields to return, reducing payload size.
    -   `params={"$select": "id,number,displayName"}`
-   `$top`: Limits the number of records returned.
    -   `params={"$top": 10}`
-   `$orderby`: Sorts the results.
    -   `params={"$orderby": "displayName desc"}`
-   `$expand`: Includes related entities in the response.
    -   `params={"$expand": "paymentTerm"}`

You can combine these to build powerful, efficient queries, as shown in the main example.

---

## Next Steps

Now that you have successfully made your first API call, you are ready to explore more of Odyn's capabilities.

-   **Authentication**: Dive deeper into [Authentication Sessions](./usage/sessions.md) to learn about custom retry logic.
-   **Configuration**: Learn how to configure [Timeouts and other settings](./advanced/configuration.md).
-   **Error Handling**: Get a complete overview of the [Exception classes](./usage/exceptions.md).
-   **API Reference**: See the full [Odyn Client API Reference](./usage/odyn.md) for details on all methods.
