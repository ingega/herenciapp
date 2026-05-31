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
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==============================================================================
    # TEST 2: Test that missing fields or malformed data triggers validation errors
    # ==============================================================================
    def test_flavor_create_validation_errors(self,client, setup_flavor):
        """
        Ensure that providing incomplete or invalid data for flavor creation
        results in appropriate validation errors.
        """
        
        product_id = setup_flavor["id"]
        
        # Act: Set the payload for flavor creation, but omit required fields or provide invalid data
        flavor_payload = {
            "description": "chicken"
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/flavors", 
            json=flavor_payload,
            follow_redirects=False
        )

        # Assert: Validation errors are returned for incomplete or invalid data
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # ==============================================================================
    # TEST 3: Test that invalid data types or formats trigger validation errors
    # ==============================================================================
    def test_flavor_create_invalid_data_types_validation_errors(self,client, setup_flavor):
        """
        Ensure that providing invalid data type for flavor creation
        results in appropriate validation errors.
        """
        
        # Act: Set the payload for flavor creation, but omit required fields or provide invalid data
        flavor_payload = {
            "product_id": "invalid_string_instead_of_int",
            "description": "chicken"
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/flavors", 
            json=flavor_payload,
            follow_redirects=False
        )

        # Assert: Validation errors are returned for incomplete or invalid data
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # ==============================================================================
    # TEST 3: Test that invalid data types or formats trigger validation errors
    # ==============================================================================
    def test_flavor_create_valid_data(self,client, session, setup_flavor):
        """
        Verify that providing valid data for flavor creation results in successful 
        creation and correct response structure.
        """
        product_id = setup_flavor["id"]
        # Act: Set the payload for flavor creation, but omit required fields or provide invalid data
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

        # Assert: Successful creation and correct response structure
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        # Assert the response
        assert "id" in response_data
        assert response_data["product_id"] == product_id
        assert response_data["description"] == "chicken"

        # Bonus assert, verify that also ths database add the new record
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()
        # Act: creates a db object
        db_product = session.get(FlavorCatalogue, product_id)
        # Assert: query executed successfully
        assert db_product is not None
        # Assert: Verify the information in database
        assert int(db_product.product_id) == product_id  # db sends string types
        assert db_product.description == "chicken"