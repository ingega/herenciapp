# tests/integration/test_using_verification.py
import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_user_verification_flow_success(client, session):
    # 1. Register - FIX: Ensure the URL matches your router prefix
    # If your main.py includes the router with prefix "/api/v1" 
    # and the user router has prefix "/users", the path is /api/v1/users/register
    user_data = {
        "email": "partner_test@herenciapp.com",
        "password": "SecurePassword123!",
        "full_name": "Test Partner"
    }
    
    # Correctly awaiting the ASYNC client
    register_response = await client.post("/api/v1/users/register", json=user_data)
    
    # If you still get a 404, check if the prefix in main.py is correct!
    assert register_response.status_code == status.HTTP_201_CREATED
    
    # 2. Extract Token from DB
    from src.api.v1.apps.users.models import VerificationToken
    from sqlalchemy import select
    
    result = await session.execute(select(VerificationToken))
    db_token = result.scalars().first()
    
    # 3. Verify
    verify_payload = {
        "email": user_data["email"],
        "token": db_token.token
    }
    verify_response = await client.post("/api/v1/users/verify", json=verify_payload)
    
    assert verify_response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_verification_fails_with_wrong_token(client, session):
    """
    Security check: Ensure wrong tokens are rejected with a 400 error
    """
    # Register a user
    user_data = {"email": "security@test.com", "password": "Password123!", "full_name": "Sec"}
    await client.post("/api/v1/users/register", json=user_data)
    
    # Try to verify with a fake token
    verify_payload = {
        "email": "security@test.com",
        "token": "WRONG_TOKEN_12345"
    }
    response = await client.post("/api/v1/users/verify", json=verify_payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid or expired token" in response.json()["detail"]

@pytest.mark.asyncio
async def test_verification_fails_for_missing_user(client):
    """
    Identity check: Reject verification for emails not in the system
    """
    verify_payload = {
        "email": "ghost@herenciapp.com",
        "token": "anytoken"
    }
    response = await client.post("/api/v1/users/verify", json=verify_payload)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]