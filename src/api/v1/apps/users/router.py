# src/api/v1/apps/users/router.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.config import get_settings, Settings
from src.api.v1.apps.users import services, schemas

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def register_user(
    user_in: schemas.UserCreate, 
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    # 1. Logic Check: Does the user already exist?
    # We refer to 'get_user_by_email' in our services module
    existing_user = services.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This email is already part of the Herencia family."
        )
    
    # 2. Execution: Create inactive user & send verification email
    # I'll call our async service that handles the password hashing and email logic
    try:
        new_user = await services.create_pending_user(db, user_in)
        return new_user
    except Exception as e:
        # Production-grade error handling: log the error and notify the user
        # We don't want to leak sensitive server info in the detail
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The kitchen had a hiccup sending your verification email. Please try again."
        )