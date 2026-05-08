# src/api/v1/auth/utils.py
from bcrypt import hashpw, gensalt
from bcrypt import checkpw

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