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

    category: Optional[ExpenseCategory] = Field(
        sa_column=Column(
            SAEnum(
                ExpenseCategory,
                name="expensecategory",
                values_callable=lambda enum: [
                    item.value for item in enum
                ],
            ),
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