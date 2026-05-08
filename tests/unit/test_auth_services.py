import pytest
from sqlmodel import Session
from src.api.v1.apps.users.services import get_user_by_email, create_user
from src.api.v1.apps.users.models import User

def test_email_normalization_works(session: Session):
    # Setup: Use the service to create the user so we test the full flow
    email = "Admin@Herenciapp.com"
    create_user(session=session, email=email, plain_password="password123")

    # Execution: Search with messy casing and spaces
    messy_email = "  ADMIN@herenciapp.com  "
    found_user = get_user_by_email(session=session, email=messy_email)

    # Assertion
    assert found_user is not None
    # Verify it was stored normalized (lowercase)
    assert found_user.email == "admin@herenciapp.com"

def test_create_duplicate_user_fails(session: Session):
    email = "test@test.com"
    create_user(session, email, "pass123")
    
    # Try to create the same user again
    duplicate = create_user(session, email, "different_pass")
    
    assert duplicate is None