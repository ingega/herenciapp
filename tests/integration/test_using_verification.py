# tests/integration/test_using_verification.py
import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_user_verification_flow_success(client, session):
    """
    Test the complete successful flow: Register -> Verify -> Account Active
    """
    # 1. Register the user
    user_data = {
        "email": "partner_test@herenciapp.com",
        "password": "SecurePassword123!",
        "full_name": "Test Partner"
    }
    register_response = await client.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == status.HTTP_201_CREATED
    
    # 2. Extract the token directly from the DB (since we mock the email service)
    # This mimics the user clicking the link in their email
    from src.api.v1.apps.users.models import VerificationToken
    from sqlalchemy import select
    
    result = await session.execute(select(VerificationToken))
    db_token = result.scalars().first()
    
    # 3. Verify the account
    verify_payload = {
        "email": user_data["email"],
        "token": db_token.token
    }
    verify_response = await client.post("/api/v1/users/verify", json=verify_payload)
    
    assert verify_response.status_code == status.HTTP_200_OK
    assert verify_response.json()["message"] == "Account successfully verified"

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