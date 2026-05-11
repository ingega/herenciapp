# src/api/v1/apps/users/services.py
from datetime import datetime, timezone, timedelta
import logging
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.api.v1.apps.users.models import User
from src.api.v1.apps.users.schemas import UserCreate
from src.api.v1.auth.utils import hash_password, generate_verification_token
from src.api.v1.apps.users.email_service import send_verification_email

logger = logging.getLogger(__name__)

def get_user_by_email(session: Session, email: str) -> User | None:
    """Retrieves a user by email with safety handling."""
    try:
        normalized_email = email.lower().strip()
        statement = select(User).where(User.email == normalized_email)
        return session.exec(statement).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error during user retrieval: {e}")
        return None

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a single user by their primary key.
    Returns the User object or None if not found.
    """
    try:
        user = session.get(User, user_id)
        if not user:
            logger.info(f"User lookup failed for ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error fetching user by ID {user_id}: {e}")
        return None

def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves a list of users with pagination.
    skip: Number of records to ignore.
    limit: Maximum number of records to return.
    """
    try:
        # Use select(User) to stay within the SQLModel API
        statement = select(User).offset(skip).limit(limit)
        results = session.exec(statement)
        users = results.all()
        return users
    except Exception as e:
        logger.error(f"Error fetching user list: {e}")
        return []

def create_user(session: Session, email: str, plain_password: str) -> User | None:
    """Creates a user with full transaction safety and duplicate checks."""
    # Logic check before database hit
    if get_user_by_email(session, email):
        logger.warning(f"Registration blocked: {email} already exists.")
        return None

    try:
        new_user = User(
            email=email.lower().strip(),
            hashed_password=hash_password(plain_password),
            is_active=True
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info(f"User {email} created successfully.")
        return new_user
    except IntegrityError:
        session.rollback()
        logger.warning(f"Integrity error: Duplicate email race condition for {email}")
        return None
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to create user {email}: {e}")
        return None

# create a temporary user, waiting for email confirmation before activating the account
async def create_pending_user(session: Session, user_data: UserCreate) -> User | None:
    """
    Creates a new user in an inactive state and prepares a verification code.
    Returns the User object if successful, None if the email is taken or an error occurs.
    """
    # 1. Normalization (The "Veteran" move to avoid duplicate accounts)
    email_clean = user_data.email.lower().strip()
    
    try:
        # 2. Check if user already exists before attempting insertion
        existing_user = session.exec(select(User).where(User.email == email_clean)).first()
        if existing_user:
            logger.warning(f"Registration attempt for existing email: {email_clean}")
            return None

        # 3. Prepare the database object
        db_user = User(
            email=email_clean,
            hashed_password=hash_password(user_data.password),
            is_active=False,  # Locked until verified
            verification_code=generate_verification_token(),
            # Set expiration for 15 minutes from now
            code_expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
        )
        
        await send_verification_email(
            email_to=db_user.email, 
            code=db_user.verification_code
        )

        session.add(db_user)
        session.commit() # The critical point where failures usually happen
        session.refresh(db_user)
        
        # 4. Success Log
        logger.info(f"Pending user created successfully: {email_clean}")
        return db_user

    except IntegrityError as e:
        # This catches race conditions where two users try to register the same email simultaneously
        session.rollback()
        logger.error(f"Database integrity error during registration for {email_clean}: {str(e)}")
        return None
    except Exception as e:
        # Catch-all for unexpected issues (connection drops, disk full, etc.)
        session.rollback()
        logger.critical(f"Unexpected system error creating user {email_clean}: {str(e)}")
        return None

def update_user(session: Session, user_id: int, email: str | None = None, 
                plain_password: str | None = None, is_active: bool | None = None) -> User | None:
    """Updates user info with rollback safety."""
    try:
        user = session.get(User, user_id)
        if not user:
            return None
        
        if email:
            user.email = email.lower().strip()
        if plain_password:
            user.hashed_password = hash_password(plain_password)
        if is_active is not None:
            user.is_active = is_active

        # Update the last modification timestamp
        user.last_modification = datetime.now(timezone.utc)


        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except SQLAlchemyError as e:
        # clean up the transaction to avoid locking issues
        session.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        return None

def delete_user(session: Session, user_id: int) -> bool:
    """
    Permanently removes a user. In a real restaurant, I will use 
    'soft delete', but for the MVP, I'll do a hard delete.
    """
    try:
        user = session.get(User, user_id)
        if not user:
            return False
            
        session.delete(user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        return False