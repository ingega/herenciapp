# tests/integreation/orders/items/test_items_update_and_delete_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.api.v1.apps.orders.models import OrderDetail as Item

# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for complex item nested creation)
# ==============================================================================
@pytest.fixture(scope="function")
def setup_item(client, authorized_client_cookies):
    """
    Creates baseline product, flavor, order, and nested item records.
    Returns a unified mapping of IDs for seamless down-stream test consumption.
    """
    # Act: Inject authenticated session cookies
    client.cookies.update(authorized_client_cookies)
    
    # 1. Create a Baseline Product
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
        "items": []
    }
    order_response = client.post("/orders/create", json=order_payload)
    assert order_response.status_code == status.HTTP_201_CREATED
    order_id = order_response.json()["id"]

    # 4. Append Item to Ticket (Endpoint returns updated Parent Order dict)
    item_payload = {
        "person_number": 1,
        "product_id": product_id,
        "flavor_id": flavor_id,
        "quantity": 2,
        "notes": "extra spicy",
        "extra_charge": 1.50
    }
    item_response = client.post(f"/orders/{order_id}/items", json=item_payload)
    assert item_response.status_code == status.HTTP_201_CREATED
    
    order_data = item_response.json()
    item_id = order_data['id']
    nested_item = order_data["items"][0]

    # Return a normalized dictionary so tests have simple access to all entity IDs
    return {
        "item_id": item_id,
        "order_id": order_id,
        "product_id": product_id,
        "flavor_id": flavor_id,
        "item_id": nested_item["id"],
        "quantity": 2,
        "person_number": nested_item["person_number"]
    }


class TestUpdateDeleteItems:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_items_update_unauthenticated_redirects(self,client, setup_item):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        order_id = setup_item["order_id"]

        # Act: once order retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.post(
            f"/orders/{order_id}/items", 
            json={
                "person_number": setup_item["person_number"],
                "product_id": setup_item["product_id"],
                "flavor_id": setup_item["flavor_id"],
                "quantity": 5  # this is the changed data
                },
            follow_redirects=False
        )
        
        # Assert: Authentication blocks (due that is a POST don't redirects any)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # ==============================================================================
    # TEST 2: test the PATCH orders/{id} enpoint 
    # ==============================================================================
    def test_items_update(self, client, authorized_client_cookies,setup_item, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the order id
        order_id = setup_item["order_id"]
        
        # Act: Execute the patch request
        response = client.post(
            f"/orders/{order_id}/items", 
            json={
                "person_number": setup_item["person_number"],
                "product_id": setup_item["product_id"],
                "flavor_id": setup_item["flavor_id"],
                "quantity": 5  # this is the changed data
                },
            follow_redirects=False
        )
        data = response.json()['items'][0]
        # Assert:  Verify that response code is a 200 OK
        assert response.status_code == status.HTTP_200_OK
        # Assert: Verify that the number of persons was successfully changed
        assert int(data["quantity"]) == 5
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()
        # Act: creates a db object
        db_item = session.get(Item, order_id)
        # Assert: query executed successfully
        assert db_item is not None
        # Assert: Verify the information in database
        assert float(db_item.quantity) == 5
        # Assert: Verify that others fields remains untouched
        assert db_item.product_id == setup_item['product_id']

    # ==============================================================================
    # TEST 3: Unauthenticated User (No Cookie / Missing Credentials) for delete endpoint
    # ==============================================================================
    def test_items_delete_unauthenticated_redirects(self, client, setup_item):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        order_id = setup_item["order_id"]
        item_id = setup_item["item_id"]

        # Act: once order retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.delete(
            f"orders/delete/{order_id}/items/{item_id}", 
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
    def test_items_delete(self, client, authorized_client_cookies,setup_item, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the order and item id
        order_id = setup_item["order_id"]
        item_id = setup_item["item_id"]

        # Assert that the order exists
        assert order_id is not None
        
        # Act: Execute the delete request
        response = client.delete(
            f"orders/delete/{order_id}/items/{item_id}", 
            follow_redirects=False
        )
        
        # Assert:  Verify that response is succesfully
        assert response.status_code == 200
        
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()

        # Act: creates a query of the deleted row
        db_order = session.get(Item, item_id)
        # Assert: query executed successfully
        assert db_order is None
    