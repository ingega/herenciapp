# src/authz/authz.py
from fastapi import HTTPException, status, Depends
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.api.v1.apps.users.models import User  # Adjust this import to point to your User database model

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        """Accepts a single string role or a list of acceptable roles"""
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user_from_cookie)) -> User:
        """
        FastAPI dependency handler that automatically receives the authenticated user
        from your cookie extraction method, verifies permissions, and passes the user forward.
        """
        # Handle dict or model field structures flexibly based on your token decoder logic
        user_role = current_user.role if isinstance(current_user, User) else current_user.get("role")
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. This endpoint requires one of the following roles: {self.allowed_roles}"
            )
            
        return current_user