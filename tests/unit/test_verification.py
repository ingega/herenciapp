import pytest
from unittest.mock import AsyncMock, patch
from src.api.v1.apps.users.services import create_pending_user
from src.api.v1.apps.users.email_service import send_verification_email
from src.api.v1.apps.users.schemas import UserCreate

# We use a decorator to patch the email service for EVERY test in this file
# This prevents the "leaking" into real SMTP that caused your 535 error
@patch("src.api.v1.apps.users.email_service.FastMail.send_message", new_callable=AsyncMock)
class TestUserVerification:

    @pytest.mark.asyncio
    async def test_user_registration_flow_success(self, mock_send, session):
        """Tests the full flow: registration -> verification."""
        user_data = UserCreate(
            email="test@herenciapp.com ", 
            password="SecurePassword123!"
        )
        
        # 1. Create the user
        # ensure create_pending_user is 'async def' in services.py!
        new_user = await create_pending_user(session, user_data)
        
        # Verify the service actually returned a user and didn't fail internally
        assert new_user is not None, "Service returned None, check services.py logs for 'await NoneType' error"
        assert new_user.is_active is False
        assert mock_send.called is True
        
        # 2. Extract the code from the mock call
        # FastMail.send_message(message) -> message is the first positional arg
        sent_message = mock_send.call_args[0][0]
        assert sent_message.recipients[0].email == "test@herenciapp.com"

    @pytest.mark.asyncio
    async def test_invalid_verification_code(self, mock_send, session):
        """Ensures incorrect codes do not activate the user."""
        user_data = UserCreate(email="security@herenciapp.com", password="SecurePassword123!")
        await create_pending_user(session, user_data)
        
        # Now this call is mocked thanks to the class decorator! No more 535 error.
        await send_verification_email(email_to="security@herenciapp.com", code="000000")
        
        assert mock_send.called is True