# src/api/v1/auth/services.py
from src.models.auth import User
from src.database import get_session

def create_user(email: str, hashed_password: str) -> User:
    """Creates a new user in the database."""
    with get_session() as session:
        user = User(email=email, hashed_password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_user_by_email(email: str) -> User | None:
    """Retrieves a user from the database by email."""
    with get_session() as session:
        # verify that email exists in the database, if not return None
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return None
        return user

def get_user_by_id(user_id: int) -> User | None:
    """Retrieves a user from the database by ID."""
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return user