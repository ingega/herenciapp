# src/api/v1/apps/users/services.py
import logging
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

def update_user(session: Session, user_id: int, email: str = None, plain_password: str = None) -> User | None:
    """Updates user info with rollback safety."""
    try:
        user = session.get(User, user_id)
        if not user:
            return None
        
        if email:
            user.email = email.lower().strip()
        if plain_password:
            user.hashed_password = hash_password(plain_password)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        return None