# tests/integration/test_update_and_delete_products_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient

# 1. app fixture in tests/conftest.py 
# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for product creation)
# ==============================================================================
@pytest.fixture(scope="function")
def setup_product(app, authorized_client_cookies):
    """
    Creates a baseline product in the catalogue to reuse across test cases.
    Injects authorized cookies to safely bypass authentication during creation.
    """
    client = TestClient(app)
    
    # Act: creates an authorized user
    client.cookies.update(authorized_client_cookies)
    
    payload = {
        "main_dish": "taco de carnitas",
        "category": "alimentos",
        "price": 28.50
    }
    
    # Act: Create the product
    response = client.post("/orders/products", json=payload)
    # Assert: the endpoint must response with a 201 response code
    assert response.status_code == status.HTTP_201_CREATED
    # our product is ready to be updated/deleted
    return response.json()


class TestUpdateDeleteProducts:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_products_update_unauthenticated_redirects(self, app, setup_product):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Initialize an clean client with no credentials context
        client = TestClient(app)
        
        product_id = setup_product["id"]
        
        # Act: Execute the patch request
        response = client.patch(
            f"/orders/products/{product_id}", 
            json={"price": 32.00},
            follow_redirects=False
        )
        
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/auth/login"
    
    # ==============================================================================
    # TEST 2: test the PATCH orders/products/{id} enpoint 
    # ==============================================================================
    def test_products_update(self, app, authorized_client_cookies,setup_product):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Initialize an clean client with no credentials context
        client = TestClient(app)

        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        product_id = setup_product["id"]
        
        # Act: Execute the patch request
        response = client.patch(
            f"/orders/products/{product_id}", 
            json={"price": 32.00},
            follow_redirects=False
        )
        data = response.json()
        # Assert:  Verify that response code is a 200 OK
        assert response.status_code == status.HTTP_200_OK
        # Assert: Verify that the price was successfully changed
        assert float(data["price"]) == 32.00 # response sends strings types
    
    