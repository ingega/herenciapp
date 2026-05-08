import logging
from sqlalchemy.exc import IntegrityError
from src.models.auth import User
from src.database import get_session
from src.api.auth.utils import hash_password # We'll create this next

# Set up logging to track production issues
logger = logging.getLogger(__name__)

def create_user(email: str, plain_password: str) -> User | None:
    """
    Robustly creates a new user.
    Handles hashing, transaction integrity, and duplicate prevention.
    """
    # 1. Verification: Check if user exists before even opening a transaction
    if get_user_by_email(email):
        logger.warning(f"Registration attempt for existing email: {email}")
        return None

    # 2. Security: Hash the password using a strong algorithm (Argon2/Bcrypt)
    hashed_pwd = hash_password(plain_password)

    try:
        with get_session() as session:
            new_user = User(
                email=email.lower().strip(), # Data normalization
                hashed_password=hashed_pwd,
                is_active=True
            )
            
            session.add(new_user)
            # The 'with' block handles the commit, but we wrap it for safety
            session.commit()
            session.refresh(new_user)
            
            logger.info(f"New user created successfully: {email}")
            return new_user

    except IntegrityError as e:
        # Handles race conditions (if two users sign up with same email at exact same ms)
        logger.error(f"Database integrity error creating user {email}: {e}")
        return None
    except Exception as e:
        # Catch-all for connection issues to your AWS Postgres container
        logger.critical(f"Unexpected error creating user {email}: {e}")
        return None

def get_user_by_email(email: str) -> User | None:
    """
    Retrieves a user by email.
    Returns None if not found, ensuring consistent return types.
    """
    with get_session() as session:
        user = session.query(User).filter(User.email == email.lower().strip()).first()
        if not user:
            logger.warning(f"User not found for email: {email}")
        return user