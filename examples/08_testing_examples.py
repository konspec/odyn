"""Testing Examples.

This example demonstrates testing patterns and examples for odyn,
including unit tests, integration tests, and mocking strategies.
"""

import unittest
from unittest.mock import Mock, patch

import requests

from odyn import BasicAuthSession, BearerAuthSession, InvalidSessionError, InvalidURLError, Odyn


def setup_test_client() -> Odyn:
    """Setup a test client with mock authentication."""
    BASE_URL = "https://api.businesscentral.dynamics.com/v2.0/test-tenant/production/"
    ACCESS_TOKEN = "test-access-token"

    session = BearerAuthSession(token=ACCESS_TOKEN)
    return Odyn(base_url=BASE_URL, session=session)


class TestOdynClient(unittest.TestCase):
    """Unit tests for Odyn client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = setup_test_client()

    def test_client_initialization(self):
        """Test client initialization with valid parameters."""
        session = BearerAuthSession(token="test-token")
        client = Odyn(base_url="https://api.businesscentral.dynamics.com/v2.0/test/production/", session=session)

        assert client.base_url == "https://api.businesscentral.dynamics.com/v2.0/test/production/"
        assert client.timeout == (60, 60)

    def test_invalid_url_initialization(self):
        """Test client initialization with invalid URL."""
        session = BearerAuthSession(token="test-token")

        with self.assertRaises(InvalidURLError):
            Odyn(base_url="not-a-valid-url", session=session)

    def test_invalid_session_initialization(self):
        """Test client initialization with invalid session."""
        with self.assertRaises(InvalidSessionError):
            Odyn(
                base_url="https://api.businesscentral.dynamics.com/v2.0/test/production/",
                session="not-a-session",
            )

    def test_invalid_timeout_initialization(self):
        """Test client initialization with invalid timeout."""
        session = BearerAuthSession(token="test-token")

        with self.assertRaises(Exception):
            Odyn(
                base_url="https://api.businesscentral.dynamics.com/v2.0/test/production/",
                session=session,
                timeout=(-1, 60),
            )


class TestOdynIntegration(unittest.TestCase):
    """Integration tests for Odyn client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = setup_test_client()

    @patch("requests.Session.request")
    def test_successful_get_request(self, mock_request):
        """Test successful GET request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [{"id": "1", "displayName": "Test Customer 1"}, {"id": "2", "displayName": "Test Customer 2"}]
        }
        mock_request.return_value = mock_response

        # Make request
        result = self.client.get("customers")

        # Assertions
        assert len(result) == 2
        assert result[0]["displayName"] == "Test Customer 1"
        assert result[1]["displayName"] == "Test Customer 2"

        # Verify request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert "customers" in call_args[0][1]

    @patch("requests.Session.request")
    def test_pagination_handling(self, mock_request):
        """Test automatic pagination handling."""
        # Mock first page response
        first_response = Mock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "value": [{"id": "1", "name": "Item 1"}],
            "@odata.nextLink": "https://api.businesscentral.dynamics.com/v2.0/test/production/customers?$skip=1",
        }

        # Mock second page response
        second_response = Mock()
        second_response.status_code = 200
        second_response.json.return_value = {"value": [{"id": "2", "name": "Item 2"}]}

        # Set up mock to return different responses
        mock_request.side_effect = [first_response, second_response]

        # Make request
        result = self.client.get("customers")

        # Assertions
        assert len(result) == 2
        assert result[0]["name"] == "Item 1"
        assert result[1]["name"] == "Item 2"

        # Verify two requests were made
        assert mock_request.call_count == 2

    @patch("requests.Session.request")
    def test_http_error_handling(self, mock_request):
        """Test HTTP error handling."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_request.return_value = mock_response

        # Make request and expect exception
        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.get("nonexistent-endpoint")

    @patch("requests.Session.request")
    def test_network_error_handling(self, mock_request):
        """Test network error handling."""
        # Mock network error
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        # Make request and expect exception
        with self.assertRaises(requests.exceptions.ConnectionError):
            self.client.get("customers")


class TestOdynSessions(unittest.TestCase):
    """Tests for Odyn session classes."""

    def test_bearer_auth_session(self):
        """Test BearerAuthSession initialization."""
        session = BearerAuthSession(token="test-token")

        assert session.headers["Authorization"] == "Bearer test-token"
        assert session._retries == 5
        assert session._backoff_factor == 2.0

    def test_basic_auth_session(self):
        """Test BasicAuthSession initialization."""
        session = BasicAuthSession(username="testuser", password="testpass")

        assert session.auth == ("testuser", "testpass")
        assert session._retries == 5

    def test_custom_session_configuration(self):
        """Test custom session configuration."""
        session = BearerAuthSession(
            token="test-token", retries=10, backoff_factor=1.5, status_forcelist=[500, 502, 503, 504]
        )

        assert session._retries == 10
        assert session._backoff_factor == 1.5
        assert session._status_forcelist == [500, 502, 503, 504]


