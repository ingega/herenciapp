# src/api/v1/auth/router.py
import logging
from fastapi import APIRouter, Request, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.api.v1.auth.auth import create_access_token
from src.config import settings
from src.database import get_db
from src.api.v1.apps.users.services import get_user_by_email
from src.api.v1.auth.utils import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

templates = Jinja2Templates(directory="src/templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "config": settings
        }
    )

@router.post("/login")
async def login_process(
    request: Request,                  # 1. Inject the raw HTTP request parameter
    session: Session = Depends(get_db)
):
    # 2. Extract and parse the raw incoming JSON body payload manually
    body = await request.json()
    email_input = body.get("email", "").strip()
    password_input = body.get("password", "") # Matches your JS field name perfectly

    # 3. Fetch user using your pre-existing DRY utility
    user = await get_user_by_email(session, email_input)
    
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password."
    )
    
    if not user:
        raise auth_exception
        
    # 4. Validate password via your native bcrypt helper
    if not verify_password(password_input, user.hashed_password):
        raise auth_exception
        
    # 5. Check account activation state
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is currently inactive. Please contact support."
        )

    # 6. Generate token payload utilizing real data from the user model
    token_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }
    access_token = create_access_token(data=token_payload)

    # 7. Simple, fast dictionary response mapping what your javascript expects
    response = JSONResponse(
        content={
            "status": "success",
            "redirect_url": "/main"
        }
    )

    # 8. Drop the secure token directly into the client's cookie pipeline
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600,
        expires=3600,
        samesite="lax",
        secure=settings.COOKIE_SECURE 
    )

    return response