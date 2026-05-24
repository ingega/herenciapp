# src/api/v1/auth/auth.py
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from typing import Optional
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from src.config import settings

# Configuration variables from your settings (with safe local fallbacks for development)
SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "SUPER_SECRET_COMPLEX_KEY_CHANGE_THIS_IN_PRODUCTION")
ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure signed JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration timestamp to the payload
    to_encode.update({"exp": expire})
    
    # Encode and return the string token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> Optional[dict]:
    """
    Decodes and verifies the signature and expiration of a JWT token.
    Returns the payload dictionary if valid, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
async def get_current_user_from_cookie(request: Request) -> dict:
    """
    FastAPI Dependency that extracts and validates the JWT from an HttpOnly cookie.
    If valid, returns the user data payload.
    If invalid or missing, raises an authorization exception or handles redirection.
    """
    # 1. Look for the cookie named 'access_token' in the incoming request
    token = request.cookies.get("access_token")
    
    if not token:
        # No token found! Raise a credentials exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # 2. Verify the signature and expiration using your utility function
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired"
        )
        
    # 3. Return the payload data (e.g., {"sub": "user@email.com", "role": "admin"})
    return payload