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