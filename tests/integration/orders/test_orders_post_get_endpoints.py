# tests/integration/test_flavor_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.api.v1.apps.orders.models import Order

# 1. app fixture in tests/conftest.py 
# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for product creation)
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
    
    order_payload = {
        "table_no": 1,
        "number_of_persons": 2,
        "items": [] # empty list, because we only want to create the order baseline.
    }
    
    # Act: Create the order
    order_response = client.post("/orders/create", json=order_payload)
    
    # Return the created order for use in other tests
    return order_response.json()

class TestOrdersEndpoints:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_order_create_unauthenticated_redirects(self,client, setup_order):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """

        # Act: clear the cookie (Unauthenticated state, because 
        # the setup_order fixture creates an order with authenticated client)
        client.cookies.clear()
        
        # Act: Set the payload for order creation
        order_payload = {
        "table_no": 1,
        "number_of_persons": 2,
        "items": []
    }
        # Act: Execute the post request
        response = client.post(
            f"/orders/create", 
            json=order_payload,
            follow_redirects=False
        )
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # ==============================================================================
    # TEST 2: Test that invalid data types or formats trigger validation errors
    # ==============================================================================
    def test_order_create_invalid_data_types_validation_errors(self,client, setup_order):
        """
        Ensure that providing invalid data type for order creation
        results in appropriate validation errors.
        """
        
        # Act: Set the payload for order creation, but omit required fields or provide invalid data
        order_payload = {
            "table_no": "invalid_string_instead_of_int",
            "number_of_persons": 2,
            "items": []
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/create", 
            json=order_payload,
            follow_redirects=False
        )

        # Assert: Validation errors are returned for incomplete or invalid data
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # ==============================================================================
    # TEST 3: Test the order creation endpoint
    # ==============================================================================
    def test_order_create_valid_data(self,client, session, setup_order):
        """
        Verify that providing valid data for order creation results in successful 
        creation and correct response structure.
        """

        # Act: Set the payload for order creation, but omit required fields or provide invalid data
        order_payload = {
            "table_no": 1,
            "number_of_persons": 2,
            "items": []
        }
        # Act: Execute the post request
        response = client.post(
            f"/orders/create", 
            json=order_payload,
            follow_redirects=False
        )

        # Assert: Successful creation and correct response structure
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        # Assert the response
        assert "id" in response_data
        assert response_data["table_no"] == 1
        assert response_data["number_of_persons"] == 2

        # Bonus assert, verify that also ths database add the new record
        # Act: clean the session for database updated veryfication

        # retrieve the order id from the response to query the database
        order_id = response_data["id"]
        session.expire_all()
        session.rollback()
        # Act: creates a db object
        db_order = session.get(Order, order_id)
        # Assert: query executed successfully
        assert db_order is not None
        # Assert: Verify the information in database
        assert int(db_order.table_no) == 1  # db sends string types
        assert db_order.number_of_persons == 2
    
    # ==============================================================================
    # TEST 4: Test the get order endpoint
    # ==============================================================================
    def test_order_get(self,client, setup_order):
        """
        Verify that the get order endpoint returns the correct data for an existing order.
        """
        # act: retrieve the order id from the setup_order fixture
        order_id = setup_order["id"]
        # now we have the order id, we can test the get endpoint
        get_order_response = client.get(
            f"/orders/{order_id}",
            follow_redirects=False
        )
        # Assert: Successful retrieval and correct response structure
        assert get_order_response.status_code == status.HTTP_200_OK
        assert "id" in get_order_response.json()
        assert get_order_response.json()["table_no"] == 1
        assert get_order_response.json()["number_of_persons"] == 2
    
    # ==============================================================================
    # TEST 5: Test the get all orders endpoint
    # ==============================================================================
    def test_order_get_all(self,client, setup_order):
        """
        Verify that the get all orders endpoint returns the correct data for existing orders.
        """
        # act: retrieve all the orders from the setup_order fixture
        get_order_response = client.get(
            f"/orders/all/",
            follow_redirects=False
        )
        # Assert: Successful retrieval and correct response structure
        assert get_order_response.status_code == status.HTTP_200_OK
        # there's only one order created by the setup_order fixture, 
        # so we can assert that the first order in the list is the one we created
        assert len(get_order_response.json()) == 1
        assert get_order_response.json()[0]["number_of_persons"] == 2
