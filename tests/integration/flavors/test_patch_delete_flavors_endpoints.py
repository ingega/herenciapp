# tests/integration/test_update_and_delete_products_endpoints.py
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
    
    payload = {
        "main_dish": "taco de carnitas",
        "category": "alimentos",
        "price": 28.50
    }
    
    # Act: Create the product
    product_response = client.post("/orders/products/", json=payload)
    # Assert: the endpoint must response with a 201 response code
    assert product_response.status_code == status.HTTP_201_CREATED
    # Act: with a valid product, add the flavor for tests cases
    product_id = product_response.json()["id"]
    flavor_response = client.post(
        "/orders/flavors/",
        json={
            "product_id": product_id,
            "description": "taco de carnitas"
        }
    )
    # our flavor is ready to be updated/deleted
    return flavor_response.json()


class TestPatchDeleteFlavors:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_flavors_update_unauthenticated_redirects(self,client, setup_flavor):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        flavor_id = setup_flavor["id"]
        product_id = setup_flavor["product_id"]

        # Act: once flavor retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.patch(
            f"/orders/flavors/{flavor_id}", 
            json={"product_id": product_id, 
                  "description": "updated description"},
            headers={"accept": "application/json"} # Explicitly flag it as JSON context
        )
        
        # Assert: AJAX protection captures it as a 401 API Error
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Read the JSON response body payload validation asset
        json_data = response.json()
        assert json_data["status"] == "error"
        assert "detail" in json_data
    
    # ==============================================================================
    # TEST 2: test the PATCH orders/flavors/{id} enpoint 
    # ==============================================================================
    def test_flavors_update(self, client, authorized_client_cookies,setup_flavor, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the product id
        product_id = setup_flavor["product_id"]
        flavor_id = setup_flavor["id"]

        # Act: Execute the patch request
        response = client.patch(
            f"/orders/flavors/{flavor_id}", 
            json={"description": "updated description"},
            follow_redirects=False
        )
        data = response.json()
        # Assert:  Verify that response code is a 200 OK
        assert response.status_code == status.HTTP_200_OK
        # Assert: Verify that the description was successfully changed
        assert data["description"] == "updated description"
        # Assert: Verify that the product_id remains unchanged
        assert data["product_id"] == product_id
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()
        # bonus: verify that the changes were made in the database and not just in the response
        # Act: creates a db object
        db_flavor = session.get(FlavorCatalogue, flavor_id)
        # Assert: query executed successfully
        assert db_flavor is not None
        # Assert: Verify the information in database
        assert int(db_flavor.product_id) == product_id  # db returns string, API returns int
        # Assert: Verify that others fields remains untouched
        assert db_flavor.description == "updated description"

    # ==============================================================================
    # TEST 3: Unauthenticated User (No Cookie / Missing Credentials) for delete endpoint
    # ==============================================================================
    def test_flavor_delete_unauthenticated_redirects(self, client, setup_flavor):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        flavor_id = setup_flavor["id"]

        # Act: once flavor retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.delete(
            f"/orders/flavors/{flavor_id}", 
            headers={"accept": "application/json"} # Explicitly flag it as JSON context
        )
        
        # Assert: AJAX protection captures it as a 401 API Error, NOT a 303 browser bounce!
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Read the JSON response body payload validation asset
        json_data = response.json()
        assert json_data["status"] == "error"
        assert "detail" in json_data
    
    # ==============================================================================
    # TEST 4: test the DELETE orders/flavors/{id} enpoint 
    # ==============================================================================
    def test_flavors_delete(self, client, authorized_client_cookies,setup_flavor, session):
        """
        Verifu that the DELETE endpoint for flavors successfully removes the flavor from the database
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the flavor id
        flavor_id = setup_flavor["id"]

        # Assert that the flavor exists
        assert flavor_id is not None
        
        # Act: Execute the delete request
        response = client.delete(
            f"/orders/flavors/{flavor_id}", 
            follow_redirects=False
        )
        
        # Assert:  Verify that response is succesfully
        assert response.status_code == 200
        
        # Act: clean the session for database updated veryfication
        session.expire_all()

        # Act: creates a query of the deleted row
        db_flavor = session.get(FlavorCatalogue, flavor_id)
        # Assert: query executed successfully
        assert db_flavor is None
    