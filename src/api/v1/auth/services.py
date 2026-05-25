# src/api/v1/auth/services.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from venv import logger
from sqlmodel import Session, select
from src.api.v1.apps.users.models import User, VerificationToken
from src.api.v1.apps.users.schemas import TokenCreate


async def create_verification_token(session: Session, 
                                    user_id: int, 
                                    token: str) -> Optional[VerificationToken]:
    try:
        # Create the actual Database Model instance
        db_token = VerificationToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        session.add(db_token)
        # Note: If your session is sync (from get_db), use session.commit()
        # If it's an AsyncSession, keep await session.commit()
        session.commit() 
        session.refresh(db_token)
        return db_token
    except Exception as e:
        logger.error(f"Error creating verification token for user {user_id}: {e}")
        session.rollback()
        return None

async def verify_registration_token(db: Session, 
                                    user: User, 
                                    token: str) -> bool:
    """
    Validates the 6-digit code against the database record for a specific user.
    """
    
    # 1. Fetch the token record
    # create a statement first
    statement = select(VerificationToken).where(
        VerificationToken.user_id == user.id,
        VerificationToken.token == token,
        VerificationToken.is_used == False
    )
    # execute the statement and get the first result
    db_token = db.exec(statement).first()

    if not db_token:
        logger.warning(f"Token not found or already used for user {user.id}")
        return False

    # 2. Check Expiration
    # I will compare the current UTC time with the token's expiration timestamp
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        logger.warning(f"Token expired for user {user.id}")
        return False

    # 3. Mark as used
    # To prevent 'replay attacks', we mark the token so it can't be used twice
    db_token.is_used = True
    db.add(db_token)
    db.commit()
    
    return True