# tests/integration/orders/kitchen/test_dashboard_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.api.v1.apps.orders.models import Order

# 1. app fixture in tests/conftest.py 
# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for items creation)
# ==============================================================================
@pytest.fixture(scope="function")
def setup_order(client, authorized_client_cookies):
    """
    Creates a baseline order in the catalogue to reuse across test cases.
    Injects authorized cookies to safely bypass authentication during creation.
    """
    
    # Act: creates an authorized user
    client.cookies.update(authorized_client_cookies)

    # Act: Add a new product uased as baseline for flavors
    
    product_payload = {
        "main_dish": "taco",
        "category": "food",
        "price": 10.00
    }
    product_response = client.post("/orders/products/", json=product_payload)
    assert product_response.status_code == status.HTTP_201_CREATED
    product_id = product_response.json()["id"]

    # 2. Create a Baseline Flavor mapped to Product
    flavor_payload = {
        "product_id": product_id,
        "description": "carne"
    }
    flavor_response = client.post("/orders/flavors/", json=flavor_payload)
    assert flavor_response.status_code == status.HTTP_201_CREATED
    flavor_id = flavor_response.json()["id"]

    # 3. Create an Empty Parent Order
    order_payload = {
        "table_no": 1,
        "number_of_persons": 2,
        "items": [
        {
        "person_number": 1,
        "product_id": product_id,
        "flavor_id": flavor_id,
        "quantity": 2,
        "notes": "extra spicy",
        "extra_charge": 1.50
            }
        ]
    }
    order_response = client.post("/orders/create", json=order_payload)
    assert order_response.status_code == status.HTTP_201_CREATED
    order_id = order_response.json()["id"]
    
    order_data = order_response.json()

    return order_data

class TestOrdersEndpoints:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_kitchen_dashboard_unauthenticated_redirects(self,client, setup_order):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """

        # Act: clear the cookie (Unauthenticated state, because 
        # the setup_order fixture creates an order with authenticated client)
        client.cookies.clear()
        
        # Act: Execute the get request
        response = client.get(
            f"/orders/kitchen/dashboard",
            follow_redirects=False
        )
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_303_SEE_OTHER
    
    # ==============================================================================
    # TEST 2: Test the endpoint with an authenticated user
    # ==============================================================================
    def test_kitchen_dashboard_authenticated_success(self, client, authorized_client_cookies):
        """
        Ensure that an authorized request loads the dashboard template layout,
        injects session structures safely, and skips auth fallback paths.
        """
        # 1. Mount cookies cleanly on the client instance to clear deprecation warnings 
        # and guarantee middleware visibility.
        client.cookies.update(authorized_client_cookies)
        
        # 2. Act: Set follow_redirects=False.
        response = client.get("/orders/kitchen/dashboard", follow_redirects=False)
        
        # Assert 1: Verify it stayed on the dashboard page (No redirection triggered!)
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        
        # Assert 2: Jinja Context Inspection
        assert response.context is not None
        assert "config" in response.context
        
        # Assert 3: Text content visual validation
        assert "opción por platillo" in response.text
        assert "Platillos" in response.text

        # 3. Cleanup client session states for test isolation
        client.cookies.clear()
