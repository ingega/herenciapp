# tests/integration/test_flavor_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.api.v1.apps.orders.models import FlavorCatalogue

# 1. app fixture in tests/conftest.py 
# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for product creation)
# ==============================================================================
@pytest.fixture(scope="function")
def setup_flavor(client, authorized_client_cookies):
    """
    Creates a baseline flavor in the catalogue to reuse across test cases.
    Injects authorized cookies to safely bypass authentication during creation.
    """
    
    # Act: creates an authorized user
    client.cookies.update(authorized_client_cookies)

    # Act: Add a new product uased as baseline for flavors
    
    product_payload = {
        "main_dish": "taco",
        "category": "alimentos",
        "price": 5.99
    }
    
    # Act: Create the product
    product_response = client.post("/orders/products", json=product_payload)
    product_id = product_response.json()["id"]
    
    # Return the created product for use in other tests
    return product_response.json()

class TestFlavorsEndpoints:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_flavor_create_unauthenticated_redirects(self,client, setup_flavor):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        product_id = setup_flavor["id"]

        # Act: once product retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Set the payload for flavor creation
        flavor_payload = {
            "product_id": product_id,
            "description": "chicken"
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/flavors", 
            json=flavor_payload,
            follow_redirects=False
        )
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/auth/login"
    