from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Float, DateTime, String


class ExpensesCategory(SQLModel, table=True):
    __tablename__ = "expenses_category"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        unique=True,
    )

    active: bool = Field(
        default=True,
        nullable=False,
    )


class Expenses(SQLModel, table=True):

    __tablename__ = "expenses"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    date: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
        ),
        default_factory=datetime.utcnow,
    )

    expense: str = Field(
        sa_column=Column(
            String(length=255),
            nullable=False,
        )
    )

    category: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(length=100),
            nullable=True,
        )
    )

    quantity: Optional[float] = Field(
        sa_column=Column(
            Float,
            nullable=True,
        )
    )

    total: Optional[float] = Field(
        sa_column=Column(
            Float,
            nullable=True,
        )
    )