class TestOdynBusinessLogic(unittest.TestCase):
    """Tests for business logic using Odyn."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = setup_test_client()

    @patch.object(Odyn, "get")
    def test_customer_analytics(self, mock_get):
        """Test customer analytics business logic."""
        # Mock customer data
        mock_customers = [
            {"id": "1", "displayName": "Customer A", "balance": 1000, "creditLimit": 5000},
            {"id": "2", "displayName": "Customer B", "balance": 2000, "creditLimit": 3000},
            {"id": "3", "displayName": "Customer C", "balance": 500, "creditLimit": 1000},
        ]
        mock_get.return_value = mock_customers

        # Test business logic
        customers = self.client.get("customers")
        total_balance = sum(c.get("balance", 0) for c in customers)
        total_credit_limit = sum(c.get("creditLimit", 0) for c in customers)

        # Assertions
        assert total_balance == 3500
        assert total_credit_limit == 9000
        assert len(customers) == 3

    @patch.object(Odyn, "get")
    def test_inventory_analysis(self, mock_get):
        """Test inventory analysis business logic."""
        # Mock inventory data
        mock_items = [
            {"id": "1", "displayName": "Item A", "inventory": 10, "unitPrice": 100},
            {"id": "2", "displayName": "Item B", "inventory": 0, "unitPrice": 50},
            {"id": "3", "displayName": "Item C", "inventory": 5, "unitPrice": 200},
        ]
        mock_get.return_value = mock_items

        # Test business logic
        items = self.client.get("items")
        out_of_stock = [item for item in items if item.get("inventory", 0) == 0]
        total_value = sum(item.get("inventory", 0) * item.get("unitPrice", 0) for item in items)

        # Assertions
        assert len(out_of_stock) == 1
        assert out_of_stock[0]["displayName"] == "Item B"
        assert total_value == 2000


class TestOdynErrorScenarios(unittest.TestCase):
    """Tests for error scenarios and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = setup_test_client()

    @patch("requests.Session.request")
    def test_malformed_json_response(self, mock_request):
        """Test handling of malformed JSON response."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response

        # Make request and expect exception
        with self.assertRaises(ValueError):
            self.client.get("customers")

    @patch("requests.Session.request")
    def test_missing_value_key(self, mock_request):
        """Test handling of response missing 'value' key."""
        # Mock response without 'value' key
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No data available"}
        mock_request.return_value = mock_response

        # Make request and expect exception
        with self.assertRaises(TypeError):
            self.client.get("customers")

    @patch("requests.Session.request")
    def test_value_not_list(self, mock_request):
        """Test handling of 'value' that is not a list."""
        # Mock response with 'value' as string instead of list
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": "not a list"}
        mock_request.return_value = mock_response

        # Make request and expect exception
        with self.assertRaises(TypeError):
            self.client.get("customers")


class TestOdynPerformance(unittest.TestCase):
    """Performance tests for Odyn client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = setup_test_client()

    @patch("requests.Session.request")
    def test_large_dataset_handling(self, mock_request):
        """Test handling of large datasets."""
        # Mock large dataset (1000 items)
        large_dataset = [{"id": str(i), "name": f"Item {i}"} for i in range(1000)]

        # Split into pages
        page_size = 100
        pages = [large_dataset[i : i + page_size] for i in range(0, len(large_dataset), page_size)]

        # Create mock responses for each page
        mock_responses = []
        for i, page in enumerate(pages):
            response = Mock()
            response.status_code = 200
            response_data = {"value": page}

            # Add next link for all pages except the last
            if i < len(pages) - 1:
                response_data["@odata.nextLink"] = (
                    f"https://api.businesscentral.dynamics.com/v2.0/test/production/items?$skip={(i + 1) * page_size}"
                )

            response.json.return_value = response_data
            mock_responses.append(response)

        mock_request.side_effect = mock_responses

        # Make request
        result = self.client.get("items")

        # Assertions
        assert len(result) == 1000
        assert mock_request.call_count == 10

    @patch("requests.Session.request")
    def test_timeout_handling(self, mock_request):
        """Test timeout handling."""
        # Mock timeout error
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

        # Make request and expect exception
        with self.assertRaises(requests.exceptions.Timeout):
            self.client.get("customers")


def run_all_tests():
    """Run all test examples."""
    print("🧪 Odyn Testing Examples")
    print("=" * 50)
    print()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestOdynClient,
        TestOdynIntegration,
        TestOdynSessions,
        TestOdynBusinessLogic,
        TestOdynErrorScenarios,
        TestOdynPerformance,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("**Test Summary:**")
    print(f"  • Tests run: {result.testsRun}")
    print(f"  • Failures: {len(result.failures)}")
    print(f"  • Errors: {len(result.errors)}")
    print(
        f"  • Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"  # noqa: E501
    )

    return result


if __name__ == "__main__":
    run_all_tests()
