from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password debe contener al menos una letra mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password debe contener al menos una letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Password debe contener al menos un número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password debe contener al menos un símbolo")
        return v

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserVerificationSchema(BaseModel):
    """
    Schema to validate the payload for the email verification endpoint.
    """
    email: EmailStr = Field(..., description="The email address of the user to verify")
    token: str = Field(..., min_length=6, max_length=6, description="The 6-digit verification code")

    model_config = ConfigDict(from_attributes=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@herenciapp.com",
                "token": "123456"
            }
        }

class TokenCreate(BaseModel):
    """
    Schema for creating a verification token, used internally in the service layer.
    """
    user_id: int
    token: str
    expires_at: datetime