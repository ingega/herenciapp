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