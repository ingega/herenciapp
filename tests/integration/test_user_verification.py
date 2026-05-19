# tests/integration/test_using_verification.py
import pytest
from fastapi import status
from sqlmodel import select
from src.api.v1.apps.users.models import VerificationToken

def test_user_verification_flow_success(client, session):
    user_data = {
        "email": "partner_test@herenciapp.com",
        "password": "SecurePassword123!"
    }
    
    # 1. Register - Path updated to match main.py (no /api/v1)
    register_response = client.post("/users/register", json=user_data)
    
    assert register_response.status_code == status.HTTP_201_CREATED
    
    # 2. Extract Token from DB using the sync session
    # We use session.exec() for SQLModel or session.execute() for SQLAlchemy
    db_token = session.exec(select(VerificationToken)).first()
    assert db_token is not None
    
    # 3. Verify
    verify_payload = {
        "email": user_data["email"],
        "token": db_token.token
    }
    verify_response = client.post("/users/verify", json=verify_payload)
    
    assert verify_response.status_code == status.HTTP_200_OK

def test_verification_fails_with_wrong_token(client, session):
    user_data = {"email": "security@test.com", "password": "Password123!"}
    client.post("/users/register", json=user_data)
    
    verify_payload = {
        "email": "security@test.com",
        "token": "WRONG_TOKEN_12345"
    }
    response = client.post("/users/verify", json=verify_payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_verification_fails_for_missing_user(client):
    """
    Identity check: Reject verification for emails not in the system
    """
    verify_payload = {
        "email": "ghost@herenciapp.com",
        "token": "anytoken"
    }
    response = client.post("/users/verify", json=verify_payload)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]