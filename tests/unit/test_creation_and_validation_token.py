# tests/unit/test_creation_and_validation_token.py
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, patch
from src.api.v1.auth.auth import create_access_token, verify_access_token

"""
The following tests validate the creation and verification of JWT tokens using the functions 
defined in src/api/v1/auth/auth.py.
Test will cover:
1. Creation of a token with a specific payload and expiration time.
2. Verification of a valid token to ensure it returns the correct payload.
3. Verification of an expired token to ensure it returns None.
"""

@patch("src.api.v1.apps.users.email_service.FastMail", autospec=True)
class TestTokenCreationAndValidation:
    def test_create_and_verify_token(self, mock_send):
        # Define a sample payload
        payload = {"user_id": 123, "username": "testuser@test.com"}
        
        # Create a token with a short expiration time (1 minute)
        token = create_access_token(data=payload, expires_delta=timedelta(minutes=1))
        
        # Verify the token immediately (should be valid)
        verified_payload = verify_access_token(token)
        assert verified_payload is not None
        assert verified_payload["user_id"] == payload["user_id"]
        assert verified_payload["username"] == payload["username"]
    
    def test_expired_token(self, mock_send):
        # Define a sample payload
        payload = {"user_id": 456, "username": "expireduser@expired.com"}
        
        # Create a token with an expiration time in the past
        token = create_access_token(data=payload, expires_delta=timedelta(minutes=-1))
        
        # Verify the token (should be expired and return None)
        verified_payload = verify_access_token(token)
        assert verified_payload is None