# tests/integration/test_using_verification.py
from unittest.mock import patch, AsyncMock
from fastapi import status
from sqlmodel import select
from src.api.v1.apps.users.models import VerificationToken

@patch("src.api.v1.apps.users.email_service.get_mail_client")
class TestUserVerificationEndpoints:

    def test_user_verification_flow_success(self, mock_get_mail_client, client, session):
        """Tests the full register -> verify API flow without sending real emails."""
        # Configure the get_mail_client mock to return an object with an AsyncMock send_message
        send_mock = AsyncMock()
        dummy_client = type("_Dummy", (), {"send_message": send_mock})()
        mock_get_mail_client.return_value = dummy_client

        user_data = {
            "email": "partner_test@herenciapp.com",
            "password": "SecurePassword123!"
        }
        
        # 1. Register - Triggers email service under the hood
        register_response = client.post("/users/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Verify the mock intercepted the call!
        assert send_mock.called is True

        # 2. Extract Token from DB using the sync session
        db_token = session.exec(select(VerificationToken)).first()
        assert db_token is not None
        
        # 3. Verify via endpoint
        verify_payload = {
            "email": user_data["email"],
            "token": db_token.token
        }
        verify_response = client.post("/users/verify", json=verify_payload)
        assert verify_response.status_code == status.HTTP_200_OK

    def test_verification_fails_with_wrong_token(self, mock_get_mail_client, client, session):
        """Ensures endpoint rejects bad verification input codes."""
        send_mock = AsyncMock()
        dummy_client = type("_Dummy", (), {"send_message": send_mock})()
        mock_get_mail_client.return_value = dummy_client

        user_data = {"email": "security@test.com", "password": "Password123!"}
        
        # Registration triggers email mock
        client.post("/users/register", json=user_data)
        assert send_mock.called is True
        
        verify_payload = {
            "email": "security@test.com",
            "token": "000000" # Explicitly wrong code
        }
        response = client.post("/users/verify", json=verify_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verification_fails_for_missing_user(self, mock_get_mail_client, client):
        """Identity check: Reject verification for emails not in the system."""
        # In this test we don't need the mail client, but ensure mock exists
        send_mock = AsyncMock()
        dummy_client = type("_Dummy", (), {"send_message": send_mock})()
        mock_get_mail_client.return_value = dummy_client

        verify_payload = {
            "email": "ghost@herenciapp.com",
            "token": "000000"
        }
        response = client.post("/users/verify", json=verify_payload)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
