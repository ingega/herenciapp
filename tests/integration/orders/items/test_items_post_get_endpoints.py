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
    nested_item = order_data["items"][0]

    # Return a normalized dictionary so tests have simple access to all entity IDs
    return {
        "order_id": order_id,
        "product_id": product_id,
        "flavor_id": flavor_id,
        "item_id": nested_item["id"],
        "person_number": nested_item["person_number"]
    }


class TestItemsEndpoints:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_item_create_unauthenticated_redirects(self, client, setup_item):
        """
        Ensure that accessing the protected endpoint without auth cookies
        blocks execution with a 401 Unauthorized response status code.
        """
        client.cookies.clear()
        order_id = setup_item["order_id"]

        item_payload = {
            "person_number": 1,
            "product_id": setup_item["product_id"],
            "flavor_id": setup_item["flavor_id"],
            "quantity": 1
        }

        # Act: Pass payload along to trigger security interceptor before validation blocks it
        response = client.post(
            f"/orders/{order_id}/items",
            json=item_payload,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # ==============================================================================
    # TEST 2: Schema Type or Format Violations
    # ==============================================================================
    def test_item_create_invalid_data_types_validation_errors(self, client, authorized_client_cookies, setup_item):
        """
        Ensure omitting required schema values (like product_id) throws a 422 error.
        """
        client.cookies.update(authorized_client_cookies)
        order_id = setup_item["order_id"]

        # Act: Omit product_id and flavor_id completely
        item_payload = {
            "person_number": 1,
            "quantity": 2,
            "notes": "extra spicy",
            "extra_charge": 1.50
        }
        
        response = client.post(
            f"/orders/{order_id}/items",
            json=item_payload,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # ==============================================================================
    # TEST 3: Successful Item Appending / Upsert Flow
    # ==============================================================================
    def test_item_create_valid_data(self, client, session, authorized_client_cookies, setup_item):
        """
        Verify that adding a unique seating item successfully alters parent ticket contents.
        """
        client.cookies.update(authorized_client_cookies)
        order_id = setup_item["order_id"]
        product_id = setup_item["product_id"]
        flavor_id = setup_item["flavor_id"]

        item_payload = {
            "person_number": 2,  # Different seat number to append a clean new line
            "product_id": product_id,
            "flavor_id": flavor_id,
            "quantity": 1,
            "notes": "mild"
        }
        
        response = client.post(
            f"/orders/{order_id}/items",
            json=item_payload,
            follow_redirects=False
        )

        assert response.status_code == status.HTTP_201_CREATED
        order_response_data = response.json()

        # REMEMBER: The endpoint answers back with the Parent Order data schema!
        assert order_response_data["id"] == order_id
        # Our fixture inserted item 1, and this test inserted item 2 -> len must be 2
        assert len(order_response_data["items"]) == 2 

        # Direct DB session validation check on Item table model
        session.expire_all()
        session.rollback()
        
        # Verify both items exist in the database linked to this order
        db_order_items = session.query(Item).filter(Item.order_id == order_id).all()
        assert len(db_order_items) == 2
    
    # ==============================================================================
    # TEST 4: Get All Orders containing updated child items
    # ==============================================================================
    def test_item_get_all(self, client, authorized_client_cookies, setup_item):
        """
        Verify that fetching all active ticket nodes handles embedded elements smoothly.
        """
        client.cookies.update(authorized_client_cookies)
        order_id = setup_item['order_id']

        get_order_response = client.get(
            f"/orders/items/all/?order_id={order_id}",
            follow_redirects=False
        )
        
        # Assert: Serialization validation passes flawlessly!
        assert get_order_response.status_code == status.HTTP_200_OK
        items_list = get_order_response.json()
        
        assert isinstance(items_list, list)
        assert len(items_list) >= 1
        
        # Extract item properties directly out of index position 0
        target_item = items_list[0]
        assert target_item["product_id"] == setup_item["product_id"]
        assert target_item["person_number"] == setup_item["person_number"]