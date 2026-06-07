# tests/integration/test_update_and_delete_products_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.api.v1.apps.orders.models import MeatCatalogue

# 1. app fixture in tests/conftest.py 
# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for product creation)
# ==============================================================================
@pytest.fixture(scope="function")
def setup_meat(client, authorized_client_cookies):
    """
    Creates a baseline meat option in the catalogue to reuse across test cases.
    Injects authorized cookies to safely bypass authentication during creation.
    """
    
    # Act: creates an authorized user
    client.cookies.update(authorized_client_cookies)
    
    payload = {
        "description": "surtida"
    }
    
    # Act: Create the product
    meat_response = client.post("/orders/flavors/meat/add", json=payload)
    # Assert: the endpoint must response with a 201 response code
    assert meat_response.status_code == status.HTTP_201_CREATED
    
    # our meat is ready to be updated/deleted
    return meat_response.json()


class TestPatchDeleteMeats:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_meats_update_unauthenticated_redirects(self,client, setup_meat):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        meat_id = setup_meat["id"]

        # once meat retreived, clear the cookie
        client.cookies.clear()

        # Act: Execute the patch request
        response = client.patch(
            f"/orders/flavors/meat/{meat_id}", 
            json={"description": "updated description"},
            follow_redirects=False
        )
        
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/auth/login"
    
    # ==============================================================================
    # TEST 2: test the PATCH orders/flavors/meat/{id} enpoint 
    # ==============================================================================
    def test_meats_update(self, client, authorized_client_cookies,setup_meat, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the meat id
        meat_id = setup_meat["id"]

        # Act: Execute the patch request
        response = client.patch(
            f"/orders/flavors/meat/{meat_id}", 
            json={"description": "updated description"},
            follow_redirects=False
        )
        data = response.json()
        # Assert:  Verify that response code is a 200 OK
        assert response.status_code == status.HTTP_200_OK
        # Assert: Verify that the description was successfully changed
        assert data["description"] == "updated description"
        # Assert: Verify that the product_id remains unchanged
        assert data["id"] == meat_id
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()
        # bonus: verify that the changes were made in the database and not just in the response
        # Act: creates a db object
        db_meat = session.get(MeatCatalogue, meat_id)
        # Assert: query executed successfully
        assert db_meat is not None
        # Assert: Verify the information in database
        assert int(db_meat.id) == meat_id  # db returns string, API returns int
        # Assert: Verify that others fields remains untouched
        assert db_meat.description == "updated description"

    # ==============================================================================
    # TEST 3: Unauthenticated User (No Cookie / Missing Credentials) for delete endpoint
    # ==============================================================================
    def test_meat_delete_unauthenticated_redirects(self, client, setup_meat):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        meat_id = setup_meat["id"]

        # Act: once meat retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.delete(
            f"/orders/flavors/meat/{meat_id}", 
            follow_redirects=False
        )
        
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/auth/login"
    
    # ==============================================================================
    # TEST 4: test the DELETE orders/flavors/meat/{id} enpoint 
    # ==============================================================================
    def test_meats_delete(self, client, authorized_client_cookies,setup_meat, session):
        """
        Verify that the DELETE endpoint for meats successfully removes the meat from the database
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the meat id
        meat_id = setup_meat["id"]

        # Assert that the meat exists
        assert meat_id is not None
        
        # Act: Execute the delete request
        response = client.delete(
            f"/orders/flavors/meat/{meat_id}", 
            follow_redirects=False
        )
        
        # Assert:  Verify that response is succesfully
        assert response.status_code == 200
        
        # Act: clean the session for database updated veryfication
        session.expire_all()

        # Act: creates a query of the deleted row
        db_meat = session.get(MeatCatalogue, meat_id)
        # Assert: query executed successfully
        assert db_meat is None
    