# src/api/v1/apps/users/router.py
import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.config import get_settings, Settings
from src.api.v1.apps.users import services, schemas
from src.api.v1.auth import services as auth_services

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def register_user(
    user_in: schemas.UserCreate, 
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    # 1. Logic Check: Does the user already exist?
    existing_user = await services.get_user_by_email(db, email=user_in.email)
    # debug
    logger.info(f"Checking if user with email {user_in.email} already exists.")

    if existing_user:
        logger.info(f"Database result for {user_in.email}: {existing_user}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This email is already part of the Herenciapp family."
        )
    
    # 2. Execution: Create inactive user & send verification email
    try:
        new_user = await services.create_pending_user(db, user_in)
        return new_user
    except Exception as e:
        # error handling: log the error and notify the user
        # Don't leak sensitive server info in the detail
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There is a problem sending your verification email. Please try again."
        )

@router.post("/verify", response_model=schemas.UserOut)
async def verify_user_email(
    payload: schemas.UserVerificationSchema, 
    session: Session = Depends(get_db)
):
    
    # 1. Identity Check: Does the user even exist?
    user = await services.get_user_by_email(session, payload.email)
    if not user:
        print("I think: Attempted verification for non-existent email.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 2. Validity Check: Is the token correct and active?
    is_valid = await auth_services.verify_registration_token(
        session, 
        user=user, 
        token=payload.token
    )

    if not is_valid:
        print("I think: Token is either wrong, expired, or already used.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # 3. Activation: Flip the switch!
    activated_user = await services.activate_user(session, user)
    
    print(f"User {payload.email} is now officially active.")
    return activated_user