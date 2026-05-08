from asyncio.log import logger
from datetime import datetime, timezone
from typing import Optional
import pytest, time
from sqlmodel import Session
from src.api.v1.apps.users.services import get_user_by_email, create_user
from src.api.v1.apps.users.services import get_user_by_id, get_all_users, update_user, delete_user
from src.api.v1.apps.users.models import User
from src.api.v1.auth.utils import hash_password

# get functions

def test_get_user_by_id_logic(session: Session):
    """
    Verifies that we can find a specific user by their unique ID.
    This is the foundation for profile pages and specific edits.
    """
    # 1. Setup: Create a real user
    original_user = create_user(session, "find_me@test.com", "secure123")
    user_id = original_user.id

    # 2. Execution
    found_user = get_user_by_id(session, user_id)

    # 3. Assertion
    assert found_user is not None
    assert found_user.id == user_id
    assert found_user.email == "find_me@test.com"

def test_get_user_by_id_returns_none_if_missing(session: Session):
    """
    Ensures the service returns None (not a crash) if the ID is invalid.
    """
    found = get_user_by_id(session, 8888)
    assert found is None

def test_get_all_users_logic(session: Session):
    """
    Tests the listing logic. Crucial for the Admin dashboard.
    """
    # 1. Setup: Add multiple users
    create_user(session, "user1@test.com", "pass1")
    create_user(session, "user2@test.com", "pass2")
    create_user(session, "user3@test.com", "pass3")

    # 2. Execution
    users_list = get_all_users(session)

    # 3. Assertion
    assert len(users_list) == 3
    # Check that it's a list of User objects
    assert users_list[0].email == "user1@test.com"

def test_get_all_users_empty_database(session: Session):
    """
    Ensures that if the kitchen is empty, we get an empty list [],
    not a None or an error. This prevents frontend loops from crashing.
    """
    users_list = get_all_users(session)
    assert users_list == []
    assert len(users_list) == 0

def test_get_user_by_email_logic(session: Session):
    """
    Verifies that we can find a specific user by their email.
    This is the foundation for profile pages and specific edits.
    """
    # 1. Setup: Create a real user
    _ = create_user(session, "find_me@test.com", "secure123")

    # 2. Execution: Find the user by email
    found_user = get_user_by_email(session, "find_me@test.com")

    # 3. Assertion
    assert found_user is not None
    assert found_user.email == "find_me@test.com"

def test_get_user_by_email_returns_none_if_missing(session: Session):
    """
    Ensures the service returns None (not a crash) if the email is invalid.
    """
    found = get_user_by_email(session, "nonexistent@test.com")
    assert found is None

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

# post functions

def test_create_duplicate_user_fails(session: Session):
    email = "test@test.com"
    create_user(session, email, "pass123")
    
    # Try to create the same user again
    duplicate = create_user(session, email, "different_pass")
    
    assert duplicate is None

# update functions
def test_update_user_logic(session: Session):
    """
    Tests email normalization, password hashing, and status change
    all in one update cycle.
    """
    # 1. Setup
    user = create_user(session, "original@test.com", "old-pass")
    user_id = user.id

    # 2. Execution
    updated = update_user(
        session, 
        user_id, 
        email="  NEW@test.com  ", 
        plain_password="new-secure-password",
        is_active=False
    )

    # 3. Assertion
    assert updated is not None
    assert updated.email == "new@test.com"  # Normalization check
    assert updated.is_active is False        # Status check
    # We don't check the hash value directly, but we check it changed
    assert updated.hashed_password != hash_password("old-pass") 

def test_update_user_timestamp_changes(session: Session):
    """
    Crucial for Herenciapp: verify that last_modification is 
    updated on every save.
    """
    # 1. Setup
    user = create_user(session, "time@test.com", "pass123")
    initial_mod_time = user.last_modification
    
    # We add a tiny sleep to ensure the clock moves forward
    # (Important for high-speed automated tests)
    time.sleep(0.01) 

    # 2. Execution
    update_user(session, user.id, is_active=True)
    session.refresh(user)

    # 3. Assertion
    assert user.last_modification > initial_mod_time
    print(f"Timestamp updated from {initial_mod_time} to {user.last_modification}")

# delete functions

def test_delete_user_lifecycle(session: Session):
    """
    Verifies that a user is truly removed from the kitchen.
    """
    # 1. Setup
    user = create_user(session, "delete_me@test.com", "pass")
    user_id = user.id

    # 2. Execution & Assertion
    # First, verify they exist
    assert get_user_by_id(session, user_id) is not None
    
    # Delete them
    success = delete_user(session, user_id)
    assert success is True

    # Verify they are gone
    assert get_user_by_id(session, user_id) is None

def test_delete_non_existent_user_returns_false(session: Session):
    """
    Ensures our kitchen doesn't crash if we try to delete someone who isn't there.
    """
    # 1. Setup
    invalid_id = 9999 

    # 2. Execution
    success = delete_user(session, invalid_id)
    
    # 3. Assertion
    assert success is False, "Service should return False when user ID does not exist"
    