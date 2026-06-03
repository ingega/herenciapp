# tests/integration/test_flavor_endpoints.py
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
    Creates a baseline meat in the catalogue to reuse across test cases.
    Injects authorized cookies to safely bypass authentication during creation.
    """
    
    # Act: creates an authorized user
    client.cookies.update(authorized_client_cookies)

    # Act: Add a new meat to the catalogue
    
    meat_payload = {
        "description": "lengua"
    }
    
    # Act: Create the meat
    meat_response = client.post("/orders/flavors/meat/add", json=meat_payload)
    
    # Return the created meat for use in other tests
    return meat_response.json()

class TestMeatsEndpoints:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_meat_create_unauthenticated_redirects(self,client):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """

        # Act: clear the cookie
        client.cookies.clear()
        
        # Act: Set the payload for meat creation
        meat_payload = {
            "description": "costilla"
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/flavors/meat/add", 
            json=meat_payload,
            follow_redirects=False
        )
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==============================================================================
    # TEST 2: Test that missing fields or malformed data triggers validation errors
    # ==============================================================================
    def test_meat_create_validation_errors(self,client, setup_meat):
        """
        Ensure that providing incomplete or invalid data for flavor creation
        results in appropriate validation errors.
        """
        
        # Act: Set the payload for meat creation, but omit required fields or provide invalid data
        meat_payload = {
            "not_description": "lengua"
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/flavors/meat/add", 
            json=meat_payload,
            follow_redirects=False
        )

        # Assert: Validation errors are returned for incomplete or invalid data
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # ==============================================================================
    # TEST 3: Test that invalid data types or formats trigger validation errors
    # ==============================================================================
    def test_meat_create_invalid_data_types_validation_errors(self,client, setup_meat):
        """
        Ensure that providing invalid data type for flavor creation
        results in appropriate validation errors.
        """
        
        # Act: Set the payload for meat creation, but omit required fields or provide invalid data
        meat_payload = {
            "description": 123  # Invalid type - should be a string
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/flavors/meat/add", 
            json=meat_payload,
            follow_redirects=False
        )

        # Assert: Validation errors are returned for incomplete or invalid data
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # ==============================================================================
    # TEST 4: Test the meat creation endpoint
    # ==============================================================================
    def test_meat_create_valid_data(self,client, session, setup_meat):
        """
        Verify that providing valid data for meat creation results in successful 
        creation and correct response structure.
        """
        product_id = setup_meat["id"]
        # Act: Set the payload for meat creation, but omit required fields or provide invalid data
        meat_payload = {
            "description": "surtido"
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/flavors/meat/add", 
            json=meat_payload,
            follow_redirects=False
        )

        # Assert: Successful creation and correct response structure
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        meat_id = response_data["id"]
        # Assert the response
        assert "id" in response_data
        assert response_data["description"] == "surtido"

        # Bonus assert, verify that also the database add the new record
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()
        # Act: creates a db object
        db_meat = session.get(MeatCatalogue, meat_id)
        # Assert: query executed successfully
        assert db_meat is not None
        # Assert: Verify the information in database
        assert int(db_meat.id) == meat_id  # db sends string types
        assert db_meat.description == "surtido"
    
    # ==============================================================================
    # TEST 5: Test the get meat endpoint
    # ==============================================================================
    def test_meat_get(self,client, setup_meat):
        """
        Verify that the get meat endpoint returns the correct data for an existing meat.
        """
        meat_id = setup_meat["id"]
        
        # Act: Execute the get request for the created meat
        get_meat_response = client.get(
            f"/orders/flavors/meat/{meat_id}",
            follow_redirects=False
        )
        # Assert: Successful retrieval and correct response structure
        assert get_meat_response.status_code == status.HTTP_200_OK
        assert "id" in get_meat_response.json()
        assert get_meat_response.json()["description"] == "lengua"