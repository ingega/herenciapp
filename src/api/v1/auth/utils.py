# src/api/v1/auth/utils.py
import secrets
import string
from bcrypt import hashpw, gensalt, checkpw

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = gensalt()
    hashed = hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored hash.
    Returns True if they match, False otherwise.
    """
    return checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def generate_verification_token(length: int = 6) -> str:
    """
    Generates a secure, random numeric string for email verification.
    Default is 6 digits (e.g., '529310').
    """
    # We use digits only to make it easy for restaurant staff to 
    # read and type from their phones.
    return "".join(secrets.choice(string.digits) for _ in range(length))