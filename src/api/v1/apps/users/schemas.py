from pydantic import BaseModel, EmailStr, Field, field_validator
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