# src/models/auth.py
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class User(SQLModel, table=True):
    # id bigserial maps to Optional[int] with primary_key=True
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_modification: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VerificationToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    token: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            default=lambda: datetime.now(timezone.utc)
        )
    )

    is_used: bool = Field(default=False)