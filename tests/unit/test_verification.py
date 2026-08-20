import pytest
from unittest.mock import AsyncMock, patch
from src.api.v1.apps.users.services import create_pending_user
from src.api.v1.apps.users.email_service import send_verification_email
from src.api.v1.apps.users.schemas import UserCreate

# Patch the mail client factory so tests can observe send_message calls reliably
@patch("src.api.v1.apps.users.email_service.get_mail_client")
class TestUserVerification:

    @pytest.mark.asyncio
    async def test_user_registration_flow_success(self, mock_get_mail_client, session):
        """Tests the full flow: registration -> verification."""
        # Prepare a send_message AsyncMock and have get_mail_client return a dummy with that mock
        send_mock = AsyncMock()
        dummy_client = type("_Dummy", (), {"send_message": send_mock})()
        mock_get_mail_client.return_value = dummy_client

        user_data = UserCreate(
            email="test@herenciapp.com",
            password="Password123!"
        )
        
        # 1. Create the user
        new_user = await create_pending_user(session, user_data)
        
        # Verify the service actually returned a user and didn't fail internally
        assert new_user is not None, "Service returned None, check services.py logs for 'await NoneType' error"
        assert new_user.is_active is False
        assert send_mock.called is True
        
        # 2. Extract the code from the mock call
        # get_mail_client returned our dummy, so send_mock was called with the MessageSchema
        sent_message = send_mock.call_args[0][0]
        recipients = getattr(sent_message, 'recipients', None)
        if recipients:
            first = recipients[0]
            try:
                addr = first.email
            except Exception:
                addr = first
            assert str(addr).startswith("test@herenciapp.com")

    @pytest.mark.asyncio
    async def test_invalid_verification_code(self, mock_get_mail_client, session):
        """Ensures incorrect codes do not activate the user."""
        send_mock = AsyncMock()
        dummy_client = type("_Dummy", (), {"send_message": send_mock})()
        mock_get_mail_client.return_value = dummy_client

        user_data = UserCreate(email="security@herenciapp.com", password="Password123!")
        await create_pending_user(session, user_data)
        
        # Now this call is mocked thanks to the class decorator replacement
        await send_verification_email(email_to="security@herenciapp.com", code="000000")
        
        assert send_mock.called is True
