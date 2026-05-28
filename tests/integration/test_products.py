# tests/integration/test_products.py

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.api.v1.apps.orders.models import Product
from src.api.v1.apps.users.services import create_user

# Assuming your authentication engine exposes the dependency function
from src.api.v1.auth.auth import get_current_user_from_cookie


# -------------------------------------------------------------------------
# Fixture: Mock Authentication Dependency Override
# -------------------------------------------------------------------------
@pytest.fixture
def mock_authenticated_user(app):
    """
    Overrides the cookie dependency to automatically return a dummy user profile
    without needing to spin up the JWT signing engine or set up actual cookies.
    """
    dummy_user = {"id": 1, "email": "chef@restaurant.com"}
    
    # Force FastAPI to resolve the dependency by yielding the dummy user directly in the override
    app.dependency_overrides[get_current_user_from_cookie] = lambda: dummy_user
    yield dummy_user
    
    # Clean up overrides after the test finishes so other tests stay pure
    app.dependency_overrides.pop(get_current_user_from_cookie, None)


# -------------------------------------------------------------------------
# 1. Test: Try to save a product without authentication
# -------------------------------------------------------------------------
def test_create_product_unauthenticated(client: TestClient):
    """
    Ensure that a naked request without cookies or dependency overrides
    gets blocked at the perimeter gate.
    """
    # 1. create a valid user to avoid the 404 response code


    payload = {
        "main_dish": "Taco Al Pastor",
        "category": "taco",
        "price": 25.50
    }
    response = client.post("orders/products", json=payload)
    
    # It should fail authentication (401 Unauthorized)
    assert response.status_code == 401


# -------------------------------------------------------------------------
# 2. Test: Send misformed data and verify validation rejection
# -------------------------------------------------------------------------
def test_create_product_malformed_data(client: TestClient, mock_authenticated_user):
    """
    Even with valid authentication, sending a missing field (like main_dish)
    or invalid numeric string should trigger a Pydantic 422 Unprocessable Entity.
    """
    # Payload missing the required 'main_dish' field entirely
    malformed_payload = {
        "category": "beverage",
        "price": 20.50
    }
    
    response = client.post("orders/products", json=malformed_payload)
    
    assert response.status_code == 422
    # Verify Pydantic validation details are attached
    assert "detail" in response.json()

# -------------------------------------------------------------------------
# 3. Test: Send invalid data and verify validation rejection
# -------------------------------------------------------------------------
def test_create_product_invalid_data(client: TestClient, mock_authenticated_user):
    """
    Even with valid authentication, sending a invalid numeric string 
    should trigger a Pydantic 422 Unprocessable Entity.
    """
    # Payload missing the required 'main_dish' field entirely
    not_valid_payload = {
        "main_dish": "Coca Cola",
        "category": "beverage",
        "price": "Not a number"
    }
    
    response = client.post("orders/products", json=not_valid_payload)
    
    assert response.status_code == 422
    # Verify Pydantic validation details are attached
    assert "detail" in response.json()

# -------------------------------------------------------------------------
# 4 & 5. Test: Assert 201 Created, Validate Output Schema & DB Persistence
# -------------------------------------------------------------------------
def test_create_product_success(client: TestClient, 
                                session: Session, mock_authenticated_user):
    """
    Asserts a successful post returns 201, matches our ProductRead serialization shape,
    and accurately writes the row into our active test database session.
    """
    payload = {
        "main_dish": "Gringa Especial",
        "category": "package",
        "price": 85.00
    }
    
    response = client.post("orders/products", json=payload)
    
    # 4. Assert Response status code is explicitly 201 CREATED
    assert response.status_code == 201
    
    # 5. Assert response JSON structure mirrors the ProductRead output shape exactly
    data = response.json()
    assert "id" in data
    assert data["main_dish"] == payload["main_dish"]
    assert data["category"] == payload["category"]
    # Convert back to float or string matching validation serialization context
    assert float(data["price"]) == payload["price"]
    
    # Bonus Elite Step: Confirm database isolation commit
    db_product = session.get(Product, data["id"])
    assert db_product is not None
    assert db_product.main_dish == "Gringa Especial"