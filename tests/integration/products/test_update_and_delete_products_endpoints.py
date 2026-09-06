# tests/integration/test_update_and_delete_products_endpoints.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.api.v1.apps.orders.models import Product

# 1. app fixture in tests/conftest.py 
# ==============================================================================
# DATA SETUP FIXTURE (Authenticated for product creation)
# ==============================================================================
@pytest.fixture(scope="function")
def setup_product(client, authorized_client_cookies):
    """
    Creates a baseline product in the catalogue to reuse across test cases.
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
    response = client.post("/orders/products/", data=payload)
    # Assert: the endpoint must response with a 201 response code
    assert response.status_code == status.HTTP_201_CREATED
    # our product is ready to be updated/deleted
    return response.json()


class TestUpdateDeleteProducts:

    # ==============================================================================
    # TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
    # ==============================================================================
    def test_products_update_unauthenticated_redirects(self,client, setup_product):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        product_id = setup_product["id"]

        # Act: once product retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.patch(
            f"/orders/products/{product_id}", 
            data={"price": 32.00},
            follow_redirects=False
        )
        
        # Assert: AJAX protection captures it as a 401 API Error
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Read the JSON response body payload validation asset
        json_data = response.json()
        assert json_data["status"] == "error"
        assert "detail" in json_data
    
    # ==============================================================================
    # TEST 2: test the PATCH orders/products/{id} enpoint 
    # ==============================================================================
    def test_products_update(
        self,
        client,
        authorized_client_cookies,
        setup_product,
        session,
    ):
        """
        Ensure an authorized user can update a product and that
        the changes are persisted correctly in the database.
        """
        # Arrange: authenticate the client
        client.cookies.update(authorized_client_cookies)

        product_id = setup_product["id"]

        update_data = {
            "main_dish": setup_product["main_dish"],
            "category": setup_product["category"],
            "price": "32.00",
        }

        # Act: update the product
        response = client.patch(
            f"/orders/products/{product_id}",
            data=update_data,
            follow_redirects=False,
        )

        # Assert: API response
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["id"] == product_id
        assert float(data["price"]) == 32.00
        assert data["main_dish"] == setup_product["main_dish"]
        assert data["category"] == setup_product["category"]

        # Arrange: refresh the SQLAlchemy session state
        session.expire_all()
        session.rollback()

        # Act: retrieve the updated product from the database
        db_product = session.get(Product, product_id)

        # Assert: product exists
        assert db_product is not None

        # Assert: updated value was persisted
        assert float(db_product.price) == 32.00

        # Assert: other fields remain unchanged
        assert db_product.main_dish == setup_product["main_dish"]
        assert db_product.category == setup_product["category"]
