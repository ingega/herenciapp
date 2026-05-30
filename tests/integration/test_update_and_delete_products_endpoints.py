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
    response = client.post("/orders/products", json=payload)
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
            json={"price": 32.00},
            follow_redirects=False
        )
        
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/auth/login"
    
    # ==============================================================================
    # TEST 2: test the PATCH orders/products/{id} enpoint 
    # ==============================================================================
    def test_products_update(self, client, authorized_client_cookies,setup_product, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the product id
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
        # Act: clean the session for database updated veryfication
        session.expire_all()
        session.rollback()
        # Act: creates a db object
        db_product = session.get(Product, product_id)
        # Assert: query executed successfully
        assert db_product is not None
        # Assert: Verify the information in database
        assert float(db_product.price) == 32.00
        # Assert: Verify that others fields remains untouched
        assert db_product.main_dish == "taco de carnitas"

    # ==============================================================================
    # TEST 3: Unauthenticated User (No Cookie / Missing Credentials) for delete endpoint
    # ==============================================================================
    def test_products_delete_unauthenticated_redirects(self, client, setup_product):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        
        product_id = setup_product["id"]

        # Act: once product retreived, clear the cookie
        client.cookies.clear()
        
        # Act: Execute the patch request
        response = client.delete(
            f"/orders/products/{product_id}", 
            follow_redirects=False
        )
        
        # Assert: Authentication blocks and redirects to login layout
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/auth/login"
    
    # ==============================================================================
    # TEST 4: test the DELETE orders/products/{id} enpoint 
    # ==============================================================================
    def test_products_delete(self, client, authorized_client_cookies,setup_product, session):
        """
        Ensure that accessing the protected UI route without an active session
        or auth cookie results in a clean redirect or unauthorized handling.
        """
        # Act: creates an authorized user
        client.cookies.update(authorized_client_cookies)
        
        # Act: retrieve the product id
        product_id = setup_product["id"]

        # Assert that the product exists
        assert product_id is not None
        
        # Act: Execute the delete request
        response = client.delete(
            f"/orders/products/{product_id}", 
            follow_redirects=False
        )
        
        # Assert:  Verify that response is succesfully
        assert response.status_code == 200
        
        # Act: clean the session for database updated veryfication
        session.expire_all()

        # Act: creates a query of the deleted row
        db_product = session.get(Product, product_id)
        # Assert: query executed successfully
        assert db_product is None
    