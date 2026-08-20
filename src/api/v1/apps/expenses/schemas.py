from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from src.api.v1.apps.expenses.models import ExpenseCategory


class ExpenseBase(SQLModel):
    """Base schema shared by create/read/update representations."""
    date: datetime = Field(default_factory=datetime.utcnow)
    expense: str = Field(max_length=255, description="Short description of the expense")
    category: Optional[ExpenseCategory] = None
    quantity: Optional[float] = None
    total: Optional[float] = None


class ExpenseCreate(ExpenseBase):
    """Schema used when creating a new expense."""
    pass


class ExpenseRead(ExpenseBase):
    """Schema used when returning expense data from the API."""
    id: int


class ExpenseUpdate(SQLModel):
    """Schema used for partial updates (PATCH). All fields optional."""
    date: Optional[datetime] = None
    expense: Optional[str] = Field(default=None, max_length=255)
    category: Optional[ExpenseCategory] = None
    quantity: Optional[float] = None
    total: Optional[float] = None


# Ensure Pydantic/SQLModel internals are rebuilt (compat)
ExpenseRead.model_rebuild()
ExpenseCreate.model_rebuild()
ExpenseUpdate.model_rebuild()
