from asyncio.log import logger
import time, pytest
from sqlmodel import Session
from src.api.v1.apps.users.services import get_user_by_email, create_user
from src.api.v1.apps.users.services import get_user_by_id, get_all_users, update_user, delete_user
from src.api.v1.auth.utils import hash_password
from src.api.v1.apps.users.schemas import UserCreate

# get functions

@pytest.mark.asyncio
async def test_get_user_by_id_logic(session: Session):
    # 1. Setup: Create a schema object
    user_in = UserCreate(email="find_me@test.com", password="Secure123!")
    
    # 2. Execution: Await the creation

    new_user = await create_user(session, user_in)
    
    # Safety check for DB pollution
    if new_user is None:
        new_user = await get_user_by_email(session, "find_me@test.com")
    
    user_id = new_user.id
    
    # 3. Action: Retrieve
    retrieved_user = get_user_by_id(session, user_id)
    
    assert retrieved_user.email == "find_me@test.com"

async def test_get_user_by_id_returns_none_if_missing(session: Session):
    """
    Ensures the service returns None (not a crash) if the ID is invalid.
    """
    found = await get_user_by_id(session, 8888)
    assert found is None

@pytest.mark.asyncio
async def test_get_all_users_logic(session: Session):
    # 1. Setup: MUST use await and UserCreate schemas
    await create_user(session, UserCreate(email="u1@t.com", password="Password1234!"))
    await create_user(session, UserCreate(email="u2@t.com", password="Password1234!"))
    
    # 2. Execution (get_all_users is currently sync in your file)
    users = get_all_users(session)
    
    # 3. Assert
    assert len(users) >= 2

def test_get_all_users_empty_database(session: Session):
    """
    Ensures that if the kitchen is empty, we get an empty list [],
    not a None or an error. This prevents frontend loops from crashing.
    """
    users_list = get_all_users(session)
    assert users_list == []
    assert len(users_list) == 0

@pytest.mark.asyncio
async def test_get_user_by_email_logic(session: Session):
    user_in = UserCreate(email="email_test@test.com", password="Password123!")
    await create_user(session, user_in)
    
    # MUST await this one
    user = await get_user_by_email(session, "email_test@test.com")
    
    assert user is not None
    assert user.email == "email_test@test.com"

@pytest.mark.asyncio
async def test_get_user_by_email_returns_none_if_missing(session: Session):
    """
    Ensures the service returns None (not a crash) if the email is invalid.
    """
    found = get_user_by_email(session, "nonexistent@test.com")
    assert found is None

@pytest.mark.asyncio
async def test_email_normalization_works(session: Session):
    # Setup: Use the service to create the user so we test the full flow
    email = "Admin@Herenciapp.com"
    new_user = UserCreate(email=email, password="Password123!")
    await create_user(session=session, user_in=new_user)

    # Execution: Search with messy casing and spaces
    messy_email = "  ADMIN@herenciapp.com  "
    found_user = await get_user_by_email(session=session, email=messy_email)

    # Assertion
    assert found_user is not None
    # Verify it was stored normalized (lowercase)
    assert found_user.email == "admin@herenciapp.com"

# post functions

@pytest.mark.asyncio
async def test_create_duplicate_user_fails(session: Session):
    email = "test@test.com"
    new_user = UserCreate(email=email, password="Wrongpass123!")
    await create_user(session, user_in=new_user)

    # Try to create the same user again
    duplicate = await create_user(session, user_in=UserCreate(email=email, password="Different_pass123!"))
    
    assert duplicate is None

# update functions
@pytest.mark.asyncio
async def test_update_user_logic(session: Session):
    """
    Tests email normalization, password hashing, and status change
    all in one update cycle.
    """
    # 1. Setup
    new_user = UserCreate(email="original@test.com", password="Old-pass1234!")
    user = await create_user(session, user_in=new_user)
    user_id = user.id

    # 2. Execution
    updated = update_user(
        session, 
        user_id, 
        email="  NEW@test.com  ", 
        plain_password="New-secure-password1!",
        is_active=False
    )

    # 3. Assertion
    assert updated is not None
    assert updated.email == "new@test.com"  # Normalization check
    assert updated.is_active is False        # Status check
    # We don't check the hash value directly, but we check it changed
    assert updated.hashed_password != hash_password("Old-pass1234!") 

@pytest.mark.asyncio
async def test_update_user_timestamp_changes(session: Session):
    """
    Crucial for Herenciapp: verify that last_modification is 
    updated on every save.
    """
    # 1. Setup
    new_user = UserCreate(email="time@test.com", password="Password123!")
    user = await create_user(session, user_in=new_user)
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

@pytest.mark.asyncio
async def test_delete_user_lifecycle(session: Session):
    # 1. Setup
    user_in = UserCreate(email="delete_me@test.com", password="Password123!")
    user = await create_user(session, user_in)
    user_id = user.id

    # 2. Execution & Assertion
    assert get_user_by_id(session, user_id) is not None
    
    # Check your services.py: if delete_user is sync, keep it like this:
    success = delete_user(session, user_id)
    assert success is True
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
    