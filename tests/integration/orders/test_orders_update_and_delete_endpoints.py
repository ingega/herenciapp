# tests/integration/test_orders_update_and_delete_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.api.v1.apps.orders.models import Order

# 1. app fixture in tests/conftest.py 
# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for order creation)
# ==============================================================================
@pytest.fixture(scope="function")
def setup_order(client, authorized_client_cookies):
    """
    Creates a baseline order in the catalogue to reuse across test cases.
    Injects authorized cookies to safely bypass authentication during creation.
    """
    
    # Act: creates an authorized user
    client.cookies.update(authorized_client_cookies)
    
    payload = {
        "table_no": 1,
        "number_of_persons": 2,
        "items": []
    }
    
    # Act: Create the order
    response = client.post("/orders/create", json=payload)
    # Assert: the endpoint must response with a 201 response code
    assert response.status_code == status.HTTP_201_CREATED
    # our order is ready to be updated/deleted
    return response.json()


class TestUpdateDeleteOrders:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_orders_update_unauthenticated_redirects(self,client, setup_order):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        order_id = setup_order["id"]

        # Act: once order retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.patch(
            f"/orders/update/{order_id}", 
            json={"number_of_persons": 3},
            follow_redirects=False,
            headers={"accept": "application/json"}
        )
        
        # Assert: AJAX protection captures it as a 401 API Error
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Read the JSON response body payload validation asset
        json_data = response.json()
        assert json_data["status"] == "error"
        assert "detail" in json_data
    
    # ==============================================================================
    # TEST 2: test the PATCH orders/{id} enpoint 
    # ==============================================================================
    def test_orders_update(self, client, authorized_client_cookies,setup_order, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the order id
        order_id = setup_order["id"]
        
        # Act: Execute the patch request
        response = client.patch(
            f"/orders/update/{order_id}", 
            json={"number_of_persons": 3},
            follow_redirects=False
        )
        data = response.json()
        # Assert:  Verify that response code is a 200 OK
        assert response.status_code == status.HTTP_200_OK
        # Assert: Verify that the number of persons was successfully changed
        assert int(data["number_of_persons"]) == 3
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()
        # Act: creates a db object
        db_order = session.get(Order, order_id)
        # Assert: query executed successfully
        assert db_order is not None
        # Assert: Verify the information in database
        assert float(db_order.number_of_persons) == 3
        # Assert: Verify that others fields remains untouched
        assert db_order.table_no == 1

    # ==============================================================================
    # TEST 3: Unauthenticated User (No Cookie / Missing Credentials) for delete endpoint
    # ==============================================================================
    def test_orders_delete_unauthenticated_redirects(self, client, setup_order):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        order_id = setup_order["id"]

        # Act: once order retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.delete(
            f"/orders/delete/{order_id}", 
            follow_redirects=False,
            headers={"accept": "application/json"}
        )
        
        # Assert: AJAX protection captures it as a 401 API Error
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Read the JSON response body payload validation asset
        json_data = response.json()
        assert json_data["status"] == "error"
        assert "detail" in json_data
    
    # ==============================================================================
    # TEST 4: test the DELETE orders/{id} enpoint 
    # ==============================================================================
    def test_orders_delete(self, client, authorized_client_cookies,setup_order, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the order id
        order_id = setup_order["id"]

        # Assert that the order exists
        assert order_id is not None
        
        # Act: Execute the delete request
        response = client.delete(
            f"/orders/delete/{order_id}", 
            follow_redirects=False
        )
        
        # Assert:  Verify that response is succesfully
        assert response.status_code == 204
        
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()

        # Act: creates a query of the deleted row
        db_order = session.get(Order, order_id)
        # Assert: query executed successfully
        assert db_order is None
    