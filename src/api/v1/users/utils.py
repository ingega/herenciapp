# src/api/v1/auth/utils.py
from bcrypt import hashpw, gensalt

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = gensalt()
    hashed = hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')