from enum import Enum
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum as SAEnum, Float, DateTime, String


class ExpenseCategory(str, Enum):
    FOOD = "food"
    BEVERAGES = "beverages"
    DESSERTS = "desserts"
    OPERATION = "operation"


class Expenses(SQLModel, table=True):
    __tablename__ = "expenses"

    id: Optional[int] = Field(default=None, primary_key=True)

    # the date of the expense (not nullable)
    date: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
    )

    # short description of the expense (not nullable)
    expense: str = Field(sa_column=Column(String(length=255), nullable=False))

    # category stored as a PostgreSQL/SQLAlchemy Enum
    category: Optional[ExpenseCategory] = Field(
        sa_column=Column(SAEnum(ExpenseCategory), nullable=True)
    )

    quantity: Optional[float] = Field(sa_column=Column(Float, nullable=True))

    total: Optional[float] = Field(sa_column=Column(Float, nullable=True))
