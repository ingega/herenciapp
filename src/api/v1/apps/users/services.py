# src/api/v1/apps/users/services.py
from datetime import datetime, timezone
import logging
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.api.v1.apps.users.models import User
from src.api.v1.auth.utils import hash_password

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