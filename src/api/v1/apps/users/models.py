# src/models/auth.py

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class User(SQLModel, table=True):
    # id bigserial maps to Optional[int] with primary_key=True
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    # Verification Fields
    verification_code: Optional[str] = None
    # Security best practice: Codes should expire (e.g., 15 minutes)
    code_expires_at: Optional[datetime] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_modification: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))